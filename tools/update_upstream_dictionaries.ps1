[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$Force,
    [string]$Python = "",
    [string]$CacheDirectory = (Join-Path ([IO.Path]::GetTempPath()) "xmjd6-upstream-git-cache")
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -lt 7) {
    throw "This updater requires PowerShell 7 or newer."
}

$RepoRoot = Split-Path -Parent $PSScriptRoot
$LockPath = Join-Path $PSScriptRoot "upstream_dictionaries.lock.json"
$SyncScript = Join-Path $PSScriptRoot "sync_upstream_dictionaries.py"

if (-not $Python) {
    $LocalPixiPython = "D:\Dev\pixi\bin\python.exe"
    if (Test-Path -LiteralPath $LocalPixiPython) {
        $Python = $LocalPixiPython
    }
    else {
        $Python = (Get-Command python -ErrorAction Stop).Source
    }
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory)] [string]$FilePath,
        [Parameter(Mandatory)] [string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
}

function Invoke-Captured {
    param(
        [Parameter(Mandatory)] [string]$FilePath,
        [Parameter(Mandatory)] [string[]]$Arguments
    )
    $Output = @(& $FilePath @Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed ($LASTEXITCODE): $FilePath $($Arguments -join ' ')"
    }
    return $Output
}

Push-Location $RepoRoot
try {
    if ($CheckOnly) {
        Invoke-Checked $Python @($SyncScript, "--check")
        return
    }

    $Lock = Get-Content -LiteralPath $LockPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $SourceSpecs = @(
        [pscustomobject]@{
            Name = "rime_jiandao"
            Source = $Lock.sources.rime_jiandao
        },
        [pscustomobject]@{
            Name = "rime_ice"
            Source = $Lock.sources.rime_ice
        }
    )

    New-Item -ItemType Directory -Path $CacheDirectory -Force | Out-Null
    $ChangedSources = [Collections.Generic.List[string]]::new()

    foreach ($Spec in $SourceSpecs) {
        $Source = $Spec.Source
        $CacheName = $Spec.Name + ".git"
        $GitDirectory = Join-Path $CacheDirectory $CacheName
        $RemoteUrl = "https://github.com/$($Source.repository).git"

        if (-not (Test-Path -LiteralPath (Join-Path $GitDirectory "HEAD"))) {
            Write-Host "Creating upstream cache for $($Source.repository)..."
            Invoke-Checked git @(
                "clone", "--bare", "--filter=blob:none", "--no-tags",
                $RemoteUrl, $GitDirectory
            )
        }

        $RemoteRef = "refs/remotes/origin/$($Source.branch)"
        Invoke-Checked git @(
            "--git-dir=$GitDirectory", "fetch", "--quiet", "--no-tags",
            "--filter=blob:none", "origin",
            "refs/heads/$($Source.branch):$RemoteRef"
        )
        $HeadOutput = @(Invoke-Captured git @(
            "--git-dir=$GitDirectory", "rev-parse", $RemoteRef
        ))
        $HeadCommit = ([string]$HeadOutput[-1]).Trim()
        $LockedCommit = [string]$Source.commit

        if ($HeadCommit -eq $LockedCommit) {
            Write-Host "$($Spec.Name): already at $($HeadCommit.Substring(0, 12))"
            continue
        }

        & git --git-dir=$GitDirectory cat-file -e "$LockedCommit`^{commit}" 2>$null
        if ($LASTEXITCODE -ne 0) {
            Invoke-Checked git @(
                "--git-dir=$GitDirectory", "fetch", "--quiet", "--no-tags",
                "--filter=blob:none", "origin", $LockedCommit
            )
        }

        $TrackedFiles = @($Source.files | ForEach-Object { [string]$_ })
        $ChangedFiles = @(Invoke-Captured git @(
            "--git-dir=$GitDirectory", "diff", "--name-only",
            $LockedCommit, $HeadCommit, "--"
        ) | Where-Object { $TrackedFiles -contains $_.Trim() })

        if ($ChangedFiles.Count -eq 0 -and -not $Force) {
            Write-Host "$($Spec.Name): upstream moved to $($HeadCommit.Substring(0, 12)), but tracked files did not change"
            continue
        }

        Write-Host "$($Spec.Name): $($LockedCommit.Substring(0, 12)) -> $($HeadCommit.Substring(0, 12))"
        foreach ($ChangedFile in $ChangedFiles) {
            Write-Host "  changed: $($ChangedFile.Trim())"
        }
        $ChangedSources.Add($Spec.Name)
    }

    if ($ChangedSources.Count -eq 0) {
        Write-Host "No relevant upstream dictionary changes."
        return
    }

    $Arguments = [Collections.Generic.List[string]]::new()
    $Arguments.Add($SyncScript)
    $Arguments.Add("--write")
    foreach ($SourceName in $ChangedSources) {
        $Arguments.Add("--refresh-source")
        $Arguments.Add($SourceName)
    }
    Invoke-Checked $Python $Arguments.ToArray()
    Invoke-Checked $Python @($SyncScript, "--check")
}
finally {
    Pop-Location
}
