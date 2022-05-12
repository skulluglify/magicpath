#!/usr/bin/env python
#cython: language_level=3

# from __future__ import annotations, division, print_function

import os, platform
import ntpath as nt
import pathlib as pl

from typing import Callable, Generator, Any, List, TypeVar, Union
from .magicpath import MagicPath
from .singletons import Path, PathFinderNSType, PathFinderType, System, WinPath

PathFinderNS = TypeVar("PathFinderNS", bound="PathFinderNS")
PathFinder = TypeVar("PathFinder", bound="PathFinder")

class PathFinderNS(PathFinderNSType):

    """
    Not Safe for multithreading

    TODOS: fixed os.path if using winlook
    
    p: Any
    p = os.path

    if self.WINDOWS:

        p = nt if os.path is not nt else p

    else:

        p = ps if os.path is not ps else p
    """

    p: MagicPath

    __FINDPATH: bool

    MAX_DEPTH: int
    MAX_DEPTH = 0 #? Infinity

    MAX_TIME_RECURSION: int
    MAX_TIME_RECURSION = 1000

    def __init__(self: PathFinderNS, *args: Any, **kwargs: Any):

        self.__dict__.update(kwargs)
        self.p = MagicPath()
        self.__FINDPATH = False

    def match(self: PathFinderNS, src: Union[str, Path], callback: Callable, depth: int = 0) -> None:

        self.matchdir(src, lambda dst: self.matchbase(dst, callback), depth)

    def matchbase(self: PathFinderNS, src: Union[str, Path], callback: Callable) -> Any:

        if isinstance(src, Path):

            src = src.src

        if self.p.is_abspath(src):

            if os.path.exists(src):

                if callable(callback):

                    callback(src)
                
                return

            cdir: str
            cbase: str
            cdir, cbase = os.path.split(src)

            pathl: pl.Path = pl.Path(cdir)

            if pathl.exists():

                zbase: str

                for p in pathl.iterdir():

                    zbase = os.path.basename(p.as_posix())

                    if zbase.lower() == cbase.lower():

                        if callable(callback):

                            callback(os.path.join(cdir, zbase))

                        return

        return

    def matchdir(self: PathFinderNS, src: Union[str, Path], callback: Callable, depth: int = 0) -> Any:

        if not self.p.is_abspath(src):

            src = self.p.abspath(src)

        paths: List[str] = [p.src for p in self.p.split(src)]

        self.__find_depth(paths, callback, depth)

        #* set back value
        self.__FINDPATH = False

    def __find_depth(self: PathFinderNS, src: List[str], callback: Callable, depth: int = 0, cdepth: int = 0, max_time_recursion: int = 0, i: int = 0) -> Any:

        #* stop recursion
        if self.__FINDPATH: return

        #* safety check
        if self.MAX_TIME_RECURSION <= max_time_recursion: return

        c: str
        c = self.p.join(*tuple(src[i] for i in range(i))).src

        n: int
        n = len(src)

        m: int
        m = self.MAX_DEPTH or depth

        if n > i:

            if c == "":

                c = self.p.abspath(
                    self.p.get_root("/")
                ).src

            cdir: str
            cbase: str
            cdir, cbase = os.path.split(c)
            
            pathl: pl.Path = pl.Path(cdir)

            if pathl.exists():

                if not cbase:

                    if self.p.is_root(cdir):

                        self.__find_depth(src, callback, depth, cdepth + 1, max_time_recursion + 1, i + 1)
                        
                        return

                zbase: str

                # zfind: bool
                # zfind = False

                for pp in pathl.iterdir():

                    if pp.is_dir():

                        zbase = os.path.basename(pp.as_posix())

                        if zbase.lower() == cbase.lower():

                            # zfind = True

                            #* change dirname to currentdir in system
                            src[i - 1] = zbase

                            #* maximum depth
                            if m > 0 and m < cdepth:

                                #* refresh path as string
                                c = self.p.join(*tuple(src[i] for i in range(i))).src

                                if callable(callback):

                                    callback(c)

                                self.__FINDPATH = True

                                return

                            self.__find_depth(src, callback, depth, cdepth + 1, max_time_recursion + 1, i + 1)
                            
                            # return
                
                # if not zfind:

                #     if callable(callback):

                #         callback(c)

                #     return

        else:

            if callable(callback):

                callback(c)

            self.__FINDPATH = True
            
            return


class PathFinder(PathFinderType):

    """
    Safe for multithrading
    but slower than PathFinderNS
    this classes is Wrapper for PathFinderNS
    """

    p: MagicPath

    def __init__(self: PathFinderType, *args: Any, **kwargs: Any):

        self.__dict__.update(kwargs)
        self.p = MagicPath()

    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* methods from MagicPath, Exclude Methods escape, unescape, shift                                              *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    MP_WORKDIR: str
    MP_WORKDIR = "/"

    MP_WINROOT: str
    MP_WINROOT = "C:\\\\"
    
    MP_WINFORCE: bool
    MP_WINFORCE = True

    MP_WINLOOK: bool
    MP_WINLOOK = False

    def winlook(self: PathFinderType, currentdir: Union[str, Path] = "/", winroot: Union[str, Path] = "C:\\\\", force: bool = True) -> bool:

        self.MP_WORKDIR = currentdir
        self.MP_WINROOT = winroot
        self.MP_WINFORCE = force
        self.MP_WINLOOK = True

        self.p.winlook(currentdir, winroot, force)

    #* disable winlook
    def reset_factory(self: PathFinderType) -> bool:

        self.MP_WORKDIR = "/"
        self.MP_WINROOT = "C:\\\\"
        self.MP_WINFORCE = True
        self.MP_WINLOOK = False

        self.p.WORKDIR = os.getcwd()
        self.p.WINDOWS = os.path is nt or platform.system().lower().startswith("win")

    def __winlook(self: PathFinderType, pf: PathFinderNSType) -> None:

        if self.MP_WINLOOK:
            pf.p.winlook(
                self.MP_WORKDIR,
                self.MP_WINROOT,
                self.MP_WINFORCE
            )
    
    def set_currentdir(self: PathFinderType, src: Union[str, Path], force: bool = False) -> bool:

        return self.p.set_currentdir(src, force)
    
    def set_win_rootdir(self: PathFinderType, src: Union[str, Path], force: bool = False) -> bool:

        return self.p.set_win_rootdir(src, force)
    
    def is_win(self: PathFinderType) -> bool:

        return self.p.is_win()
    
    def split(self: PathFinderType, src: Union[str, Path], diff: bool = False) -> Generator[Any, None, None]:

        yield from self.p.split(src, diff)
    
    def get_root(self: PathFinderType, src: Union[str, Path]) -> Path:

        return self.p.get_root(src)
    
    # def shift(self: PathFinderType, src: Union[str, Path]) -> Path:

    #     return self.p.shift(src)
    
    def is_root(self: PathFinderType, src: Union[str, Path], diff: bool = False) -> bool:

        return self.p.is_root(src, diff)
    
    def is_abspath(self: PathFinderType, src: Union[str, Path]) -> bool:

        return self.p.is_abspath(src)
    
    def is_diff(self: PathFinderType, system: Union[str, System]) -> bool:

        return self.p.is_diff(system)
    
    def abspath(self: PathFinderType, src: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path:

        return self.p.abspath(src, diff, winroot)
    
    def join(self: PathFinderType, *srcs: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path:

        return self.p.join(*srcs, diff, winroot)
    
    def hook(self: PathFinderType, fn: Callable, src: Union[str, Path]) -> Any:

        return self.p.hook(fn, src)

    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* methods from MagicPath, Exclude Methods escape, unescape, shift                                              *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    def __getpf(self: PathFinderType) -> PathFinderNSType:

        pf: PathFinderNSType = PathFinderNS()
        self.__winlook(pf)
        return pf

    def __nosupports(self: PathFinderType, pf: PathFinderNSType, name: Union[str, Callable] = "this func") -> None:

        if callable(name):

            name = name.__name__

        if self.p.is_diff(System.Windows if pf.p.is_win() else System.Other):

            raise ValueError(f"PathFinder: {name} not support for different platform")

    def match(self: PathFinderType, src: Union[str, Path], callback: Callable, depth: int = 0) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.match)

        pf.match(src, callback, depth)

    def matchbase(self: PathFinderType, src: Union[str, Path], callback: Callable) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.matchbase)

        pf.matchbase(src, callback)

    def matchdir(self: PathFinderType, src: Union[str, Path], callback: Callable, depth: int = 0) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.matchdir)

        pf.matchdir(src, callback, depth)

    def match_hook(self: PathFinderType, fn: Callable, src: Union[str, Path], depth: int = 0) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.match_hook)

        pf.p.hook(lambda dst: pf.match(dst, fn, depth), src)

    def matchbase_hook(self: PathFinderType, fn: Callable, src: Union[str, Path]) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.matchbase_hook)

        pf.p.hook(lambda dst: pf.matchbase(dst, fn), src)

    def matchdir_hook(self: PathFinderType, fn: Callable, src: Union[str, Path], depth: int = 0) -> None:

        pf: PathFinderNSType = self.__getpf()
        self.__nosupports(pf, self.matchdir_hook)
        
        pf.p.hook(lambda dst: pf.matchdir(dst, fn, depth), src)
