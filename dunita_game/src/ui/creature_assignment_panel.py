"""
Creature Assignment Panel - Panel para asignar criaturas a recintos
Permite al jugador gestionar qué criatura va a qué edificio.
"""
import pygame
from src.config import Colors, SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.widgets import Panel, Button, ScrollableList
from src.utils.asset_manager import assets


class CreatureAssignmentPanel:
    """
    Panel de dos columnas: criaturas sin asignar (izquierda)
    y recintos disponibles (derecha). El jugador selecciona
    una criatura y un recinto y pulsa 'Asignar'.
    """

    def __init__(self, economy):
        self.economy = economy
        self.visible = False
        self.selected_creature = None
        self.selected_building = None
        self.message = ""
        self.message_color = Colors.UI_TEXT
        self.message_timer = 0.0
        self._build_ui()

    def _build_ui(self):
        pw, ph = 700, 500
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        self._px, self._py = px, py
        self._pw, self._ph = pw, ph

        self.panel = Panel(px, py, pw, ph, "ASIGNACIÓN DE CRIATURAS")

        col_w = (pw - 30) // 2
        list_h = ph - 140

        # Lista de criaturas
        self.creature_list = ScrollableList(
            px + 10, py + 75, col_w, list_h,
            item_height=48,
            on_select=self._on_creature_select
        )

        # Lista de edificios
        self.building_list = ScrollableList(
            px + col_w + 20, py + 75, col_w, list_h,
            item_height=48,
            on_select=self._on_building_select
        )

        # Botón asignar
        self.btn_assign = Button(
            px + pw // 2 - 80, py + ph - 55, 160, 42,
            "ASIGNAR",
            callback=self._on_assign,
            font_size='medium',
            color_normal=(60, 80, 40)
        )

        # Botón cerrar
        self.btn_close = Button(
            px + pw - 50, py + 5, 40, 30, "X",
            callback=self.close, font_size='small',
            color_normal=Colors.RED
        )

    def _on_creature_select(self, idx: int, item: dict):
        self.selected_creature = item

    def _on_building_select(self, idx: int, item: dict):
        self.selected_building = item

    def _on_assign(self):
        if not self.selected_creature:
            self._show_message("Selecciona una criatura.", Colors.UI_ERROR)
            return
        if not self.selected_building:
            self._show_message("Selecciona un recinto.", Colors.UI_ERROR)
            return

        cid = self.selected_creature.get('instance_id', '')
        bid = self.selected_building.get('instance_id', '')

        success, msg = self.economy.assign_creature_to_building(cid, bid)
        color = Colors.UI_SUCCESS if success else Colors.UI_ERROR
        self._show_message(msg, color)

        if success:
            self.selected_creature = None
            self.selected_building = None
            self._refresh_lists()

        try:
            from src.systems.audio_manager import audio
            audio.play_sfx('place' if success else 'error')
        except Exception:
            pass

    def _show_message(self, msg: str, color=None):
        self.message = msg
        self.message_color = color or Colors.UI_TEXT
        self.message_timer = 3.0

    def _refresh_lists(self):
        """Actualiza las listas con datos actuales de la economía."""
        creatures = self.economy.creatures
        buildings = self.economy.buildings

        # Criaturas sin asignar
        unassigned = [c for c in creatures if not c.get('recinto_id')]
        self.creature_list.set_items(unassigned)

        # Edificios con espacio disponible
        available_buildings = []
        for b in buildings:
            assigned = len(b.get('criaturas_asignadas', []))
            capacity = b.get('capacidadMaxima', 5)
            if assigned < capacity:
                b_display = dict(b)
                b_display['nombre'] = f"{b['nombre']} ({assigned}/{capacity})"
                available_buildings.append(b_display)

        self.building_list.set_items(available_buildings)

    def open(self):
        self.visible = True
        self._refresh_lists()

    def close(self):
        self.visible = False

    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.open()

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False

        self.creature_list.handle_event(event)
        self.building_list.handle_event(event)
        self.btn_assign.handle_event(event)
        self.btn_close.handle_event(event)

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

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.panel.draw(surface)

        font_small = assets.get_font('small')
        font_tiny = assets.get_font('tiny')

        # Encabezados de columnas
        col_w = (self._pw - 30) // 2
        creatures_header = font_small.render("CRIATURAS SIN ASIGNAR", True, Colors.GOLD)
        surface.blit(creatures_header, (self._px + 10, self._py + 52))

        buildings_header = font_small.render("RECINTOS DISPONIBLES", True, Colors.GOLD)
        surface.blit(buildings_header, (self._px + col_w + 20, self._py + 52))

        # Separador vertical
        pygame.draw.line(
            surface, Colors.UI_PANEL_BORDER,
            (self._px + col_w + 15, self._py + 40),
            (self._px + col_w + 15, self._py + self._ph - 60),
            1
        )

        # Listas
        self.creature_list.draw(surface)
        self.building_list.draw(surface)

        # Detalle de selección actual
        if self.selected_creature or self.selected_building:
            self._draw_selection_summary(surface, font_tiny)

        # Botones
        self.btn_assign.draw(surface)
        self.btn_close.draw(surface)

        # Mensaje de feedback
        if self.message and self.message_timer > 0:
            msg_surf = font_small.render(self.message, True, self.message_color)
            msg_rect = msg_surf.get_rect(
                centerx=self._px + self._pw // 2,
                bottom=self._py + self._ph - 10
            )
            msg_bg = pygame.Surface((msg_surf.get_width() + 20, msg_surf.get_height() + 8), pygame.SRCALPHA)
            msg_bg.fill((*Colors.UI_PANEL, 200))
            surface.blit(msg_bg, (msg_rect.left - 10, msg_rect.top - 4))
            surface.blit(msg_surf, msg_rect)

    def _draw_selection_summary(self, surface, font):
        """Muestra un resumen de la selección actual."""
        parts = []
        if self.selected_creature:
            parts.append(f"Criatura: {self.selected_creature.get('nombre', '?')}")
        if self.selected_building:
            parts.append(f"Recinto: {self.selected_building.get('nombre', '?')}")

        if parts:
            text = "  →  ".join(parts)
            surf = font.render(text, True, Colors.BLUE_SPICE)
            x = self._px + self._pw // 2 - surf.get_width() // 2
            y = self._py + self._ph - 75
            surface.blit(surf, (x, y))
