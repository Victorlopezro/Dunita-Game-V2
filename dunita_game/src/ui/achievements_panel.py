"""
Achievements Panel - Panel de logros del juego
Muestra el progreso y los logros desbloqueados.
"""
import pygame
from src.config import Colors, SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.widgets import Panel, Button
from src.utils.asset_manager import assets
from src.systems.achievements import AchievementManager, Achievement


class AchievementToast:
    """
    Notificación emergente (toast) que aparece al desbloquear un logro.
    Se muestra en la esquina inferior derecha y desaparece tras unos segundos.
    """

    DURATION = 4.0
    WIDTH = 320
    HEIGHT = 70

    def __init__(self, achievement: Achievement):
        self.achievement = achievement
        self.timer = 0.0
        self.y_offset = self.HEIGHT + 10  # Empieza fuera de pantalla

    @property
    def done(self) -> bool:
        return self.timer >= self.DURATION

    @property
    def alpha(self) -> int:
        ratio = self.timer / self.DURATION
        if ratio < 0.15:
            return int(255 * ratio / 0.15)
        elif ratio > 0.75:
            return int(255 * (1.0 - ratio) / 0.25)
        return 255

    def update(self, dt: float):
        self.timer += dt
        # Deslizar hacia arriba al aparecer
        target_y = 0
        self.y_offset += (target_y - self.y_offset) * 8 * dt

    def draw(self, surface: pygame.Surface, slot_index: int):
        """Dibuja el toast en la posición correspondiente al slot."""
        w, h = self.WIDTH, self.HEIGHT
        x = SCREEN_WIDTH - w - 15
        y = SCREEN_HEIGHT - h - 15 - slot_index * (h + 8) + self.y_offset

        alpha = self.alpha
        toast_surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Fondo con borde dorado
        pygame.draw.rect(toast_surf, (*Colors.UI_PANEL, alpha), (0, 0, w, h))
        pygame.draw.rect(toast_surf, (*Colors.GOLD_DARK, alpha), (0, 0, w, h), 2)
        # Barra izquierda de color
        pygame.draw.rect(toast_surf, (*Colors.GOLD, alpha), (0, 0, 5, h))

        font_small = assets.get_font('small')
        font_tiny = assets.get_font('tiny')

        # Icono y título
        icon_surf = font_small.render(self.achievement.icon, True, (*Colors.GOLD, alpha))
        toast_surf.blit(icon_surf, (12, 10))

        title_surf = font_small.render("¡LOGRO DESBLOQUEADO!", True, (*Colors.GOLD, alpha))
        toast_surf.blit(title_surf, (12 + icon_surf.get_width() + 6, 8))

        name_surf = font_small.render(self.achievement.name, True, (*Colors.WHITE, alpha))
        toast_surf.blit(name_surf, (12, 32))

        desc_surf = font_tiny.render(self.achievement.description[:50], True, (*Colors.UI_TEXT_DIM, alpha))
        toast_surf.blit(desc_surf, (12, 50))

        surface.blit(toast_surf, (x, y))


class AchievementsPanel:
    """
    Panel completo de logros accesible desde el menú de pausa.
    Muestra todos los logros con su estado y progreso.
    """

    def __init__(self, achievement_manager: AchievementManager):
        self.manager = achievement_manager
        self.visible = False
        self._toasts: list = []
        self._build_ui()

    def _build_ui(self):
        pw, ph = 700, 540
        px = (SCREEN_WIDTH - pw) // 2
        py = (SCREEN_HEIGHT - ph) // 2
        self.panel = Panel(px, py, pw, ph, "LOGROS DE ARRAKIS")
        self.btn_close = Button(
            px + pw - 50, py + 5, 40, 30, "X",
            callback=self.close, font_size='small',
            color_normal=Colors.RED
        )
        self._px, self._py = px, py
        self._pw, self._ph = pw, ph

    def open(self):
        self.visible = True

    def close(self):
        self.visible = False

    def toggle(self):
        if self.visible:
            self.close()
        else:
            self.open()

    def add_toast(self, achievement: Achievement):
        """Agrega una notificación toast para un logro desbloqueado."""
        self._toasts.append(AchievementToast(achievement))

    def update(self, dt: float):
        for toast in self._toasts:
            toast.update(dt)
        self._toasts = [t for t in self._toasts if not t.done]

    def handle_event(self, event) -> bool:
        if not self.visible:
            return False
        self.btn_close.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.close()
            return True
        return True

    def draw(self, surface: pygame.Surface):
        # Siempre dibujar los toasts, incluso si el panel está cerrado
        for i, toast in enumerate(self._toasts):
            toast.draw(surface, i)

        if not self.visible:
            return

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        self.panel.draw(surface)
        self.btn_close.draw(surface)

        achievements = self.manager.get_all()
        unlocked_count = sum(1 for a in achievements if a.unlocked)
        total_count = len(achievements)

        font_small = assets.get_font('small')
        font_tiny = assets.get_font('tiny')

        # Contador de logros
        counter_text = f"Desbloqueados: {unlocked_count}/{total_count}"
        counter_surf = font_small.render(counter_text, True, Colors.GOLD)
        surface.blit(counter_surf, (self._px + 15, self._py + 40))

        # Barra de progreso global
        bar_w = self._pw - 30
        bar_h = 10
        bar_x = self._px + 15
        bar_y = self._py + 62
        pygame.draw.rect(surface, Colors.UI_BTN_NORMAL, (bar_x, bar_y, bar_w, bar_h))
        fill_w = int(bar_w * (unlocked_count / max(1, total_count)))
        pygame.draw.rect(surface, Colors.GOLD, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(surface, Colors.UI_PANEL_BORDER, (bar_x, bar_y, bar_w, bar_h), 1)

        # Grid de logros: 2 columnas
        col_w = (self._pw - 30) // 2
        card_h = 80
        padding = 8
        start_y = self._py + 85

        for i, ach in enumerate(achievements):
            col = i % 2
            row = i // 2
            cx = self._px + 15 + col * (col_w + padding)
            cy = start_y + row * (card_h + padding)

            # Fondo de la tarjeta
            card_color = Colors.GOLD_DARK if ach.unlocked else Colors.UI_BTN_NORMAL
            card_surf = pygame.Surface((col_w, card_h), pygame.SRCALPHA)
            card_surf.fill((*card_color, 200))
            border_color = Colors.GOLD if ach.unlocked else Colors.UI_PANEL_BORDER
            pygame.draw.rect(card_surf, border_color, (0, 0, col_w, card_h), 2)

            # Icono
            icon_surf = font_small.render(ach.icon, True, Colors.GOLD if ach.unlocked else Colors.UI_TEXT_DIM)
            card_surf.blit(icon_surf, (8, 8))

            # Nombre
            name_color = Colors.WHITE if ach.unlocked else Colors.UI_TEXT_DIM
            name_surf = font_small.render(ach.name, True, name_color)
            card_surf.blit(name_surf, (8 + icon_surf.get_width() + 6, 6))

            # Descripción
            desc_surf = font_tiny.render(ach.description[:45], True, Colors.UI_TEXT_DIM)
            card_surf.blit(desc_surf, (8, 32))

            # Barra de progreso individual
            prog_w = col_w - 16
            prog_h = 8
            prog_x, prog_y = 8, card_h - 18
            pygame.draw.rect(card_surf, Colors.UI_BTN_NORMAL, (prog_x, prog_y, prog_w, prog_h))
            prog_fill = int(prog_w * (ach.progress / max(1, ach.target)))
            prog_color = Colors.GOLD if ach.unlocked else Colors.BLUE_SPICE
            pygame.draw.rect(card_surf, prog_color, (prog_x, prog_y, prog_fill, prog_h))
            pygame.draw.rect(card_surf, Colors.UI_PANEL_BORDER, (prog_x, prog_y, prog_w, prog_h), 1)

            # Texto de progreso
            prog_text = f"{int(ach.progress)}/{int(ach.target)}"
            prog_surf = font_tiny.render(prog_text, True, Colors.UI_TEXT_DIM)
            card_surf.blit(prog_surf, (prog_x + prog_w - prog_surf.get_width(), prog_y - 12))

            surface.blit(card_surf, (cx, cy))
