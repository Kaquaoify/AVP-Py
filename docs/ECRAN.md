# Réglages de l'écran

Ce guide explique la page :

```text
Paramètres > Réglages écran
```

## Objectif

AVP-Py peut utiliser HDMI-CEC pour :

- sortir un téléviseur de veille ;
- sélectionner automatiquement l'entrée HDMI du Raspberry Pi ;
- mettre le téléviseur en veille ;
- appliquer ces actions aux horaires de diffusion.

HDMI-CEC est différent de HDMI ARC. CEC transporte les commandes de contrôle, tandis qu'ARC concerne principalement le retour audio.

## 1. Vérifier la compatibilité

Le Raspberry Pi doit être directement relié au téléviseur avec un câble HDMI compatible.

Le téléviseur doit prendre en charge HDMI-CEC et cette fonction doit être activée dans ses réglages. Son nom dépend de la marque :

- Samsung : `Anynet+` ;
- LG : `SIMPLINK` ;
- Sony : `BRAVIA Sync` ;
- Panasonic : `VIERA Link` ;
- Philips : `EasyLink`.

D'autres marques utilisent généralement le nom `HDMI-CEC`, `CEC` ou `Contrôle HDMI`.

## 2. Choisir la marque

Dans `Marque du téléviseur`, sélectionne la marque concernée.

Les commandes d'alimentation utilisées par AVP-Py sont des commandes CEC standard. La marque permet surtout d'indiquer le nom commercial de la fonction et de préparer de futures adaptations si certains modèles en ont besoin.

Si la marque n'est pas proposée, utilise :

```text
Autre marque — CEC standard
```

## 3. Choisir le port HDMI

Sélectionne le port utilisé sur le Raspberry Pi :

- `HDMI 0 (/dev/cec0)` ;
- `HDMI 1 (/dev/cec1)`.

Si l'adaptateur sélectionné n'est pas détecté, essaie l'autre port puis vérifie le câble HDMI.

## 4. Tester les commandes

Clique sur :

- `Allumer et sélectionner l'entrée HDMI` pour sortir le téléviseur de veille et afficher l'entrée du Raspberry Pi ;
- `Mettre en veille` pour placer le téléviseur en veille.

Le résultat apparaît sur la page. La section `Détails techniques` contient la réponse de l'outil CEC en cas de problème.

Une commande signalée comme envoyée ne garantit pas que le téléviseur l'a appliquée. Vérifie toujours le comportement réel de l'écran.

## 5. Lier l'écran aux horaires

Va dans :

```text
Paramètres > Horaires
```

Coche :

```text
Allumer et mettre en veille l'écran automatiquement selon ces horaires
```

AVP-Py tente alors :

- d'allumer le téléviseur au début d'une plage active ;
- de sélectionner l'entrée HDMI du Raspberry Pi ;
- de mettre le téléviseur en veille à la fin de la plage ;
- de remettre l'écran dans l'état attendu après un redémarrage du service.

En cas d'échec, AVP-Py écrit l'erreur dans ses journaux et réessaie après cinq minutes.

## Dépannage

Si aucune commande ne fonctionne :

1. active HDMI-CEC dans les réglages du téléviseur ;
2. branche directement le Raspberry Pi au téléviseur ;
3. essaie l'autre port HDMI dans AVP-Py ;
4. vérifie que `cec-ctl` et l'adaptateur sont indiqués comme disponibles ;
5. redémarre le téléviseur et le Raspberry Pi ;
6. essaie un autre câble HDMI.

Commande de diagnostic en SSH :

```bash
cec-ctl -d /dev/cec0 --playback -S
```

Remplace `/dev/cec0` par `/dev/cec1` si le second port HDMI est utilisé.

## Limites

- la mise hors tension est une mise en veille, pas une coupure électrique ;
- certains téléviseurs appliquent seulement une partie des commandes CEC ;
- certains modèles désactivent CEC dans certains modes d'économie d'énergie ;
- la compatibilité doit être vérifiée sur chaque modèle de téléviseur utilisé.

## Guides liés

- [Configuration des horaires](HORAIRES.md)
- [Installation Raspberry Pi](INSTALL_RPI.md)
- [FAQ](FAQ.md)
