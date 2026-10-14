"""Redraws the nine charts 1.7 in tall into figs_poster/, leaving room on the poster for the interpretation under each chart.

Runs the notebook source with two changes (figure height and output folder), so the charts stay identical otherwise.
Run: MPLBACKEND=Agg ../.venv/bin/python make_poster_figs.py
"""

from pathlib import Path

src = Path("shrinkflation.py").read_text()
for old, new in [("FIG_W, FIG_H = 2.36, 2.2", "FIG_W, FIG_H = 2.36, 1.7"), ('Path("figs")', 'Path("figs_poster")'), ('"figs/', '"figs_poster/')]:
    assert old in src, old
    src = src.replace(old, new)
exec(compile(src, "shrinkflation.py", "exec"))
