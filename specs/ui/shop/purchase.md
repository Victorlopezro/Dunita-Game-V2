# SPEC: ShopUI Purchase Flow

## Descripción

Gestiona la compra de elementos en la tienda del juego según la pestaña activa, y en el caso de edificios activa el modo de construcción posterior.

## Inputs

- `tab` (str): pestaña activa de la tienda; valores posibles `'creatures'`, `'buildings'`, `'items'`.
- `selected_item` (dict or None): item seleccionado de la lista.
- `economy` (`EconomyManager`): subsistema de economía que realiza la compra.

## Outputs

- `message` (str): texto mostrado de éxito o error.
- `message_color` (color): color para el mensaje (`UI_SUCCESS` o `UI_ERROR`).
- `pending_building_placement` (dict or None): instancia de edificio creada solo cuando se compró un edificio con éxito.
- `visible` (bool): la tienda se cierra si se compra con éxito un edificio.

## Reglas de negocio

- Si `selected_item` es `None`, no se realiza ninguna compra y se muestra `"Selecciona un item primero."`.
- Según `tab`:
  - `'creatures'`: llama a `economy.buy_creature(selected_item)`.
  - `'buildings'`: llama a `economy.buy_building(selected_item)`.
  - cualquier otro valor, incluido `'items'`: llama a `economy.buy_item(selected_item)`.
- Si la compra es exitosa y `tab == 'buildings'` y `instance` no es `None`:
  - cierra la tienda (`visible = False`).
  - asigna `pending_building_placement = instance`.
- Reproduce `audio.play_sfx('buy')` en compras exitosas y `audio.play_sfx('error')` en fallos si el audio está disponible.
- El mensaje de resultado se muestra con color verde para éxito y rojo para error.

## Edge cases

- Si `buy_building` retorna `(True, msg, None)`, la tienda no recibe `pending_building_placement` aunque la compra sea exitosa.
- Si `tab` contiene un valor distinto de `'creatures'` y `'buildings'`, se trata como tienda de ítems.
- Si `economy.buy_*` lanza una excepción, la excepción se captura solo en la reproducción de audio, no en la compra.
- Si `selected_item` no tiene los campos esperados por el método de economía, la compra puede fallar en la lógica de economía.

## Supuestos

- Se asume que la instancia de edificio devuelta por `buy_building` es válida y contiene `instance_id`.
- Se asume que la tienda no necesita refrescar la lista tras la compra en este método.
- No se valida internamente que `tab` sea exactamente una de las pestañas conocidas.
