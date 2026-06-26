<h3 align="center">AVP-Py</h3>

---

<p align="center"> Lecteur vidéo autonome pour Raspberry Pi 5 destiné au digital signage.
    <br> 
    <br>
</p>

## 📝 Sommaire
- [A propos](#about)
- [Premiers pas](#getting_started)
- [Utilisation](#usage)
- [Développé avec](#built_using)
- [TODO](/TODO.md)

## 🧐 A propos <a name = "about"></a>
Connectez un Raspberry Pi à un écran, installez l'application et gérez tout à distance. Fini les clés USB et les recherches de télécommandes, accédez simplement à l'interface web, ajoutez des médias dans un dossier partagé Google Drive et laissez le reste s'effectuer automatiquement.

## 🏁 Premiers pas <a name = "getting_started"></a>

### Prérequis


```
- un Raspberry Pi 5 (anciens modèles possibles mais non testés au niveau de la puissance pour afficher des vidéos)
- OS requis: Raspberry Pi OS Lite 64-Bit
- une connexion internet
- un accès SSH au RPi ou un clavier/souris
```

### Installation

En SSH ou via la console du RPi
```bash
curl -fsSL https://raw.githubusercontent.com/Kaquaoify/AVP-Py/main/scripts/install.sh -o install-avp-py.sh

chmod +x install-avp-py.sh

./install-avp-py.sh https://github.com/Kaquaoify/AVP-Py.git
```

Une fois l'installation terminée
```bash
sudo reboot
```

### Après installation
L'interface web sera directement accessible à l'adresse suivante: 
```text
http://nom-appareil.local:8000
```

Le mot de passe par défaut est `1234`.

À changer après installation dans `Paramètres > Admin`.

L'écran connecté au RPi doit afficher un fond noir uniquement.


## 🎈 Utilisation <a name="usage"></a>
Les guides détaillés sont dans le dossier [`docs/`](docs/).


## ⛏️ Développé avec <a name = "built_using"></a>
- [Python](https://www.python.org/) + [FastAPI](https://fastapi.tiangolo.com/) - Application web locale
- [Jinja2](https://jinja.palletsprojects.com/) - Interface HTML
- [rclone](https://rclone.org/) - Synchronisation Google Drive / stockage distant
- [mpv](https://mpv.io/) - Lecture vidéo
- [FFmpeg](https://ffmpeg.org/) - Analyse vidéo et miniatures

<br>
<br>
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