#!/usr/bin/env python
#cython: language_level=3

import datetime, os

from .singletons import *
from .magicpath import *
from .pathfinder import *

def __wm() -> None:

    context: str

    context = "#==============================================================#\n# MagicPath created by <skulluglify@outlook.com/>              #\n# version build v1.0.0 alpha, 2022-05-13 19:37:33.692429       #\n#==============================================================#"

    print(context)

    
if not str(os.getenv("DISABLE_WM_MAGICPATH")).lower() in ("1","y","true"):

     __wm()

