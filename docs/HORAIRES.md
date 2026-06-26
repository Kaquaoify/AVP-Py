# Configuration des horaires

Ce guide explique la page :

```text
Paramètres > Horaires
```

Les horaires définissent quand AVP-Py doit lire les vidéos, synchroniser les médias et redémarrer le Raspberry Pi.

## 1. Jours actifs

La section `Jours actifs` permet de choisir les jours où la lecture automatique est autorisée.

Exemple :

- coche `Lun`, `Mar`, `Mer`, `Jeu`, `Ven` pour une lecture uniquement en semaine ;
- coche tous les jours pour une lecture quotidienne ;
- décoche un jour pour empêcher la lecture automatique ce jour-là.

## 2. Début et fin de lecture

Les champs suivants contrôlent la plage horaire de lecture :

- `Début lecture` ;
- `Fin lecture`.

Exemple :

```text
Début lecture : 08:00
Fin lecture   : 20:00
```

Dans cet exemple, AVP-Py lance ou maintient la lecture entre 08:00 et 20:00, les jours actifs.

En dehors de cette plage, la lecture automatique s'arrête.

## 3. Synchronisation des médias

Le champ `Synchro médias` définit l'heure à laquelle AVP-Py lance la synchronisation rclone.

Exemple :

```text
Synchro médias : 03:00
```

La synchronisation n'est utilisée que si la source des médias est `Synchronisation rclone`.

Si la source active est `Gestion locale depuis l'interface web`, l'heure de synchronisation reste enregistrée, mais la synchronisation rclone est mise en pause.

## 4. Redémarrage quotidien

Le champ `Redémarrage` définit l'heure du redémarrage automatique.

La case `Redémarrage quotidien activé` permet d'activer ou désactiver ce comportement.

Exemple recommandé pour un appareil d'affichage :

```text
Redémarrage : 06:00
```

Un redémarrage quotidien peut aider à garder un Raspberry Pi stable sur une installation longue durée.

## 5. Sauvegarder

Après modification :

1. vérifie les jours cochés ;
2. vérifie les heures ;
3. clique sur `Sauvegarder`.

Les nouveaux horaires sont appliqués par le service AVP-Py.

## 6. Points à vérifier

Si la lecture ne se lance pas au moment attendu :

- vérifie que le jour actuel est coché ;
- vérifie que l'heure interne du Raspberry Pi est correcte ;
- vérifie la plage `Début lecture` / `Fin lecture` ;
- vérifie qu'au moins une vidéo est disponible localement ;
- vérifie que le service AVP-Py tourne.

L'heure interne du Raspberry Pi est affichée en bas à droite de la page d'accueil.
