# SharpManager PC-1403 · macOS V5 flux continu

Cette version est prévue pour le firmware SharpStream fourni dans la même archive.
Elle conserve l'envoi TAP/BASIC et la réception CSAVE. Avec ce firmware, le Mac
reçoit un ACK dès que chaque bloc de 64 octets est accepté dans le tampon
circulaire. Le signal cassette est généré en parallèle par Timer1. Quand le
tampon est vide, XIN conserve une tonalité de bits 1 ; la fin réelle des
impulsions est annoncée par ETX. Le journal indique alors « Signal cassette
terminé » : le Sharp ne renvoie toutefois aucune confirmation de CLOAD réussi.

## Construction sur le Mac mini M4

Installer Python 3 avec Tkinter et les outils Xcode en ligne de commande. Ouvrir
build-macos.command après décompression complète. L'application sera créée
dans dist/SharpManager-PC1403-V5-Flux.app. Le .app doit être compilé sur le
Mac ; cette archive contient les sources et le script, sans binaire macOS.

## Essai

Sauvegarder d'abord le programme du Sharp. Fermer SharpManager et débrancher
le connecteur Sharp de la Pro Mini avant de téléverser le firmware. Ouvrir
SharpStream/SharpStream.ino dans Arduino IDE, choisir Arduino Pro or Pro Mini,
ATmega328P 5 V / 16 MHz et le port FTDI, puis téléverser. Le fichier
SharpStream.hex compilé est aussi fourni pour les outils AVR compatibles.
Reconnecter le Sharp et ouvrir l'application V5. La connexion doit afficher
« synchro 2s - flux continu V5 ». Lancer CLOAD puis envoyer le TAP, comme avant.
Essayer le même fichier plusieurs fois et relever les réussites et erreurs 8.
Ne pas ajouter de pause de 1 ms entre les octets dans Tape.ino.

Pour revenir à la version précédente, téléverser le firmware original depuis
SharpOriginalV5/SharpOriginalV5.ino et réutiliser l'application macOS V4.

La nouvelle émission n'a pas encore été testée avec le Sharp réel. Le firmware
emploie Timer1 et la broche Arduino D4 (PD4) pour XIN, comme le câblage actuel. Le
compilateur AVR a mesuré 8 144 octets de flash et 670 octets de RAM statique.
Les sources du firmware sont issues de SharpManager (Apache 2.0).
