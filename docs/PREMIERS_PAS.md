# Premiers pas

Ce guide décrit les premières actions à effectuer après l'installation d'AVP-Py sur un Raspberry Pi.

## Objectif

À la fin de ce guide, tu dois pouvoir :

- ouvrir l'interface web ;
- comprendre la page d'accueil ;
- choisir le mode de gestion des médias ;
- lancer un premier test de lecture ;
- savoir quels réglages faire en priorité.

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

Change-le après la première connexion dans :

```text
Paramètres > Admin
```

## 2. Comprendre la page d'accueil

La page d'accueil sert au contrôle quotidien de l'affichage.

Elle permet de :

- lancer ou mettre en pause la lecture ;
- passer à la vidéo précédente ou suivante ;
- régler le volume ;
- voir l'état du lecteur ;
- voir la vidéo en cours ;
- consulter la liste des médias locaux ;
- accéder aux paramètres ;
- vérifier l'heure interne du Raspberry Pi en bas à droite.

Si aucun média n'est disponible, la page indique qu'aucun média local n'est présent.

## 3. Choisir la source des médias

Va dans :

```text
Paramètres > Configuration des dossiers
```

Deux modes sont disponibles :

- `Synchronisation rclone` : les vidéos viennent d'un dossier distant, par exemple Google Drive ;
- `Gestion locale depuis l'interface web` : les vidéos sont envoyées directement dans AVP-Py.

Les deux modes sont exclusifs. Il faut choisir un mode principal pour éviter qu'une synchronisation distante supprime des fichiers envoyés localement.

## 4. Configurer les horaires

Va dans :

```text
Paramètres > Horaires
```

Configure au minimum :

- les jours actifs ;
- l'heure de début de lecture ;
- l'heure de fin de lecture ;
- l'heure de synchronisation des médias ;
- le redémarrage quotidien, si souhaité.

L'heure utilisée est celle du Raspberry Pi. Elle est rappelée en bas à droite de la page d'accueil.

## 5. Tester la lecture

Après avoir ajouté ou synchronisé des vidéos :

1. reviens sur la page d'accueil ;
2. vérifie que les médias apparaissent dans la liste ;
3. clique sur `Play` ;
4. vérifie l'écran relié au Raspberry Pi.

Si rien ne s'affiche, vérifie :

- qu'au moins une vidéo est disponible localement ;
- que les fichiers vidéo sont dans un format accepté ;
- que l'horaire autorise la lecture à ce moment ;
- que le service AVP-Py est actif ;
- que l'écran est bien connecté au Raspberry Pi.

## 6. Réglages recommandés après installation

Après la première connexion, configure :

1. le nom de l'appareil dans `Paramètres > Admin` ;
2. le mot de passe administrateur ;
3. la source des médias ;
4. les horaires ;
5. les réglages réseau si l'appareil doit être déplacé chez un client.

AVP-Py est prévu pour une utilisation locale sur le réseau du site. Ne l'expose pas directement sur Internet.

## Guides liés

- [Configuration admin](ADMIN.md)
- [Configuration des horaires](HORAIRES.md)
- [Configuration rclone](RCLONE.md)
- [Utilisation en mode local](MODE_LOCAL.md)
- [Réglages réseau](RESEAU.md)
