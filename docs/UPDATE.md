## Mise à jour

Depuis le Raspberry Pi, en SSH :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

Ne pas ajouter `sudo` devant cette commande. Le script demande lui-même les droits administrateur quand ils sont nécessaires.

Le script [`scripts/update.sh`](scripts/update.sh) :

1. récupère la dernière version avec `git pull --ff-only` ;
2. met à jour les paquets système nécessaires ;
3. met à jour les dépendances Python ;
4. réinstalle la définition du service ;
5. redémarre AVP-Py.

Pour vérifier le service :

```bash
sudo systemctl status avp-py.service
```