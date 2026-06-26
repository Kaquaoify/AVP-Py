# Configuration admin

Ce guide explique la page :

```text
Paramètres > Admin
```

Cette page sert à configurer l'identité réseau de l'appareil et le mot de passe administrateur.

## 1. Nom de l'appareil

Le champ `Nom de l'appareil` définit le nom visible du Raspberry Pi dans AVP-Py.

Il définit aussi l'adresse réseau locale :

```text
http://nom-appareil.local:8000
```

Exemple :

```text
hall-entree
```

Adresse correspondante :

```text
http://hall-entree.local:8000
```

Les espaces et accents sont convertis en caractères simples et en tirets.

Exemple :

```text
Hall Entrée
```

devient généralement :

```text
hall-entree
```

## 2. Changer le mot de passe administrateur

Le mot de passe par défaut est :

```text
1234
```

Il doit être changé après l'installation.

Dans `Nouveau mot de passe` :

1. saisis le nouveau mot de passe ;
2. clique sur `Sauvegarder` ;
3. conserve ce mot de passe dans un endroit sûr.

AVP-Py n'utilise pas de nom d'utilisateur : l'accès se fait uniquement par mot de passe.

## 3. Après changement du nom de l'appareil

Après avoir modifié le nom de l'appareil, l'ancienne adresse `.local` peut ne plus répondre.

Utilise la nouvelle adresse indiquée par AVP-Py :

```text
http://nouveau-nom.local:8000
```

Si l'adresse `.local` ne répond pas immédiatement :

- attends quelques secondes ;
- recharge la page ;
- vérifie que ton appareil est sur le même réseau ;
- utilise l'adresse IP du Raspberry Pi si nécessaire.

## 4. Bonnes pratiques

Pour une installation client :

- ne garde pas le mot de passe par défaut ;
- choisis un nom d'appareil court et lisible ;
- évite les espaces, accents et caractères spéciaux dans le nom ;
- garde AVP-Py accessible uniquement sur le réseau local ;
- ne publie jamais les fichiers de configuration contenant des tokens rclone.

## 5. Exemple de configuration

Pour un écran situé dans un hall d'entrée :

```text
Nom de l'appareil : hall-entree
Adresse web       : http://hall-entree.local:8000
```

Pour un écran en salle d'attente :

```text
Nom de l'appareil : salle-attente
Adresse web       : http://salle-attente.local:8000
```
