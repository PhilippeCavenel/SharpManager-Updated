# Modifications archivées

Les fichiers de code des snapshots reproduisent les sources livrées pendant le projet ; aucune nouvelle modification fonctionnelle n’a été réalisée pour cet archivage. Le 6 octobre 2026, les README et notices LIRE-MOI ont été traduits en anglais. Leurs textes originaux restent conservés dans l’historique Git et leurs empreintes initiales dans le manifeste.

| Partie | Adaptations présentes |
| --- | --- |
| macOS | Interface Python / Tkinter, protocole série avec un lecteur unique, conversion BASIC/TAP et construction Apple Silicon. |
| Windows | Conversion BASIC PC-1403, réception CSAVE, isolation des accès série et des préférences, récupération de connexion, progression et compatibilité avec le firmware continu. |
| Protocole V5.2 | Délai ACK de 20 secondes, détection du firmware continu, distinction ACK / ETX final, récupération RTS/DTR après trois SYN sans réponse. |
| Arduino | Flux cassette produit par interruption Timer1, tampon circulaire de 256 octets, ACK différé tant que moins de 64 places sont libres, variantes de fin de signal et firmware précédent conservés. |
| Exemples | Tests aux frontières de blocs 64 / 65 octets, Bonjour, chronomètre, adaptation 8K et traductions de Queen’s Quest ; corrections françaises `THEN LET`. |

Les commentaires et résultats de tests existants sont conservés. Le compte rendu Windows V5.2 annonce une compilation et des simulations, mais précise que cette application n’a pas été testée avec la liaison FTDI physique ou le Sharp. Les textes historiques décrivent l’état au moment de chaque livraison et ne valent pas confirmation de l’état ultérieur du matériel.

Les mentions de modification exigées par Apache 2.0 §4(b) doivent accompagner les fichiers modifiés lors d’une redistribution publique. Les fichiers de code des snapshots sont ici conservés tels que livrés pour préserver leur fidélité ; avant publication, vérifier et compléter ces mentions dans les fichiers concernés, ou préparer une branche de distribution portant ces mentions et excluant les composants aux droits non établis.
