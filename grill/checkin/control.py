# data, fs path
# if data is not file:
#    datafile = dumptodisk
# else:
#    datafile = data
# fspath.copy(datafile) OR move, if move, replace with new fspath

import json
from pathlib import Path
from functools import singledispatch

from fs.base import FS
from fs.osfs import OSFS
from fs.copy import copy_file, copy_dir
from fs.move import move_file, move_dir


def _checkin(src_fs: FS, src_path: str, dst_fs: FS, dst_path: str, move: bool=False):
    dst_dir = Path(dst_path).parent.as_posix()
    if not dst_fs.exists(dst_dir):
        dst_fs.makedirs(dst_dir)
    if src_fs.isfile(src_path):
        method = move_file if move else copy_file
    else:
        method = move_dir if move else copy_dir
    method(src_fs, src_path, dst_fs, dst_path)
    if move:
        src_fs.settext(rf'{src_path}.checkin', json.dumps({repr(dst_fs): dst_path}))
    return dst_fs, dst_path


@singledispatch
def checkin(src_fs: FS, src_path: str, dst_fs: FS, dst_path: str, move: bool=False):
    """Checkin data to a file system"""
    return _checkin(**locals())


@checkin.register(Path)
def __(src_path: Path, dst_path: Path, move: bool=False):
    """Overloaded function to allow checking in within the same OSFS with only Path instances"""
    src_path = src_path.resolve()
    src_fs = OSFS(src_path.parent.as_posix())
    src_path = src_path.name
    existing_parent = next(p for p in dst_path.parents if p.exists())
    dst_fs = OSFS(existing_parent.as_posix())
    dst_path = dst_path.relative_to(existing_parent).as_posix()
    return _checkin(src_fs, src_path, dst_fs, dst_path, move)


def cleantree(tgt_fs: FS, name: str):
    method = tgt_fs.remove if tgt_fs.isfile(name) else tgt_fs.removetree
    method(name)
    remaining_parts = Path(name).parts
    if len(remaining_parts) > 1:
        # if dst_path included more than 1 directory we are left with the top parent
        tgt_fs.removedir(remaining_parts[0])
