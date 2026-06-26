# Premiers pas

Ce guide décrit les premières actions à faire après l'installation d'AVP-Py sur le Raspberry Pi.

## 1. Ouvrir l'interface web

Depuis un appareil connecté au même réseau que le Raspberry Pi, ouvre :

```text
http://nom-appareil.local:8000
```

Exemple :

```text
http://hall-entree.local:8000
```

Le mot de passe par défaut est :

```text
1234
```

Change-le rapidement dans `Paramètres > Admin`.

## 2. Comprendre la page d'accueil

La page d'accueil sert au contrôle quotidien.

Elle permet de :

- lancer ou mettre en pause la lecture ;
- passer à la vidéo précédente ou suivante ;
- régler le volume ;
- voir l'état du lecteur ;
- voir la vidéo en cours ;
- voir la liste des médias locaux ;
- accéder aux paramètres ;
- vérifier l'heure interne du Raspberry Pi en bas à droite.

Si aucun média n'est présent, la page indique qu'aucun média local n'est disponible.

## 3. Choisir la source des médias

Va dans :

```text
Paramètres > Configuration des dossiers
```

Deux modes sont disponibles :

- `Synchronisation rclone` : les vidéos viennent d'un dossier distant, par exemple Google Drive ;
- `Gestion locale depuis l'interface web` : les vidéos sont envoyées directement depuis l'interface AVP-Py.

Les deux modes ne doivent pas modifier les mêmes fichiers en même temps.

En mode rclone, le dossier distant est la source principale.  
En mode local, l'interface web permet d'envoyer, supprimer, renommer et réordonner les vidéos.

## 4. Configurer les horaires

Va dans :

```text
Paramètres > Horaires
```

Définis :

- les jours actifs ;
- l'heure de début de lecture ;
- l'heure de fin de lecture ;
- l'heure de synchronisation des médias ;
- l'heure de redémarrage quotidien, si activé.

Le Raspberry Pi utilise son horloge interne. Vérifie l'heure affichée en bas à droite de la page d'accueil.

## 5. Tester la lecture

Après avoir ajouté ou synchronisé des vidéos :

1. reviens sur la page d'accueil ;
2. vérifie que les médias apparaissent dans la liste ;
3. clique sur `Play` ;
4. contrôle que l'écran relié au Raspberry Pi affiche bien la vidéo.

Si la lecture ne démarre pas, vérifie d'abord :

- qu'il existe au moins une vidéo locale ;
- que l'horaire de lecture autorise la lecture à ce moment ;
- que le service AVP-Py est actif ;
- que les fichiers vidéo sont lisibles par `mpv`.

## 6. Réglages recommandés après installation

Après la première connexion, configure au minimum :

1. le nom de l'appareil dans `Paramètres > Admin` ;
2. le mot de passe administrateur ;
3. la source des médias ;
4. les horaires ;
5. le Wi-Fi de secours dans `Paramètres > Réseau`, si l'appareil doit être déplacé.

AVP-Py est prévu pour une utilisation locale sur le réseau du site. Ne l'expose pas directement sur Internet.
