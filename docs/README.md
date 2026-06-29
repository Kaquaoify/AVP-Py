# Documentation AVP-Py

Bienvenue dans la documentation utilisateur d'AVP-Py.

AVP-Py est une application d'affichage vidéo pour Raspberry Pi. Elle se pilote depuis une interface web locale et peut fonctionner avec une synchronisation distante via rclone ou avec une gestion locale des vidéos.

## Démarrage

- [Premiers pas](PREMIERS_PAS.md)
  Première connexion, page d'accueil, choix du mode médias et réglages essentiels.

- [Installation Raspberry Pi](INSTALL_RPI.md)
  Installation complète sur Raspberry Pi OS Lite, service système et premier accès.

- [Mise à jour](UPDATE.md)
  Commande de mise à jour depuis le Raspberry Pi et vérification du service.

## Utilisation

- [Configuration des horaires](HORAIRES.md)
  Jours actifs, heures de lecture, synchronisation médias et redémarrage quotidien.

- [Réglages de l'écran](ECRAN.md)
  Contrôle HDMI-CEC, tests d'allumage et de veille, choix du port HDMI et automatisation horaire.

- [Configuration rclone](RCLONE.md)
  Connexion à Google Drive ou à un autre stockage distant avec rclone.

- [Utilisation en mode local](MODE_LOCAL.md)
  Envoi, suppression, renommage et ordre de lecture des vidéos depuis l'interface web.

## Réseau et administration

- [Installation avec nouveau réseau Internet](NOUVEAU_RESEAU.md)
  Connexion du Raspberry Pi à un Wi-Fi client grâce au hotspot de configuration.

- [Réglages réseau](RESEAU.md)
  Adresse locale, IP du Raspberry Pi, hotspot de secours et interfaces réseau.

- [Configuration admin](ADMIN.md)
  Nom de l'appareil, adresse `.local` et mot de passe administrateur.

## Support

- [FAQ](FAQ.md)
  Questions fréquentes et format à copier pour ajouter de nouvelles réponses.

- [Développement local](LOCAL_DEV.md)
  Lancer AVP-Py sur un PC pour tester l'interface et les changements de code.

## Accès rapide

Après installation, l'interface web est généralement disponible à l'adresse :

```text
http://nom-appareil.local:8000
```

Le mot de passe par défaut est :

```text
1234
```

Change ce mot de passe après la première connexion dans `Paramètres > Admin`.
