import json
import os

import firebase_admin
from firebase_admin import credentials, db


def _load_credentials():
    json_data = os.getenv("FIREBASE_CREDENTIALS_JSON")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if json_data:
        try:
            parsed = json.loads(json_data)
            return credentials.Certificate(parsed)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_CREDENTIALS_JSON no contiene JSON válido") from exc

    if credentials_path and os.path.exists(credentials_path):
        return credentials.Certificate(credentials_path)

    raise RuntimeError("No se ha configurado credencial de Firebase.")


def get_realtime_db():
    if not firebase_admin._apps:
        cred = _load_credentials()

        database_url = os.getenv("FIREBASE_DATABASE_URL")
        if not database_url:
            raise RuntimeError("Falta FIREBASE_DATABASE_URL")

        firebase_admin.initialize_app(cred, {
            "databaseURL": database_url
        })

    return db
