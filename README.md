# AVP-Py

AVP-Py est un lecteur vidéo autonome pour Raspberry Pi 5 destiné au digital signage.

Il synchronise un dossier Google Drive avec un dossier local via `rclone`, génère les miniatures et métadonnées avec `ffmpeg/ffprobe`, puis lit les vidéos en boucle avec `mpv` selon des horaires configurables depuis une interface web locale.

## Choix techniques

- OS recommandé : Raspberry Pi OS Lite 64-bit
- Backend et interface admin : Python + FastAPI + templates HTML
- Base de données : aucune en v1, configuration dans `/var/lib/avp-py/config.json`
- Synchronisation : `rclone sync`
- Lecture vidéo : `mpv`
- Miniatures et métadonnées : `ffmpeg` et `ffprobe`
- Démarrage automatique : service `systemd`
- Configuration réseau de secours : NetworkManager + `nmcli`

## Accès web

Après installation :

```text
http://nom-appareil.local:8000
```

Mot de passe par défaut :

```text
1234
```

## Configuration Wi-Fi sur site

Si le Raspberry Pi ne trouve aucun réseau connu au démarrage, AVP-Py crée automatiquement un Wi-Fi de secours :

```text
AVP-SETUP-nom-appareil
```

Mot de passe par défaut du Wi-Fi de secours :

```text
avpsetup123
```

Depuis un téléphone ou un ordinateur, connecte-toi à ce Wi-Fi puis ouvre :

```text
http://10.42.0.1:8000/setup/wifi
```

La page permet de choisir le Wi-Fi client, d'entrer son mot de passe et de connecter le Raspberry Pi. Une fois la connexion réussie, le hotspot de secours est coupé et l'app redevient accessible via :

```text
http://nom-appareil.local:8000
```

Le comportement est réglable depuis `Paramètres > Réseau`.

## Installation rapide sur Raspberry Pi

Sur un Raspberry Pi fraîchement installé avec Raspberry Pi OS Lite 64-bit :

```bash
curl -fsSL https://raw.githubusercontent.com/CHANGE_ME/AVP-Py/main/scripts/install.sh -o install-avp-py.sh
chmod +x install-avp-py.sh
./install-avp-py.sh https://github.com/CHANGE_ME/AVP-Py.git
```

Pour définir le nom `.local` pendant l'installation :

```bash
AVP_HOSTNAME=hall-entree ./install-avp-py.sh https://github.com/CHANGE_ME/AVP-Py.git
```

L'adresse sera alors :

```text
http://hall-entree.local:8000
```

Remplace `CHANGE_ME` par l'organisation ou l'utilisateur GitHub réel quand le dépôt est créé.

## Mise à jour

Depuis le Raspberry Pi :

```bash
/opt/avp-py/app/scripts/update.sh
```

Le script fait un `git pull`, met à jour les dépendances Python et redémarre le service.

## Configuration Google Drive

La page `Paramètres > Configuration des dossiers` permet de régler :

- le dossier local qui recevra les vidéos ;
- le nom du remote `rclone` ;
- le chemin du dossier Google Drive ;
- le contenu optionnel de `rclone.conf`.

Pour une configuration simple, tu peux générer le remote sur le Raspberry Pi :

```bash
rclone config
```

Puis utiliser le nom du remote dans l'interface web, par exemple `gdrive`.

Si tu colles un contenu `rclone.conf` dans l'interface web, AVP-Py l'écrit dans `/var/lib/avp-py/rclone.conf` et l'utilise pour les tests et synchronisations.

## Fonctionnement

- Les médias sont triés par nom de fichier.
- Le dossier local est le miroir du dossier Google Drive : un fichier supprimé de Google Drive sera supprimé localement au prochain `rclone sync`.
- Les miniatures sont générées après la synchronisation.
- La lecture démarre et s'arrête selon les jours et heures configurés.
- Hors lecture, le player reste sur une fenêtre noire via `mpv --idle`.
- Un redémarrage quotidien est activé par défaut à `06:00` et peut être désactivé.
- Si aucun réseau LAN/Wi-Fi connu n'est disponible, le Pi démarre un hotspot de configuration.

## Logs

Les logs sont disponibles dans :

```text
/var/lib/avp-py/logs
```

Ils sont aussi consultables depuis `Paramètres > Logs`.

## Service systemd

Commandes utiles :

```bash
sudo systemctl status avp-py
sudo systemctl restart avp-py
sudo journalctl -u avp-py -f
```

## Développement local

Sur PC :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn avppy.app:app --reload --host 127.0.0.1 --port 8000
```

Sous Windows, les commandes `mpv` via socket Unix sont ignorées par le contrôleur. L'interface web et la configuration restent testables.
