# Modifications archivées

Les fichiers de code des snapshots reproduisent les sources livrées pendant le projet ; aucune nouvelle modification fonctionnelle n’a été réalisée pour cet archivage. Le 6 octobre 2026, les README et notices LISEZ-MOI ont été traduits en anglais. Leurs textes originaux restent conservés dans l’historique Git et leurs empreintes initiales dans le manifeste.

| Partie | Adaptations présentes |
| --- | --- |
| macOS | Interface Python / Tkinter, protocole série avec un lecteur unique, conversion BASIC/TAP et construction Apple Silicon. |
| Linux, ajouté le 6 octobre 2026 | Port expérimental issu de macOS V5.2 : détection `ttyUSB` / `ttyACM`, priorité FTDI, interface et diagnostics anglais, aide aux droits série, scripts Ubuntu, bundle PyInstaller et tests série par pseudo-terminal Linux. Les commandes du protocole, ACK de 20 secondes et ETX final sont conservés. Les sources Mac, Windows et firmware restent inchangées. |
| Windows | Conversion BASIC PC-1403, réception CSAVE, isolation des accès série et des préférences, récupération de connexion, progression et compatibilité avec le firmware continu. |
| Protocole V5.2 | Délai ACK de 20 secondes, détection du firmware continu, distinction ACK / ETX final, récupération RTS/DTR après trois SYN sans réponse. |
| Arduino | Flux cassette produit par interruption Timer1, tampon circulaire de 256 octets, ACK différé tant que moins de 64 places sont libres, variantes de fin de signal et firmware précédent conservés. |
| Exemples | Tests aux frontières de blocs 64 / 65 octets, Bonjour, chronomètre, adaptation 8K et traductions de Queen’s Quest ; corrections françaises `THEN LET`. |

Les commentaires et résultats de tests existants sont conservés. Le compte rendu Windows V5.2 annonce une compilation et des simulations, mais précise que cette application n’a pas été testée avec la liaison FTDI physique ou le Sharp. Les textes historiques décrivent l’état au moment de chaque livraison et ne valent pas confirmation de l’état ultérieur du matériel.

Le nouveau port Linux dispose de ses propres mentions de modification, instructions en anglais et tests logiciels. La compilation des convertisseurs, la conversion BASIC/TAP et les échanges série simulés ont été vérifiés sous Ubuntu 24.04.3 x86_64. Le bundle PyInstaller a été construit. Les essais de l’interface sur un bureau Ubuntu et les transferts FTDI / Pro Mini / Sharp physiques restent à effectuer ; voir `linux/README.md`.

L’attribution de Queen’s Quest précise désormais que Patrick Zumstein a publié le programme sur la page Facebook « 80's Sharp pocket computers » et qu’il reste sa propriété. Les programmes BASIC et TAP ne sont pas modifiés. Cette mention ne vaut pas licence de redistribution.

Les mentions de modification exigées par Apache 2.0 §4(b) doivent accompagner les fichiers modifiés lors d’une redistribution publique. Les fichiers de code des snapshots sont ici conservés tels que livrés pour préserver leur fidélité ; avant publication, vérifier et compléter ces mentions dans les fichiers concernés, ou préparer une branche de distribution portant ces mentions et excluant les composants aux droits non établis.

Le 8 octobre 2026, les 16 notices ont été renommées en `LISEZ-MOI`, avec mise à jour des références et des scripts de compilation. Une procédure Windows détaille maintenant l’installation du SDK .NET 10, le choix x64/ARM64, la réouverture du terminal et le runtime x64 nécessaire au binaire actuel. Le script Windows courant vérifie la présence de `dotnet` et du SDK 10 avant compilation. Les scripts archivés changent uniquement leurs références aux notices renommées ; les sources de l’application et du firmware ne changent pas. Le manifeste conserve les chemins et empreintes d’origine.

Mise à jour du 8 octobre 2026 : Philippe Cavenel confirme le fonctionnement sur Mac, Ubuntu et Windows sous Parallels avec son matériel. Les instructions Windows intègrent le problème de PATH de dotnet et l’installation du pilote FTDI ARM64, y compris PnPUtil. Il s’agit de résultats déclarés par l’utilisateur ; les versions précises des OS et le détail de chaque opération testée ne sont pas fournis. Voir `VALIDATION-2026-10-08.md`. PocketTools est inchangé ; la publication publique de Queen’s Quest sans licence sur Facebook est consignée comme provenance, sans lui attribuer de licence nouvelle.
