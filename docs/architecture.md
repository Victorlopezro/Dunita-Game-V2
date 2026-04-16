# Arquitectura del Sistema

## Arquitectura General

El proyecto Dunita sigue un patrón de arquitectura aproximado a Clean Architecture (Arquitectura Limpia), dividido en capas concéntricas que separan responsabilidades y facilitan el mantenimiento y testing.

### Capas Principales

1. **Domain (Dominio)**: Contiene las entidades de negocio, servicios de dominio puros y objetos de valor. Esta capa es independiente de frameworks y representa las reglas de negocio centrales.

2. **Application (Aplicación)**: Define los casos de uso y puertos (interfaces) para interactuar con el dominio. Coordina la lógica de aplicación sin depender de detalles de infraestructura.

3. **Infrastructure (Infraestructura)**: Implementa los adaptadores concretos para persistencia, UI externa y configuración. Esta capa contiene detalles técnicos como acceso a archivos JSON, Pygame, etc.

4. **Presentation/UI**: Maneja la interfaz de usuario y la presentación, incluyendo estados del juego, widgets y managers de UI.

### Patrón de Diseño

- **Máquina de Estados**: El motor principal (`Engine`) gestiona transiciones entre estados (MainMenu, LoadingScreen, Gameplay) usando el patrón State.

- **Adaptadores y Puertos**: La capa de aplicación define interfaces (puertos) que la infraestructura implementa (adaptadores), permitiendo inyección de dependencias y testing.

- **Repositorio**: Patrón Repository para abstracción de persistencia de datos de juego.

## Módulos Principales

### Engine (`src/engine.py`)
- **Responsabilidad**: Motor principal del juego, gestiona el bucle de eventos, renderizado y máquina de estados.
- **Dependencias**: Estados, configuración, assets.
- **Interfaz**: `change_state()`, `run()`, métodos de guardado/carga.

### Estados (`src/states/`)
- **MainMenuState**: Maneja el menú principal, configuración y navegación inicial.
- **LoadingScreenState**: Pantalla de carga con animaciones y transición al gameplay.
- **GameplayState**: Estado principal de juego, coordina economía, mundo, UI y eventos.

### Sistemas (`src/systems/`)
- **AudioManager**: Gestiona música de fondo y efectos de sonido, con fallback procedural.
- **EconomyManager**: Lógica de compras, inventario y gestión económica.
- **EconomyManagerAdapter**: Adaptador entre repositorio y servicios de dominio.
- **World**: Generación procedural del mapa, renderizado de tiles y entidades.

### UI (`src/ui/`)
- **UIManager**: Gestiona la interfaz de usuario, tienda, inventario y notificaciones.
- **Widgets**: Componentes reutilizables como botones, paneles y sliders.

### Domain (`src/domain/`)
- **Entities**: Definiciones de entidades inmutables (Creature, Building, Item, etc.).
- **Services**: Lógica de dominio pura (EconomyService).
- **Value Objects**: Objetos de valor para datos específicos.

### Application (`src/application/`)
- **Use Cases**: Casos de uso como comprar criatura o avanzar turno.
- **Ports**: Interfaces abstractas (GameRepository).

### Infrastructure (`src/infrastructure/`)
- **Adapters**: Implementaciones concretas (JsonGameRepository).
- **Config**: Configuración y constantes del juego.

## Flujo de Datos

### Ciclo Principal
1. `main.py` inicializa Pygame y crea el `Engine`.
2. `Engine` registra estados y entra en el bucle principal.
3. En cada frame:
   - Procesa eventos → Estado actual.
   - Actualiza lógica → Estado actual (llama a sistemas como Economy, World).
   - Renderiza → Estado actual (dibuja UI, mundo).

### Interacción Usuario → Dominio
1. Usuario interactúa con UI (ej: comprar edificio en tienda).
2. `UIManager` captura evento y llama a `GameplayState`.
3. `GameplayState` invoca caso de uso en `Application` (ej: BuyBuildingUseCase).
4. Caso de uso valida reglas de dominio usando `Domain Services`.
5. Persistencia via `Infrastructure Adapters` (JSON).

### Economía y Mundo
- `EconomyManager` maneja estado económico en memoria.
- `EconomyManagerAdapter` sincroniza con `JsonGameRepository` para persistencia.
- `World` genera chunks procedurales y renderiza basado en estado de juego.

### Audio
- `AudioManager` carga archivos o genera proceduralmente.
- Estados llaman `play_bgm(state)` para cambiar música.

## Dependencias y Acoplamiento

- **Bajo acoplamiento**: Capas superiores no dependen de inferiores; usan interfaces.
- **Inyección de dependencias**: `Engine` inyecta dependencias a estados.
- **Separación de responsabilidades**: Cada módulo tiene una responsabilidad clara.
- **Testing**: Arquitectura facilita mocking de dependencias para tests unitarios.

## Consideraciones Técnicas

- **Pygame**: Framework principal para renderizado, eventos y audio.
- **JSON**: Persistencia simple y portable.
- **Procedural Generation**: Mapas y audio generados dinámicamente.
- **Pixel Art**: Estilo visual consistente con assets 8-bit.