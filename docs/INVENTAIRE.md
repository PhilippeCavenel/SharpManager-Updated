# Archived delivery inventory

Archive date: 6 October 2026. Delivery checksums below refer to the original delivery files.

| Delivery | Retained files | Status | SHA-256 checksum |
| --- | ---: | --- | --- |
| Chronometre_PC1403.zip | 3 | Complete ZIP, CRCs checked | `f1c808623c46cdd4d79c862b5e697e0f7bf780beadf444bc51225ec1543e8f95` |
| QUEENS_QUEST_PC1403_8K.zip | 3 | Complete ZIP, CRCs checked | `14efce1cfeab9578523772d45155f72d006f8be02cc004ba897fc0f6bb3f21ae` |
| SharpManager_PC1403_FluxContinu_V5.zip | 33 | Complete ZIP, CRCs checked | `055d68710ad73fbe0a744172dc6a3628fdd6cf6832f2d3544dbad6b36247c403` |
| SharpManager_PC1403_macOS_M4_V3.zip | 11 | Complete ZIP, CRCs checked | `bacb7dc840d2f302fe9c2bc9cfd0d83f542d5c3393fee04d42f939598429a44a` |
| SharpManager_PC1403_macOS_M4_V4.zip | 11 | Complete ZIP, CRCs checked | `ff33bf17799a6f4ca759b87b28338c7418c1b7e4fee1cf25fc04f6b4b8f2aab1` |
| SharpManager_PC1403_macOS_M4_sources.zip | 11 | Complete ZIP, CRCs checked | `f10feeda2131e646dc3998e9cd5ea7d0980258af16c5484c612004623a6c2afb` |
| SharpManager_PC1403_macOS_V5.1_ACK20s.zip | 11 | Complete ZIP, CRCs checked | `52a8c3c58880094a5ebda04dc48e2fb4dce2350310d63f76bd072d0dd6f2b174` |
| SharpManager_PC1403_macOS_V5.2_Connexion.zip | 12 | Complete ZIP, CRCs checked | `b5d83c0757ce16752d700b1ddc38dd5bdd549670126e75f30d0c0ae3251b1498` |
| Sharp_PC1403_Firmware_Fin200ms_Compile.zip | 22 | Complete ZIP, CRCs checked | `153e8260141aa24508f6ac505f2a501c3d7b1e22ad9789351710ae2ce60656c1` |
| Sharp_PC1403_Firmware_Fin200ms_Essai.zip | 21 | Complete ZIP, CRCs checked | `26942197d7c7e797b435870a9b695f83a060b7c73a80678ec72eecd4cec1802e` |
| Sharp_PC1403_Firmware_FluxContinu_Garde64.zip | 22 | Complete ZIP, CRCs checked | `df944b5d8cae8d4fef448709545fc4cb9161561d9af11e1b039d4cf709d87960` |
| SharpManager_BASIC_PC1403_Sources.zip | 94 | Truncated archive, CRC-checked recovery | `f2e6c7e43982e0e26c6c352b51441ac4a5a2a913de122c7bc0d146c30c767810` |
| SharpManager_BASIC_PC1403_Windows.zip | 21 | Complete ZIP, CRCs checked | `4d3770ba7a2ddc0625689c66f5cf0115b7f316806cbb0ac75addb313010bdb36` |
| SharpManager_PC1403_Windows_V5.2_FluxContinu.zip | 18 | Complete ZIP, CRCs checked | `27846c39582786c5c94bc1bafe938bef607dc5d7a7abc33f45ecb7046e30e8cc` |
| SharpManager_PC1403_Windows_V5.2_Sources.zip | 84 | Complete ZIP, CRCs checked | `8b0fffad7da5e94536f80c934b8cb7ca78657d727383cd0a54cba2db6b0ba087` |
| Tests_Chargement_Sharp_64_65.zip | 5 | Complete ZIP, CRCs checked | `0beefd9ec9010bc4d6226acb0d90f980dd4e72db0c4bda07545b9c2f38dbb5a5` |
| BONJOUR.bas | 1 | Complete source file | `6451ac8c0c101984e0a6f5a8c862dfa57879a8f0432d66f81e73060d7f5786ee` |
| CHRONO.bas | 1 | Complete source file | `ba217e83b84a31a7154488c606c5e5863ad73ada917729db586fdd02437e2ac1` |
| Queens_Quest_PC-1403_FR.bas | 1 | Complete source file | `61120de2334d7f5491a2ea8095db66eb6c13dac51560409abe3407d03a2686e3` |
| Queens_Quest_PC-1403_FR_LITE.bas | 1 | Complete source file | `417feb0e5e909544d7fc12be5c4c016d8ce8ce7e070a49701df04893b801856d` |
| Queens_Quest_PC1403_8K_FR_corrige.bas | 1 | Complete source file | `cea9774cab2f4f086c9f28e37965ca61e5675b4d466f45f77d2a79d8d11ecc56` |
| queen's quest.bas | 1 | Complete source file | `decfee5c65977d009791ee278d07cbde38b4424ecfb7f18a9fd8513f810fe0a9` |

## Recovery of the older Windows archive

`SharpManager_BASIC_PC1403_Sources.zip` has no ZIP central directory. Recovery follows its local file headers: each retained entry was decompressed and checked against its recorded size and CRC-32. Recovery stops at `SharpManager/docs/public/tex-svg-full-JPZ3Q247.min.js.map`, which contains an incomplete compressed stream. The preceding 394 entries were recovered. Generated website documentation was excluded from the source archive; application files, Arduino files and source documentation preceding the truncated entry were retained. Any contents following that entry are unknown.

## Scope

Windows executable distributions were not copied in full: their source files, examples, firmware and notices were retained. Source and Mac packages were extracted with their original directory structure, excluding caches, build outputs and generated website documentation. Source code and firmware retain their original bytes. Reference copies in `macos`, `windows` and `firmware` match the corresponding snapshots.

The original compressed archives are not duplicated in Git: their source files can be browsed directly. The manifest provides original delivery checksums and the checksum of each imported file.

## New Linux port

The `linux` directory was added on 6 October 2026 from the current `macos`
V5.2 sources at commit `ef5732e848ec4433bfe18b792595556c12da0c76`. It is a new
port, not another original delivery. Its application and protocol files record
the modifications; the copied PocketTools C sources, makefile, NOTICE and
SharpManager license retain their original bytes. Linux setup, launch and
bundle scripts, English instructions and pseudo-terminal integration tests
are included. `docs/source-manifest.json` records these files under `linux_port`.

The Queen's Quest ownership notice was added to the repository documentation
and `examples/queens-quest/README.md`; the BASIC and TAP files remain unchanged.

## English documentation update

On 6 October 2026, 25 README and LISEZ-MOI files were translated into English. The upstream README was already English and remains unchanged. Original documentation is retained at commit `2737fe4916bee1ff1dda7640e8b0242335d22ae7`. The source manifest keeps each translated imported file's original checksum and size in `original_sha256` and `original_bytes`; `sha256` and `bytes` describe the current English document. Code, firmware, BASIC and TAP files were not changed. Existing commands, file paths, protocol identification strings and application UI labels are preserved.

## Instruction filenames and Windows setup, 8 October 2026

The 16 instruction files now use `LISEZ-MOI` filenames. References and build scripts use these current names; `source_entry` and `original_path` in the manifest preserve delivery provenance. Windows SDK installation is documented in `windows/README.md`, with x64 / ARM64 guidance and a build prerequisite check. Archive build scripts were changed only to reference the renamed instruction files. Application and firmware code was not changed.
