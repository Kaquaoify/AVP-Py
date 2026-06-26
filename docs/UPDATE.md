# Mise à jour

Ce guide explique comment mettre à jour AVP-Py sur le Raspberry Pi.

## Commande recommandée

Connecte-toi au Raspberry Pi en SSH, puis lance :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

Ne mets pas `sudo` devant cette commande.

Le script utilise lui-même les droits administrateur quand c'est nécessaire, mais le `git pull` doit être fait avec l'utilisateur propriétaire de l'installation.

## Ce que fait le script

Le script [`scripts/update.sh`](../scripts/update.sh) :

1. récupère la dernière version avec `git pull --ff-only` ;
2. met à jour les paquets système nécessaires ;
3. met à jour les dépendances Python ;
4. réinstalle la définition du service systemd ;
5. redémarre AVP-Py.

## Vérifier le service

Après la mise à jour :

```bash
sudo systemctl status avp-py.service
```

Pour suivre les logs :

```bash
sudo journalctl -u avp-py.service -f
```

## Erreurs fréquentes

### Permission denied

Si cette commande échoue :

```bash
/opt/avp-py/app/scripts/update.sh
```

utilise explicitement Bash :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

Le fichier peut ne pas avoir le droit d'exécution après récupération depuis Git.

### command not found avec sudo

Si cette commande échoue :

```bash
sudo /opt/avp-py/app/scripts/update.sh
```

n'utilise pas `sudo` directement.

Lance plutôt :

```bash
bash /opt/avp-py/app/scripts/update.sh
```

## Guides liés

- [Installation Raspberry Pi](INSTALL_RPI.md)
- [FAQ](FAQ.md)
