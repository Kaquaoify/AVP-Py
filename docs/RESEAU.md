# Réglages réseau

Ce guide explique la page :

```text
Paramètres > Réseau
```

## Objectif

Cette page permet de consulter l'état réseau du Raspberry Pi et de configurer le hotspot de secours.

Elle affiche notamment :

- l'état de la connexion ;
- l'état du mode setup ;
- le SSID du hotspot de configuration ;
- l'adresse locale `nom-appareil.local:8000` ;
- l'IP locale du Raspberry Pi ;
- la liste des interfaces réseau.

## 1. Lire le bloc d'état

Le haut de la page affiche :

- `Connexion` : indique si une connexion réseau est active ;
- `Setup` : indique si le hotspot de configuration est actif ;
- `SSID setup` : nom du Wi-Fi de secours.

## 2. Lire le bloc Accès local

Le bloc `Accès local` rappelle les adresses à utiliser pour ouvrir AVP-Py.

Adresse réseau :

```text
http://nom-appareil.local:8000
```

Adresse IP locale :

```text
http://adresse-ip-du-pi:8000
```

L'adresse `.local` est plus lisible, mais l'adresse IP est utile si la résolution mDNS ne fonctionne pas sur un appareil client.

## 3. Configurer le hotspot de secours

Les champs disponibles sont :

- `Interface Wi-Fi` : interface utilisée pour le Wi-Fi, généralement `wlan0` ;
- `Délai avant setup` : temps d'attente avant de démarrer le hotspot si aucun réseau n'est disponible ;
- `Préfixe SSID setup` : début du nom du hotspot ;
- `Mot de passe setup` : mot de passe du hotspot ;
- `Hotspot de secours activé` : active ou désactive le mécanisme.

Le mot de passe setup doit contenir entre 8 et 63 caractères.

## 4. Actions disponibles

La page propose trois actions principales :

- `Sauvegarder` : enregistre les réglages ;
- `Démarrer setup` : lance immédiatement le hotspot de configuration ;
- `Arrêter setup` : coupe le hotspot de configuration.

Utilise `Démarrer setup` uniquement si tu veux forcer le mode configuration.

## 5. Interfaces réseau

Le tableau `Interfaces` liste les interfaces détectées par NetworkManager.

Il permet de vérifier :

- le nom de l'interface ;
- son type ;
- son état ;
- la connexion NetworkManager utilisée.

Si aucune information n'est affichée, NetworkManager peut être absent, inactif ou inaccessible.

## Dépannage

Si AVP-Py n'est pas joignable par `nom-appareil.local` :

1. essaie l'adresse IP affichée dans `Accès local` ;
2. vérifie que l'appareil client est sur le même réseau ;
3. attends quelques secondes après un changement de nom ;
4. redémarre le client ou vide son cache DNS si nécessaire.

Si le hotspot ne démarre pas :

- vérifie que le hotspot de secours est activé ;
- vérifie que l'interface Wi-Fi est correcte ;
- vérifie l'état du service NetworkManager ;
- consulte les logs AVP-Py.

Commande utile :

```bash
sudo systemctl status NetworkManager.service
```

## Guides liés

- [Installation avec nouveau réseau Internet](NOUVEAU_RESEAU.md)
- [Configuration admin](ADMIN.md)
- [FAQ](FAQ.md)
