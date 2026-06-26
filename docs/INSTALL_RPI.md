# Installation Raspberry Pi

Ce guide décrit l'installation d'AVP-Py sur un Raspberry Pi.

## Prérequis

- Raspberry Pi 5 recommandé ;
- Raspberry Pi OS Lite 64-bit ;
- accès Internet pendant l'installation ;
- accès SSH ou clavier branché au Raspberry Pi ;
- dépôt GitHub AVP-Py accessible.

## 1. Installer Raspberry Pi OS

Avec Raspberry Pi Imager, installe :

```text
Raspberry Pi OS Lite 64-bit
```

Active SSH si tu veux faire l'installation à distance.
Il faut retenir le nom de l'appareil indiqué lors de cette installation.

## 2. Premier démarrage

Connecte-toi au Raspberry Pi en SSH ou via la console, puis mets le système à jour :

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

Redémarre si le système le demande.

## 3. Installer AVP-Py

Télécharge le script d'installation :

```bash
curl -fsSL https://raw.githubusercontent.com/Kaquaoify/AVP-Py/main/scripts/install.sh -o install-avp-py.sh
chmod +x install-avp-py.sh
```

Lance l'installation :

```bash
./install-avp-py.sh https://github.com/Kaquaoify/AVP-Py.git
```

Pour définir le nom réseau pendant l'installation :

```bash
AVP_HOSTNAME=hall-entree ./install-avp-py.sh https://github.com/Kaquaoify/AVP-Py.git
```

Remplace `hall-entree` par le nom souhaité pour l'appareil.

## 4. Boîtier Argon40

Par défaut, le script AVP-Py installe aussi le logiciel officiel Argon40 pour gérer le ventilateur et le bouton d'alimentation des boîtiers compatibles.

Il ne relance pas l'installateur si `argononed` est déjà installé.

Pour ignorer cette étape sur un Raspberry Pi sans boîtier Argon40 :

```bash
AVP_INSTALL_ARGON40=0 AVP_HOSTNAME=hall-entree ./install-avp-py.sh https://github.com/Kaquaoify/AVP-Py.git
```

Après installation, configure au besoin la courbe du ventilateur avec :

```bash
argonone-config
```

Le script Argon40 peut mettre à jour des paquets, l'EEPROM et la configuration matérielle. Redémarre le Raspberry Pi après la première installation.

## 5. Ouvrir l'interface web

Depuis un navigateur connecté au même réseau :

```text
http://nom-appareil.local:8000
```

Mot de passe par défaut :

```text
1234
```

Change ce mot de passe dans :

```text
Paramètres > Admin
```

## 6. Premier réglage des médias

Dans :

```text
Paramètres > Configuration des dossiers
```

Choisis une source :

- `Synchronisation rclone` pour utiliser Google Drive ou un stockage distant ;
- `Gestion locale depuis l'interface web` pour envoyer les vidéos directement dans AVP-Py.

Voir aussi :

- [Configuration rclone](RCLONE.md)
- [Utilisation en mode local](MODE_LOCAL.md)

## 7. Premier réglage des horaires

Dans :

```text
Paramètres > Horaires
```

Configure :

1. les jours actifs ;
2. l'heure de début de lecture ;
3. l'heure de fin de lecture ;
4. l'heure de synchronisation ;
5. le redémarrage quotidien.

Voir [Configuration des horaires](HORAIRES.md).

## 8. Installation chez un client sans réseau connu

Si le Raspberry Pi démarre sans Ethernet et sans Wi-Fi connu, AVP-Py crée automatiquement un hotspot de configuration :

```text
AVP-SETUP-hall-entree
```

Mot de passe par défaut :

```text
avpsetup123
```

Connecte un téléphone ou un ordinateur à ce Wi-Fi, puis ouvre :

```text
http://10.42.0.1:8000/setup/wifi
```

Choisis le Wi-Fi client, entre le mot de passe et valide.

Voir [Installation avec nouveau réseau Internet](NOUVEAU_RESEAU.md).

## 9. Vérifier le service

Après installation :

```bash
sudo systemctl status avp-py.service
```

Commandes utiles :

```bash
sudo systemctl restart avp-py.service
sudo journalctl -u avp-py.service -f
```

## Notes écran noir

AVP-Py lance `mpv` en plein écran avec une fenêtre noire en mode idle.

Sur un appareil de production, Raspberry Pi OS Lite évite l'affichage d'un bureau. Des messages de boot peuvent encore apparaître avant le lancement du service.

## Guides liés

- [Premiers pas](PREMIERS_PAS.md)
- [Mise à jour](UPDATE.md)
- [Réglages réseau](RESEAU.md)
