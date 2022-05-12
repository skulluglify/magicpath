#!/usr/bin/env python
#cython: language_level=3

# from __future__ import annotations, division, print_function

import os, platform
import ntpath as nt
import posixpath as ps
import pathlib as pl

from typing import Callable, Generator, Any, List, TypeVar, Union
from .singletons import Path, PathFinderNSType, System, MagicPathType, WinPath

#? make dynamic path
#? platform.system() in ("Linux", "Darwin", "Java", "Windows")

MagicPath = TypeVar("MagicPath", bound="MagicPath")

class MagicPath(MagicPathType):

    ALPHABET: str
    ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    WINDOWS: bool
    WINDOWS = os.path is nt or platform.system().lower().startswith("win")
    
    #? debug only
    # WINDOWS = True

    WORKDIR: str
    WORKDIR = os.getcwd()
    
    WINROOT: str
    WINROOT = "C:\\\\"

    def winlook(self: MagicPathType, currentdir: Union[str, Path] = "/", winroot: Union[str, Path] = "C:\\\\", force: bool = True) -> bool:

        if isinstance(currentdir, Path):

            currentdir = currentdir.src

        if isinstance(winroot, Path):

            winroot = winroot.src

        if currentdir == "/" or not currentdir:

            currentdir = winroot

        self.WORKDIR = currentdir
        self.WINROOT = winroot
        
        self.WINDOWS = True

        return True

    def set_currentdir(self: MagicPathType, src: Union[str, Path], force: bool = False) -> bool:

        if isinstance(src, Path):

            src = src.src

        if os.path.exists(src) or force:

            if not force:
                
                os.chdir(src)
            
            self.WORKDIR = src

            return True

        return False

    def set_win_rootdir(self: MagicPathType, src: Union[str, Path], force: bool = False) -> bool:

        if isinstance(src, Path):

            src = src.src

        if os.path.exists(src) or force:
            
            self.WINROOT = src

            return True

        return False

    def is_win(self: MagicPathType) -> bool:

        return self.WINDOWS

    def __is_win(self: MagicPathType, diff: bool = False) -> bool:

        #* win diff == pos
        #* win not diff == nt
        #* not win diff == nt
        #* not win not diff == ps

        #* 1 1 0
        #* 1 0 1
        #* 0 1 1
        #* 0 0 0

        return self.WINDOWS ^ diff

    def split(self: MagicPathType, src: Union[str, Path], diff: bool = False) -> Generator[Any, None, None]:

        dst: str

        if isinstance(src, Path):

            #* make auto identify
            diff = self.is_diff(System.Windows) if src.is_win else diff

            #* get src from Path
            dst = src.src

        else:

            #* src as string
            dst = src

        # if self.is_abspath(dst):
        #     yield from self.__split(dst, diff)

        if self.is_abspath(dst):
            
            yield WinPath(src="") if self.__is_win(diff) else Path(src="")

        yield from self.__split(dst, diff)

    def __split(self: MagicPathType, src: str, diff: bool = False) -> Generator[Any, None, None]:

        cdir: str
        cbase: str

        cdir, cbase = nt.split(src) if self.WINDOWS ^ diff else ps.split(src)

        #? not cdir as non empty string
        if not (self.is_root(cdir, diff) or not cdir):

            yield from self.__split(cdir, diff)

        cbase = self.unescape(cbase)

        yield WinPath(src=cbase) if self.__is_win(diff) else Path(src=cbase)

    def get_root(self: MagicPathType, src: Union[str, Path]) -> Path:

        if isinstance(src, Path):

            src = src.src

        #* win rootdir
        if src.__getitem__(slice(0, 1, 1)).lower() in self.ALPHABET \
            and src.__getitem__(slice(1, 2, 1)) == ":" \
            and len(src) >= 4:

            return WinPath(src=src.__getitem__(slice(0, 4, 1)))

        #* posix rootdir
        elif src.startswith("/"):

            return Path(src="/")

        #* current dir
        elif src in ("",):

            # cwd: str
            # cwd = self.WORKDIR

            return WinPath(src=self.WORKDIR) if self.WINDOWS else Path(src=self.WORKDIR)

        #* make it posix
        #* bad idea but still work enough
        #* get first dirname
        else:

            return self.shift(src)

    def shift(self: MagicPathType, src: Union[str, Path]) -> Path:

        if isinstance(src, Path):

            src = src.src

        context: str
        context = ""

        for c in src:

            if c in ("/", "\\", ""): break
            context += c

        if context == "":

            # cwd: str
            # cwd = self.WORKDIR

            return WinPath(src=self.WORKDIR) if self.WINDOWS else Path(src=self.WORKDIR)

        return WinPath(src=context) if self.WINDOWS else Path(src=context)

    def is_root(self: MagicPathType, src: Union[str, Path], diff: bool = False) -> bool:

        if isinstance(src, Path):

            src = src.src

        #* win diff == pos
        #* win not diff == nt
        #* not win diff == nt
        #* not win not diff == ps

        #* 1 1 0
        #* 1 0 1
        #* 0 1 1
        #* 0 0 0

        if self.WINDOWS ^ diff:

            return src.__getitem__(slice(0, 1, 1)).lower() in self.ALPHABET \
            and src.__getitem__(slice(1, 2, 1)) == ":" \
            and len(src) == 4

        return src in ("/", "")

    def escape(self: MagicPathType, context: str) -> str:

        if " " in context:

            context = "\"" + context + "\"" if self.WINDOWS else context.replace(" ", "\\ ")
        
        #* bad idea but still work enough
        return context

    def unescape(self: MagicPathType, context: str) -> str:

        n: int
        n = len(context)

        if n > 1:
            if context.startswith("\'") and context.endswith("\'"):

                #* "new folder" = new folder
                context = context.__getitem__(slice(1, n - 1, 1))
            
            elif context.startswith("\"") and context.endswith("\""):

                #* 'new folder' = new folder
                context = context.__getitem__(slice(1, n - 1, 1))
            
            else:

                #* new\ folder = new folder
                context = context.replace("\\", "")

        #* fixed starts characters, path only
        if context.startswith("\'") or context.startswith("\""):
            context = context.__getitem__(slice(1, None, 1))

        #* fixed ends characters, path only
        if context.endswith("\'") or context.endswith("\""):
            context = context.__getitem__(slice(0, len(context) - 1, 1))
        
        #* bad idea but still work enough
        return context

    def is_abspath(self: MagicPathType, src: Union[str, Path]) -> bool:

        if isinstance(src, Path):

            src = src.src

        #* path is win
        #* path is posix
        return src.startswith("/") or src.startswith("\\") or (
            src.__getitem__(slice(0, 1, 1)).lower() in self.ALPHABET \
            and src.__getitem__(slice(1, 2, 1)) == ":" \
            and len(src) >= 4
        )

    def is_diff(self: MagicPathType, system: Union[str, System]) -> bool:

        #* win win not diff
        #* win pos diff
        #* pos win diff
        #* pos pos not diff

        #* 1 1 0
        #* 1 0 1
        #* 0 1 1
        #* 0 0 0

        system = system.value if isinstance(system, System) else system

        return self.WINDOWS ^ (system.lower().startswith("win"))

    def abspath(self: MagicPathType, src: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path:

        if isinstance(src, Path):

            diff = self.WINDOWS != src.is_win
            src = src.src

        #* win win regular
        #* win pos non-regular
        #* pos win non-regular
        #* pos pos regular

        if isinstance(winroot, Path):

            winroot = winroot.src

        if winroot == "/" or winroot == "\\" or not winroot:

            winroot = self.WINROOT

        # todos: __file__ make point to get absolute path

        dst: str
        root: str

        dst = ""
        root = winroot if self.WINDOWS else "/"

        #* if using winlook
        #* fixed os.path
        p: Any
        p = os.path

        if self.WINDOWS:

            p = nt if os.path is not nt else p

        else:

            p = ps if os.path is not ps else p

        if not diff:

            if self.is_abspath(src):

                dst = src
            
            else:

                #* join path
                dst = p.join(
                    self.WORKDIR,
                    src
                )

        else:

            paths: List[str]

            if self.is_abspath(src):

                paths = [self.escape(p.src) for p in self.split(src, True)]

                #* join path
                dst = self.__join([root, *paths])

            else:

                paths = [self.escape(p.src) for p in self.split(src, True)]

                #* join path
                dst = self.__join([self.WORKDIR, *paths])

        return WinPath(src=dst) if self.WINDOWS else Path(src=dst)

    def join(self: MagicPathType, *srcs: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path:

        c: str
        d: bool
        t: List[str] = []

        if isinstance(winroot, Path):

            winroot = winroot.src

        if winroot == "/" or winroot == "\\" or not winroot:

            winroot = self.WINROOT

        for s in srcs:

            #* s is Path

            if isinstance(s, Path):

                c = s.src
                d = self.WINDOWS != s.is_win

            else:

                c = s
                d = diff

            #* quick append 
            if not d:

                if not self.is_abspath(c):

                    t.append(c)

                    #* shortage
                    continue

            #* branch path to multiple base path
            for p in self.split(c, d):

                #* p is Path
                
                t.append(
                    self.escape(
                        p if not isinstance(p, Path) else p.src
                    )
                )

        return WinPath(src=self.__join(t, winroot)) if self.WINDOWS else Path(src=self.__join(t))


    def __join(self, srcs: List[str], winroot: str = "\\") -> str:

        n: int
        dst: str
        chain: str

        if winroot == "/" or winroot == "\\":

            winroot = self.WINROOT
        
        n = len(srcs)
        dst = ""
        chain = "\\" if self.WINDOWS else "/"

        for (i, src) in enumerate(srcs):

            if src == "":

                if i == 0:
                    
                    dst = winroot if self.WINDOWS else "/"
                    
                continue

            if src.startswith("/") or src.startswith("\\"):
                src = src.__getitem__(slice(1, None, 1))

            if src.endswith("/") or src.endswith("\\"):
                src = src.__getitem__(slice(0, len(src) - 1, 1))

            dst += src + chain if i != n - 1 else src

        return dst

    def hook(self: MagicPathType, fn: Callable, src: Union[str, Path]) -> Any:

        #* handling error, type error
        if not callable(fn):

            #* bypass
            # fn = lambda x: x

            #* raise error
            raise TypeError("fn must be callable!")

        #* get absolute path
        dst: Path
        dst = self.abspath(src)

        #* debug
        # print(dst)

        #* src is Path (Base)
        return fn(
            self.__join(
                [
                    self.unescape(p.src) for p in self.split(dst, self.WINDOWS != dst.is_win)
                ]
            )
        )
