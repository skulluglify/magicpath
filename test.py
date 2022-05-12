#!/usr/bin/env python

import os
from pathfinder import PathFinder
from singletons import PathFinderType, Path, WinPath

#* testing ...
if str(__name__).upper() in ("__MAIN__",):

    fp: PathFinderType = PathFinder()

    pwd = os.path.dirname(__file__)
    pwd = Path(src=pwd) if not fp.is_win() else WinPath(src=pwd)

    fp.winlook()
    print(fp.abspath(pwd))

    fp.reset_factory()
    print(fp.abspath(pwd))
