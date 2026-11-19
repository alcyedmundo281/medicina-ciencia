"""Generador y validador del libro Medicina y Ciencia (JSON -> QMD -> Quarto HTML / PDF / EPUB)."""

from __future__ import annotations

ANCHO_MM = 170
ALTO_MM = 244
ANCHO_PULGADAS = 6.69
ALTO_PULGADAS = 9.61
ANCHO_PT = ANCHO_MM * 72.0 / 25.4
ALTO_PT = ALTO_MM * 72.0 / 25.4
TOLERANCIA_PT = 2.0

NOMBRE_SALIDA = "libro-medicina-y-ciencia"
