# SharpManager PC-1403 pour macOS Apple Silicon

Application macOS dédiée au PC-1403 et à la Pro Mini avec le firmware **Arduino Driver 1.3**, y compris la variante V5 « synchro 2s ». Elle reprend le protocole série et les conversions Pocket Tools. Les fonctions CE-140F de disque et l'upload du firmware ne sont pas implémentés.

## Construire sur le Mac mini M4

1. Installer Python 3 macOS depuis python.org (avec Tkinter), et les outils de ligne de commande Apple avec `xcode-select --install` si absents.
2. Décompresser toute l'archive, puis ouvrir `build-macos.command` depuis le Finder. En cas de blocage de sécurité, clic droit → Ouvrir. Le script installe les dépendances Python dans le dossier `.venv` local et compile les outils Pocket Tools pour Apple Silicon.
3. L'application obtenue se trouve dans `dist/SharpManager-PC1403-V4.app` et son titre indique « macOS V4 ». Elle n'est pas signée ni notarisée : pour sa première ouverture, utiliser clic droit → Ouvrir si macOS le demande.

La compilation doit être faite sur le Mac. Cette archive contient les sources et le script de construction, **pas un binaire macOS déjà compilé**.

## Utiliser

- Brancher le câble FTDI ; choisir son port `/dev/cu.usbserial…` dans la liste et cliquer **Connecter**, puis **Ping**. Laisser l'autre SharpManager fermé.
- **Envoyer .tap** ou **Envoyer BASIC .bas** : choisir un fichier, lancer `CLOAD` en mode RUN sur le Sharp, puis confirmer sur le Mac. Le logiciel convertit le `.bas` en mémoire et envoie le contenu au firmware.
- **Recevoir CSAVE** : cliquer sur le bouton, confirmer le dialogue, puis lancer `CSAVE` sur le Sharp. Choisir ensuite le nom du `.tap` ; si la cassette est un BASIC non protégé, un `.bas` portant le même nom est aussi créé. Garder le `.tap` comme sauvegarde originale et pour vérifier le retour `CSAVE → CLOAD`.
- **Essai : pause de 50 ms entre blocs** : mode expérimental pour comparer le même `.tap` avec et sans pause entre les blocs série de 64 octets. La fréquence des impulsions émises par la Pro Mini ne change pas. Noter les réussites et les erreurs 8 pour chaque mode.
- La sortie `LPRINT` apparaît dans le journal.

La conversion exige des lignes BASIC numérotées dans l'ordre. Les transferts doivent être vérifiés sur le matériel ; une erreur 8 intermittente observée sous Windows n'est pas supposée corrigée par le changement d'ordinateur.

Ce port utilise les sources Apache 2.0 de SharpManager et les sources Pocket Tools incluses pour usage personnel non commercial (voir `PocketTools/NOTICE.txt`).
