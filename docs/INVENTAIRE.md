# Inventaire des livraisons archivées

Date : 6 octobre 2026. Les empreintes correspondent aux fichiers de livraison originaux.

| Livraison | Fichiers retenus | État | Empreinte SHA-256 |
| --- | ---: | --- | --- |
| Chronometre_PC1403.zip | 3 | ZIP complet, CRC vérifiés | `f1c808623c46cdd4d79c862b5e697e0f7bf780beadf444bc51225ec1543e8f95` |
| QUEENS_QUEST_PC1403_8K.zip | 3 | ZIP complet, CRC vérifiés | `14efce1cfeab9578523772d45155f72d006f8be02cc004ba897fc0f6bb3f21ae` |
| SharpManager_PC1403_FluxContinu_V5.zip | 33 | ZIP complet, CRC vérifiés | `055d68710ad73fbe0a744172dc6a3628fdd6cf6832f2d3544dbad6b36247c403` |
| SharpManager_PC1403_macOS_M4_V3.zip | 11 | ZIP complet, CRC vérifiés | `bacb7dc840d2f302fe9c2bc9cfd0d83f542d5c3393fee04d42f939598429a44a` |
| SharpManager_PC1403_macOS_M4_V4.zip | 11 | ZIP complet, CRC vérifiés | `ff33bf17799a6f4ca759b87b28338c7418c1b7e4fee1cf25fc04f6b4b8f2aab1` |
| SharpManager_PC1403_macOS_M4_sources.zip | 11 | ZIP complet, CRC vérifiés | `f10feeda2131e646dc3998e9cd5ea7d0980258af16c5484c612004623a6c2afb` |
| SharpManager_PC1403_macOS_V5.1_ACK20s.zip | 11 | ZIP complet, CRC vérifiés | `52a8c3c58880094a5ebda04dc48e2fb4dce2350310d63f76bd072d0dd6f2b174` |
| SharpManager_PC1403_macOS_V5.2_Connexion.zip | 12 | ZIP complet, CRC vérifiés | `b5d83c0757ce16752d700b1ddc38dd5bdd549670126e75f30d0c0ae3251b1498` |
| Sharp_PC1403_Firmware_Fin200ms_Compile.zip | 22 | ZIP complet, CRC vérifiés | `153e8260141aa24508f6ac505f2a501c3d7b1e22ad9789351710ae2ce60656c1` |
| Sharp_PC1403_Firmware_Fin200ms_Essai.zip | 21 | ZIP complet, CRC vérifiés | `26942197d7c7e797b435870a9b695f83a060b7c73a80678ec72eecd4cec1802e` |
| Sharp_PC1403_Firmware_FluxContinu_Garde64.zip | 22 | ZIP complet, CRC vérifiés | `df944b5d8cae8d4fef448709545fc4cb9161561d9af11e1b039d4cf709d87960` |
| SharpManager_BASIC_PC1403_Sources.zip | 94 | Archive tronquée, récupération CRC | `f2e6c7e43982e0e26c6c352b51441ac4a5a2a913de122c7bc0d146c30c767810` |
| SharpManager_BASIC_PC1403_Windows.zip | 21 | ZIP complet, CRC vérifiés | `4d3770ba7a2ddc0625689c66f5cf0115b7f316806cbb0ac75addb313010bdb36` |
| SharpManager_PC1403_Windows_V5.2_FluxContinu.zip | 18 | ZIP complet, CRC vérifiés | `27846c39582786c5c94bc1bafe938bef607dc5d7a7abc33f45ecb7046e30e8cc` |
| SharpManager_PC1403_Windows_V5.2_Sources.zip | 84 | ZIP complet, CRC vérifiés | `8b0fffad7da5e94536f80c934b8cb7ca78657d727383cd0a54cba2db6b0ba087` |
| Tests_Chargement_Sharp_64_65.zip | 5 | ZIP complet, CRC vérifiés | `0beefd9ec9010bc4d6226acb0d90f980dd4e72db0c4bda07545b9c2f38dbb5a5` |
| BONJOUR.bas | 1 | Source complète | `6451ac8c0c101984e0a6f5a8c862dfa57879a8f0432d66f81e73060d7f5786ee` |
| CHRONO.bas | 1 | Source complète | `ba217e83b84a31a7154488c606c5e5863ad73ada917729db586fdd02437e2ac1` |
| Queens_Quest_PC-1403_FR.bas | 1 | Source complète | `61120de2334d7f5491a2ea8095db66eb6c13dac51560409abe3407d03a2686e3` |
| Queens_Quest_PC-1403_FR_LITE.bas | 1 | Source complète | `417feb0e5e909544d7fc12be5c4c016d8ce8ce7e070a49701df04893b801856d` |
| Queens_Quest_PC1403_8K_FR_corrige.bas | 1 | Source complète | `cea9774cab2f4f086c9f28e37965ca61e5675b4d466f45f77d2a79d8d11ecc56` |
| queen's quest.bas | 1 | Source complète | `decfee5c65977d009791ee278d07cbde38b4424ecfb7f18a9fd8513f810fe0a9` |

## Récupération de l’ancienne archive Windows

`SharpManager_BASIC_PC1403_Sources.zip` ne contient pas de répertoire central ZIP. La récupération suit ses en-têtes locaux ; chaque entrée retenue a été décompressée puis vérifiée par sa taille et son CRC-32. Elle s’arrête sur `SharpManager/docs/public/tex-svg-full-JPZ3Q247.min.js.map`, dont le flux compressé est incomplet. Les 394 entrées précédentes ont été récupérées. La documentation web générée a été exclue de l’archive des sources ; les fichiers applicatifs, Arduino et les documents sources précédents sont conservés. Le contenu éventuel après l’entrée tronquée n’est pas connu.

## Périmètre

Les distributions exécutables Windows ne sont pas recopiées intégralement : leurs fichiers sources, exemples, firmwares et notices sont conservés. Les paquets sources et Mac sont extraits avec leur arborescence d’origine, hormis caches, sorties de construction et documentation web générée. Les originaux importés gardent exactement leurs octets. Les copies de référence dans `macos`, `windows` et `firmware` sont identiques aux versions correspondantes des snapshots.

Les archives compressées originales ne sont pas dupliquées dans Git : leurs fichiers sources sont consultables directement. Le manifeste fournit les empreintes originales des livraisons et celles de chaque fichier importé.
