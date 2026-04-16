"""
Achievements System - Sistema de logros para Dune Dominion
Registra y evalúa condiciones de logros durante el gameplay.
"""
from dataclasses import dataclass, field
from typing import List, Callable, Optional


@dataclass
class Achievement:
    """Representa un logro del juego"""
    id: str
    name: str
    description: str
    icon: str = "★"
    unlocked: bool = False
    progress: float = 0.0  # 0.0 a 1.0
    target: float = 1.0
    category: str = "general"

    @property
    def is_complete(self) -> bool:
        return self.unlocked or self.progress >= self.target


# Catálogo de logros disponibles
ACHIEVEMENT_CATALOG = [
    Achievement(
        id="first_building",
        name="Constructor de Arrakis",
        description="Coloca tu primer edificio en el desierto.",
        icon="🏠",
        target=1.0,
        category="construccion"
    ),
    Achievement(
        id="first_creature",
        name="Domador de Dunas",
        description="Recluta tu primera criatura.",
        icon="🦂",
        target=1.0,
        category="criaturas"
    ),
    Achievement(
        id="survive_3_nights",
        name="Superviviente del Desierto",
        description="Sobrevive 3 noches consecutivas.",
        icon="🌙",
        target=3.0,
        category="supervivencia"
    ),
    Achievement(
        id="kill_10_enemies",
        name="Guardián de la Especia",
        description="Elimina 10 enemigos.",
        icon="⚔️",
        target=10.0,
        category="combate"
    ),
    Achievement(
        id="reach_day_30",
        name="Veterano de Arrakis",
        description="Alcanza el día 30.",
        icon="📅",
        target=30.0,
        category="general"
    ),
    Achievement(
        id="earn_100k_solaris",
        name="Magnate de la Especia",
        description="Acumula 100,000 Solaris.",
        icon="💰",
        target=100000.0,
        category="economia"
    ),
    Achievement(
        id="build_5_buildings",
        name="Arquitecto Imperial",
        description="Construye 5 edificios.",
        icon="🏛️",
        target=5.0,
        category="construccion"
    ),
    Achievement(
        id="recruit_5_creatures",
        name="Señor de las Bestias",
        description="Recluta 5 criaturas.",
        icon="🐉",
        target=5.0,
        category="criaturas"
    ),
    Achievement(
        id="equip_weapon",
        name="Guerrero Fremen",
        description="Equipa tu primera arma.",
        icon="🗡️",
        target=1.0,
        category="combate"
    ),
    Achievement(
        id="hire_mercenary",
        name="Señor de la Guerra",
        description="Contrata un mercenario.",
        icon="🛡️",
        target=1.0,
        category="combate"
    ),
]


class AchievementManager:
    """
    Gestor de logros. Evalúa condiciones y notifica al gameplay
    cuando se desbloquea un nuevo logro.
    """

    def __init__(self):
        self._achievements = {a.id: a for a in ACHIEVEMENT_CATALOG}
        self._callbacks: List[Callable] = []
        self._newly_unlocked: List[Achievement] = []
        self._nights_survived = 0
        self._enemies_killed = 0
        self._was_night = False

    def add_callback(self, callback: Callable):
        """Registra un callback que se llama al desbloquear un logro."""
        self._callbacks.append(callback)

    def get_all(self) -> List[Achievement]:
        return list(self._achievements.values())

    def get_unlocked(self) -> List[Achievement]:
        return [a for a in self._achievements.values() if a.unlocked]

    def get_newly_unlocked(self) -> List[Achievement]:
        """Devuelve y limpia la lista de logros recién desbloqueados."""
        result = self._newly_unlocked.copy()
        self._newly_unlocked.clear()
        return result

    def _unlock(self, achievement_id: str):
        ach = self._achievements.get(achievement_id)
        if ach and not ach.unlocked:
            ach.unlocked = True
            ach.progress = ach.target
            self._newly_unlocked.append(ach)
            for cb in self._callbacks:
                try:
                    cb(ach)
                except Exception:
                    pass

    def _update_progress(self, achievement_id: str, value: float):
        ach = self._achievements.get(achievement_id)
        if ach and not ach.unlocked:
            ach.progress = min(value, ach.target)
            if ach.progress >= ach.target:
                self._unlock(achievement_id)

    def on_building_placed(self, total_buildings: int):
        self._update_progress("first_building", 1.0)
        self._update_progress("build_5_buildings", float(total_buildings))

    def on_creature_recruited(self, total_creatures: int):
        self._update_progress("first_creature", 1.0)
        self._update_progress("recruit_5_creatures", float(total_creatures))

    def on_enemy_killed(self):
        self._enemies_killed += 1
        self._update_progress("kill_10_enemies", float(self._enemies_killed))

    def on_night_survived(self):
        self._nights_survived += 1
        self._update_progress("survive_3_nights", float(self._nights_survived))

    def on_weapon_equipped(self):
        self._update_progress("equip_weapon", 1.0)

    def on_mercenary_hired(self):
        self._update_progress("hire_mercenary", 1.0)

    def on_gold_changed(self, gold: int):
        self._update_progress("earn_100k_solaris", float(gold))

    def on_day_advanced(self, day: int):
        self._update_progress("reach_day_30", float(day))

    def on_night_changed(self, is_night: bool):
        """Llamar cada frame para detectar transición día→noche."""
        if self._was_night and not is_night:
            # Transición noche→día: sobrevivió la noche
            self.on_night_survived()
        self._was_night = is_night

    def to_dict(self) -> dict:
        """Serializa el estado para guardado."""
        return {
            "nights_survived": self._nights_survived,
            "enemies_killed": self._enemies_killed,
            "achievements": {
                aid: {"unlocked": a.unlocked, "progress": a.progress}
                for aid, a in self._achievements.items()
            }
        }

    def from_dict(self, data: dict):
        """Restaura el estado desde guardado."""
        self._nights_survived = data.get("nights_survived", 0)
        self._enemies_killed = data.get("enemies_killed", 0)
        for aid, state in data.get("achievements", {}).items():
            if aid in self._achievements:
                self._achievements[aid].unlocked = state.get("unlocked", False)
                self._achievements[aid].progress = state.get("progress", 0.0)
