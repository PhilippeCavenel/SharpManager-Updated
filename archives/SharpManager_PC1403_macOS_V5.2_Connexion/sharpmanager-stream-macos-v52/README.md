# SharpManager PC-1403 · macOS V5.2 flux continu

Cette version reprend les sources macOS V5.1 et le firmware « synchro 2s - flux
continu V5 » déjà installé. Elle conserve le délai d'ACK de 20 secondes et le
suivi des blocs pendant un long transfert. Il n'est pas nécessaire de reflasher
la Pro Mini.

## Correction de la connexion

Après un transfert interrompu, le firmware peut encore être occupé dans CLOAD
et ne plus répondre aux octets SYN. La V5.2 essaie d'abord trois SYN. Si elle
n'obtient aucune réponse, elle envoie une impulsion sur RTS (relié à DTR/reset
sur ce montage), attend la fin du bootloader, puis réessaie. Une erreur pendant
un envoi ferme le port afin de permettre cette récupération à la connexion
suivante. Ce reset peut interrompre un transfert encore actif ; il est réservé
à la connexion lorsqu'aucun SYN n'a répondu.

## Construction sur le Mac mini M4

Décompresser entièrement, ouvrir build-macos.command. Python 3 avec Tkinter et
les outils Xcode en ligne de commande sont nécessaires. L'application est créée
dans dist/SharpManager-PC1403-V5.2-Flux.app. Fermer l'ancien SharpManager
avant de lancer cette application. Ce ZIP contient les sources, pas un binaire
macOS prêt à lancer.

## Fichier d'essai fourni

Le programme queen's quest.bas fourni par Philippe est converti en un TAP de
5 717 octets (90 blocs série). Il se redécode en 258 lignes BASIC. Le fichier
test/queens_quest_PC1403.tap dans l'archive permet de tester directement
« Envoyer .tap ». Le fichier source original n'est pas modifié.

En cas d'échec de l'envoi, relever le message complet, notamment le numéro du
bloc et s'il s'agit d'une erreur Arduino ou d'un délai d'attente. Le message
« Signal cassette terminé » confirme la fin de l'émission, pas la réussite de
CLOAD sur le Sharp.

Les sources SharpManager sont sous licence Apache 2.0 ; voir
PocketTools/NOTICE.txt pour les conditions des convertisseurs.
