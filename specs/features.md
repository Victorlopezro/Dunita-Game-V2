# Dunita - Dune Dominion: Features Specification

## 1. Current Features

### 1.1 Gameplay & World
- **Infinite Procedural Map**: The game generates an infinite desert map using chunks and deterministic noise. It includes sand, rock, and oasis tiles.
- **Day/Night Cycle**: A 5-minute day and 2-minute night cycle. Enemies spawn at night, while visitors arrive during the day.
- **Building Placement**: Players can purchase buildings from the shop and place them on the grid-based map. Buildings have specific sizes and collision rules.
- **Player Movement & Combat**: The player can move using WASD, equip weapons, and shoot projectiles at enemies.
- **Entities**:
  - **Enemies**: Spawn at night, pursue the player, and deal contact damage.
  - **Visitors**: Wander around buildings during the day.
  - **Mercenaries**: Can be hired to defend the player and attack enemies.

### 1.2 Economy & Management
- **Solaris (Currency)**: The primary resource used for purchasing items, creatures, and buildings.
- **Shop System**: A UI panel with tabs for Creatures, Buildings, and Items. It displays prices, descriptions, and stats.
- **Inventory**: An 8-slot inventory for storing weapons and potions. Items can be equipped or consumed.
- **Turn Advancement**: Players can advance the day or week, which calculates and deducts upkeep costs for creatures and buildings.
- **Creature Management**: Creatures can be purchased and assigned to buildings. They have daily and weekly feeding costs.

### 1.3 UI & Accessibility
- **HUD**: Displays current Solaris, day, number of creatures, daily upkeep, and inventory slots.
- **Notifications**: Floating text messages that appear for events (e.g., purchases, turn advancement, errors).
- **Settings Menu**: Allows adjusting resolution, toggling fullscreen/vsync, and changing master/BGM/SFX volumes.
- **Accessibility Menu**: Includes colorblind filters (protanopia, deuteranopia, tritanopia), font scaling, photosensitivity toggle, and text speed adjustment.

### 1.4 Audio & Assets
- **Dynamic Audio**: Background music changes based on the current game state (Menu, Loading, Gameplay).
- **Procedural Audio Fallback**: If music files are missing, the game generates chiptune-style audio buffers.
- **Asset Management**: Sprites and fonts are loaded dynamically, with fallback placeholders for missing assets.

## 2. Planned Features (To Be Implemented)

### 2.1 UI/UX Improvements
- **Consistent Styling**: Ensure all UI panels, buttons, and text use the established Dune color palette and pixel-art style.
- **Responsiveness**: Fix issues where UI elements might overlap or not scale correctly with resolution changes.
- **Live Volume Updates**: Ensure that volume changes in the settings menu immediately affect procedurally generated BGM, not just file-based music.

### 2.2 Refactoring & Stability
- **Unify Configuration**: Remove the legacy `src.config` and update all imports to use `src.infrastructure.config.config`.
- **Decouple UI**: Refactor `ShopUI` and `BuildModeUI` to interact with the economy system through clean interfaces or events, rather than direct state manipulation.
- **Fix Tests**: Update the test environment configuration so that `pytest` can correctly resolve the `src` module, ensuring all tests pass.

### 2.3 New Functionalities
*(Note: Specific new functionalities will be detailed here based on user requirements. For now, the focus is on stabilizing the current feature set and completing the SDD refactor.)*

- **Feature A**: [Description of Feature A]
- **Feature B**: [Description of Feature B]
- **Feature C**: [Description of Feature C]
