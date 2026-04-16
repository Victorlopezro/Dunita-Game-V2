"""
Minimap - Minimapa en tiempo real para Dune Dominion
Muestra la posición del jugador, edificios y entidades cercanas.
"""
import pygame
import math
from src.config import Colors, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.systems.world import TileType, TILE_COLORS


MINIMAP_TILE_COLORS = {
    TileType.SAND:  (180, 140, 80),
    TileType.ROCK:  (90, 88, 75),
    TileType.OASIS: (40, 80, 130),
    TileType.FLOOR: (70, 55, 35),
}


class Minimap:
    """
    Minimapa que muestra un área alrededor del jugador.
    Se dibuja en la esquina inferior izquierda.
    """

    SIZE = 180           # Tamaño en píxeles del minimapa
    TILE_RENDER_SIZE = 4 # Píxeles por tile en el minimapa
    RADIUS_TILES = SIZE // (TILE_RENDER_SIZE * 2)  # Radio de tiles visibles

    def __init__(self, world_map):
        self.world = world_map
        self._surface = pygame.Surface((self.SIZE, self.SIZE), pygame.SRCALPHA)
        self._update_timer = 0.0
        self._update_interval = 0.5  # Actualizar cada 0.5 segundos
        self._dirty = True

    def update(self, dt: float, player_tx: int, player_ty: int):
        """Actualiza el minimapa si ha cambiado la posición del jugador."""
        self._update_timer += dt
        if self._update_timer >= self._update_interval:
            self._update_timer = 0.0
            self._dirty = True
            self._player_tx = player_tx
            self._player_ty = player_ty

    def _rebuild(self):
        """Reconstruye la superficie del minimapa."""
        self._surface.fill((0, 0, 0, 0))
        r = self.RADIUS_TILES
        ts = self.TILE_RENDER_SIZE
        cx = self.SIZE // 2
        cy = self.SIZE // 2

        ptx = getattr(self, '_player_tx', 0)
        pty = getattr(self, '_player_ty', 0)

        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                tx = ptx + dx
                ty = pty + dy
                tile = self.world.get_tile(tx, ty)
                color = MINIMAP_TILE_COLORS.get(tile, (180, 140, 80))

                # Verificar si hay un edificio en este tile
                if (tx, ty) in self.world.buildings_on_map:
                    color = (180, 120, 60)  # Color especial para edificios

                px_x = cx + dx * ts
                px_y = cy + dy * ts
                pygame.draw.rect(self._surface, (*color, 220), (px_x, px_y, ts, ts))

        self._dirty = False

    def draw(self, surface: pygame.Surface, player, enemies=None, mercenaries=None):
        """Dibuja el minimapa en la esquina inferior izquierda."""
        if self._dirty:
            self._rebuild()

        margin = 10
        x = margin
        y = SCREEN_HEIGHT - self.SIZE - margin - 20  # Espacio para la etiqueta

        # Fondo con borde
        bg = pygame.Surface((self.SIZE + 4, self.SIZE + 4), pygame.SRCALPHA)
        bg.fill((*Colors.UI_PANEL, 200))
        pygame.draw.rect(bg, Colors.UI_PANEL_BORDER, (0, 0, self.SIZE + 4, self.SIZE + 4), 2)
        # Esquinas decorativas
        for cx, cy in [(0, 0), (self.SIZE, 0), (0, self.SIZE), (self.SIZE, self.SIZE)]:
            pygame.draw.rect(bg, Colors.UI_HIGHLIGHT, (cx, cy, 4, 4))
        surface.blit(bg, (x - 2, y - 2))

        surface.blit(self._surface, (x, y))

        # Punto del jugador (siempre en el centro)
        cx = x + self.SIZE // 2
        cy = y + self.SIZE // 2
        pygame.draw.circle(surface, Colors.GOLD, (cx, cy), 4)
        pygame.draw.circle(surface, Colors.WHITE, (cx, cy), 4, 1)

        # Puntos de enemigos
        if enemies:
            ptx = getattr(self, '_player_tx', int(player.px // TILE_SIZE))
            pty = getattr(self, '_player_ty', int(player.py // TILE_SIZE))
            ts = self.TILE_RENDER_SIZE
            r = self.RADIUS_TILES

            for enemy in enemies:
                if not enemy.alive:
                    continue
                etx = int(enemy.px // TILE_SIZE)
                ety = int(enemy.py // TILE_SIZE)
                dx = etx - ptx
                dy = ety - pty
                if abs(dx) <= r and abs(dy) <= r:
                    ex = x + self.SIZE // 2 + dx * ts
                    ey = y + self.SIZE // 2 + dy * ts
                    pygame.draw.circle(surface, Colors.RED, (ex, ey), 3)

        # Puntos de mercenarios
        if mercenaries:
            ptx = getattr(self, '_player_tx', int(player.px // TILE_SIZE))
            pty = getattr(self, '_player_ty', int(player.py // TILE_SIZE))
            ts = self.TILE_RENDER_SIZE
            r = self.RADIUS_TILES

            for merc in mercenaries:
                if not merc.alive:
                    continue
                mtx = int(merc.px // TILE_SIZE)
                mty = int(merc.py // TILE_SIZE)
                dx = mtx - ptx
                dy = mty - pty
                if abs(dx) <= r and abs(dy) <= r:
                    mx = x + self.SIZE // 2 + dx * ts
                    my = y + self.SIZE // 2 + dy * ts
                    pygame.draw.circle(surface, Colors.UI_SUCCESS, (mx, my), 3)

        # Etiqueta
        font = pygame.font.SysFont(None, 14)
        label = font.render("MAPA", True, Colors.UI_TEXT_DIM)
        surface.blit(label, (x + self.SIZE // 2 - label.get_width() // 2,
                              y + self.SIZE + 3))
