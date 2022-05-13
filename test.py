#!/usr/bin/env python
#cython: language_level=3

import os, sys, time
from magicpath import PathFinder, PathFinderType, Path, WinPath

__file__: str = sys.argv.__getitem__(0)

#* testing ...
if str(__name__).upper() in ("__MAIN__",):

    fp: PathFinderType = PathFinder()

    pwd = os.path.dirname(os.path.abspath(__file__))
    pwd = Path(src=pwd) if not fp.is_win() else WinPath(src=pwd)

    a = time.perf_counter()
    
    fp.winlook()
    print(fp.abspath(pwd))

    b = time.perf_counter()

    fp.reset_factory()
    print(fp.abspath(pwd))

    c = time.perf_counter()

    print("{:10.10f}".format(b - a))
    print("{:10.10f}".format(c - b))

    a = time.perf_counter()
    
    fp.winlook(currentdir="C:\\\\Home\\Skulluglify\\Desktop\\Projekt\\MagicPath")
    print(fp.abspath(""))

    b = time.perf_counter()

    fp.reset_factory()
    print(fp.abspath(""))

    c = time.perf_counter()

    print("{:10.10f}".format(b - a))
    print("{:10.10f}".format(c - b))
