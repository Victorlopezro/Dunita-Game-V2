# SPEC: WorldMap.place_building

## Descripción

Coloca un edificio en el mapa procedural si la zona objetivo está libre y no contiene rocas ni otro edificio.

## Inputs

- `tx` (int): coordenada x de tile de la esquina superior izquierda del edificio.
- `ty` (int): coordenada y de tile de la esquina superior izquierda del edificio.
- `building_instance` (dict): datos del edificio, se muta para almacenar `tile_x`, `tile_y` y `size`.
- `size` (int, opcional): ancho y alto del edificio en tiles. Por defecto `3`.

## Outputs

- `bool`: `True` si el edificio se colocó con éxito, `False` si la colocación falló.

## Reglas de negocio

- Para cada tile en el rectángulo definido por `tx..tx+size-1`, `ty..ty+size-1`:
  - Si `self.get_tile(nx, ny)` es `TileType.ROCK`, la colocación falla.
  - Si `(nx, ny)` ya existe en `self.buildings_on_map`, la colocación falla.
- Si la colocación es válida:
  - Cada tile del área se asigna en `self.buildings_on_map[(nx, ny)] = building_instance`.
  - Se ajusta `building_instance['tile_x'] = tx`, `building_instance['tile_y'] = ty`, `building_instance['size'] = size`.
  - Retorna `True`.
- No hay validación adicional de valores negativos o tipos de entrada.

## Edge cases

- Si `tx` o `ty` son negativos, el método aún intenta colocar el edificio y solo falla si encuentra rocas o un edificio existente en la zona.
- Si `size` es 0 o negativa, el bucle no itera y el método devuelve `True` tras asignar `tile_x`, `tile_y` y `size` al edificio.
- Si el área cruza chunks no generados, `get_tile` genera los chunks necesarios de forma determinista.
- Si `building_instance` ya tiene `tile_x`/`tile_y` definidos, se sobrescriben con la nueva posición.

## Supuestos

- Se asume que `self.buildings_on_map` es un diccionario de coordenadas a instancias de edificios.
- Se asume que el tamaño predeterminado de un edificio es `3` tiles a menos que se pase otro valor.
- No se especifica si los edificios pueden superponerse de forma parcial; el código lo prohíbe completamente.
