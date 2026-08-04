# Third-party sources

The generated dictionaries below retain their upstream provenance. Exact source
commits and generated-file checksums are recorded in
`tools/upstream_dictionaries.lock.json`.

## `xmjd6.danzi.dict.yaml`

- Upstream: <https://github.com/amorphobia/rime-jiandao>
- Source: `dicts/01.danzi.txt`
- Build-rule reference: `scripts/make_dicts.sh`
- License: GNU Affero General Public License 3.0 or later
- License copy: `licenses/rime-jiandao-AGPL-3.0.txt`

The local synchronization tool reproduces the relevant `make_dicts.sh`
behavior for this repository: it writes an xmjd6-specific Rime header and then
appends the upstream single-character rows unchanged.

## `xmjd6.ice.dict.yaml`

- Upstream: <https://github.com/iDvel/rime-ice>
- Sources: `cn_dicts/base.dict.yaml`, `cn_dicts/ext.dict.yaml`, and
  `cn_dicts/others.dict.yaml`
- License: GNU General Public License 3.0
- License copy: `licenses/rime-ice-GPL-3.0.txt`

Rime-Ice rows are converted from annotated full pinyin to JianDao 6 codes by
`tools/sync_upstream_dictionaries.py`. Existing local dictionaries take
precedence: duplicate text is excluded, then upstream duplicates are removed in
the order `base`, `ext`, `others`. Entries that cannot be aligned to a precise
upstream single-character reading are skipped rather than assigned a guessed
code. Within that source order, higher upstream weights receive shorter codes;
lower-priority homophones receive successive stroke suffixes. Remaining exact
full-code collisions are pruned against the existing local collision-rate
baseline, with no more than eight new combined candidates per code.

## `xmjd6.en.dict.yaml`

- Upstream: <https://github.com/iDvel/rime-ice>
- Sources: `en_dicts/en.dict.yaml` and `en_dicts/en_ext.dict.yaml`
- License: GNU General Public License 3.0
- License copy: `licenses/rime-ice-GPL-3.0.txt`

The two English sources are merged in main-then-extension order. Codes are
normalized to reachable lowercase letter sequences and prefixed with `i` before
the generated dictionary is imported into the main xmjd6 table. This removes
the need for a separate auxiliary English schema while keeping English entries
isolated from JianDao 6 codes.

## Lua input and ZZZC implementation

- Upstream: <https://github.com/wzxmer/rime-txjx>
- Integrated commit: `da5635358e68d337f9858202b3fe5f7f14fc94d0`
- Sources: modular input processor, ZZZC operation-chain implementation,
  completion/reverse-hint optimizations, OpenCC lookup optimizations, newline
  filter, merge scripts, documentation, and regression-test design
- License: MIT
- License copy: `licenses/rime-txjx-MIT.txt`
- Integration lock: `tools/upstream_code.lock.json`

The implementation is adapted rather than copied as a whole: module names are
kept below `lua/xmjd6/`, state keys use the xmjd6 namespace, OpenCC assets stay
below `opencc/xmjd6/`, and the main processor preserves this repository's `i`
English prefix and JianDao 6 top-up behavior. TXJX dictionaries, schema files,
root-level OpenCC data, opaque platform binaries, and project-specific release
configuration are intentionally not imported.
