## Arquitectura actual

El proyecto está organizado como un juego 2D de gestión con una estructura aproximada de capas:
- `main.py`: punto de entrada que arranca el motor y registra estados.
- `src/engine.py`: motor principal con máquina de estados, bucle de juego y gestión de configuración/guardado.
- `src/infrastructure/`: persistencia y configuración de datos.
- `src/domain/`: entidades de negocio, servicios de dominio y puertos.
- `src/application/`: casos de uso y puertos de repositorio.
- `src/systems/`: subsistemas de juego como audio, economía y mundo procedural.
- `src/ui/`: widgets y lógica de interfaz de usuario.
- `src/utils/`: gestión de assets y utilidades.

La arquitectura parece querer soportar un patrón hexagonal o limpio, pero en la práctica mezcla enfoques de dominio rico con lógica procedural y dependencias directas.

## Módulos y responsabilidades

- `main.py`
  - Inicializa Pygame.
  - Crea el `Engine`.
  - Registra los estados del juego: menú principal, loading y gameplay.
  - Lanza el ciclo de ejecución.

- `src/engine.py`
  - Inicializa la ventana, el reloj, carga assets y configuración.
  - Controla la máquina de estados y la transición entre ellos.
  - Gestiona el ciclo principal de eventos, actualización y render.
  - Provee métodos de guardado/carga básica de partidas y ajustes.
  - Define la clase base `BaseState` para estados.

- `src/infrastructure/config/config.py`
  - Define rutas, constantes del juego, tamaños de pantalla, tiempos y ajustes por defecto.
  - Provee carga/guardado de settings y datos de juego desde JSON.

- `src/config.py`
  - Provee constantes globales similares al config de infraestructura.
  - Contiene valores de pantalla, directorios, colores y funciones de assets.
  - Se usa de forma inconsistente junto a `src.infrastructure.config.config`.

- `src/utils/asset_manager.py`
  - Carga fuentes, sprites y assets de UI.
  - Genera placeholders para assets faltantes.
  - Provee soporte opcional de filtros de daltonismo (requiere `numpy`).

- `src/ui/widgets.py`
  - Define componentes básicos de UI: botones, paneles, sliders, toggles, labels y listas scroll.
  - Implementa eventos y dibujo de elementos pixel art.

- `src/ui/ui_manager.py`
  - Implementa la HUD del juego, tienda, panel de turno y notificaciones.
  - Gestiona interacciones de inventario, compra, equipamiento y visualización de estado.

- `src/states/main_menu.py`
  - Contiene lógica del menú principal y subpaneles de configuración, accesibilidad y créditos.
  - Implementa un fondo animado, botones y paneles configurables.

- `src/states/loading_screen.py`
  - Estado de carga con barra de progreso simulada, tips de lore y transición al gameplay.

- `src/states/gameplay.py`
  - Estado principal de juego: inicializa el repositorio, economía, mundo, jugador, cámara y UI.
  - Controla pausa, compras, colocación de edificios, disparos, avance de turno y notificaciones.

- `src/systems/audio_manager.py`
  - Gestiona BGM y SFX.
  - Intenta cargar archivos de audio; en caso de fallo genera audio chiptune procedural.
  - Controla volúmenes master, BGM y SFX.

- `src/systems/world.py`
  - Genera un mapa infinito por chunks con tile-based procedural generation.
  - Dibuja tiles y edificios.
  - Controla el jugador y la cámara.

- `src/systems/economy_manager.py`
  - Lógica de economía basada en diccionarios: compras, inventario, asignación de criaturas, avance de turnos y gastos.

- `src/systems/economy_manager_adapter.py`
  - Adaptador entre repositorio y lógica de economía/servicios más modernos.
  - Usa `EconomyService` y casos de uso para persistencia basada en dominio.
  - Mezcla entidades de dominio con estructuras de datos tipo diccionario.

- `src/domain/entities.py`
  - Define entidades inmutables tipo `Creature`, `Building`, `Item`, `Weapon` y `GameState`.

- `src/domain/services/economy_service.py`
  - Lógica de dominio pura para compra de criaturas, edificios, ítems y avance de turnos.

- `src/application/use_cases/economy_use_cases.py`
  - Casos de uso de aplicación para comprar criatura, avanzar turno y asignar criatura a edificio.

- `src/application/ports/game_repository.py`
  - Interfaz abstracta del repositorio de juego.

- `src/infrastructure/adapters/json_game_repository.py`
  - Persistencia JSON de `GameState`, settings y datos de juego.
  - Convierte entre entidades de dominio y dicts con keys en español.

## Dependencias

Internas:
- Estados conectados mediante `Engine` y `BaseState`.
- `GameplayState` depende de `JsonGameRepository`, `EconomyManagerAdapter`, `WorldMap`, `PlayerController`, `Camera`, varias entidades de `systems.entities` y UI de `ui_manager`.
- `ShopUI` y `HUD` dependen del subsistema de economía para realizar compras y equipamiento.
- `audio_manager` se usa en múltiples estados y widgets para reproducir BGM/SFX.
- `AssetManager` es un singleton global en `src.utils.asset_manager`.
- `EconomyManagerAdapter` conecta el repositorio con `EconomyService` y `economy_use_cases`.
- `JsonGameRepository` implementa el puerto `GameRepository`.

Externas:
- `pygame`: motor gráfico, eventos, audio y superficies.
- `json`, `os`, `math`, `random`, `sys`: librerías estándar.
- `numpy` opcional en `AssetManager.apply_colorblind_filter`.

## Problemas detectados

1. Inconsistencia arquitectónica
   - Existe una intención de capa limpia (`domain`, `application`, `infrastructure`), pero el juego mezcla datos dict con entidades de dominio.
   - `src/config.py` y `src/infrastructure/config/config.py` duplican responsabilidades y se importan de forma inconsistente.
   - `EconomyManagerAdapter` intenta adaptar dos estilos distintos y deja una integración frágil.

2. Código duplicado y mezcla de paradigmas
   - Hay economía gestionada en `EconomyManager` y otra lógica adaptada en `EconomyManagerAdapter`/`EconomyService`.
   - Algunas funciones de persistencia y conversión aparecen en dos lugares similares (`JsonGameRepository` y el adaptador).
   - `Engine` manipula directamente `save_data` y también utiliza repositorio, lo que puede causar desincronizaciones.

3. Code smells
   - Funciones largas y estados monolíticos: `MainMenuState._build_settings_panel`, `GameplayState.on_enter`, `ShopUI.draw/_draw_detail` son extensos y mezclan UI con lógica.
   - Campos no usados: en `Button`, `_sfx_hover_played` se inicializa pero no se utiliza.
   - Comentarios que indican hacks: `pending_building_placement` en `ShopUI` es un puente ad-hoc entre capas.
   - Uso de strings literales y valores mágicos en muchos sitios (`'ARMA'`, `'POCION'`, `'RECLUTA'`, coordenadas, tiempos).

4. Posibles bugs
   - En `EconomyService.buy_item`, la clave de datos del daño usa `item_data.get('daÃ±o', 10)` en lugar de `daño`, lo que parece un error de codificación/encoding.
   - `EconomyManagerAdapter._build_state_from_dict` puede crear `Position(None, None)` para edificios sin coordenadas, lo que puede ser ofensivo para la lógica que asume posiciones válidas.
   - `WorldMap.is_walkable` ignora edificios y devuelve `True` para terreno dentro de edificios según el comentario; puede permitir al jugador entrar en zonas construidas.
   - `Engine.apply_display_settings` reaplica la pantalla pero actualiza solo `self.current_state.screen`, no otros elementos dependientes de pantalla.
   - `MainMenuState` usa `from src.config import save_settings` en vez del mismo módulo de configuración que `Engine`, lo que refuerza la duplicación.
   - `AudioManager._update_volumes` reconoce que la música generada no puede cambiar volumen sin recargar, pero no aplica el cambio, dejando el ajuste de volumen de BGM inconsistente.

5. Incoherencias de diseño
   - El modelo de datos usa entidades inmutables (`@dataclass(frozen=True)`) pero después el adaptador y la UI trabajan con dicts mutables.
   - `JsonGameRepository` usa claves en castellano y objetos de dominio, mientras que la UI y los subsistemas esperan estructuras mixtas.
   - La lógica de progreso de carga es visual y separada, pero no hay señal clara de si el juego real está listo; la carga es siempre simulada.
   - El motor de audio mezcla carga de archivos con generación procedural de música y SFX, creando un único componente con responsabilidad múltiple.

## Funcionalidades clave

- Menú principal con opciones de nueva partida, cargar partida, configuración, accesibilidad y créditos.
- Pantalla de carga con animación, tips y progreso ficticio de 7 segundos.
- Gameplay con:
  - Mapa procedural infinito basado en chunks y ruido determinista.
  - Control de jugador sobre el mundo y cámara suavizada.
  - HUD con saldo, día, criaturas, gasto diario e inventario.
  - Tienda de criaturas, edificios e ítems con selección y compra.
  - Sistema de economía: oro, inventario, compra de armas/pociones, contratación de mercenarios/reclutas.
  - Colocación de edificios en el mapa y asignación de criaturas a recintos.
  - Avance de turno (día/semana) con cálculo de coste de alimentación y mantenimiento.
  - Notificaciones en pantalla.
- Gestión de assets y gráficos: sprites de criaturas, edificios, tiles y UI.
- Audio con música de fondo por estado, efectos de sonido y fallback procedural.
- Configuración de usuario persistente: resolución, fullscreen, vsync, volumen, escala de fuente y modo daltonismo.
- Persistencia de juego en JSON para partida guardada y ajustes.

