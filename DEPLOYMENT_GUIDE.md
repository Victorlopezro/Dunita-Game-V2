# Guía de Despliegue: Railway + Firebase para Dunita Game

Esta guía te llevará paso a paso a desplegar el backend de Dunita Game usando Railway y Firebase.

## Paso 1: Configurar Firebase

### 1.1 Crear proyecto en Firebase
1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Haz clic en "Crear un proyecto" o "Add project"
3. Nombre del proyecto: `dunita-game-backend`
4. Habilita Google Analytics (opcional)
5. Selecciona cuenta de Google
6. Espera a que se cree el proyecto

### 1.2 Configurar Firestore Database
1. En el menú lateral, ve a "Firestore Database"
2. Haz clic en "Crear base de datos"
3. Selecciona "Comenzar en modo de producción"
4. Elige una ubicación (recomendado: `us-central1` o `europe-west1`)
5. Espera a que se cree la base de datos

### 1.3 Crear cuenta de servicio
1. Ve a "Configuración del proyecto" (icono de engranaje)
2. Pestaña "Cuentas de servicio"
3. Haz clic en "Generar nueva clave privada"
4. Se descargará un archivo JSON con las credenciales
5. **IMPORTANTE**: Guarda este archivo de forma segura, no lo subas a Git

### 1.4 Configurar reglas de seguridad (Firestore)
Ve a "Firestore Database" > "Reglas" y pega estas reglas básicas:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir lectura/escritura para game_states y settings
    match /game_states/{userId} {
      allow read, write: if request.auth != null || true; // Cambia a request.auth != null para producción
    }
    match /user_settings/{userId} {
      allow read, write: if request.auth != null || true; // Cambia a request.auth != null para producción
    }
  }
}
```

## Paso 2: Preparar el Backend para Railway

### 2.1 Crear archivo de configuración de Railway
Crea el archivo `backend/railway.json`:

```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT"
  }
}
```

### 2.2 Crear archivo .env para Railway
Crea `backend/.env.railway` con las variables de entorno:

```bash
# Puerto asignado por Railway
PORT=8000

# Credenciales de Firebase (copia el contenido del JSON descargado)
FIREBASE_CREDENTIALS_JSON={"type": "service_account", "project_id": "...", ...}

# O usa el archivo de credenciales (sube el archivo JSON a Railway)
# FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json
```

## Paso 3: Desplegar en Railway

### 3.1 Crear cuenta en Railway
1. Ve a [Railway.app](https://railway.app)
2. Regístrate con GitHub
3. Conecta tu cuenta de GitHub

### 3.2 Crear nuevo proyecto
1. Haz clic en "New Project"
2. Selecciona "Deploy from GitHub repo"
3. Busca y selecciona tu repositorio `Dunita-Game-V2`
4. Railway detectará automáticamente que es un proyecto Python

### 3.3 Configurar variables de entorno
1. Ve a la pestaña "Variables" en tu proyecto Railway
2. Agrega estas variables:

```
PORT=8000
FIREBASE_CREDENTIALS_JSON=<contenido_del_json_de_firebase>
```

**Nota**: Para `FIREBASE_CREDENTIALS_JSON`, copia todo el contenido del archivo JSON de credenciales de Firebase (sin saltos de línea).

### 3.4 Desplegar
1. Railway comenzará a construir automáticamente
2. Espera a que termine el despliegue
3. Una vez desplegado, verás una URL como: `https://dunita-game-backend.up.railway.app`

### 3.5 Verificar el despliegue
1. Ve a `https://tu-url-de-railway/health` (debería devolver `{"status": "ok", "service": "dunita-game-backend"}`)
2. Prueba los endpoints:
   - `GET /game-data` - Debería devolver los datos del juego
   - `GET /game-state/test-user` - Debería devolver error 404 (usuario no existe)

## Paso 4: Configurar el Juego para usar el Backend Remoto

### 4.1 Crear archivo .env en el directorio raíz
Crea `.env` en la raíz del proyecto:

```bash
# URL del backend desplegado en Railway
REMOTE_API_URL=https://tu-url-de-railway.up.railway.app

# ID de usuario para guardar/cargar partidas
REMOTE_USER_ID=tu_usuario_unico

# Timeout para llamadas remotas (opcional)
REMOTE_REQUEST_TIMEOUT=8.0
```

### 4.2 Ejecutar el juego con backend remoto
```bash
cd dunita_game
python main.py
```

El juego ahora:
- Intentará cargar la partida desde Firebase primero
- Si no hay partida remota, usará el guardado local
- Al guardar, sincronizará con Firebase y mantendrá copia local

## Paso 5: Probar la Integración Completa

### 5.1 Prueba básica
1. Ejecuta el juego con las variables de entorno configuradas
2. Crea una nueva partida
3. Juega un poco y guarda
4. Cierra el juego
5. Vuelve a abrirlo - debería cargar desde Firebase

### 5.2 Verificar en Firebase
1. Ve a Firebase Console > Firestore Database
2. Deberías ver documentos en las colecciones:
   - `game_states/tu_usuario_unico`
   - `user_settings/tu_usuario_unico`

### 5.3 Probar múltiples dispositivos
1. Configura el mismo `REMOTE_USER_ID` en otro dispositivo
2. Ejecuta el juego - debería cargar la misma partida

## Paso 6: Configuración de Producción (Opcional)

### 6.1 Autenticación en Firebase
Para producción, configura autenticación:

1. En Firebase Console > Authentication
2. Habilita proveedores (Google, Email/Password, etc.)
3. Modifica las reglas de Firestore para requerir autenticación
4. Actualiza el backend para manejar tokens de autenticación

### 6.2 Variables de entorno adicionales
```bash
# Para producción
FIREBASE_PROJECT_ID=tu-project-id
FIREBASE_AUTH_DOMAIN=tu-project.firebaseapp.com
```

### 6.3 Monitoreo
- Configura logs en Railway
- Monitorea uso de Firestore
- Configura alertas de errores

## Solución de Problemas

### Error: "No module named 'firebase_admin'"
- Verifica que las dependencias estén en `backend/requirements.txt`
- Railway debería instalarlas automáticamente

### Error: "Invalid credentials"
- Verifica que `FIREBASE_CREDENTIALS_JSON` tenga el JSON completo
- Asegúrate de que no haya caracteres especiales mal escapados

### Error: "Connection timeout"
- Verifica que la URL de Railway sea correcta
- Aumenta `REMOTE_REQUEST_TIMEOUT` si es necesario

### El juego no guarda remotamente
- Verifica que las variables de entorno estén configuradas
- Revisa los logs del juego (debería mostrar errores de conexión)
- Prueba los endpoints manualmente con curl/Postman

## Comandos Útiles

```bash
# Probar backend localmente
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload

# Ver logs de Railway
railway logs

# Ver variables de entorno
railway variables

# Redeploy
railway up
```

## Costos Estimados

- **Railway**: ~$5/mes (hobby plan)
- **Firebase**: Primeros 50,000 reads/writes gratis, luego ~$0.06 por 100,000 operaciones

¡Tu juego Dunita ahora está desplegado y puede guardar partidas en la nube!