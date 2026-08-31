Backend (Flask)

Quick start (macOS / Linux):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=run.py
flask db init  # first time
flask db migrate -m "init"
flask db upgrade
python seed.py
flask run
```

API runs on `http://127.0.0.1:5000` by default.
