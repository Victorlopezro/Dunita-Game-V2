# SPEC: EconomyManager.advance_turn

## Descripción

Avanza un turno de día o semana, descuenta los costos de alimentación de criaturas y mantenimiento de edificios, y actualiza el día.

## Inputs

- `turn_type` (str): valor esperado `'day'` o cualquier otra cadena interpretada como semana (`'week'`).

## Outputs

- `dict` con las claves:
  - `turn_type`, `days_advanced`, `new_day`, `feed_cost`, `maint_cost`, `total_cost`, `previous_gold`, `new_gold`, `feed_breakdown`, `maint_breakdown`, `bankrupt`.

## Reglas de negocio

- Si `turn_type == 'day'`, `multiplier = 1`; de lo contrario, `multiplier = 7`.
- `feed_cost` suma `costeAlimentacionDiario * multiplier` por cada criatura en `self.creatures`.
- `maint_cost` suma `mantenimiento * multiplier` por cada edificio en `self.buildings`.
- `total_cost = feed_cost + maint_cost`.
- Se guarda `previous_gold = self.gold` antes de restar costos.
- Se aplica `self.gold -= total_cost` usando el setter que impone `max(0, int(value))`.
- Se actualiza `self.save_data['day'] = self.day + multiplier`.
- El resultado incluye `bankrupt = self.gold <= 0`.
- Se envía notificación `"Turno avanzado: -{total_cost} Solaris"`.

## Edge cases

- Si `turn_type` no es `'day'`, se trata automáticamente como una semana de 7 días.
- Si `self.creatures` o `self.buildings` están vacíos, sus costos son 0.
- Si los valores de `costeAlimentacionDiario` o `mantenimiento` faltan en los datos, se usan los valores por defecto `10`.
- Si el costo excede el oro disponible, el oro se convierte en 0 pero el turno aún avanza.
- Si `self.save_data['day']` no estaba definido, `self.day` usa 1 como valor predeterminado.

## Supuestos

- Se asume que `self.creatures` y `self.buildings` son listas de diccionarios con claves esperadas.
- Se asume que `self.gold` se puede actualizar sin validar el tipo más allá de `int`.
- No se considera el caso de `turn_type == 'week'` con entradas inválidas tipo `None`; se trata como semana.
