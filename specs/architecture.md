# Dunita - Dune Dominion: Architecture Specifications

## 1. Architectural Pattern
The game follows a **State Machine** architecture at the highest level, combined with an emerging **Domain-Driven Design (DDD)** and **Spec-Driven Development (SDD)** approach for the business logic.

### 1.1 State Machine
The `Engine` class manages the game loop and transitions between states:
- `MainMenuState`: Handles the main menu, settings, accessibility, and credits.
- `LoadingScreenState`: Simulates a loading screen with lore tips and creature showcases.
- `GameplayState`: The core game loop, managing the world, economy, entities, and UI.

### 1.2 Domain-Driven Design (DDD)
The project is transitioning to a layered architecture:
- **Domain Layer**: Contains immutable dataclasses (`Creature`, `Building`, `Item`, `Weapon`, `GameState`) representing the core business entities.
- **Application Layer**: Contains use cases (`BuyCreatureUseCase`, `AdvanceTurnUseCase`) that orchestrate domain logic and persistence.
- **Infrastructure Layer**: Contains adapters (`JsonGameRepository`) for data persistence and configuration.
- **Presentation/UI Layer**: Contains Pygame-based UI components (`HUD`, `ShopUI`, `TurnPanel`).

## 2. Core Systems

### 2.1 Economy System
The economy is managed by the `EconomyManagerAdapter`, which bridges the legacy mutable dictionary-based system with the new immutable domain entities. It handles:
- Solaris (currency) management.
- Purchasing creatures, buildings, and items.
- Inventory management and weapon equipping.
- Turn advancement (daily/weekly upkeep costs).

### 2.2 World System
The `WorldMap` class generates an infinite procedural map using deterministic noise based on a seed. It manages:
- Tile types (Sand, Rock, Oasis, Floor).
- Building placement and collision detection.
- Camera following the player.

### 2.3 Entity System
Entities (`PlayerController`, `Enemy`, `Visitor`, `Mercenary`, `Projectile`) are updated and drawn every frame in the `GameplayState`. They handle movement, collision, and combat logic.

### 2.4 Audio System
The `AudioManager` singleton handles background music (BGM) and sound effects (SFX). It supports both file-based audio and procedural chiptune generation as a fallback.

## 3. Technical Debt & Refactoring Plan

### 3.1 Import Inconsistencies
Currently, configuration is imported from both `src.config` and `src.infrastructure.config.config`. This must be unified to use a single source of truth, preferably `src.infrastructure.config.config`.

### 3.2 UI Coupling
UI components like `ShopUI` directly interact with the `EconomyManagerAdapter` and manipulate game state (e.g., `pending_building_placement`). This logic should be decoupled, with UI components emitting events or calling specific use cases.

### 3.3 Mutable vs. Immutable State
The transition to DDD is incomplete. The `EconomyManagerAdapter` still relies heavily on mutable dictionaries for UI compatibility. The refactor should aim to fully adopt immutable domain entities throughout the application, updating the UI to consume these entities directly.

### 3.4 Testing
Tests currently fail due to `ModuleNotFoundError: No module named 'src'`. The test environment must be configured to include the project root in the `PYTHONPATH`.

## 4. Directory Structure
```text
dunita_game/
├── main.py                 # Entry point
├── src/
│   ├── application/        # Use cases and ports
│   ├── domain/             # Entities and value objects
│   ├── infrastructure/     # Adapters and configuration
│   ├── states/             # Game states (MainMenu, Loading, Gameplay)
│   ├── systems/            # Core systems (Audio, Economy, World, Entities)
│   ├── ui/                 # UI components and widgets
│   ├── utils/              # Utilities (AssetManager)
│   ├── config.py           # Legacy configuration (to be deprecated)
│   └── engine.py           # Game engine and state machine
├── data/                   # Game data (JSON)
├── assets/                 # Sprites and music
└── tests/                  # Unit tests
```
