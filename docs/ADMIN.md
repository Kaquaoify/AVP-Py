# Configuration admin

Ce guide explique la page :

```text
Paramètres > Admin
```

## Objectif

La page `Admin` permet de configurer :

- le nom de l'appareil ;
- l'adresse locale en `.local` ;
- le mot de passe administrateur ;
- la mise à jour de l'application.

Le bandeau supérieur de toutes les pages authentifiées permet également de redémarrer le Raspberry Pi.

## 1. Modifier le nom de l'appareil

Le champ `Nom de l'appareil` définit le nom visible dans AVP-Py.

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

Les espaces, accents et caractères spéciaux sont convertis en nom compatible réseau.

Exemple :

```text
Hall Entrée
```

devient :

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

AVP-Py n'utilise pas de nom d'utilisateur : l'accès administrateur se fait uniquement par mot de passe.

## 3. Lancer une mise à jour depuis l'interface web

La page `Admin` contient un bloc `Mise à jour de l'application`.

Pour lancer une mise à jour :

1. saisis le mot de passe de confirmation ;
2. clique sur `Lancer la mise à jour` ;
3. attends que la page revienne automatiquement sur l'administration.

Le mot de passe de confirmation par défaut est :

```text
1234
```

Ce mot de passe ne remplace pas le mot de passe administrateur. Il sert seulement à éviter un clic involontaire.

La mise à jour lance le script :

```bash
/opt/avp-py/app/scripts/update.sh
```

Le service AVP-Py redémarre à la fin de la mise à jour.

## 4. Après changement du nom

Après modification du nom de l'appareil, l'ancienne adresse `.local` peut ne plus répondre.

Utilise la nouvelle adresse indiquée par AVP-Py :

```text
http://nouveau-nom.local:8000
```

Si la nouvelle adresse ne répond pas immédiatement :

- attends quelques secondes ;
- recharge la page ;
- vérifie que ton appareil est sur le même réseau ;
- utilise l'adresse IP du Raspberry Pi si nécessaire.

L'adresse IP est visible dans :

```text
Paramètres > Réseau
```

## Bonnes pratiques

Pour une installation client :

- ne garde pas le mot de passe par défaut ;
- choisis un nom court et lisible ;
- évite les espaces, accents et caractères spéciaux dans le nom ;
- garde AVP-Py accessible uniquement sur le réseau local ;
- ne publie jamais de configuration contenant un token rclone.

## Redémarrer le Raspberry Pi

Le bouton `Redémarrer` est disponible dans le bandeau supérieur, à côté de `Déconnexion`.

Après confirmation :

1. AVP-Py demande le redémarrage avec une commande système fixe ;
2. le navigateur attend que le Raspberry Pi s'arrête ;
3. la page d'accueil est rouverte automatiquement lorsque le service répond de nouveau.

L'action exige une session administrateur AVP-Py active. Elle utilise :

```bash
sudo -n /usr/bin/systemctl reboot
```

Les scripts d'installation et de mise à jour ajoutent la commande `systemctl reboot` aux autorisations `sudo` sans mot de passe d'AVP-Py. Aucun argument fourni par le navigateur n'est transmis à la commande système.

Ils autorisent aussi le lancement du script de mise à jour AVP-Py via une commande fixe :

```bash
sudo -n /bin/bash /opt/avp-py/app/scripts/update.sh
```

Aucun chemin fourni par le navigateur n'est transmis à cette commande.

## Exemples

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

## Guides liés

- [Réglages réseau](RESEAU.md)
- [Premiers pas](PREMIERS_PAS.md)
- [FAQ](FAQ.md)
