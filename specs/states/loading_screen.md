# SPEC: Loading Screen Timer and Transition

## Descripción

El estado de carga muestra una pantalla de carga simulada de exactamente 7000 ms (7 segundos) y, al completarse, transiciona automáticamente al estado de gameplay.

## Inputs

- `dt` (float): tiempo transcurrido desde el último frame en segundos.
- `mode` (str): modo de carga; se acepta `'new'` o `'load'`.
- `kwargs` (dict): parámetros opcionales que se reenvían al estado de gameplay.
- `game_data` (dict): datos cargados del juego para mostrar tips y criaturas.

## Outputs

- Transición interna al estado `GameState.GAMEPLAY` mediante `engine.change_state` cuando se completa el temporizador.
- Actualización de animación de tips, criaturas y puntos de progreso internos.
- No devuelve valores explícitos.

## Reglas de negocio

- El temporizador avanza con `elapsed_ms += dt * 1000.0`.
- La duración total del loading es `LOADING_DURATION_MS` (7000 ms).
- Mientras `elapsed_ms < total_ms`, el estado sigue activo y no transiciona.
- Cuando `elapsed_ms >= total_ms` por primera vez, se marca `done` y se llama a `engine.change_state(GameState.GAMEPLAY, **kwargs)`.
- No hay forma de omitir la pantalla de carga mediante eventos de usuario.
- Los tips de lore rotan cada `tip_duration` de 1.8 segundos.
- Las criaturas mostradas rotan cada `creature_duration` de 2.0 segundos.
- La barra de progreso usa una curva predefinida no lineal y se calcula a partir de `elapsed_ms / total_ms`.

## Edge cases

- Si `dt` es 0, la pantalla de carga no avanza.
- Si `elapsed_ms` salta por encima de `total_ms` en una sola actualización, la transición ocurre inmediatamente en esa actualización.
- Si `game_data` no contiene `lore_tips`, se usan mensajes por defecto.
- Si `game_data['creatures']` está vacío o no existe, no se dibuja ninguna criatura en la pantalla de carga.
- Si `mode` no es `'new'` ni `'load'`, el estado aún se comporta igual porque `mode` solo se almacena y no se valida.

## Supuestos

- Se asume que `engine.change_state` manejará correctamente la creación del siguiente estado.
- No hay validación de `kwargs`; se asume que el estado de gameplay los acepta sin error.
- Si el temporizador se supera, la transición no se repite porque `done` previene múltiples llamadas.
