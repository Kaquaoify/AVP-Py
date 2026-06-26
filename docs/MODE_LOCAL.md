# Utilisation en mode local

Ce guide explique le mode :

```text
Gestion locale depuis l'interface web
```

Ce mode permet d'envoyer, supprimer, renommer et organiser les vidéos directement depuis AVP-Py, sans Google Drive ni rclone actif.

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

Ou utilise le bouton `Gérer les médias` si disponible depuis la page d'accueil.

La page affiche :

- le nombre de vidéos ;
- l'espace disque disponible ;
- la liste des vidéos locales ;
- les actions d'envoi, suppression, renommage et ordre de lecture.

## 3. Envoyer des vidéos

Dans la zone `Sélectionner une ou plusieurs vidéos` :

1. choisis une ou plusieurs vidéos ;
2. clique sur `Envoyer les vidéos` ;
3. laisse la page ouverte pendant l'envoi.

Formats vidéo acceptés :

```text
.avi, .m4v, .mkv, .mov, .mp4, .mpeg, .mpg, .webm
```

Si un fichier porte le même nom qu'un fichier existant, AVP-Py ajoute un suffixe pour éviter d'écraser l'ancien fichier.

## 4. Renommer une vidéo

Dans la liste des vidéos :

1. modifie le nom dans le champ de la vidéo ;
2. garde une extension vidéo valide ;
3. clique sur `Renommer`.

Exemple :

```text
accueil-hall.mp4
```

## 5. Changer l'ordre de lecture

Utilise les boutons :

```text
↑
↓
```

Ils permettent de monter ou descendre une vidéo dans l'ordre de lecture.

L'ordre est conservé par AVP-Py dans sa configuration locale.

## 6. Supprimer une vidéo

Clique sur :

```text
Supprimer
```

Une confirmation est demandée avant la suppression.

La suppression est définitive côté Raspberry Pi.

## 7. Publier la playlist

Après avoir ajouté ou réorganisé des vidéos, clique sur :

```text
Publier la playlist
```

AVP-Py régénère la playlist utilisée par le lecteur.

## 8. Revenir au mode rclone

Pour revenir à Google Drive ou à une autre source distante :

1. va dans `Paramètres > Configuration des dossiers` ;
2. choisis `Synchronisation rclone` ;
3. sauvegarde ;
4. teste la connexion si nécessaire ;
5. lance une synchronisation.

Attention : en mode rclone, le dossier distant redevient la source de vérité. Les fichiers locaux absents du dossier distant peuvent être supprimés lors de la prochaine synchronisation.
