# SPEC: EconomyManager.buy_building

## Descripción

Compra un edificio deductando su coste del oro disponible y añade una instancia del edificio al estado de la partida.

## Inputs

- `building_data` (dict): datos del edificio, al menos con las claves `id`, `nombre` y opcionalmente `coste`, `stats`, `capacidadMaxima`, `tagEspeciesPermitidas`, `sprite`.

## Outputs

- `tuple`: `(success: bool, message: str, building_instance: dict or None)`.

## Reglas de negocio

- Calcula `cost` con `building_data.get('coste', 0)`.
- Si el jugador no puede permitirse el costo, retorna `(False, "Fondos insuficientes. Necesitas {cost} Solaris.", None)` y no modifica el estado.
- Si puede pagar, resta `cost` de `self.gold`.
- Crea `building_instance` con campos:
  - `id`, `nombre`, `sprite`, `coste`, `mantenimiento`, `capacidadMaxima`, `tagEspeciesPermitidas`, `criaturas_asignadas`, `tile_x`, `tile_y`, `instance_id`.
- El mantenimiento usa `building_data.get('stats', {}).get('mantenimiento', 10)`.
- La capacidad usa `building_data.get('capacidadMaxima', 5)`.
- `criaturas_asignadas` inicializa como lista vacía.
- `tile_x` y `tile_y` quedan en `None` hasta colocación.
- Genera `instance_id` con `_generate_id()`.
- Agrega la instancia a `self.save_data['buildings']`.
- Envía una notificación con texto `"Edificio adquirido: {building_data['nombre']}"`.
- Retorna `(True, "Has adquirido {nombre} por {cost} Solaris.", building_instance)`.

## Edge cases

- Si `building_data` carece de `id` o `nombre`, el método todavía crea un edificio con valores `None` y no lo valida.
- Si `coste` no está presente, se asume `0`.
- Si `building_data['stats']` no es un dict, el acceso a `.get('mantenimiento', 10)` fallará.
- Si `self.save_data['buildings']` no es una lista, el código fallará al intentar `append`.

## Supuestos

- Se asume que el inventario de edificios existe en `self.save_data['buildings']` como lista.
- Se asume que `building_data['stats']` es un diccionario válido si existe.
- No se valida la unicidad de `instance_id`.
