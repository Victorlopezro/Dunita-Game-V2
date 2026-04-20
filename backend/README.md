# Backend Dunita para Railway + Firebase

Este backend es un servicio REST mínimo para guardar la partida y la configuración de los usuarios en Firebase.

## Requisitos

- Python 3.10+
- Dependencias en `backend/requirements.txt`
- Proyecto Firebase con credenciales de servicio

## Variables de entorno

- `FIREBASE_CREDENTIALS_PATH`: ruta local al JSON de credenciales de Firebase
- `FIREBASE_CREDENTIALS_JSON`: contenido del JSON de credenciales (opcional)
- `PORT`: puerto donde se expondrá el servidor

## Endpoints principales

- `GET /game-state/{user_id}`
- `POST /game-state/{user_id}`
- `GET /settings/{user_id}`
- `POST /settings/{user_id}`
- `GET /game-data`

## Ejecución local

1. Crear entorno virtual
2. Instalar dependencias:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Exportar variables de entorno
4. Ejecutar:
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

## Despliegue en Railway

- Conecta este repositorio a Railway.
- Define `PORT` y las credenciales de Firebase.
- Usa el comando de inicio:
  ```bash
  uvicorn backend.main:app --host 0.0.0.0 --port $PORT
  ```
