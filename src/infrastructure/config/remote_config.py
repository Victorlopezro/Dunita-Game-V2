import os

REMOTE_API_URL = os.getenv('REMOTE_API_URL', '').strip()
REMOTE_USER_ID = os.getenv('REMOTE_USER_ID', 'default').strip()
USE_REMOTE_REPOSITORY = bool(REMOTE_API_URL)
REMOTE_REQUEST_TIMEOUT = float(os.getenv('REMOTE_REQUEST_TIMEOUT', '8.0'))
