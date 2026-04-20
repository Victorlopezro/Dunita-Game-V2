import json
import os

import firebase_admin
from firebase_admin import credentials, firestore


def _load_credentials():
    json_data = os.getenv("FIREBASE_CREDENTIALS_JSON")
    credentials_path = os.getenv("FIREBASE_CREDENTIALS_PATH")

    if json_data:
        try:
            parsed = json.loads(json_data)
            return credentials.Certificate(parsed)
        except json.JSONDecodeError as exc:
            raise RuntimeError("La variable FIREBASE_CREDENTIALS_JSON no contiene JSON válido") from exc

    if credentials_path and os.path.exists(credentials_path):
        return credentials.Certificate(credentials_path)

    raise RuntimeError(
        "No se ha configurado credencial de Firebase. Use FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH."
    )


def get_firestore_client():
    if not firebase_admin._apps:
        cred = _load_credentials()
        firebase_admin.initialize_app(cred)
    return firestore.client()
