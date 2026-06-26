# Configuration des horaires

Ce guide explique la page :

```text
Paramètres > Horaires
```

## Objectif

Les horaires définissent :

- les jours où la lecture est autorisée ;
- la plage horaire de lecture ;
- l'heure de synchronisation des médias ;
- l'heure du redémarrage quotidien.

## 1. Choisir les jours actifs

Dans `Jours actifs`, coche les jours où l'écran doit diffuser les vidéos.

Exemples :

- tous les jours : coche `Lun` à `Dim` ;
- semaine uniquement : coche `Lun` à `Ven` ;
- fermeture le dimanche : décoche `Dim`.

Un jour non coché empêche la lecture automatique ce jour-là.

## 2. Définir la plage de lecture

Les champs à régler sont :

- `Début lecture` ;
- `Fin lecture`.

Exemple :

```text
Début lecture : 08:00
Fin lecture   : 20:00
```

Dans cet exemple, AVP-Py diffuse les vidéos entre 08:00 et 20:00, uniquement les jours actifs.

En dehors de cette plage, la lecture automatique s'arrête.

## 3. Définir l'heure de synchronisation

Le champ `Synchro médias` définit l'heure de synchronisation rclone.

Exemple :

```text
Synchro médias : 03:00
```

Cette synchronisation est utilisée uniquement si la source des médias est :

```text
Synchronisation rclone
```

Si AVP-Py est en mode local, l'heure reste enregistrée mais la synchronisation rclone est ignorée.

## 4. Configurer le redémarrage quotidien

Le champ `Redémarrage` définit l'heure du redémarrage automatique.

La case `Redémarrage quotidien activé` permet d'activer ou désactiver ce comportement.

Exemple recommandé :

```text
Redémarrage : 06:00
```

Un redémarrage quotidien peut aider à garder une installation Raspberry Pi stable dans le temps.

## 5. Sauvegarder

Après modification :

1. vérifie les jours cochés ;
2. vérifie les heures ;
3. clique sur `Sauvegarder`.

Les nouveaux réglages sont utilisés par le service AVP-Py.

## Dépannage

Si la lecture ne démarre pas au moment prévu :

- vérifie que le jour actuel est coché ;
- vérifie l'heure interne du Raspberry Pi sur la page d'accueil ;
- vérifie `Début lecture` et `Fin lecture` ;
- vérifie qu'au moins une vidéo est disponible ;
- vérifie que le service AVP-Py fonctionne.

Commande utile en SSH :

```bash
sudo systemctl status avp-py.service
```

## Guides liés

- [Premiers pas](PREMIERS_PAS.md)
- [Configuration rclone](RCLONE.md)
- [Utilisation en mode local](MODE_LOCAL.md)
