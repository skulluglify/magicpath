#!/usr/bin/env python
#cython: language_level = 3

import os
import sys
import importlib
import importlib.util
import marshal
import struct
import time

def code_to_source(src: str, dst: str = ""):

    if os.path.exists(src):

        if not dst:

            dst = src + "c"

        with open(src, "r") as fr:

            filename = os.path.basename(fr.name)
            sourcecode = fr.read()
            codeobj = compile(
                source=sourcecode,
                filename=filename,
                flags=0,
                mode="exec",
                optimize=1
            )
            
            bytecodes = marshal.dumps(codeobj)

            blank = struct.pack("<I", 0) ## little-endian
            modifdate = struct.pack("<I", int(time.time()))
            fsize = struct.pack("<I", os.fstat(fr.fileno()).st_size)

            with open(dst, "wb") as fw:


                data = bytearray(importlib.util.MAGIC_NUMBER)

                if (3,7) <= sys.version_info:

                    data.extend(blank)
                
                data.extend(modifdate)

                if (3,2) <= sys.version_info:

                    data.extend(fsize)

                data.extend(bytecodes)

                fw.write(data)

if str(__name__).upper() in ("__MAIN__",):

    code_to_source("./__init__.py")
    code_to_source("./singletons.py")
    code_to_source("./magicpath.py")
    code_to_source("./pathfinder.py")
