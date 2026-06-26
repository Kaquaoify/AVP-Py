# Utilisation en mode local

Ce guide explique le mode :

```text
Gestion locale depuis l'interface web
```

## Objectif

Le mode local permet de gérer les vidéos directement dans AVP-Py, sans Google Drive ni synchronisation rclone active.

Depuis l'interface web, tu peux :

- envoyer des vidéos ;
- renommer des vidéos ;
- supprimer des vidéos ;
- modifier l'ordre de lecture ;
- publier la playlist.

## 1. Activer le mode local

Va dans :

```text
Paramètres > Configuration des dossiers
```

Dans `Source des médias`, choisis :

```text
Gestion locale depuis l'interface web
```

Puis clique sur :

```text
Sauvegarder
```

Quand ce mode est actif, rclone est mis en pause sans effacer sa configuration.

## 2. Ouvrir la gestion des médias

Va dans :

```text
Paramètres > Gestion des médias
```

La page affiche :

- le nombre de vidéos ;
- l'espace disque disponible ;
- la liste des vidéos locales ;
- les actions disponibles pour chaque fichier.

## 3. Envoyer des vidéos

Dans `Sélectionner une ou plusieurs vidéos` :

1. choisis une ou plusieurs vidéos ;
2. clique sur `Envoyer les vidéos` ;
3. garde la page ouverte pendant l'envoi.

Formats vidéo acceptés :

```text
.avi, .m4v, .mkv, .mov, .mp4, .mpeg, .mpg, .webm
```

Si un fichier porte déjà le même nom, AVP-Py ajoute automatiquement un suffixe pour éviter d'écraser le fichier existant.

## 4. Renommer une vidéo

Dans la liste des médias :

1. modifie le nom dans le champ de la vidéo ;
2. garde une extension vidéo valide ;
3. clique sur `Renommer`.

Exemple :

```text
accueil-hall.mp4
```

## 5. Modifier l'ordre de lecture

Utilise les boutons :

```text
↑
↓
```

Ils permettent de monter ou descendre une vidéo dans la playlist.

L'ordre choisi est conservé localement par AVP-Py.

## 6. Supprimer une vidéo

Clique sur :

```text
Supprimer
```

Une confirmation est demandée avant la suppression.

La suppression est définitive côté Raspberry Pi.

## 7. Publier la playlist

Après ajout, suppression, renommage ou changement d'ordre, clique sur :

```text
Publier la playlist
```

AVP-Py régénère la playlist utilisée par le lecteur.

## 8. Revenir au mode rclone

Pour revenir à une source distante :

1. va dans `Paramètres > Configuration des dossiers` ;
2. choisis `Synchronisation rclone` ;
3. clique sur `Sauvegarder` ;
4. teste la connexion ;
5. lance une synchronisation.

Attention : en mode rclone, le dossier distant redevient la source de référence. Les fichiers locaux absents du dossier distant peuvent être supprimés lors de la prochaine synchronisation.

## Guides liés

- [Configuration rclone](RCLONE.md)
- [Configuration des horaires](HORAIRES.md)
- [FAQ](FAQ.md)
