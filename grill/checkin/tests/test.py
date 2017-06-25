import unittest
from pathlib import Path
from contextlib import contextmanager
from functools import partial, partialmethod

from fs.osfs import OSFS
from fs.zipfs import ZipFS
from fs.tarfs import TarFS
from fs.tempfs import TempFS
from grill.checkin import checkin, cleantree

root_path = Path(__file__).parent

copy_dir_path = Path.joinpath(root_path, 'test_copy')
move_dir_path = Path.joinpath(root_path, 'test_move')


def setup():
    root_test = OSFS(root_path)
    root_test.copydir('test_copy', 'test_move', True)


@contextmanager
def checking_in(*args):
    dst_fs, dst_path = checkin(*args)
    try:
        yield dst_fs, dst_path
    finally:
        cleantree(dst_fs, dst_path)

setup()


class TestFS(unittest.TestCase):
    copy_fs_src = OSFS(copy_dir_path)
    copy_file_src = 'src/file.txt'
    copy_dir_src = 'src/directory'
    copy_fs_tgt = OSFS(copy_dir_path)
    copy_file_tgt = 'tgt/file.txt'
    copy_dir_tgt = 'tgt/directory'

    move_fs_src = OSFS(move_dir_path)
    move_file_src = 'src/file.txt'
    move_dir_src = 'src/directory'
    move_fs_tgt = OSFS(move_dir_path)
    move_file_tgt = 'tgt/file.txt'
    move_dir_tgt = 'tgt/directory'

    def _checkin_integrity(self, dst_fs, dst_path, type_method_name):
        self.assertTrue(dst_fs.exists(dst_path))
        self.assertTrue(getattr(dst_fs, type_method_name)(dst_path))

    _copy_file_integrity = partialmethod(_checkin_integrity, type_method_name='isfile')
    _copy_dir_integrity = partialmethod(_checkin_integrity, type_method_name='isdir')

    def _move_file_integrity(self, dst_fs, dst_path, exists_method):
        self._copy_file_integrity(dst_fs, dst_path)
        self.assertFalse(exists_method())

    def _move_dir_integrity(self, dst_fs, dst_path, exists_method):
        self._copy_dir_integrity(dst_fs, dst_path)
        self.assertFalse(exists_method())

    def test_copy(self):
        setup()
        # file
        with checking_in(self.copy_fs_src, self.copy_file_src, self.copy_fs_tgt, self.copy_file_tgt) as result:
            self._copy_file_integrity(*result)

        # dir
        with checking_in(self.copy_fs_src, self.copy_dir_src, self.copy_fs_tgt, self.copy_dir_tgt) as result:
            self._copy_dir_integrity(*result)

    def test_move(self):
        setup()
        # file
        with checking_in(self.move_fs_src, self.move_file_src, self.move_fs_tgt, self.move_file_tgt, True) as result:
            self._move_file_integrity(*result, partial(self.move_fs_src.exists, self.move_file_src))

        # dir
        with checking_in(self.move_fs_src, self.move_dir_src, self.move_fs_tgt, self.move_dir_tgt, True) as result:
            self._move_dir_integrity(*result, partial(self.move_fs_src.exists, self.move_dir_src))


class TestOSFS(TestFS):

    def test_copy(self):
        super().test_copy()
        setup()
        # file
        src_path = Path.joinpath(copy_dir_path, self.copy_file_src)
        with checking_in(src_path, Path.joinpath(root_path, 'test_copy_same')) as result:
            self._copy_file_integrity(*result)

        with checking_in(src_path, Path('from/cwd')) as result:
            self._copy_file_integrity(*result)

        # dir
        src_path = Path.joinpath(copy_dir_path, self.copy_dir_src)
        with checking_in(src_path, Path.joinpath(root_path, 'test_copy_same')) as result:
            self._copy_dir_integrity(*result)

        with checking_in(src_path, Path('from/cwd')) as result:
            self._copy_dir_integrity(*result)

    def test_move(self):
        super().test_move()
        setup()
        # file
        src_path = Path.joinpath(move_dir_path, self.move_file_src)
        with checking_in(src_path, Path.joinpath(root_path, 'test_move_same'), True) as result:
            self._move_file_integrity(*result, src_path.exists)

        setup()
        with checking_in(src_path, Path('from/cwd'), True) as result:
            self._move_file_integrity(*result, src_path.exists)

        # dir
        setup()
        src_path = Path.joinpath(move_dir_path, self.move_dir_src)
        with checking_in(src_path, Path.joinpath(root_path, 'test_move_same'), True) as result:
            self._move_dir_integrity(*result, src_path.exists)

        setup()
        with checking_in(src_path, Path('from/cwd'), True) as result:
            self._move_dir_integrity(*result, src_path.exists)


class TestZipFS(TestFS):
    copy_fs_tgt = ZipFS('copy.zip', write=True)
    move_fs_tgt = ZipFS('move.zip', write=True)


class TestTarFS(TestFS):
    copy_fs_tgt = TarFS('copy.tar', write=True)
    move_fs_tgt = TarFS('move.tar', write=True)


class TestTempFS(TestFS):
    copy_fs_tgt = TempFS('copy')
    move_fs_tgt = TempFS('move')
