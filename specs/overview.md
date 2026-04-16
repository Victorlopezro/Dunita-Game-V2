# Dunita - Dune Dominion: System Overview

## 1. Introduction
Dunita (Dune Dominion) is a 2D real-time strategy and management game set in the Dune universe. Players manage resources (Solaris), construct buildings, recruit creatures, and survive in an infinite procedural desert map with a day/night cycle.

## 2. Core Mechanics
- **Infinite Procedural Map**: Generated in chunks using deterministic noise, featuring sand, rock, and oasis tiles.
- **Economy & Management**: Players earn and spend Solaris to buy creatures, buildings, and items.
- **Day/Night Cycle**: Affects gameplay, with enemies spawning at night and visitors arriving during the day.
- **Combat & Survival**: Players can equip weapons, shoot projectiles, and hire mercenaries to defend against enemies.
- **Building Placement**: Grid-based placement system for structures.

## 3. Technical Stack
- **Language**: Python 3.8+
- **Engine**: Pygame 2.6+
- **Architecture**: State Machine + Entity-Component-like System (Domain-Driven Design refactor in progress).
- **Data Storage**: JSON for game data, save files, and settings.

## 4. Current State & Technical Debt
The project is currently undergoing a refactor towards Spec-Driven Development (SDD) and Domain-Driven Design (DDD).
- **Mixed Paradigms**: The codebase mixes legacy mutable dictionaries with new immutable domain dataclasses.
- **Coupling**: UI components (`ShopUI`, `HUD`) are tightly coupled with the `EconomyManagerAdapter`.
- **Inconsistent Imports**: Configuration is imported from both `src.config` and `src.infrastructure.config.config`.
- **UI/UX Issues**: Some UI elements lack responsiveness, and the pause menu/settings application has minor bugs (e.g., volume not updating live for generated BGM).
- **Testing**: Tests exist but fail due to incorrect import paths (`src` module not found in PYTHONPATH during test execution).

## 5. Goals of the Refactor
1. Unify the architecture under the DDD/SDD pattern.
2. Decouple UI from business logic.
3. Fix import paths and ensure tests pass.
4. Improve UI/UX consistency and responsiveness.
5. Add new features safely without breaking existing functionality.
