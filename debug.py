"""Runner rápido para exploração na IDE."""
from __future__ import annotations
import sys
from pathlib import Path
from rocketpy import Flight

from configs import HEFESTO, IREC, MOTOR_IREC
from src.ambiente import build_irec
from src.calculos.motor import derivar_motor
from src.construtor_foguete import build_rocket

d = derivar_motor(MOTOR_IREC)
print(
    f"Motor: {d.nome} (fonte={d.fonte}), "
    f"impulse={d.total_impulse:.1f} N·s, "
    f"FS={d.diagnosticos[0].valor:.3f}"
)

foguete = build_rocket(HEFESTO, modo="calculado", tipo_aletas="freeform")
env = build_irec()
voo = Flight(rocket=foguete.rocket, environment=env, **IREC)
apogee_agl = voo.apogee - env.elevation
print(f"Apogeu AGL (modo={foguete.modo}): {apogee_agl:.1f} m | Margem mín: {voo.min_stability_margin:.3f} cal")
