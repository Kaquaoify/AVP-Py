# AVP-Py

<div align="center">
  <strong>Lecteur vidéo autonome pour Raspberry Pi 5 destiné au digital signage.</strong>
  <br>
  <sub>Synchronisation Google Drive, lecture plein écran, horaires programmables et administration web locale.</sub>
</div>

<br>

AVP-Py est un lecteur vidéo autonome pour Raspberry Pi 5 destiné au digital signage.

Il synchronise un dossier Google Drive avec un dossier local via `rclone`, génère les miniatures et métadonnées avec `ffmpeg/ffprobe`, puis lit les vidéos en boucle avec `mpv` selon des horaires configurables depuis une interface web locale.

---

## Sommaire

[Choix techniques](#choix-techniques) · [Accès web](#accès-web) · [Configuration Wi-Fi sur site](#configuration-wi-fi-sur-site) · [Installation Raspberry Pi](#installation-rapide-sur-raspberry-pi) · [Mise à jour](#mise-à-jour)

[Configuration Google Drive](#configuration-google-drive) · [Fonctionnement](#fonctionnement) · [Logs](#logs) · [Service systemd](#service-systemd) · [Développement local](#développement-local) · [Crédit](#crédit-de-développement)

---

## Choix techniques

- OS recommandé : Raspberry Pi OS Lite 64-bit
- Backend et interface admin : Python + FastAPI + templates HTML
- Base de données : aucune en v1, configuration dans `/var/lib/avp-py/config.json`
- Synchronisation : `rclone sync`
- Lecture vidéo : `mpv`
- Miniatures et métadonnées : `ffmpeg` et `ffprobe`
- Démarrage automatique : service `systemd`
- Configuration réseau de secours : NetworkManager + `nmcli`

---

## Accès web

Après installation :

```text
http://nom-appareil.local:8000
```

Mot de passe par défaut :

```text
1234
```

---

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

La page permet de choisir le Wi-Fi client, d'entrer son mot de passe et de connecter le Raspberry Pi.

Une fois la connexion réussie, le hotspot de secours est coupé et l'app redevient accessible via :

```text
http://nom-appareil.local:8000
```

Le comportement est réglable depuis `Paramètres > Réseau`.

---

## Installation rapide sur Raspberry Pi

Sur un Raspberry Pi fraîchement installé avec Raspberry Pi OS Lite 64-bit :

```bash
curl -fsSL https://raw.githubusercontent.com/CHANGE_ME/AVP-Py/main/scripts/install.sh -o install-avp-py.sh
chmod +x install-avp-py.sh
./install-avp-py.sh https://github.com/CHANGE_ME/AVP-Py.git
```

Script source : [`scripts/install.sh`](scripts/install.sh).

Pour définir le nom `.local` pendant l'installation :

```bash
AVP_HOSTNAME=hall-entree ./install-avp-py.sh https://github.com/CHANGE_ME/AVP-Py.git
```

L'adresse sera alors :

```text
http://hall-entree.local:8000
```

Remplace `CHANGE_ME` par l'organisation ou l'utilisateur GitHub réel quand le dépôt est créé.

---

## Mise à jour

Depuis le Raspberry Pi :

```bash
/opt/avp-py/app/scripts/update.sh
```

Le script [`scripts/update.sh`](scripts/update.sh) fait un `git pull`, met à jour les dépendances Python et redémarre le service.

---

## Configuration Google Drive

La page `Paramètres > Configuration des dossiers` permet de régler :

- le dossier local qui recevra les vidéos ;
- le nom du remote `rclone` ;
- le chemin du dossier Google Drive ;
- le contenu complet de `rclone.conf`, token Google inclus.

AVP-Py n'attend pas uniquement le JSON du token. La méthode recommandée consiste à
créer le remote complet sur un ordinateur avec un navigateur, puis à copier son bloc
de configuration dans l'interface du Raspberry Pi.

### Pairage depuis un ordinateur

1. Installe [`rclone`](https://rclone.org/downloads/) sur un ordinateur disposant d'un navigateur.
2. Ouvre un terminal et lance :

```text
rclone config
```

3. Choisis `n` pour créer un nouveau remote.
4. Donne-lui le nom `gdrive`.
5. Choisis le stockage `drive` correspondant à Google Drive.
6. Sauf besoin particulier, laisse `client_id` et `client_secret` vides.
7. Choisis l'accès complet à Drive, puis refuse la configuration avancée.
8. Accepte l'authentification automatique et connecte-toi au compte Google dans le navigateur.
9. Termine l'assistant, puis demande l'emplacement du fichier généré :

```text
rclone config file
```

10. Ouvre `rclone.conf` et copie tout le bloc `[gdrive]`. Sa structure ressemble à ceci :

```ini
[gdrive]
type = drive
scope = drive
token = {"access_token":"...","refresh_token":"..."}
```

11. Dans AVP-Py, renseigne :

    - **Nom du remote rclone** : `gdrive` ;
    - **Chemin du dossier Google Drive** : par exemple `Affichage/Hall entree` ;
    - **Contenu complet de rclone.conf** : le bloc copié, avec son vrai token.

12. Clique sur `Sauvegarder`, puis `Tester la connexion` et enfin
    `Synchroniser maintenant`.

Si le dossier a été partagé par un autre compte, ajoute-le de préférence comme
raccourci dans `Mon Drive`, puis utilise le chemin de ce raccourci dans AVP-Py.

Le token permet d'accéder au Drive : ne le publie jamais dans GitHub, des captures
d'écran ou des logs. AVP-Py conserve la configuration dans `/var/lib/avp-py` et
l'utilise uniquement pour les tests et les synchronisations `rclone`.

---

## Fonctionnement

- Les médias sont triés par nom de fichier.
- Le dossier local est le miroir du dossier Google Drive : un fichier supprimé de Google Drive sera supprimé localement au prochain `rclone sync`.
- Les miniatures sont générées après la synchronisation.
- La lecture démarre et s'arrête selon les jours et heures configurés.
- Hors lecture, le player reste sur une fenêtre noire via `mpv --idle`.
- Un redémarrage quotidien est activé par défaut à `06:00` et peut être désactivé.
- Si aucun réseau LAN/Wi-Fi connu n'est disponible, le Pi démarre un hotspot de configuration.

---

## Logs

Les logs sont disponibles dans :

```text
/var/lib/avp-py/logs
```

Ils sont aussi consultables depuis `Paramètres > Logs`.

---

## Service systemd

Le service installé est basé sur [`systemd/avp-py.service`](systemd/avp-py.service).

Commandes utiles :

```bash
sudo systemctl status avp-py
sudo systemctl restart avp-py
sudo journalctl -u avp-py -f
```

---

## Développement local

Sur PC :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn avppy.app:app --reload --host 127.0.0.1 --port 8000
```

Les dépendances Python sont listées dans [`requirements.txt`](requirements.txt).

Le guide Raspberry Pi complet est disponible dans [`docs/INSTALL_RPI.md`](docs/INSTALL_RPI.md).

Sous Windows, les commandes `mpv` via socket Unix sont ignorées par le contrôleur. L'interface web et la configuration restent testables.
<br/>

<br/>
<br/>


<div align="center">
  <table>
    <tr>
      <td align="center">
        <strong>Développé avec l'aide de Codex et ChatGPT</strong><br>
        <sub>Architecture, implémentation et documentation assistées par OpenAI Codex.</sub>
      </td>
    </tr>
  </table>
</div>
