## Développement local

Sur PC :

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn avppy.app:app --reload --host 127.0.0.1 --port 8000
```

Les dépendances Python sont listées dans [`requirements.txt`](requirements.txt).

Sous Windows, les commandes `mpv` via socket Unix sont ignorées par le contrôleur. L'interface web et la configuration restent testables.