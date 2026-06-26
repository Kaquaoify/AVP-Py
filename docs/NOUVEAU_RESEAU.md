# Installation avec nouveau réseau Internet

Ce guide explique comment connecter un Raspberry Pi AVP-Py à un nouveau Wi-Fi lorsqu'il arrive sur un site client.

## Objectif

Si le Raspberry Pi ne trouve aucun réseau connu au démarrage, AVP-Py démarre automatiquement un hotspot de configuration.

Ce hotspot permet de connecter le Raspberry Pi au Wi-Fi du client depuis un téléphone ou un ordinateur.

## 1. Démarrer le Raspberry Pi sur le nouveau site

Branche :

1. l'alimentation ;
2. l'écran, si nécessaire ;
3. le câble Ethernet, si disponible.

Si aucun Ethernet ni Wi-Fi connu n'est disponible, attends le délai de détection configuré.

Par défaut, ce délai est de 75 secondes.

## 2. Se connecter au Wi-Fi de configuration

Le Raspberry Pi crée un réseau Wi-Fi du type :

```text
AVP-SETUP-nom-appareil
```

Exemple :

```text
AVP-SETUP-hall-entree
```

Mot de passe par défaut :

```text
avpsetup123
```

Connecte un téléphone ou un ordinateur à ce réseau.

## 3. Ouvrir la page de configuration Wi-Fi

Une fois connecté au hotspot du Raspberry Pi, ouvre :

```text
http://10.42.0.1:8000/setup/wifi
```

La page permet de :

- choisir un réseau Wi-Fi détecté ;
- entrer le mot de passe Wi-Fi ;
- renseigner un SSID manuel si le réseau est masqué.

## 4. Connecter le Raspberry Pi au Wi-Fi client

Dans la page de configuration :

1. choisis le réseau Wi-Fi du client ;
2. entre le mot de passe ;
3. valide.

Si la connexion réussit :

- le hotspot de configuration s'arrête ;
- le Raspberry Pi rejoint le réseau client ;
- AVP-Py redevient accessible depuis ce réseau.

## 5. Ouvrir AVP-Py sur le nouveau réseau

Depuis le réseau client, ouvre :

```text
http://nom-appareil.local:8000
```

Exemple :

```text
http://hall-entree.local:8000
```

Si l'adresse `.local` ne répond pas, récupère l'adresse IP du Raspberry Pi depuis la box ou le routeur, puis ouvre :

```text
http://adresse-ip-du-pi:8000
```

## 6. Modifier les réglages du hotspot

Une fois connecté à AVP-Py, va dans :

```text
Paramètres > Réseau
```

Cette page permet de modifier :

- l'interface Wi-Fi ;
- le délai avant démarrage du hotspot ;
- le préfixe du SSID setup ;
- le mot de passe setup ;
- l'activation du hotspot de secours.

Le mot de passe setup doit contenir au moins 8 caractères.

## Dépannage

Si le hotspot n'apparaît pas :

- attends au moins le délai de détection configuré ;
- redémarre le Raspberry Pi ;
- vérifie que le hotspot de secours est activé dans `Paramètres > Réseau` ;
- vérifie que l'interface Wi-Fi configurée est correcte, généralement `wlan0`.

Si la connexion au Wi-Fi client échoue :

- vérifie le mot de passe Wi-Fi ;
- vérifie que le réseau est bien visible ;
- utilise le champ SSID manuel si le réseau est masqué ;
- rapproche le Raspberry Pi du point d'accès.

AVP-Py n'a pas besoin d'être exposé sur Internet pour cette opération.

## Guides liés

- [Réglages réseau](RESEAU.md)
- [Premiers pas](PREMIERS_PAS.md)
- [FAQ](FAQ.md)
