# FAQ




## Je ne peux pas ouvrir `http://nom-appareil.local:8000`, que vérifier ?

Vérifie d'abord que ton ordinateur ou ton téléphone est connecté au même réseau local que le Raspberry Pi.

Ensuite :

1. ouvre `Paramètres > Réseau` si tu as encore accès à l'interface ;
2. regarde l'adresse indiquée dans le bloc `Accès local` ;
3. essaie l'adresse IP directe, par exemple `http://192.168.1.42:8000` ;
4. vérifie que le service AVP-Py est actif sur le Raspberry Pi.

Commande utile en SSH :

```bash
sudo systemctl status avp-py.service
```

Si l'adresse `.local` ne fonctionne pas mais que l'IP fonctionne, le problème vient probablement de la résolution mDNS côté réseau ou côté appareil client.

---

## Mes vidéos envoyées en mode local ont disparu, pourquoi ?

Le mode rclone et le mode local ne doivent pas gérer les mêmes fichiers en même temps.

Si AVP-Py est repassé en `Synchronisation rclone`, le dossier distant redevient la source de référence. Lors du prochain `rclone sync`, un fichier local absent du dossier distant peut être supprimé.

Pour éviter ça :

1. utilise `Gestion locale depuis l'interface web` si les vidéos sont gérées directement dans AVP-Py ;
2. utilise `Synchronisation rclone` si Google Drive ou un stockage distant est la source principale ;
3. évite de mélanger les deux modes sur le même dossier.

---

## La synchronisation rclone échoue, que vérifier ?

Vérifie les informations dans `Paramètres > Configuration des dossiers`.

Contrôle en priorité :

- le `Nom du remote rclone`, par exemple `gdrive` ;
- le `Chemin du dossier distant` ;
- le contenu complet de `rclone.conf` ;
- l'accès du compte Google au dossier distant ;
- la connexion Internet du Raspberry Pi.

Utilise ensuite le bouton :

```text
Tester la connexion
```

Si le test fonctionne, lance :

```text
Synchroniser maintenant
```

---

## Pourquoi une vidéo importée est-elle en attente de réencodage ?

Les vidéos dépassant `2560×1440` sont réduites pour améliorer la fluidité de lecture.

Si une vidéo est en cours de lecture, AVP-Py la suspend pendant le traitement puis la relance lorsque celui-ci est terminé. Une lecture déjà arrêtée avant le traitement reste arrêtée.

Une conversion 4K peut prendre longtemps sur le Raspberry Pi. Son état et le nom du fichier en cours sont actualisés automatiquement dans `Configuration des dossiers` et `Gestion des médias`.

Consulte l'état dans `Configuration des dossiers` ou `Gestion des médias`, puis vérifie les erreurs avec :

```bash
sudo tail -n 100 /var/lib/avp-py/logs/media-optimizer.log
```

Voir [Optimisation de la résolution des médias](OPTIMISATION_MEDIAS.md).

---

## Pourquoi les boutons d'allumage et de veille ne fonctionnent-ils pas ?

Vérifie d'abord que HDMI-CEC est activé dans les réglages du téléviseur. Selon la marque, cette fonction peut s'appeler `Anynet+`, `SIMPLINK`, `BRAVIA Sync`, `VIERA Link` ou `EasyLink`.

Dans `Paramètres > Réglages écran`, vérifie ensuite :

1. que `cec-ctl` est disponible ;
2. que l'adaptateur sélectionné est détecté ;
3. que le bon port HDMI est sélectionné.

Le Raspberry Pi doit idéalement être relié directement au téléviseur. Consulte [Réglages de l'écran](ECRAN.md) pour le diagnostic complet.

---

## Pourquoi la console apparaît-elle si l'écran est branché après le démarrage ?

Après un branchement HDMI tardif, le connecteur vidéo peut être disponible avant la sortie audio HDMI. Dans ce cas, `mpv` doit utiliser temporairement une sortie audio silencieuse pour continuer la vidéo au lieu d'abandonner la lecture.

Après avoir branché l'écran, attends quelques secondes. La lecture doit démarrer sans appuyer sur `Play`.

Lorsque la lecture est mise en pause ou que la plage horaire se termine, AVP-Py charge une image noire interne dans `mpv`. Cela maintient la sortie HDMI active et évite le retour de la console.

Si la console reste affichée, vérifie :

```bash
sudo journalctl -u avp-py.service -n 100 --no-pager
sudo tail -n 100 /var/lib/avp-py/logs/mpv.log
ls -l /var/lib/avp-py/mpv.sock
```

Consulte aussi [Réglages de l'écran](ECRAN.md).

---

## Pourquoi le bouton Redémarrer ne fonctionne-t-il pas ?

Le bouton nécessite une session administrateur active et les droits `sudo` installés par AVP-Py.

Vérifie en SSH :

```bash
sudo -n /usr/bin/systemctl reboot
```

Attention : cette commande redémarre immédiatement le Raspberry Pi si les droits sont corrects.

Si elle demande un mot de passe ou renvoie une erreur, relance la mise à jour :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

---

## Pourquoi le bouton de mise à jour web ne fonctionne-t-il pas ?

Le bouton `Lancer la mise à jour` se trouve dans `Paramètres > Admin`.

Il nécessite :

- une session administrateur active ;
- le mot de passe de confirmation `1234` ;
- les droits `sudo` installés par AVP-Py.

Si le bouton échoue, relance une fois la mise à jour en SSH pour réinstaller les droits :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

Ensuite, le bouton web doit pouvoir lancer :

```bash
sudo -n /bin/bash /opt/avp-py/app/scripts/update.sh
```

Les logs de la mise à jour web sont écrits dans :

```bash
/var/lib/avp-py/logs/update.log
```

---

## Le Raspberry Pi arrive chez un client sans Wi-Fi connu, comment le connecter ?

Si aucun réseau connu n'est disponible au démarrage, AVP-Py démarre un hotspot de configuration.

Connecte un téléphone ou un ordinateur au Wi-Fi :

```text
AVP-SETUP-nom-appareil
```

Mot de passe par défaut :

```text
avpsetup123
```

Puis ouvre :

```text
http://10.42.0.1:8000/setup/wifi
```

Choisis le Wi-Fi client, entre son mot de passe et valide.
