# SPEC: AudioManager.play_bgm

## Descripción

Reproduce la música de fondo para un estado de juego dado. Selecciona un archivo de audio existente por estado o, si no encuentra archivos, usa música generada procedural.

## Inputs

- `state` (str): nombre del estado de juego (`GameState.MAIN_MENU`, `GameState.LOADING`, `GameState.GAMEPLAY`, etc.).

## Outputs

- Inicia reproducción de música en loop, ya sea desde un archivo o como sonido generado.
- No devuelve valor.

## Reglas de negocio

- Si el manager no está inicializado (`self._initialized` es `False`), no hace nada.
- Determina la pista asociada al estado consultando `_bgm_tracks`.
- Si está usando archivos reales (`_use_generated` es `False`):
  - Si la misma pista ya está cargada en `_current_track`, no reinicia la reproducción.
  - Si hay una pista para el estado, la carga con `pygame.mixer.music.load`, ajusta el volumen y reproduce en loop infinito.
  - Si no hay pista para el estado, detiene la música con `pygame.mixer.music.stop()`.
- Si está usando música generada (`_use_generated` es `True`):
  - Si el estado actual ya es el mismo, no reinicia la reproducción.
  - Llama a `pygame.mixer.stop()` y crea un `Sound` desde el buffer procedural correspondiente.
  - Reproduce el sonido en `Channel(0)` en loop infinito.
- Actualiza `_current_state` y `_current_track` al nuevo estado/pista.
- Captura excepciones de reproducción y solo imprime advertencias.

## Edge cases

- Si no existe archivo de audio para el estado, la función detiene la reproducción actual.
- Si `state` es el mismo que el actual y la pista coincide, no repone la música.
- Si la reproducción falla por error de `pygame`, se ignora el fallo sin interrumpir el flujo.
- Si `_use_generated` es `True` pero no hay buffer generado para el estado, no se reproduce música.
- Si se llama con un estado desconocido, se tratará como un estado sin pista y detendrá la música en modo de archivos.

## Supuestos

- Se asume que `_bgm_tracks` y `_bgm_buffers` ya están inicializados antes de invocar `play_bgm`.
- Se asume que `pygame.mixer` está disponible si `_initialized` es `True`.
- No se especifica qué volumen aplica exactamente cuando la pista ya se estaba reproduciendo.
