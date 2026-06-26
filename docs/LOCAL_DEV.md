# Développement local

Ce guide explique comment lancer AVP-Py sur un PC pour tester l'interface et les changements de code.

## Prérequis

- Python 3 ;
- Git ;
- dépendances Python du projet ;
- dépôt AVP-Py cloné localement.

Certaines fonctions Raspberry Pi ne sont pas disponibles sur Windows, notamment les commandes `mpv` via socket Unix et les commandes réseau `nmcli`.

## 1. Créer l'environnement Python

Depuis la racine du projet :

```bash
python -m venv .venv
```

Sous Windows PowerShell :

```powershell
.venv\Scripts\activate
```

Sous Linux ou macOS :

```bash
source .venv/bin/activate
```

## 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les dépendances principales sont :

- FastAPI ;
- Uvicorn ;
- Jinja2 ;
- python-multipart.

## 3. Lancer le serveur local

```bash
uvicorn avppy.app:app --reload --host 127.0.0.1 --port 8000
```

Ouvre ensuite :

```text
http://127.0.0.1:8000
```

## 4. Valider rapidement le code

Compilation Python :

```bash
python -m compileall avppy
```

Import de l'application :

```bash
python -c "import avppy.app; print('app import OK')"
```

## 5. Données locales

En développement local, AVP-Py utilise par défaut le dossier :

```text
data/
```

Ce dossier contient les fichiers générés localement, par exemple :

- configuration ;
- médias ;
- miniatures ;
- logs ;
- fichier rclone actif.

Ces fichiers ne doivent pas être publiés dans Git.

## Limites en développement local

Sur PC, certaines fonctions sont seulement partiellement testables :

- lecture vidéo plein écran avec `mpv` ;
- socket IPC Unix de `mpv` ;
- configuration réseau via NetworkManager ;
- hotspot de secours ;
- intégration systemd.

L'interface web, les formulaires, les templates et la configuration restent testables.

## Guides liés

- [Installation Raspberry Pi](INSTALL_RPI.md)
- [Mise à jour](UPDATE.md)
