# Configuration rclone

Ce guide explique comment utiliser AVP-Py avec une source distante, par exemple Google Drive.

La page concernée est :

```text
Paramètres > Configuration des dossiers
```

## 1. Principe

En mode `Synchronisation rclone`, AVP-Py synchronise un dossier distant vers le dossier local du Raspberry Pi.

Le dossier distant est la source de vérité.

Conséquence importante : si un fichier est supprimé du dossier distant, il sera supprimé du Raspberry Pi lors du prochain `rclone sync`.

## 2. Informations à renseigner dans AVP-Py

Dans `Paramètres > Configuration des dossiers`, sélectionne :

```text
Synchronisation rclone
```

Puis renseigne :

- `Dossier local sur le Raspberry Pi` : dossier où les vidéos seront stockées localement ;
- `Nom du remote rclone` : par exemple `gdrive` ;
- `Chemin du dossier distant` : par exemple `Affichage/Hall entree` ;
- `Contenu complet de rclone.conf` : le bloc de configuration rclone, token inclus.

AVP-Py attend le contenu complet de `rclone.conf`, pas uniquement le token.

## 3. Créer la configuration rclone

Sur un ordinateur disposant d'un navigateur, installe rclone puis lance :

```bash
rclone config
```

Crée un nouveau remote :

1. choisis `n` pour créer un nouveau remote ;
2. nomme-le `gdrive` ;
3. choisis le stockage `drive` pour Google Drive ;
4. suis l'authentification dans le navigateur ;
5. termine la configuration.

Ensuite, affiche le chemin du fichier de configuration :

```bash
rclone config file
```

Ouvre le fichier indiqué et copie tout le bloc correspondant au remote.

Exemple de structure :

```ini
[gdrive]
type = drive
scope = drive
token = {"access_token":"...","refresh_token":"..."}
```

Le vrai fichier contient des valeurs privées. Ne les publie jamais.

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

AVP-Py lance une commande rclone de test sur le dossier distant.

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

AVP-Py lance la synchronisation immédiatement.

Les fichiers du dossier distant sont copiés vers le dossier local. Les miniatures et métadonnées sont ensuite régénérées.

## 7. Synchronisation automatique

L'heure de synchronisation automatique se règle dans :

```text
Paramètres > Horaires
```

Champ :

```text
Synchro médias
```

Cette synchronisation automatique est ignorée si AVP-Py est en mode local.

## 8. Passer temporairement en mode local

Tu peux passer de `Synchronisation rclone` à `Gestion locale depuis l'interface web`.

Dans ce cas :

- rclone est mis en pause ;
- la configuration rclone n'est pas effacée ;
- l'heure de synchronisation reste enregistrée ;
- les modifications locales deviennent possibles depuis l'interface web.

En revenant au mode rclone, les anciens réglages rclone sont réutilisés.

Attention : au prochain `rclone sync`, le dossier distant redevient la référence.
