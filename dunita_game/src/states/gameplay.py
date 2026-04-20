"""
DUNE DOMINION - Estado: Gameplay
Loop principal con mapa infinito, ciclo día/noche, enemigos, visitantes y logros.
"""
import pygame
import math
import random
import os

from src.engine import BaseState
from src.infrastructure.config.config import (
    GameState, Colors, SCREEN_WIDTH, SCREEN_HEIGHT,
    TILE_SIZE, DAY_DURATION_SEC, NIGHT_DURATION_SEC, ENEMY_SPAWN_RATE,
    SAVE_FILE, SETTINGS_FILE, DATA_DIR
)
from src.infrastructure.adapters.json_game_repository import JsonGameRepository
from src.infrastructure.adapters.remote_game_repository import RemoteGameRepository
from src.infrastructure.config.remote_config import (
    REMOTE_API_URL,
    REMOTE_USER_ID,
    USE_REMOTE_REPOSITORY,
)
from src.utils.asset_manager import assets
from src.systems.audio_manager import audio
from src.systems.economy_manager import EconomyManager
from src.systems.world import WorldMap, PlayerController, Camera
from src.systems.entities import Enemy, Visitor, Mercenary, Projectile
from src.systems.achievements import AchievementManager
from src.ui.ui_manager import HUD, ShopUI, TurnPanel, BuildModeUI, Notification
from src.ui.minimap import Minimap
from src.ui.achievements_panel import AchievementsPanel
from src.ui.creature_assignment_panel import CreatureAssignmentPanel


class GameplayState(BaseState):

    def on_enter(self, **kwargs):
        # Música de gameplay
        audio.play_bgm(GameState.GAMEPLAY)

        # Repositorio y economía
        local_repository = JsonGameRepository(SAVE_FILE, SETTINGS_FILE, os.path.join(DATA_DIR, 'game_data.json'))
        if USE_REMOTE_REPOSITORY:
            self.repository = RemoteGameRepository(REMOTE_API_URL, REMOTE_USER_ID, local_repository)
        else:
            self.repository = local_repository
        from src.systems.economy_manager_adapter import EconomyManagerAdapter
        self.economy = EconomyManagerAdapter(self.repository, initial_state=self.engine.save_data)
        self.economy.add_callback(self._on_economy_event)

        # Mapa infinito
        seed = self.engine.save_data.get('seed', None)
        self.world = WorldMap(seed=seed)
        if seed is None:
            self.engine.save_data['seed'] = self.world.seed

        # Restaurar edificios colocados
        for building in self.economy.buildings:
            tx = building.get('tile_x')
            ty = building.get('tile_y')
            if tx is not None and ty is not None:
                self.world.place_building(tx, ty, building)

        # Jugador
        px = self.engine.save_data.get('player_pos', [0, 0])
        self.player = PlayerController(px[0], px[1], self.world)

        # Cámara
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        self.camera.x = self.player.px - SCREEN_WIDTH // 2
        self.camera.y = self.player.py - SCREEN_HEIGHT // 2

        # UI principal
        self.hud = HUD(self.economy, self.player)
        self.shop = ShopUI(self.economy, self.engine.game_data)
        self.turn_panel = TurnPanel(self.economy)
        self.build_mode = BuildModeUI(self.world, self.economy)

        # Nuevas funcionalidades
        self.minimap = Minimap(self.world)
        self.achievement_manager = AchievementManager()
        self.achievement_panel = AchievementsPanel(self.achievement_manager)
        self.creature_assignment = CreatureAssignmentPanel(self.economy)

        # Restaurar estado de logros si existe
        achievements_data = self.engine.save_data.get('achievements', {})
        if achievements_data:
            self.achievement_manager.from_dict(achievements_data)

        # Conectar callback de logros
        self.achievement_manager.add_callback(self._on_achievement_unlocked)

        # Notificaciones
        self.notifications = []

        # Estado de pausa
        self.paused = False
        self._init_pause_menu()

        # Ciclo día/noche
        self.time_elapsed = self.engine.save_data.get('time_elapsed', 0.0)
        self.is_night = False
        self.night_alpha = 0

        # Entidades
        self.enemies = []
        self.visitors = []
        self.mercenaries = []
        self.projectiles = []
        self.spawn_timer = 0
        self.visitor_spawn_timer = 0

        # Lore inicial si es partida nueva
        if kwargs.get('is_new', False):
            self._show_initial_lore()

    def _init_pause_menu(self):
        from src.ui.widgets import Panel, Button, Slider, Label
        pw, ph = 420, 500
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        self.pause_panel = Panel(px, py, pw, ph, "MENÚ DE PAUSA")

        y = py + 60
        self.pause_widgets = []

        # Sliders de sonido
        self.pause_widgets.append(Label(px + 40, y, "CONFIGURACIÓN DE SONIDO", font_size='small', color=Colors.GOLD))
        y += 40

        def set_master(v):
            self.engine.settings['master_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 340, 20, value=self.engine.settings.get('master_vol', 0.8), label="Maestro", callback=set_master))
        y += 50

        def set_bgm(v):
            self.engine.settings['bgm_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 340, 20, value=self.engine.settings.get('bgm_vol', 0.6), label="Música", callback=set_bgm))
        y += 50

        def set_sfx(v):
            self.engine.settings['sfx_vol'] = v
            self.engine.apply_audio_settings()
        self.pause_widgets.append(Slider(px + 40, y, 340, 20, value=self.engine.settings.get('sfx_vol', 0.7), label="Efectos", callback=set_sfx))
        y += 70

        # Botones de acción
        self.pause_widgets.append(Button(
            px + 110, y, 200, 40, "CONTINUAR",
            callback=self._toggle_pause
        ))
        y += 50

        self.pause_widgets.append(Button(
            px + 110, y, 200, 40, "GUARDAR PARTIDA",
            callback=self._save_game,
            color_normal=(40, 70, 40)
        ))
        y += 50

        self.pause_widgets.append(Button(
            px + 110, y, 200, 40, "LOGROS",
            callback=self.achievement_panel.open,
            color_normal=(40, 40, 80)
        ))
        y += 50

        self.pause_widgets.append(Button(
            px + 110, y, 200, 40, "MENÚ PRINCIPAL",
            callback=lambda: self.engine.change_state(GameState.MAIN_MENU),
            color_normal=Colors.RED
        ))

    def _toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            audio.play_sfx('click')
        else:
            from src.infrastructure.config.config import save_settings
            save_settings(self.engine.settings)

    def _save_game(self):
        """Guarda la partida actual."""
        self.engine.save_data['time_elapsed'] = self.time_elapsed
        self.engine.save_data['player_pos'] = [self.player.px, self.player.py]
        self.engine.save_data['achievements'] = self.achievement_manager.to_dict()
        self.engine.save_game()
        self._add_notification("Partida guardada.", Colors.UI_SUCCESS)
        audio.play_sfx('success')

    def _show_initial_lore(self):
        lore = [
            "Año 10191. La Casa Atreides toma el control de Arrakis.",
            "El Duque Leto busca alianzas con los Fremen.",
            "Pero las sombras de la Casa Harkonnen acechan...",
            "Tu misión: Establecer un enclave y asegurar la Especia.",
            "La supervivencia es el primer paso hacia el poder."
        ]
        for line in lore:
            self._add_notification(line, Colors.GOLD)

        # Recursos iniciales
        self.economy.gold += 15000
        self._add_notification("+15000 Solaris de la Casa Atreides", Colors.GREEN)

        # Edificio inicial automático
        if not self.economy.buildings:
            basic_building_data = next(
                (b for b in self.engine.game_data['buildings'] if b['id'] == 'caseta_basica'), None
            )
            if basic_building_data:
                success, msg, instance = self.economy.buy_building(basic_building_data)
                if success:
                    self.world.place_building(0, 0, instance)
                    self.economy.place_building(instance['instance_id'], 0, 0)
                    self._add_notification("Puesto de avanzada establecido.", Colors.UI_SUCCESS)
                    self.achievement_manager.on_building_placed(len(self.economy.buildings))

                    # Posicionar jugador en tile libre
                    tx, ty = 5, 5
                    while not self.world.is_walkable(tx, ty):
                        tx += 1
                    self.player.px = tx * TILE_SIZE
                    self.player.py = ty * TILE_SIZE

    def _on_economy_event(self, message):
        self._add_notification(message, Colors.UI_TEXT)

    def _on_achievement_unlocked(self, achievement):
        """Callback al desbloquear un logro."""
        self.achievement_panel.add_toast(achievement)
        self._add_notification(f"¡Logro: {achievement.name}!", Colors.GOLD)
        audio.play_sfx('success')

    def _add_notification(self, text, color):
        self.notifications.append(Notification(text, color))

    def handle_events(self, events):
        for event in events:
            # Logros panel tiene prioridad si está abierto
            if self.achievement_panel.visible:
                if self.achievement_panel.handle_event(event):
                    continue

            # Panel de asignación
            if self.creature_assignment.visible:
                if self.creature_assignment.handle_event(event):
                    continue

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.achievement_panel.visible:
                        self.achievement_panel.close()
                    elif self.creature_assignment.visible:
                        self.creature_assignment.close()
                    elif self.build_mode.active:
                        self.build_mode.deactivate()
                    else:
                        self._toggle_pause()

                if not self.paused and not self.achievement_panel.visible and not self.creature_assignment.visible:
                    if event.key == pygame.K_TAB:
                        self.shop.toggle()
                    if event.key == pygame.K_e:
                        self.shop.toggle()
                        if self.shop.visible:
                            self._add_notification("Accediendo al Mercado de Especia...", Colors.GOLD)
                    if event.key == pygame.K_b:
                        if not self.build_mode.active:
                            pending = next((b for b in self.economy.buildings if not b.get('tile_x')), None)
                            if pending:
                                self.build_mode.activate(pending)
                            else:
                                self._add_notification("No tienes edificios para colocar.", Colors.UI_ERROR)
                        else:
                            self.build_mode.deactivate()
                    if event.key == pygame.K_c:
                        # Abrir panel de asignación de criaturas
                        self.creature_assignment.toggle()
                    if event.key == pygame.K_F1:
                        # Abrir panel de logros
                        self.achievement_panel.toggle()
                    if event.key == pygame.K_F5:
                        self._save_game()

            if not self.paused and not self.achievement_panel.visible and not self.creature_assignment.visible:
                if self.hud.handle_event(event):
                    return
                if self.shop.handle_event(event):
                    return

                if self.build_mode.active:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.build_mode.try_place():
                            self._add_notification("Edificio colocado con éxito.", Colors.UI_SUCCESS)
                            self.achievement_manager.on_building_placed(len(self.economy.buildings))

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if not self.shop.visible and not self.build_mode.active:
                        self._handle_shoot(event.pos)
            else:
                if not self.achievement_panel.visible and not self.creature_assignment.visible:
                    for w in self.pause_widgets:
                        w.handle_event(event)

    def _handle_shoot(self, mouse_pos):
        if not self.player.equipped_weapon:
            self._add_notification("No tienes un arma equipada.", Colors.RED)
            return

        weapon = self.player.equipped_weapon
        world_mx = mouse_pos[0] + self.camera.x
        world_my = mouse_pos[1] + self.camera.y

        self.projectiles.append(Projectile(
            self.player.px, self.player.py,
            world_mx, world_my,
            weapon.damage,
            speed=600 if weapon.id == 'lasgun' else 400,
            sprite_key='ui_projectile'
        ))

        audio.play_sfx('click')
        self.player.anim_timer = 0

    def update(self, dt):
        if self.paused:
            for w in self.pause_widgets:
                w.update(dt)
            return

        # Actualizar paneles secundarios
        self.achievement_panel.update(dt)
        self.creature_assignment.update(dt)

        # Activar modo construcción si hay edificio pendiente
        if self.shop.pending_building_placement:
            self.build_mode.activate(self.shop.pending_building_placement)
            self.shop.pending_building_placement = None
            self._add_notification("Modo Construcción: Elige dónde situar el edificio", Colors.GOLD)

        # Spawn de mercenario contratado
        if self.economy.pending_mercenary_spawn:
            tipo = self.economy.pending_mercenary_spawn
            self.economy.pending_mercenary_spawn = None
            is_elite = (tipo == 'MERCENARIO')
            mx = self.player.px + random.randint(-50, 50)
            my = self.player.py + random.randint(-50, 50)
            self.mercenaries.append(Mercenary(mx, my, is_elite))
            self._add_notification(f"{tipo} contratado y listo para el combate.", Colors.UI_SUCCESS)
            self.achievement_manager.on_mercenary_hired()

        # Ciclo día/noche
        self.time_elapsed += dt
        cycle_time = self.time_elapsed % (DAY_DURATION_SEC + NIGHT_DURATION_SEC)

        was_night = self.is_night
        self.is_night = cycle_time > DAY_DURATION_SEC

        # Notificar al gestor de logros sobre el ciclo
        self.achievement_manager.on_night_changed(self.is_night)

        if self.is_night:
            self.night_alpha = min(150, self.night_alpha + dt * 50)
            if not was_night:
                self._add_notification("Cae la noche... Los peligros acechan.", Colors.RED)
                self.visitors = []

            self.spawn_timer += dt
            if self.spawn_timer >= ENEMY_SPAWN_RATE:
                self.spawn_timer = 0
                self._spawn_enemy()
        else:
            self.night_alpha = max(0, self.night_alpha - dt * 50)
            if was_night:
                self._add_notification("Amanece en Arrakis.", Colors.GOLD)
                self.enemies = []
                result = self.economy.advance_turn('day')
                self.achievement_manager.on_day_advanced(result.get('new_day', self.economy.day))
                self.achievement_manager.on_gold_changed(result.get('new_gold', self.economy.gold))

            self.visitor_spawn_timer += dt
            if self.visitor_spawn_timer >= 10.0:
                self.visitor_spawn_timer = 0
                self._spawn_visitors()

        # Movimiento del jugador
        if not self.shop.visible and not self.build_mode.active and not self.creature_assignment.visible:
            keys = pygame.key.get_pressed()
            dx, dy = self.player.handle_input(keys, self.engine.settings)

            if dx != 0 or dy != 0:
                if dx != 0 and dy != 0:
                    dist = math.sqrt(dx * dx + dy * dy)
                    dx /= dist
                    dy /= dist

                new_px = self.player.px + dx * self.player.speed * dt
                new_py = self.player.py + dy * self.player.speed * dt

                tx = int(new_px // TILE_SIZE)
                ty = int(new_py // TILE_SIZE)

                if self.world.is_walkable(tx, ty) and (tx, ty) not in self.world.buildings_on_map:
                    self.player.px = new_px
                    self.player.py = new_py

            self.player.update(dt)
        else:
            self.player.is_moving = False
            self.player.update(dt)

        self.camera.follow(self.player, dt)

        # Actualizar entidades
        enemies_before = len(self.enemies)
        for e in self.enemies:
            e.update(dt, self.player, self.world)
        for v in self.visitors:
            v.update(dt, self.player, self.world)
        for m in self.mercenaries:
            m.update(dt, self.player, self.world, self.enemies)
        for p in self.projectiles:
            p.update(dt, self.enemies)

        # Contar enemigos eliminados
        enemies_killed = enemies_before - sum(1 for e in self.enemies if e.alive)
        for _ in range(max(0, enemies_killed)):
            self.achievement_manager.on_enemy_killed()

        # Limpiar entidades muertas
        self.projectiles = [p for p in self.projectiles if p.alive]
        self.enemies = [e for e in self.enemies if e.alive]
        self.mercenaries = [m for m in self.mercenaries if m.alive]

        # Actualizar notificaciones y UI
        for n in self.notifications:
            n.update(dt)
        self.notifications = [n for n in self.notifications if not n.done]
        self.shop.update(dt)

        # Actualizar minimap
        ptx = int(self.player.px // TILE_SIZE)
        pty = int(self.player.py // TILE_SIZE)
        self.minimap.update(dt, ptx, pty)

        # Modo construcción
        if self.build_mode.active:
            self.build_mode.update_ghost(pygame.mouse.get_pos(), self.camera.x, self.camera.y)

        # Verificar logros de inventario/armas
        for item in self.economy.inventory:
            if item.get('equipado') and item.get('tipo') == 'ARMA':
                self.achievement_manager.on_weapon_equipped()

        # Verificar logros de criaturas
        self.achievement_manager.on_creature_recruited(len(self.economy.creatures))

    def _spawn_enemy(self):
        angle = random.uniform(0, math.pi * 2)
        dist = random.uniform(200, 400)
        ex = self.player.px + math.cos(angle) * dist
        ey = self.player.py + math.sin(angle) * dist

        tx, ty = int(ex // TILE_SIZE), int(ey // TILE_SIZE)
        if self.world.is_walkable(tx, ty):
            day_mult = 1.0 + (self.economy.day / 10.0)
            self.enemies.append(Enemy(ex, ey, day_mult))

    def _spawn_visitors(self):
        num_buildings = len(self.economy.buildings)
        num_creatures = len(self.economy.creatures)
        target_visitors = min(15, (num_buildings * 2) + (num_creatures // 2))

        if len(self.visitors) < target_visitors:
            if self.economy.buildings:
                b = random.choice(self.economy.buildings)
                if b.get('tile_x') is not None:
                    vx = b['tile_x'] * TILE_SIZE + random.randint(-50, 50)
                    vy = b['tile_y'] * TILE_SIZE + random.randint(-50, 50)
                    self.visitors.append(Visitor(vx, vy))

    def draw(self, screen):
        # Mundo
        self.world.draw(screen, int(self.camera.x), int(self.camera.y), SCREEN_WIDTH, SCREEN_HEIGHT)

        # Entidades
        for v in self.visitors:
            v.draw(screen, self.camera.x, self.camera.y)
        for m in self.mercenaries:
            m.draw(screen, self.camera.x, self.camera.y)
        for e in self.enemies:
            e.draw(screen, self.camera.x, self.camera.y)
        for p in self.projectiles:
            p.draw(screen, self.camera.x, self.camera.y)
        self.player.draw(screen, self.camera.x, self.camera.y)

        # Overlay nocturno
        if self.night_alpha > 0:
            night_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            night_surf.fill((10, 10, 30, int(self.night_alpha)))
            screen.blit(night_surf, (0, 0))

        # HUD y UI
        self.hud.draw(screen)
        self.turn_panel.draw(screen)
        self.shop.draw(screen)

        # Minimap (esquina inferior izquierda)
        self.minimap.draw(screen, self.player, self.enemies, self.mercenaries)

        # Modo construcción
        if self.build_mode.active:
            self.build_mode.draw(screen, self.camera.x, self.camera.y)

        # Barra de vida del jugador (sobre el HUD)
        self._draw_player_health(screen)

        # Indicador de ciclo día/noche
        self._draw_time_hud(screen)

        # Barra de controles en la parte inferior
        self._draw_controls_help(screen)

        # Notificaciones flotantes
        for i, n in enumerate(self.notifications):
            n.draw(screen, 20, 105 + i * 28)

        # Panel de asignación de criaturas
        self.creature_assignment.draw(screen)

        # Panel de logros (incluye toasts)
        self.achievement_panel.draw(screen)

        # Menú de pausa
        if self.paused:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            self.pause_panel.draw(screen)
            for w in self.pause_widgets:
                w.draw(screen)

    def _draw_player_health(self, screen):
        """Dibuja la barra de vida del jugador bajo el HUD."""
        bar_w = 200
        bar_h = 14
        x = 20
        y = 108

        hp_ratio = max(0.0, self.player.hp / self.player.max_hp)
        hp_color = (
            Colors.UI_SUCCESS if hp_ratio > 0.6
            else Colors.ORANGE if hp_ratio > 0.3
            else Colors.UI_ERROR
        )

        # Fondo
        pygame.draw.rect(screen, Colors.UI_BTN_NORMAL, (x, y, bar_w, bar_h))
        # Relleno
        fill_w = int(bar_w * hp_ratio)
        pygame.draw.rect(screen, hp_color, (x, y, fill_w, bar_h))
        # Borde
        pygame.draw.rect(screen, Colors.UI_PANEL_BORDER, (x, y, bar_w, bar_h), 2)

        # Texto
        font = assets.get_font('tiny')
        hp_text = f"HP: {int(self.player.hp)}/{self.player.max_hp}"
        hp_surf = font.render(hp_text, True, Colors.WHITE)
        screen.blit(hp_surf, (x + bar_w // 2 - hp_surf.get_width() // 2, y + 1))

    def _draw_controls_help(self, screen):
        font = assets.get_font('tiny')
        help_text = "WASD: Mover | TAB/E: Tienda | B: Construir | C: Criaturas | F1: Logros | F5: Guardar | Click: Atacar | ESC: Pausa"
        text_surf = font.render(help_text, True, Colors.WHITE)

        bg_rect = pygame.Rect(0, SCREEN_HEIGHT - 28, SCREEN_WIDTH, 28)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((0, 0, 0, 160))
        screen.blit(bg_surf, bg_rect)

        text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 14))
        screen.blit(text_surf, text_rect)

    def _draw_time_hud(self, screen):
        font = assets.get_font('small')
        cycle_name = "NOCHE" if self.is_night else "DÍA"
        color = Colors.RED if self.is_night else Colors.GOLD

        # Indicador de ciclo
        cycle_surf = font.render(f"◆ {cycle_name} ◆", True, color)
        screen.blit(cycle_surf, (SCREEN_WIDTH // 2 - cycle_surf.get_width() // 2, 10))

        # Barra de progreso del ciclo
        total_cycle = DAY_DURATION_SEC + NIGHT_DURATION_SEC
        cycle_time = self.time_elapsed % total_cycle
        progress = cycle_time / total_cycle

        bar_w = 200
        bar_h = 6
        bx = SCREEN_WIDTH // 2 - bar_w // 2
        by = 32

        pygame.draw.rect(screen, Colors.UI_BTN_NORMAL, (bx, by, bar_w, bar_h))
        fill_color = Colors.RED if self.is_night else Colors.GOLD
        pygame.draw.rect(screen, fill_color, (bx, by, int(bar_w * progress), bar_h))
        pygame.draw.rect(screen, Colors.UI_PANEL_BORDER, (bx, by, bar_w, bar_h), 1)
