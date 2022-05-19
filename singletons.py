#!/usr/bin/env python
#cython: language_level=3

# from __future__ import annotations, division, print_function

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Generator, List, Any, TypeVar, Union, Callable

# @dataclass(frozen=True, order=True)
# class Path(object):

#     src: str = field(defaut="")
#     is_win: bool = field(default=False, repr=False)

#     #todos: make symlink less processing without using new module class
#     #* unused variable for now
#     symlinks: List[Union[str, Path]] = field(default_factory=list, compare=False, hash=False, repr=False)

# @dataclass(frozen=True, order=True)
# class WinPath(Path):

#     is_win: bool = field(default=True, repr=False)


Path: Any
Path = TypeVar("Path", bound="Path")


@dataclass(frozen=False, order=True)
class Path(object):

    src: str = ""
    is_win: bool = False

    #todos: make symlink less processing without using new module class
    #* unused variable for now
    # symlinks: List[Union[str, Path]] = []

    def __init__(self: Path, src: str, is_win: bool = False, symlinks: List[Union[str, Path]] = []):

        self.src = src
        self.is_win = is_win
        self.symlinks = symlinks

    def __repr__(self: Path):

        return f"Path(src=\"{self.src}\")"


@dataclass(frozen=False, order=True)
class WinPath(Path):

    is_win: bool = True

    def __init__(self: Path, src: str, is_win: bool = False, symlinks: List[Union[str, Path]] = []):

        self.src = src
        self.is_win = is_win
        self.symlinks = symlinks

    def __repr__(self: Path):

        return f"WinPath(src=\"{self.src}\")"


MagicPathType: Any
MagicPathType = TypeVar("MagicPathType", bound="MagicPathType")


class System(Enum):

    Linux: str = "Linux"
    Darwin: str = "Darwin"
    Java: str = "Java"
    Windows: str = "Windows"
    Other: str = "Other"


class MagicPathType(ABC):

    ALPHABET: str

    WINDOWS: bool
    
    WORKDIR: str
    WINROOT: str

    @abstractmethod
    def winlook(self: MagicPathType, currentdir: Union[str, Path] = "/", winroot: Union[str, Path] = "C:\\\\", force: bool = True) -> bool: pass

    @abstractmethod
    def set_currentdir(self: MagicPathType, src: Union[str, Path], force: bool = False) -> bool: pass

    @abstractmethod
    def set_win_rootdir(self: MagicPathType, src: Union[str, Path], force: bool = False) -> bool: pass

    @abstractmethod
    def is_win(self: MagicPathType) -> bool: pass

    @abstractmethod
    def split(self: MagicPathType, src: Union[str, Path], diff: bool = False) -> Generator[Any, None, None]: pass

    @abstractmethod
    def get_root(self: MagicPathType, src: Union[str, Path]) -> Path: pass

    @abstractmethod
    def shift(self: MagicPathType, src: Union[str, Path]) -> Path: pass

    @abstractmethod
    def is_root(self: MagicPathType, src: Union[str, Path], diff: bool = False) -> bool: pass

    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* uncommon functional methods, only for purposes the kind of classes                                           *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    @abstractmethod
    def escape(self: MagicPathType, context: str) -> str: pass

    @abstractmethod
    def unescape(self: MagicPathType, context: str) -> str: pass
    
    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* uncommon functional methods, only for purposes the kind of classes                                           *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    @abstractmethod
    def is_abspath(self: MagicPathType, src: Union[str, Path]) -> bool: pass

    @abstractmethod
    def is_diff(self: MagicPathType, system: Union[str, System]) -> bool: pass

    @abstractmethod
    def abspath(self: MagicPathType, src: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path: pass

    @abstractmethod
    def join(self: MagicPathType, *srcs: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path: pass

    @abstractmethod
    def hook(self: MagicPathType, fn: Callable, src: Union[str, Path]) -> Any: pass


PathFinderType: Any
PathFinderType = TypeVar("PathFinderType", bound="PathFinderType")


class PathFinderType(ABC):

    p: MagicPathType
    
    MAX_DEPTH: int
    MAX_TIME_RECURSION: int

    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* methods from MagicPath                                                                                       *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    MP_WORKDIR: str
    MP_WINROOT: str
    MP_WINFORCE: bool
    MP_WINLOOK: bool

    @abstractmethod
    def winlook(self: PathFinderType, currentdir: Union[str, Path] = "/", winroot: Union[str, Path] = "C:\\\\", force: bool = True) -> bool: pass

    @abstractmethod
    def reset_factory(self: PathFinderType) -> bool: pass

    @abstractmethod
    def set_currentdir(self: PathFinderType, src: Union[str, Path], force: bool = False) -> bool: pass
    
    @abstractmethod
    def set_win_rootdir(self: PathFinderType, src: Union[str, Path], force: bool = False) -> bool: pass
    
    @abstractmethod
    def is_win(self: PathFinderType) -> bool: pass
    
    @abstractmethod
    def split(self: PathFinderType, src: Union[str, Path], diff: bool = False) -> Generator[Any, None, None]: pass
    
    @abstractmethod
    def get_root(self: PathFinderType, src: Union[str, Path]) -> Path: pass
    
    # @abstractmethod
    # def shift(self: PathFinderType, src: Union[str, Path]) -> Path: pass
    
    @abstractmethod
    def is_root(self: PathFinderType, src: Union[str, Path], diff: bool = False) -> bool: pass
    
    @abstractmethod
    def is_abspath(self: PathFinderType, src: Union[str, Path]) -> bool: pass
    
    @abstractmethod
    def is_diff(self: PathFinderType, system: Union[str, System]) -> bool: pass
    
    @abstractmethod
    def abspath(self: PathFinderType, src: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path: pass
    
    @abstractmethod
    def join(self: PathFinderType, *srcs: Union[str, Path], diff: bool = False, winroot: Union[str, Path] = "\\") -> Path: pass
    
    @abstractmethod
    def hook(self: PathFinderType, fn: Callable, src: Union[str, Path]) -> Any: pass

    #****************************************************************************************************************#
    #*                                                                                                              *#
    #* methods from MagicPath                                                                                       *#
    #*                                                                                                              *#
    #****************************************************************************************************************#

    @abstractmethod
    def match(self: PathFinderType, src: Union[str, Path], callback: Callable, depth: int = 0) -> None: pass

    @abstractmethod
    def match_hook(self: PathFinderType, fn: Callable, src: Union[str, Path], depth: int = 0) -> None: pass

    @abstractmethod
    def matchbase(self: PathFinderType, src: Union[str, Path], callback: Callable) -> None: pass

    @abstractmethod
    def matchbase_hook(self: PathFinderType, fn: Callable, src: Union[str, Path]) -> None: pass

    @abstractmethod
    def matchdir(self: PathFinderType, src: Union[str, Path], callback: Callable, depth: int = 0) -> None: pass

    @abstractmethod
    def matchdir_hook(self: PathFinderType, fn: Callable, src: Union[str, Path], depth: int = 0) -> None: pass
