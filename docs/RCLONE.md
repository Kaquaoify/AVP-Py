# Configuration rclone

Ce guide explique comment utiliser AVP-Py avec une source distante, par exemple Google Drive.

La page concernée est :

```text
Paramètres > Configuration des dossiers
```

## Objectif

En mode `Synchronisation rclone`, AVP-Py synchronise un dossier distant vers le dossier local du Raspberry Pi.

Le dossier distant est la source de référence. Si un fichier est supprimé du dossier distant, il sera supprimé localement lors du prochain `rclone sync`.

## 1. Activer le mode rclone

Va dans :

```text
Paramètres > Configuration des dossiers
```

Dans `Source des médias`, sélectionne :

```text
Synchronisation rclone
```

## 2. Renseigner les champs AVP-Py

Les champs à compléter sont :

- `Dossier local sur le Raspberry Pi` : dossier où les vidéos seront stockées localement ;
- `Nom du remote rclone` : par exemple `gdrive` ;
- `Chemin du dossier distant` : par exemple `Affichage/Hall entree` ;
- `Contenu complet de rclone.conf` : bloc de configuration rclone complet, token inclus.

AVP-Py attend le contenu complet du bloc `rclone.conf`, pas uniquement le token.

## 3. Créer le remote rclone

Sur un ordinateur avec navigateur, installe rclone puis lance :

```bash
rclone config
```

Crée un nouveau remote :

1. choisis `n` pour créer un nouveau remote ;
2. nomme-le `gdrive` ;
3. choisis le stockage `drive` pour Google Drive ;
4. laisse `client_id` et `client_secret` vides sauf besoin particulier ;
5. choisis le niveau d'accès souhaité ;
6. accepte l'authentification automatique ;
7. connecte-toi au compte Google dans le navigateur ;
8. termine l'assistant.

Affiche ensuite le chemin du fichier généré :

```bash
rclone config file
```

Ouvre le fichier indiqué et copie tout le bloc du remote.

Exemple de structure :

```ini
[gdrive]
type = drive
scope = drive
token = {"access_token":"...","refresh_token":"..."}
```

Le vrai fichier contient des valeurs privées. Ne le publie jamais dans GitHub, dans des captures d'écran ou dans des logs.

## 4. Coller la configuration dans AVP-Py

Dans AVP-Py :

1. colle le bloc complet dans `Contenu complet de rclone.conf` ;
2. vérifie que `Nom du remote rclone` correspond au nom du bloc, par exemple `gdrive` ;
3. renseigne le chemin distant si les vidéos sont dans un sous-dossier ;
4. clique sur `Sauvegarder`.

## 5. Tester la connexion

Clique sur :

```text
Tester la connexion
```

AVP-Py vérifie que rclone peut lire le dossier distant.

Si le test échoue, vérifie :

- le nom du remote ;
- le chemin du dossier distant ;
- le contenu complet de `rclone.conf` ;
- l'accès du compte Google au dossier ;
- la connexion Internet du Raspberry Pi.

## 6. Lancer une synchronisation manuelle

Clique sur :

```text
Synchroniser maintenant
```

AVP-Py copie les fichiers du dossier distant vers le dossier local, puis régénère les miniatures et les métadonnées.

## 7. Synchronisation automatique

L'heure de synchronisation automatique se règle dans :

```text
Paramètres > Horaires
```

Champ :

```text
Synchro médias
```

Cette synchronisation est ignorée si AVP-Py est en mode local.

## 8. Passer temporairement en mode local

Tu peux passer de `Synchronisation rclone` à `Gestion locale depuis l'interface web`.

Dans ce cas :

- rclone est mis en pause ;
- la configuration rclone n'est pas effacée ;
- l'heure de synchronisation reste enregistrée ;
- les modifications locales deviennent possibles.

En revenant au mode rclone, les anciens réglages sont réutilisés.

Attention : au prochain `rclone sync`, le dossier distant redevient la source de référence.

## Guides liés

- [Utilisation en mode local](MODE_LOCAL.md)
- [Configuration des horaires](HORAIRES.md)
- [FAQ](FAQ.md)
