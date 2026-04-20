# Dunita - Dune Dominion V2

Dunita es un juego 2D de estrategia, gestión y supervivencia ambientado en el universo de Dune. El jugador debe gestionar recursos (Solaris), construir recintos, reclutar criaturas y sobrevivir a los peligros del desierto en un mapa infinito generado proceduralmente.

## Características Principales

- **Mapa Infinito Procedural**: Explora un desierto sin fin generado mediante ruido determinista, con biomas de arena, roca y oasis.
- **Ciclo Día/Noche**: El tiempo avanza dinámicamente. Durante el día llegan visitantes a tus recintos; por la noche, los enemigos acechan.
- **Economía y Gestión**: Compra edificios, recluta criaturas y asigna cada una a su recinto ideal. Gestiona el mantenimiento diario y semanal.
- **Combate y Supervivencia**: Equipa armas, contrata mercenarios y defiende tu base de los ataques nocturnos.
- **Sistema de Logros**: Desbloquea logros a medida que progresas en el juego, con notificaciones en tiempo real.
- **Minimapa**: Visualiza tu entorno, edificios y enemigos cercanos en un minimapa integrado en el HUD.
- **Accesibilidad**: Incluye filtros para daltonismo (protanopia, deuteranopia, tritanopia), ajuste de escala de fuente y modo para fotosensibilidad.

## Requisitos del Sistema

- Python 3.8 o superior
- Pygame 2.6.1 o superior
- Pytest (para testing)

## Instalación y Ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Victorlopezro/Dunita-Game-V2.git
   cd Dunita-Game-V2
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el juego:
   ```bash
   cd dunita_game
   python main.py
   ```
## Infraestructura preparada para despliegue

Este repositorio ya incluye un backend de ejemplo listo para desplegar en Railway y una configuración inicial para conectar con Firebase. El backend se encuentra en `backend/` y expone endpoints para guardar:

- `GET /game-state/{user_id}`
- `POST /game-state/{user_id}`
- `GET /settings/{user_id}`
- `POST /settings/{user_id}`
- `GET /game-data`

También se ha preparado el juego para usar un repositorio remoto cuando se define `REMOTE_API_URL` en el entorno.

```bash
REMOTE_API_URL=http://localhost:8000
REMOTE_USER_ID=default
```

Para el backend de Firebase, consulta `backend/README.md`.
## Controles

- **W, A, S, D / Flechas**: Mover al jugador.
- **Click Izquierdo**: Disparar arma equipada / Interactuar con UI.
- **TAB / E**: Abrir/Cerrar la Tienda.
- **B**: Activar modo construcción (si hay un edificio pendiente).
- **C**: Abrir panel de asignación de criaturas.
- **F1**: Ver panel de logros.
- **F5**: Guardado rápido.
- **Espacio**: Avanzar turno (día) rápidamente.
- **ESC**: Pausar el juego / Cerrar paneles.

## Arquitectura y Refactorización (SDD/DDD)

El proyecto ha sido refactorizado siguiendo los principios de **Spec-Driven Development (SDD)** y **Domain-Driven Design (DDD)**. 

- **Modularidad**: La lógica de negocio (economía, entidades) está separada de la capa de presentación (UI).
- **Especificaciones**: La documentación técnica se encuentra en la carpeta `/specs`, detallando la arquitectura, características y visión general del sistema.
- **Tests**: Se incluye una suite de pruebas unitarias con `pytest` para garantizar la estabilidad de los sistemas core.

Para ejecutar los tests:
```bash
pytest tests/ -v
```

## Estructura del Proyecto

```text
dunita_game/
├── main.py                 # Punto de entrada
├── src/
│   ├── application/        # Casos de uso (DDD)
│   ├── domain/             # Entidades y servicios de dominio
│   ├── infrastructure/     # Adaptadores (JSON, Config)
│   ├── states/             # Máquina de estados (Menú, Gameplay)
│   ├── systems/            # Sistemas core (Mundo, Entidades, Audio, Logros)
│   └── ui/                 # Componentes de interfaz (HUD, Tienda, Minimapa, Logros)
├── data/                   # Datos del juego (JSON)
├── assets/                 # Sprites, fuentes y música
└── specs/                  # Documentación SDD
```

## Créditos

Desarrollado por Victorlopezro y contribuidores. Inspirado en el universo de Dune de Frank Herbert.
