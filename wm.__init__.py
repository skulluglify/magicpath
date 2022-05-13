#!/usr/bin/env python
#cython: language_level=3

import datetime, os

from .singletons import *
from .magicpath import *
from .pathfinder import *

def __wm() -> None:

    context: str

    ## watermark

    print(context)

    
if not str(os.getenv("DISABLE_WM_MAGICPATH")).lower() in ("1","y","true"):

     __wm()
