"""
UI Manager - Gestión de todas las interfaces del Gameplay
Tienda, Inventario, Panel de Turno, HUD, Notificaciones
"""
import pygame
import math
from src.config import Colors, SCREEN_WIDTH, SCREEN_HEIGHT, INVENTORY_SIZE
from src.ui.widgets import Button, Panel, Label, ScrollableList, ProgressBar
from src.utils.asset_manager import assets
from src.systems.economy_manager import EconomyManager


class Notification:
    """Notificación flotante temporal"""
    
    def __init__(self, text: str, color=None, duration: float = 3.0):
        self.text = text
        self.color = color or Colors.UI_TEXT
        self.duration = duration
        self.timer = 0.0
        self.y_offset = 0.0
    
    @property
    def alpha(self) -> int:
        ratio = self.timer / self.duration
        if ratio < 0.1:
            return int(255 * ratio / 0.1)
        elif ratio > 0.8:
            return int(255 * (1.0 - ratio) / 0.2)
        return 255
    
    @property
    def done(self) -> bool:
        return self.timer >= self.duration
    
    def update(self, dt: float):
        self.timer += dt
        self.y_offset -= 20 * dt  # Flotar hacia arriba
        
    def draw(self, surface: pygame.Surface, x: int, y: int):
        font = assets.get_font('small')
        alpha = self.alpha
        text_surf = font.render(self.text, True, self.color)
        
        if alpha < 255:
            temp_surf = pygame.Surface(text_surf.get_size(), pygame.SRCALPHA)
            temp_surf.blit(text_surf, (0, 0))
            temp_surf.set_alpha(alpha)
            surface.blit(temp_surf, (x, y + self.y_offset))
        else:
            surface.blit(text_surf, (x, y + self.y_offset))


class HUD:
    """Heads-Up Display: saldo, día, criaturas, inventario rápido"""
    
    def __init__(self, economy: EconomyManager, player=None):
        self.economy = economy
        self.player = player
        self.inv_rects = []
    
    def draw(self, surface: pygame.Surface):
        # Panel superior izquierdo
        panel_w, panel_h = 300, 90
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel_surf.fill((*Colors.UI_PANEL, 210))
        pygame.draw.rect(panel_surf, Colors.UI_PANEL_BORDER, (0, 0, panel_w, panel_h), 2)
        # Esquinas decorativas
        for cx, cy in [(0, 0), (panel_w - 4, 0), (0, panel_h - 4), (panel_w - 4, panel_h - 4)]:
            pygame.draw.rect(panel_surf, Colors.UI_HIGHLIGHT, (cx, cy, 4, 4))
        surface.blit(panel_surf, (10, 10))
        
        summary = self.economy.get_summary()
        font = assets.get_font('medium')
        font_small = assets.get_font('small')
        font_tiny = assets.get_font('tiny')
        
        # Saldo con icono de moneda
        gold_text = f"◆ {summary['gold']:,} Solaris"
        gold_surf = font.render(gold_text, True, Colors.GOLD)
        surface.blit(gold_surf, (20, 18))
        
        # Día y criaturas en la misma línea
        day_text = f"Día {summary['day']}"
        day_surf = font_small.render(day_text, True, Colors.UI_TEXT)
        surface.blit(day_surf, (20, 48))
        
        crit_text = f"| Criaturas: {summary['num_creatures']}"
        crit_surf = font_small.render(crit_text, True, Colors.UI_TEXT_DIM)
        surface.blit(crit_surf, (20 + day_surf.get_width() + 5, 48))
        
        # Gasto diario estimado
        upkeep = summary['daily_upkeep']
        upkeep_color = Colors.UI_ERROR if upkeep > summary['gold'] * 0.1 else Colors.UI_TEXT_DIM
        upkeep_text = f"Gasto/día: -{upkeep:,} Sol."
        upkeep_surf = font_tiny.render(upkeep_text, True, upkeep_color)
        surface.blit(upkeep_surf, (20, 72))
        
        # Panel inventario (esquina superior derecha)
        self._draw_inventory_hud(surface, summary)
    
    def _draw_inventory_hud(self, surface, summary):
        """Dibuja slots de inventario en HUD"""
        slot_size = 44
        margin = 4
        total_w = INVENTORY_SIZE * (slot_size + margin) + margin
        start_x = SCREEN_WIDTH - total_w - 10
        start_y = 10
        
        # Fondo
        bg_h = slot_size + margin * 2 + 16
        bg = pygame.Surface((total_w, bg_h), pygame.SRCALPHA)
        bg.fill((*Colors.UI_PANEL, 210))
        pygame.draw.rect(bg, Colors.UI_PANEL_BORDER, (0, 0, bg.get_width(), bg.get_height()), 2)
        # Esquinas decorativas
        for cx, cy in [(0, 0), (total_w - 4, 0), (0, bg_h - 4), (total_w - 4, bg_h - 4)]:
            pygame.draw.rect(bg, Colors.UI_HIGHLIGHT, (cx, cy, 4, 4))
        surface.blit(bg, (start_x, start_y))
        
        inventory = self.economy.inventory
        font_tiny = assets.get_font('tiny')
        self.inv_rects = []
        
        for i in range(INVENTORY_SIZE):
            sx = start_x + margin + i * (slot_size + margin)
            sy = start_y + margin
            
            slot_rect = pygame.Rect(sx, sy, slot_size, slot_size)
            self.inv_rects.append(slot_rect)
            
            if i < len(inventory):
                item = inventory[i]
                color = Colors.GOLD_DARK if item.get('equipado') else Colors.UI_BTN_HOVER
                pygame.draw.rect(surface, color, slot_rect)
                
                sprite_key = item.get('sprite')
                if sprite_key:
                    sprite = assets.get_sprite(sprite_key)
                    if sprite:
                        s_w, s_h = sprite.get_size()
                        ratio = min(32 / s_w, 32 / s_h)
                        scaled = pygame.transform.scale(sprite, (int(s_w * ratio), int(s_h * ratio)))
                        surface.blit(scaled, scaled.get_rect(center=slot_rect.center))
                elif item.get('tipo') == 'ARMA':
                    pygame.draw.rect(surface, Colors.GRAY_LIGHT, (sx + 10, sy + 10, 24, 24))
                else:
                    pygame.draw.circle(surface, Colors.BLUE_SPICE, slot_rect.center, slot_size // 3)
                
                # Nombre corto
                name = item['nombre'][:5]
                name_surf = font_tiny.render(name, True, Colors.WHITE)
                surface.blit(name_surf, (sx + 2, sy + slot_size - 14))
                
                # Indicador de equipado
                if item.get('equipado'):
                    eq_surf = font_tiny.render("EQ", True, Colors.GOLD)
                    surface.blit(eq_surf, (sx + slot_size - eq_surf.get_width() - 2, sy + 2))
            else:
                pygame.draw.rect(surface, Colors.UI_BTN_NORMAL, slot_rect)
            
            pygame.draw.rect(surface, Colors.UI_PANEL_BORDER, slot_rect, 2)
        
        # Label de inventario debajo de los slots
        inv_label = font_tiny.render(
            f"INV {len(inventory)}/{INVENTORY_SIZE}",
            True, Colors.UI_TEXT_DIM
        )
        surface.blit(inv_label, (
            start_x + total_w // 2 - inv_label.get_width() // 2,
            start_y + slot_size + margin + 2
        ))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, rect in enumerate(self.inv_rects):
                if rect.collidepoint(event.pos):
                    if i < len(self.economy.inventory):
                        item = self.economy.inventory[i]
                        if item.get('tipo') == 'ARMA':
                            success, msg, weapon = self.economy.equip_weapon(item['instance_id'])
                            if success and self.player:
                                self.player.equipped_weapon = weapon
                            return True
                        else:
                            self.economy.use_item(item['instance_id'])
                            return True
        return False


class ShopUI:
    """
    Interfaz de Tienda - Carga dinámicamente datos de las APIs
    Muestra: Sprite, Nombre, Descripción, Precio (Compra), Mantenimiento
    """
    
    def __init__(self, economy: EconomyManager, game_data: dict):
        self.economy = economy
        self.game_data = game_data
        self.visible = False
        self.tab = 'creatures'
        self.selected_item = None
        self.message = ''
        self.message_timer = 0.0
        self.message_color = Colors.UI_TEXT
        self.pending_building_placement = None
        
        self._build_ui()
    
    def _build_ui(self):
        pw, ph = 820, 580
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        
        self.panel = Panel(px, py, pw, ph, "TIENDA DE ARRAKIS")
        
        # Tabs con mejor espaciado
        tab_w = 170
        tab_y = py + 38
        self.btn_tab_creatures = Button(
            px + 10, tab_y, tab_w, 32, "CRIATURAS",
            callback=lambda: self._set_tab('creatures'), font_size='small'
        )
        self.btn_tab_buildings = Button(
            px + 10 + tab_w + 5, tab_y, tab_w, 32, "EDIFICIOS",
            callback=lambda: self._set_tab('buildings'), font_size='small'
        )
        self.btn_tab_items = Button(
            px + 10 + (tab_w + 5) * 2, tab_y, tab_w, 32, "ITEMS",
            callback=lambda: self._set_tab('items'), font_size='small'
        )
        
        # Lista de items
        self.item_list = ScrollableList(
            px + 10, py + 80, 290, ph - 140,
            item_height=52,
            on_select=self._on_item_select
        )
        
        # Panel de detalle
        self.detail_panel = Panel(px + 310, py + 80, pw - 320, ph - 140)
        
        # Botón comprar
        self.btn_buy = Button(
            px + pw // 2 - 90, py + ph - 55, 180, 42,
            "COMPRAR",
            callback=self._on_buy,
            font_size='medium',
            color_normal=Colors.BROWN_DARK,
            color_hover=(80, 50, 30)
        )
        
        # Botón cerrar
        self.btn_close = Button(
            px + pw - 50, py + 5, 40, 30, "X",
            callback=self.close, font_size='small',
            color_normal=Colors.RED
        )
        
        self._refresh_list()
    
    def _set_tab(self, tab: str):
        self.tab = tab
        self.selected_item = None
        self._refresh_list()
    
    def _refresh_list(self):
        """Actualiza la lista según el tab activo"""
        if self.tab == 'creatures':
            items = self.game_data.get('creatures', [])
        elif self.tab == 'buildings':
            items = [b for b in self.game_data.get('buildings', []) if not b.get('esInicial', False)]
        else:
            items = self.game_data.get('items', [])
        
        self.item_list.set_items(items)
        self._current_items = items
    
    def _on_item_select(self, idx: int, item: dict):
        self.selected_item = item
    
    def _on_buy(self):
        if not self.selected_item:
            self._show_message("Selecciona un item primero.", Colors.UI_ERROR)
            return
        
        item = self.selected_item
        success = False
        msg = ""
        instance = None
        
        if self.tab == 'creatures':
            success, msg = self.economy.buy_creature(item)
        elif self.tab == 'buildings':
            success, msg, instance = self.economy.buy_building(item)
        else:
            success, msg = self.economy.buy_item(item)
        
        color = Colors.UI_SUCCESS if success else Colors.UI_ERROR
        self._show_message(msg, color)
        
        if success and self.tab == 'buildings' and instance:
            self.close()
            self.pending_building_placement = instance
        
        try:
            from src.systems.audio_manager import audio
            audio.play_sfx('buy' if success else 'error')
        except Exception:
            pass
    
    def _show_message(self, msg: str, color=None):
        self.message = msg
        self.message_color = color or Colors.UI_TEXT
        self.message_timer = 3.0
    
    def open(self):
        self.visible = True
        self._refresh_list()
    
    def close(self):
        self.visible = False
    
    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.open()
    
    def handle_event(self, event):
        if not self.visible:
            return False
        
        self.btn_tab_creatures.handle_event(event)
        self.btn_tab_buildings.handle_event(event)
        self.btn_tab_items.handle_event(event)
        self.item_list.handle_event(event)
        self.btn_buy.handle_event(event)
        self.btn_close.handle_event(event)
        
        # Cerrar con Escape
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        
        return True
    
    def update(self, dt: float):
        if self.message_timer > 0:
            self.message_timer -= dt
    
    def draw(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        # Overlay semitransparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        self.panel.draw(surface)
        
        # Resaltar tab activo
        active_color = Colors.GOLD_DARK
        if self.tab == 'creatures':
            self.btn_tab_creatures.color_normal = active_color
        else:
            self.btn_tab_creatures.color_normal = Colors.UI_BTN_NORMAL
        if self.tab == 'buildings':
            self.btn_tab_buildings.color_normal = active_color
        else:
            self.btn_tab_buildings.color_normal = Colors.UI_BTN_NORMAL
        if self.tab == 'items':
            self.btn_tab_items.color_normal = active_color
        else:
            self.btn_tab_items.color_normal = Colors.UI_BTN_NORMAL
        
        self.btn_tab_creatures.draw(surface)
        self.btn_tab_buildings.draw(surface)
        self.btn_tab_items.draw(surface)
        
        # Lista
        self.item_list.draw(surface)
        
        # Detalle del item seleccionado
        self._draw_detail(surface)
        
        # Botones
        self.btn_buy.draw(surface)
        self.btn_close.draw(surface)
        
        # Mensaje de feedback
        if self.message and self.message_timer > 0:
            font = assets.get_font('small')
            msg_surf = font.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(
                centerx=self.panel.rect.centerx,
                bottom=self.panel.rect.bottom - 10
            )
            # Fondo del mensaje
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 8), pygame.SRCALPHA)
            msg_bg.fill((*Colors.UI_PANEL, 200))
            surface.blit(msg_bg, (msg_rect.left - 10, msg_rect.top - 4))
            surface.blit(msg_surf, msg_rect)
    
    def _draw_detail(self, surface: pygame.Surface):
        """Dibuja detalle del item seleccionado"""
        self.detail_panel.draw(surface)
        
        if not self.selected_item:
            font = assets.get_font('small')
            hint = font.render("Selecciona un item de la lista", True, Colors.UI_TEXT_DIM)
            hint_rect = hint.get_rect(center=self.detail_panel.rect.center)
            surface.blit(hint, hint_rect)
            return
        
        item = self.selected_item
        dp = self.detail_panel.rect
        x, y = dp.left + 12, dp.top + 12
        
        # Sprite
        if self.tab == 'creatures':
            sprite_key = f"creature_{item.get('id', '')}"
        elif self.tab == 'buildings':
            sprite_key = f"building_{item.get('sprite', '').replace('.png', '')}"
        else:
            sprite_key = None
        
        if sprite_key:
            sprite = assets.get_sprite(sprite_key)
            if sprite:
                sprite_scaled = pygame.transform.scale(sprite, (80, 80))
                surface.blit(sprite_scaled, (dp.right - 92, dp.top + 12))
        
        # Nombre
        font_large = assets.get_font('large')
        name_surf = font_large.render(item.get('nombre', ''), True, Colors.GOLD)
        surface.blit(name_surf, (x, y))
        y += name_surf.get_height() + 4
        
        # Categoría/tipo
        font_small = assets.get_font('small')
        cat = item.get('categoria', item.get('tipo', ''))
        cat_surf = font_small.render(cat.upper(), True, Colors.UI_TEXT_DIM)
        surface.blit(cat_surf, (x, y))
        y += cat_surf.get_height() + 8
        
        # Separador
        pygame.draw.line(surface, Colors.UI_PANEL_BORDER, (x, y), (dp.right - 10, y), 1)
        y += 10
        
        # Descripción (con wrap)
        desc = item.get('descripcion', '')
        font_tiny = assets.get_font('tiny')
        words = desc.split()
        lines = []
        current_line = []
        max_w = dp.width - 24
        
        for word in words:
            test = ' '.join(current_line + [word])
            if font_tiny.size(test)[0] > max_w and current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                current_line.append(word)
        if current_line:
            lines.append(' '.join(current_line))
        
        for line in lines[:5]:
            line_surf = font_tiny.render(line, True, Colors.UI_TEXT)
            surface.blit(line_surf, (x, y))
            y += line_surf.get_height() + 2
        
        y += 12
        
        # Precio y estadísticas
        if self.tab == 'creatures':
            price = item.get('costeCompra', 0)
            feed_d = item.get('costeAlimentacionDiario', 0)
            feed_w = item.get('costeAlimentacionSemanal', 0)
            can_afford = self.economy.can_afford(price)
            
            price_color = Colors.GOLD if can_afford else Colors.UI_ERROR
            price_surf = font_small.render(f"Precio: {price:,} Solaris", True, price_color)
            surface.blit(price_surf, (x, y)); y += 22
            
            feed_surf = font_small.render(f"Alimentación/día: {feed_d} Sol.", True, Colors.ORANGE)
            surface.blit(feed_surf, (x, y)); y += 22
            
            feed_w_surf = font_small.render(f"Alimentación/semana: {feed_w} Sol.", True, Colors.ORANGE)
            surface.blit(feed_w_surf, (x, y)); y += 22
            
            tags = item.get('tags', [])
            if tags:
                tags_surf = font_tiny.render(f"Bioma: {', '.join(tags)}", True, Colors.BLUE_SPICE)
                surface.blit(tags_surf, (x, y)); y += 18
            
            cap = item.get('capacidadRequerida', '')
            if cap:
                cap_surf = font_tiny.render(f"Recinto requerido: {cap}", True, Colors.BLUE_SPICE)
                surface.blit(cap_surf, (x, y))
        
        elif self.tab == 'buildings':
            price = item.get('coste', 0)
            stats = item.get('stats', {})
            maint = stats.get('mantenimiento', 0)
            cap = item.get('capacidadMaxima', 0)
            can_afford = self.economy.can_afford(price)
            
            price_color = Colors.GOLD if can_afford else Colors.UI_ERROR
            price_surf = font_small.render(f"Precio: {price:,} Solaris", True, price_color)
            surface.blit(price_surf, (x, y)); y += 22
            
            maint_surf = font_small.render(f"Mantenimiento/día: {maint} Sol.", True, Colors.ORANGE)
            surface.blit(maint_surf, (x, y)); y += 22
            
            cap_surf = font_small.render(f"Capacidad: {cap} criaturas", True, Colors.UI_TEXT)
            surface.blit(cap_surf, (x, y)); y += 22
            
            tags = item.get('tagEspeciesPermitidas', [])
            if tags:
                tags_surf = font_tiny.render(f"Acepta: {', '.join(tags)}", True, Colors.BLUE_SPICE)
                surface.blit(tags_surf, (x, y))
        
        else:  # items
            price = item.get('coste', 0)
            tipo = item.get('tipo', '')
            can_afford = self.economy.can_afford(price)
            
            price_color = Colors.GOLD if can_afford else Colors.UI_ERROR
            price_surf = font_small.render(f"Precio: {price:,} Solaris", True, price_color)
            surface.blit(price_surf, (x, y)); y += 22
            
            tipo_color = Colors.BLUE_SPICE if tipo == 'POCION' else Colors.UI_TEXT
            tipo_surf = font_small.render(f"Tipo: {tipo}", True, tipo_color)
            surface.blit(tipo_surf, (x, y)); y += 22
            
            if tipo in ['POCION', 'ARMA']:
                inv_count = len(self.economy.inventory)
                inv_color = Colors.UI_ERROR if inv_count >= INVENTORY_SIZE else Colors.UI_TEXT
                inv_surf = font_tiny.render(
                    f"Inventario: {inv_count}/{INVENTORY_SIZE} slots",
                    True, inv_color
                )
                surface.blit(inv_surf, (x, y)); y += 18
            
            if tipo == 'ARMA':
                daño = item.get('daño', 0)
                rango = item.get('rango', 0)
                cadencia = item.get('cadencia', 0)
                
                daño_surf = font_tiny.render(f"Daño: {daño}", True, Colors.RED)
                surface.blit(daño_surf, (x, y)); y += 16
                
                rango_surf = font_tiny.render(f"Rango: {rango}px", True, Colors.BLUE_SPICE)
                surface.blit(rango_surf, (x, y)); y += 16
                
                cad_surf = font_tiny.render(f"Cadencia: {cadencia}s", True, Colors.UI_TEXT)
                surface.blit(cad_surf, (x, y)); y += 16
            
            efectos = item.get('efectos', [])
            for efecto in efectos[:3]:
                ef_surf = font_tiny.render(f"+ {efecto}", True, Colors.UI_SUCCESS)
                surface.blit(ef_surf, (x, y)); y += 16


class TurnPanel:
    """Panel de avance de turno con resumen de gastos"""
    
    def __init__(self, economy: EconomyManager):
        self.economy = economy
        self.visible = False
        self.last_result = None
        self.show_result = False
        self.result_timer = 0.0
        
        btn_w = 150
        btn_x = SCREEN_WIDTH - btn_w - 10
        self.btn_day = Button(
            btn_x, SCREEN_HEIGHT - 100, btn_w, 40,
            "AVANZAR DÍA",
            callback=self._advance_day,
            font_size='small',
            color_normal=(60, 80, 40)
        )
        self.btn_week = Button(
            btn_x, SCREEN_HEIGHT - 55, btn_w, 40,
            "AVANZAR SEMANA",
            callback=self._advance_week,
            font_size='small',
            color_normal=(80, 60, 20)
        )
    
    def _advance_day(self):
        self.last_result = self.economy.advance_turn('day')
        self.show_result = True
        self.result_timer = 4.0
        try:
            from src.systems.audio_manager import audio
            audio.play_sfx('turn')
        except Exception:
            pass
    
    def _advance_week(self):
        self.last_result = self.economy.advance_turn('week')
        self.show_result = True
        self.result_timer = 4.0
        try:
            from src.systems.audio_manager import audio
            audio.play_sfx('turn')
        except Exception:
            pass
    
    def handle_event(self, event):
        self.btn_day.handle_event(event)
        self.btn_week.handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._advance_day()
    
    def update(self, dt: float):
        if self.result_timer > 0:
            self.result_timer -= dt
            if self.result_timer <= 0:
                self.show_result = False
    
    def draw(self, surface: pygame.Surface):
        self.btn_day.draw(surface)
        self.btn_week.draw(surface)
        
        if self.show_result and self.last_result:
            self._draw_result(surface)
    
    def _draw_result(self, surface: pygame.Surface):
        """Muestra resumen del turno"""
        r = self.last_result
        pw, ph = 340, 210
        px = SCREEN_WIDTH - pw - 170
        py = SCREEN_HEIGHT - ph - 20
        
        panel_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
        panel_surf.fill((*Colors.UI_PANEL, 230))
        pygame.draw.rect(panel_surf, Colors.GOLD_DARK, (0, 0, pw, ph), 2)
        # Esquinas decorativas
        for cx, cy in [(0, 0), (pw - 4, 0), (0, ph - 4), (pw - 4, ph - 4)]:
            pygame.draw.rect(panel_surf, Colors.UI_HIGHLIGHT, (cx, cy, 4, 4))
        surface.blit(panel_surf, (px, py))
        
        font = assets.get_font('small')
        font_tiny = assets.get_font('tiny')
        
        turn_type = "DÍA" if r.get('turn_type') == 'day' else "SEMANA"
        title = font.render(f"RESOLUCIÓN DE {turn_type}", True, Colors.GOLD)
        surface.blit(title, (px + 10, py + 10))
        
        y = py + 36
        
        feed_surf = font_tiny.render(f"Alimentación: -{r.get('feed_cost', 0):,} Sol.", True, Colors.ORANGE)
        surface.blit(feed_surf, (px + 10, y)); y += 18
        
        maint_surf = font_tiny.render(f"Mantenimiento: -{r.get('maint_cost', 0):,} Sol.", True, Colors.ORANGE)
        surface.blit(maint_surf, (px + 10, y)); y += 18
        
        pygame.draw.line(surface, Colors.UI_PANEL_BORDER,
                         (px + 10, y), (px + pw - 10, y), 1)
        y += 8
        
        total_surf = font.render(f"Total: -{r.get('total_cost', 0):,} Sol.", True, Colors.RED)
        surface.blit(total_surf, (px + 10, y)); y += 28
        
        new_gold_surf = font.render(f"Saldo: {r.get('new_gold', 0):,} Sol.", True, Colors.GOLD)
        surface.blit(new_gold_surf, (px + 10, y)); y += 28
        
        day_surf = font_tiny.render(f"Día actual: {r.get('new_day', 1)}", True, Colors.UI_TEXT_DIM)
        surface.blit(day_surf, (px + 10, y))
        
        if r.get('bankrupt'):
            bankrupt_surf = font.render("¡BANCARROTA!", True, Colors.UI_ERROR)
            bankrupt_rect = bankrupt_surf.get_rect(centerx=px + pw // 2, bottom=py + ph - 10)
            surface.blit(bankrupt_surf, bankrupt_rect)


class BuildModeUI:
    """UI para modo de construcción (grid placement)"""
    
    def __init__(self, world_map, economy: EconomyManager):
        self.world = world_map
        self.economy = economy
        self.active = False
        self.building_to_place = None
        self.ghost_pos = (0, 0)
        self.can_place = False
        self.building_size = 3
    
    def activate(self, building_instance: dict):
        self.active = True
        self.building_to_place = building_instance
        capacidad = self.building_to_place.get('stats', {}).get('capacidad', 5)
        self.building_size = 3 + (capacidad - 5) // 20
        self.building_size = max(2, min(self.building_size, 6))
    
    def deactivate(self):
        self.active = False
        self.building_to_place = None
    
    def update_ghost(self, mouse_pos: tuple, camera_x: int, camera_y: int):
        """Actualiza posición fantasma según cursor"""
        from src.config import TILE_SIZE
        mx, my = mouse_pos
        tile_x = int((mx + camera_x) // TILE_SIZE)
        tile_y = int((my + camera_y) // TILE_SIZE)
        self.ghost_pos = (tile_x, tile_y)
        
        self.can_place = True
        for dy in range(self.building_size):
            for dx in range(self.building_size):
                nx, ny = tile_x + dx, tile_y + dy
                if not self.world.is_walkable(nx, ny) or (nx, ny) in self.world.buildings_on_map:
                    self.can_place = False
                    break
    
    def try_place(self) -> bool:
        """Intenta colocar el edificio en la posición actual"""
        if not self.active or not self.building_to_place or not self.can_place:
            return False
        
        tx, ty = self.ghost_pos
        success = self.world.place_building(tx, ty, self.building_to_place, self.building_size)
        if success:
            self.economy.place_building(self.building_to_place['instance_id'], tx, ty)
            self.deactivate()
            try:
                from src.systems.audio_manager import audio
                audio.play_sfx('place')
            except Exception:
                pass
        return success
    
    def draw(self, surface: pygame.Surface, camera_x: int, camera_y: int):
        """Dibuja fantasma del edificio"""
        if not self.active or not self.building_to_place:
            return
        
        from src.config import TILE_SIZE
        tx, ty = self.ghost_pos
        sx = tx * TILE_SIZE - camera_x
        sy = ty * TILE_SIZE - camera_y
        
        target_size = int(self.building_size * TILE_SIZE)
        color_tint = (100, 255, 100, 150) if self.can_place else (255, 100, 100, 150)
        
        sprite_name = self.building_to_place.get('sprite', 'caseta_basica.png')
        if sprite_name.endswith('.png'):
            sprite_name = sprite_name[:-4]
        sprite_key = f"building_{sprite_name}"
        sprite = assets.get_sprite(sprite_key)
        
        if sprite and sprite_key in assets._sprites:
            scaled = pygame.transform.scale(sprite, (target_size, target_size))
            tinted = scaled.copy()
            tinted.fill(color_tint, special_flags=pygame.BLEND_RGBA_MULT)
            surface.blit(tinted, (sx, sy))
        else:
            ghost_surf = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
            ghost_surf.fill(color_tint)
            surface.blit(ghost_surf, (sx, sy))
        
        border_color = (0, 255, 0) if self.can_place else (255, 0, 0)
        pygame.draw.rect(surface, border_color, (sx, sy, target_size, target_size), 2)
        
        # Hint centrado en la parte inferior de la pantalla
        font = assets.get_font('small')
        hint_text = "Click para colocar | Esc para cancelar" if self.can_place else "No se puede colocar aquí"
        hint_color = Colors.UI_SUCCESS if self.can_place else Colors.UI_ERROR
        hint = font.render(hint_text, True, hint_color)
        
        hint_bg = pygame.Surface((hint.get_width() + 20, hint.get_height() + 8), pygame.SRCALPHA)
        hint_bg.fill((*Colors.UI_PANEL, 200))
        hint_x = SCREEN_WIDTH // 2 - hint.get_width() // 2
        hint_y = SCREEN_HEIGHT - 45
        surface.blit(hint_bg, (hint_x - 10, hint_y - 4))
        surface.blit(hint, (hint_x, hint_y))
