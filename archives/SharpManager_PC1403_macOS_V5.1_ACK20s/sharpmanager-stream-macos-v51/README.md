# SharpManager PC-1403 · macOS V5.1 flux continu

Cette version corrige l'attente des acquittements pour les longs transferts TAP.
Elle est compatible avec le firmware « synchro 2s - flux continu V5 » déjà
installé sur la Pro Mini. Il n'est pas nécessaire de reflasher le firmware.

## Construction sur le Mac mini M4

Après extraction complète de l'archive, ouvrir build-macos.command. Il utilise
Python 3 avec Tkinter et les outils Xcode en ligne de commande pour construire
l'application dist/SharpManager-PC1403-V5.1-Flux.app. Le .app doit être créé
sur le Mac ; cette archive ne contient pas de binaire macOS.

Fermer l'ancienne application V5 avant de lancer la V5.1. Choisir le port FTDI,
connecter, puis vérifier que le journal affiche « flux continu V5 ». Lancer
CLOAD sur le Sharp et envoyer le TAP comme avant.

Pour chaque bloc de 64 octets, SharpManager V5.1 attend maintenant jusqu'à
20 secondes l'ACK (au lieu de 5 secondes, ou 8 pour le premier bloc). Le journal
indique le nombre d'octets acceptés toutes les huit trames. En cas d'échec,
le message donne le numéro du bloc et la plage d'octets concernée. Après le
dernier ACK, l'application attend encore ETX : ce signal signifie que les
impulsions cassette sont terminées, pas que le Sharp a réussi CLOAD.

Si l'erreur devient « Erreur Arduino 1 » sur un bloc, c'est le délai interne du
firmware qui expire : il faudra alors corriger ce délai côté Arduino. Une
nouvelle erreur « 20 s » désignerait un acquittement absent ou perdu ; noter
le bloc indiqué pour poursuivre le diagnostic.

Les sources SharpManager sont sous licence Apache 2.0. Les sources Pocket Tools
incluses ont leurs propres conditions (voir PocketTools/NOTICE.txt).
