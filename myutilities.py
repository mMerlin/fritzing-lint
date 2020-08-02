#!/usr/bin/env python
# coding=utf-8

'''
Utility methods collection
'''

# pipenv shell
# pipenv run pylint myutilities.py

import contextlib
import sys
import argparse
from pathlib import Path, PosixPath
import stat
import errno

ERROR_INVALID_NAME = 123
LINK_NEST_LIMIT = 5


@contextlib.contextmanager
def smart_filehandle(filehandle):
    '''wrapper method to be able to safely use an open file handle with 'with' '''
    try:
        yield filehandle
    finally:
        if filehandle is not sys.stdin and filehandle is not sys.stdout:
            filehandle.close()
# end def smart_filehandle()

def stat_following_link(src_path: str, action_object: argparse.Action) -> stat:
    '''follow through any link to get stat for real file'''
    if not isinstance(src_path, str) or not src_path:
        msg = "%r is not a valid path" % src_path
        raise argparse.ArgumentError(action_object, msg)
    nest_depth = 0
    have_link = True
    ex_path = src_path
    while have_link:
        followed_path = lstat_throwing_argument_error(ex_path, nest_depth, action_object, src_path)
        # do not want to follow symbolic links during folder walk, but
        # CAN use a symbolic link to point to the root folder
        have_link = stat.S_ISLNK(followed_path.st_mode)
        if have_link:
            nest_depth += 1
            if nest_depth > LINK_NEST_LIMIT:
                # resolve expands all of the nested links in a single
                # operation: never going to process more than a 2nd level
                msg = "%r is a too deeply nested series of links" % src_path
                raise argparse.ArgumentError(action_object, msg)
            ex_path = Path(src_path).resolve()
    return followed_path
# end def stat_following_link:

def lstat_throwing_argument_error(
        target_path: (str, PosixPath), current_depth: int,
        action_object: argparse.Action, starting_path: str) -> stat:
    '''handle errors around getting the stat information for a path'''
    try:
        return Path(target_path).lstat()
    except OSError as exc:
        if hasattr(exc, 'winerror'):
            # pylint: disable=no-member
            print(exc.winerror)  # DEBUG running on windows
            if exc.winerr == ERROR_INVALID_NAME:
                msg = "%r is not a valid path" % starting_path
                raise argparse.ArgumentError(action_object, msg)
        if exc.errno == errno.ENOENT:
            if current_depth > 0:
                msg = "Folder that %r references does not exist" % starting_path
            else:
                msg = "%r does not exist" % starting_path
            raise argparse.ArgumentError(action_object, msg)
        if exc.errno == errno.ENAMETOOLONG:
            msg = "%r is not a valid path" % starting_path
            raise argparse.ArgumentError(action_object, msg)
        print(exc.errno)  # DEBUG
    except ValueError as exc:
        msg = "%r is not a valid path" % starting_path
        raise argparse.ArgumentError(action_object, msg)
# end def lstat_throwing_argument_error:


class ExistingDir(argparse.Action):
    '''verify passed argument is a path to an existing directory'''
    # pylint: disable=too-few-public-methods
    def __call__(self, parser, namespace, src_path, option_string=None):
        '''verify that the path references an existing folder'''
        leaf_stat = stat_following_link(src_path, self)
        if not stat.S_ISDIR(leaf_stat.st_mode):
            msg = "%r is not a directory" % src_path
            raise argparse.ArgumentError(self, msg)
        setattr(namespace, self.dest, src_path)
    # end def __call__:
# end class ExistingDir:


class ReadableFile(argparse.Action):
    '''verify passed argument is a path to an existing readable normal file'''
    # pylint: disable=too-few-public-methods
    def __call__(self, parser, namespace, src_path, option_string=None):
        leaf_stat = stat_following_link(src_path, self)
        if not stat.S_ISREG(leaf_stat.st_mode):
            msg = "%r is not a regular file" % src_path
            raise argparse.ArgumentError(self, msg)
        setattr(namespace, self.dest, src_path)
    # end def __call__:
# end class ReadableFile:

# variables
#   cSpell:words
