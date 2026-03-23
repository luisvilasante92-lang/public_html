# -*- coding: utf-8 -*-
"""
WSGI для Phusion Passenger (Beget и др.).
Пути к проекту берутся от расположения этого файла — не хардкодьте домашний каталог.
"""
import glob
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

# Локальный venv на сервере: venv/lib/pythonX.Y/site-packages
for _site in sorted(
    glob.glob(os.path.join(_ROOT, 'venv', 'lib', 'python*', 'site-packages')),
    reverse=True,
):
    if _site not in sys.path:
        sys.path.insert(0, _site)

from run import app as application
