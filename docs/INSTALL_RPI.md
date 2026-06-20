# Installation Raspberry Pi

## 1. Installer l'OS

Utilise Raspberry Pi Imager avec :

```text
Raspberry Pi OS Lite 64-bit
```

Active SSH dans l'image si tu veux gérer l'installation à distance.

## 2. Premier démarrage

Connecte-toi au Raspberry Pi en SSH, puis mets le système à jour :

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

## 3. Installer AVP-Py

Quand le dépôt GitHub public existe, lance :

```bash
curl -fsSL https://raw.githubusercontent.com/CHANGE_ME/AVP-Py/main/scripts/install.sh -o install-avp-py.sh
chmod +x install-avp-py.sh
AVP_HOSTNAME=hall-entree ./install-avp-py.sh https://github.com/CHANGE_ME/AVP-Py.git
```

Remplace `hall-entree` par le nom lisible de l'appareil.

## 4. Ouvrir l'interface

Depuis un navigateur sur le même réseau :

```text
http://hall-entree.local:8000
```

Mot de passe par défaut :

```text
1234
```

## 4b. Installation chez un client sans réseau connu

Si le Raspberry Pi démarre sans LAN et sans Wi-Fi connu, il crée automatiquement un réseau de configuration :

```text
AVP-SETUP-hall-entree
```

Mot de passe par défaut :

```text
avpsetup123
```

Connecte un téléphone à ce réseau, puis ouvre :

```text
http://10.42.0.1:8000/setup/wifi
```

Choisis le Wi-Fi du client, entre le mot de passe et valide. Si la connexion réussit, le hotspot est coupé et le Pi rejoint le réseau client.

Tu peux modifier le nom du hotspot, son mot de passe, l'interface Wi-Fi et le délai de détection dans :

```text
Paramètres > Réseau
```

## 5. Configurer les médias

Dans `Paramètres > Configuration des dossiers` :

1. Choisis `Synchronisation rclone` ou `Gestion locale depuis l'interface web`.
2. En mode rclone, renseigne le remote, le chemin distant et `rclone.conf`, puis teste la connexion.
3. En mode manuel, sauvegarde puis ouvre `Paramètres > Gestion des médias` pour envoyer les vidéos.

Le passage en mode manuel met rclone en pause sans effacer sa configuration. Revenir
au mode rclone restaure donc immédiatement les réglages précédents.

## 6. Configurer les horaires

Dans `Paramètres > Horaires` :

1. Coche les jours actifs.
2. Renseigne l'heure de début et l'heure de fin.
3. Renseigne l'heure de synchronisation.
4. Garde ou désactive le redémarrage quotidien.

## 7. Mettre à jour

```bash
/opt/avp-py/app/scripts/update.sh
```

## Notes écran noir

AVP-Py lance `mpv` en plein écran avec une fenêtre noire en mode idle. Pour un appareil de production, Raspberry Pi OS Lite évite l'affichage d'un bureau. Les messages de boot peuvent encore apparaître avant le lancement du service.
