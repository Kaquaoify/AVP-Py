# Optimisation de la résolution des médias

AVP-Py peut réduire automatiquement la résolution des vidéos trop grandes afin de limiter les pertes de FPS pendant la lecture.

## Résolution maximale

Une vidéo est réencodée lorsque sa largeur dépasse `2560` pixels ou lorsque sa hauteur dépasse `1440` pixels.

La nouvelle vidéo respecte :

- une résolution maximale de `2560×1440` ;
- les proportions de l'image originale ;
- le nombre d'images par seconde original ;
- le codec H.264 si la source est en H.264 ;
- le codec HEVC si la source est en HEVC ou dans un autre codec.

AVP-Py ne définit aucune nouvelle fréquence d'image pendant le réencodage.

La piste audio est copiée lorsqu'elle est compatible MP4. Dans le cas contraire, elle est convertie en AAC.

## Traitement en arrière-plan

Le réencodage est effectué fichier par fichier avec une priorité système basse.

Le traitement :

1. attend que la lecture vidéo soit inactive ;
2. écrit le résultat dans un fichier temporaire ;
3. remplace le fichier de lecture uniquement si FFmpeg termine correctement ;
4. s'interrompt et se remet en attente si une lecture démarre.

Une vidéo incomplète n'est donc jamais publiée dans la playlist.

Le traitement d'une longue vidéo 4K peut prendre beaucoup de temps sur un Raspberry Pi.

## Mode local

Après l'envoi d'une vidéo depuis `Gestion des médias`, AVP-Py vérifie sa résolution.

Si elle dépasse `2560×1440` :

- un avertissement est affiché après l'envoi ;
- le réencodage est placé dans la file d'attente ;
- l'original est remplacé par le MP4 réduit uniquement après une conversion réussie.

Le bouton `Réencodage manuel` permet de vérifier à nouveau tous les médias locaux.

## Mode rclone

Le Drive reste la source de référence.

AVP-Py utilise deux dossiers :

```text
/var/lib/avp-py/rclone-source
/var/lib/avp-py/media
```

Le premier est un miroir exact du stockage distant. Le second est la bibliothèque réellement lue par `mpv`.

Après chaque synchronisation réussie :

1. rclone termine les téléchargements, modifications et suppressions dans le miroir source ;
2. AVP-Py vérifie tous les fichiers vidéo ;
3. les vidéos compatibles sont liées ou copiées dans la bibliothèque de lecture ;
4. les vidéos trop grandes sont réencodées ;
5. les fichiers supprimés du Drive sont retirés de la bibliothèque de lecture.

Le miroir séparé évite que rclone retélécharge à chaque synchronisation les originaux qui ont été réduits localement.

Les vidéos réencodées utilisent davantage d'espace disque, car l'original distant reste conservé dans le miroir source.

## Lancer une vérification manuelle

Le bouton `Réencodage manuel` est disponible dans :

```text
Paramètres > Configuration des dossiers
```

et dans :

```text
Paramètres > Gestion des médias
```

Le bouton place la vérification dans la file d'attente. Il ne lance pas plusieurs conversions simultanément.

## Bandeau sur la page d'accueil

Lorsqu'au moins un fichier de la bibliothèque a été réduit, un bandeau rouge reste affiché en bas de la page d'accueil.

Le bandeau disparaît lorsque les fichiers concernés n'existent plus, par exemple après leur suppression manuelle ou leur retrait du Drive.

## Journaux

Les erreurs FFmpeg sont enregistrées dans :

```text
/var/lib/avp-py/logs/media-optimizer.log
```

Les messages généraux sont disponibles avec :

```bash
sudo journalctl -u avp-py.service -f
```

## Guides liés

- [Configuration rclone](RCLONE.md)
- [Utilisation en mode local](MODE_LOCAL.md)
- [Configuration des horaires](HORAIRES.md)
- [FAQ](FAQ.md)
