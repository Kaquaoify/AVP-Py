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

## Pourquoi les boutons d'allumage et de veille ne fonctionnent-ils pas ?

Vérifie d'abord que HDMI-CEC est activé dans les réglages du téléviseur. Selon la marque, cette fonction peut s'appeler `Anynet+`, `SIMPLINK`, `BRAVIA Sync`, `VIERA Link` ou `EasyLink`.

Dans `Paramètres > Réglages écran`, vérifie ensuite :

1. que `cec-ctl` est disponible ;
2. que l'adaptateur sélectionné est détecté ;
3. que le bon port HDMI est sélectionné.

Le Raspberry Pi doit idéalement être relié directement au téléviseur. Consulte [Réglages de l'écran](ECRAN.md) pour le diagnostic complet.

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
