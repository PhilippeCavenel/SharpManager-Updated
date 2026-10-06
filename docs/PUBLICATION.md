# Licence d’origine et ouverture au public

Vérification effectuée le 6 octobre 2026.

## SharpManager

- Dépôt : https://github.com/codaris/SharpManager
- Licence : https://github.com/codaris/SharpManager/blob/main/LICENSE
- Auteur indiqué : **Wayne Venables / Codaris**, copyright 2024 dans le fichier de licence.
- Référence amont consultée : `9ee535e0ef16a0248180e539b381a6b78c4ffb8b`.
- Texte officiel : https://www.apache.org/licenses/LICENSE-2.0

Apache 2.0 §§2 et 4 permet de reproduire, modifier et redistribuer publiquement le code et ses dérivés. Le code SharpManager peut donc être publié dans un dépôt distinct. Il n’est pas nécessaire de demander une autorisation supplémentaire à l’auteur pour les usages déjà couverts par cette licence.

Pour redistribuer : fournir la licence (§4a), signaler les modifications dans les fichiers modifiés (§4b), conserver les mentions d’origine pertinentes (§4c) et reproduire un éventuel NOTICE amont (§4d). Aucun fichier NOTICE n’a été trouvé dans l’arbre amont consulté. L’archive contient néanmoins un NOTICE d’attribution et un résumé des modifications. Le texte anglais de la licence prévaut.

Les snapshots conservés sans changement de contenu peuvent ne pas comporter toutes les mentions de modification par fichier. Les compléter dans une branche de distribution avant la publication publique. L’attribution ne doit pas laisser entendre que l’auteur d’origine approuve ces adaptations.

## Composants indépendants

| Élément | Information retrouvée | Effet sur la publication |
| --- | --- | --- |
| PocketTools : `bas2img`, `bin2wav`, `wav2bin`, leurs sources C et manuel | Les paquets contiennent un NOTICE « personal, non-commercial use ». Les auteurs et historiques figurent dans les sources et le manuel. Le manuel qualifie le logiciel de « free software », mais cela n’établit pas à lui seul une autorisation détaillée de redistribution publique. | Ne pas lui appliquer Apache 2.0. Confirmer les droits applicables à ces versions, ou distribuer SharpManager sans ces fichiers en renvoyant vers leur fournisseur. |
| SharpPocketToolsGUI | https://github.com/SilverGreen93/SharpPocketToolsGUI possède une licence MIT pour son projet. Il s’agit de l’interface graphique qui fournit aussi les outils PocketTools ; ce dépôt ne prouve pas que tous les outils tiers inclus deviennent MIT. | Garder distincts les droits de l’interface et ceux des convertisseurs. |
| Queen’s Quest et adaptations françaises / 8K / TAP | **Patrick Zumstein** a publié le programme sur la page Facebook **« 80's Sharp pocket computers »**, selon la provenance communiquée par Philippe Cavenel, et **le programme reste sa propriété**. Le fichier original identifie Patrick Zumstein, septembre 2026. Aucune licence de redistribution n’a été retrouvée dans les fichiers fournis ; sa publication sur Facebook n’en constitue pas une. | Conserver cette attribution. Obtenir l’accord de l’auteur ou une licence couvrant la redistribution et les adaptations ; à défaut, exclure le jeu et ses dérivés de la distribution publique. |
| Exemples Bonjour, chronomètre, tests de transfert | Livrables du projet ; pas de code attribué à un auteur tiers identifié dans ces exemples. | Conserver leur provenance ; les distinguer de Queen’s Quest. |

Provenance PocketTools conservée dans les paquets :

- https://github.com/SilverGreen93/SharpPocketToolsGUI/releases/tag/v1.4
- https://www.peil-partner.de/ifhe.de/sharp/ (l’adresse a renvoyé 404 lors de la vérification)
- Sources C et `Pocket_Tools_Manual_200.pdf` inclus dans l’archive Windows.

Le port Linux ajouté le 6 octobre 2026 reprend le code SharpManager sous Apache 2.0 avec des mentions de modification dans les fichiers Python adaptés. Les sources et notices PocketTools copiées dans `linux/PocketTools` conservent leurs droits indépendants.

La question de la publication concerne aussi les copies historiques, les TAP du jeu et les composants embarqués dans les dossiers macOS / Windows / Linux. Exclure seulement un dossier principal ne suffit pas si des copies restent dans les archives ou dans l’historique accessible. Le dépôt reste privé à l’issue de cet archivage ; aucun changement de visibilité n’est effectué.
