# SPEC: EconomyManager.buy_item

## Descripción

Compra un ítem y lo adiciona al inventario o marca una contratación de entidad según el tipo de ítem.

## Inputs

- `item_data` (dict): datos del ítem, incluyendo `coste`, `tipo`, `id`, `nombre`, `descripcion`, `efectos`, `daño`, `rango`, `cadencia`, `sprite`.

## Outputs

- `tuple`: `(success: bool, message: str)`.

## Reglas de negocio

- Obtiene `cost` con `item_data.get('coste', 0)`.
- Normaliza `tipo` con `item_data.get('tipo', '').upper()`.
- Si no puede pagar, retorna `(False, "Fondos insuficientes. Necesitas {cost} Solaris.")`.
- Si el tipo es `'RECLUTA'` o `'MERCENARIO'`:
  - Resta `cost` de `self.gold`.
  - Establece `self.pending_mercenary_spawn = tipo`.
  - Retorna `(True, "{item_data['nombre']} contratado.")`.
- Si el tipo es `'POCION'` o `'ARMA'`:
  - Si `len(self.inventory) >= INVENTORY_SIZE`, retorna `(False, "Inventario lleno ({len(self.inventory)}/{INVENTORY_SIZE}).")`.
  - Resta `cost` de `self.gold`.
  - Construye `item_instance` con campos estándar y atributos adicionales:
    - Para `POCION`: `efectos`.
    - Para `ARMA`: `daño`, `rango`, `cadencia`, `sprite`, `equipado=False`.
  - Añade el item al inventario y retorna `(True, "{nombre} añadido al inventario.")`.
- Para cualquier otro tipo:
  - Resta `cost` de `self.gold`.
  - Retorna `(True, "Ítem adquirido: {nombre}")`.

## Edge cases

- Si `type` no está presente, se trata como tipo desconocido y se descuenta el coste sin almacenar el item.
- Si `item_data['sprite']` o campos específicos no existen, se usan valores por defecto.
- Si `item_data['tipo']` tiene minúsculas, se normaliza con `upper()`.
- Si `item_data['coste']` no está presente, se asume `0`.
- Si `item_data['efectos']` no es una lista, se almacena tal cual en `item_instance`.

## Supuestos

- Se asume que `self.inventory` es una lista y `INVENTORY_SIZE` es un entero.
- Se asume que la llamada a `self.pending_mercenary_spawn = tipo` es suficiente para el flujo posterior de contratación.
- No se valida si el item ya existe en el inventario.
