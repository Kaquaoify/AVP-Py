# Installation avec nouveau réseau Internet

Ce guide explique comment connecter un Raspberry Pi AVP-Py à un nouveau réseau lorsqu'il arrive sur un site où il ne connaît pas encore le Wi-Fi.

Le principe : si le Raspberry Pi ne trouve aucun réseau connu au démarrage, AVP-Py démarre automatiquement un hotspot de configuration.

## 1. Démarrer le Raspberry Pi sur le nouveau site

Branche :

1. l'alimentation ;
2. l'écran, si nécessaire ;
3. le réseau Ethernet, si disponible.

Si aucun Ethernet ni Wi-Fi connu n'est disponible, attends le délai de détection configuré.

Par défaut, le délai est de 75 secondes.

## 2. Se connecter au Wi-Fi de configuration

Le Raspberry Pi crée un réseau Wi-Fi du type :

```text
AVP-SETUP-nom-appareil
```

Exemple :

```text
AVP-SETUP-hall-entree
```

Le mot de passe par défaut est :

```text
avpsetup123
```

Depuis un téléphone ou un ordinateur, connecte-toi à ce réseau Wi-Fi.

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
- AVP-Py redevient accessible depuis le réseau client.

## 5. Ouvrir AVP-Py sur le nouveau réseau

Depuis le réseau client, ouvre :

```text
http://nom-appareil.local:8000
```

Exemple :

```text
http://hall-entree.local:8000
```

Si le nom `.local` ne répond pas, récupère l'adresse IP du Raspberry Pi depuis la box ou le routeur du client, puis ouvre :

```text
http://adresse-ip-du-pi:8000
```

## 6. Modifier les réglages du hotspot

Une fois connecté à l'interface AVP-Py, va dans :

```text
Paramètres > Réseau
```

Cette page permet de modifier :

- l'interface Wi-Fi ;
- le délai avant démarrage du setup ;
- le préfixe du SSID setup ;
- le mot de passe setup ;
- l'activation du hotspot de secours.

Le mot de passe setup doit contenir au moins 8 caractères.

## 7. Dépannage

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
