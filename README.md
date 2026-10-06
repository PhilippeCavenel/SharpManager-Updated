# SharpManager-Updated

Archive des sources et des exemples du projet **Sharp PC-1403** de Philippe Cavenel, au **6 octobre 2026**.
Le projet reprend [SharpManager de Wayne Venables / Codaris](https://github.com/codaris/SharpManager).

| Contenu | Révision de référence | Dossier |
| --- | --- | --- |
| Application macOS, Python / Tkinter, Apple Silicon | V5.2 « Connexion / flux continu » | [macos](macos/) |
| Application Windows, C# / WPF, .NET 10 | V5.2 « Flux continu » | [windows](windows/) |
| Firmware Pro Mini ATmega328P, 5 V / 16 MHz | V5 « Flux continu — garde 64 » | [firmware](firmware/) |
| BASIC et TAP : Bonjour, chronomètre, tests 64/65 octets, Queen’s Quest | Toutes les variantes retrouvées, dont la version française 8K corrigée | [examples](examples/) |
| Révisions antérieures et copies des sources livrées | Mac, Windows et Arduino | [archives](archives/) |

## Construire et utiliser

- **Mac** : consulter [macos/README.md](macos/README.md), puis lancer `macos/build-macos.command` sur macOS arm64 avec Python 3 / Tkinter et les outils Xcode.
- **Windows** : SDK .NET 10 pour construire ; exécuter `BuildWindowsBasic.bat` depuis le dossier `windows`. Le runtime .NET 10 Desktop x64 est nécessaire pour l’application publiée. Voir [les instructions V5.2](windows/LIRE-MOI-WINDOWS-V52.txt).
- **Arduino** : ouvrir `firmware/SharpStreamSafe/SharpStreamSafe.ino` dans Arduino IDE avec le profil Pro Mini ATmega328P 5 V / 16 MHz. Voir [les instructions du firmware](firmware/LIRE-MOI.txt).
- Les scripts de construction, les ressources, les tests existants, les sources des convertisseurs et les firmwares HEX fournis sont conservés avec les sources.

Les transferts utilisent des blocs série de 64 octets, un tampon circulaire Arduino et Timer1 pour produire le signal cassette en continu. La V5.2 attend jusqu’à 20 secondes chaque ACK et distingue l’ACK de bloc du signal ETX de fin d’émission. Les limites et tests documentés par chaque livraison restent applicables : l’archivage ne constitue pas un nouvel essai matériel.

## Traçabilité

Les fichiers livrés sont conservés **sans modification de contenu**. [L’inventaire](docs/INVENTAIRE.md) indique les révisions et leurs empreintes ; [le manifeste](docs/source-manifest.json) permet de vérifier chaque fichier importé. Les exécutables d’application Windows, les caches et la documentation web générée ne sont pas archivés en tant que sources ; les outils PocketTools inclus dans les paquets sources sont conservés.

L’ancien `SharpManager_BASIC_PC1403_Sources.zip` est tronqué dans une entrée de documentation web générée. Les 394 entrées précédentes ont été récupérées avec vérification de taille et de CRC, dont les 49 fichiers `.cs`, `.py`, `.ino`, `.c` et `.h` identifiés. La récupération n’établit pas ce qui pouvait suivre l’entrée tronquée. Les archives sources Mac et Windows V5.2 sont complètes. Détails dans [l’inventaire](docs/INVENTAIRE.md).

## Licence et publication

**Le SharpManager d’origine est sous licence Apache 2.0**, qui autorise la modification et la redistribution publique, y compris commerciale, avec les conditions de la licence. La licence et l’attribution d’origine sont conservées dans [LICENSE](LICENSE) et [NOTICE](NOTICE).

La licence principale ne doit pas être étendue automatiquement aux composants indépendants. **Les droits de redistribution des convertisseurs PocketTools et de Queen’s Quest restent à confirmer**. Ce dépôt d’archivage reste privé ; il faut régler ces points avant de publier son contenu intégral. [Conditions de publication détaillées](docs/PUBLICATION.md).
