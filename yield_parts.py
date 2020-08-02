#!/usr/bin/env python
# coding=utf-8

'''
iterate of (selected) Fritzing part folders / files, yielding on at a time

concept:

A generator function that starts by creating an instance of a class that uses
configuration information (argparse.Namespace variant) to select (specify) a
set of files to be processed.  Once the instance is configured, `yield` the
file specifications one at a time. The main logic for that should be in the
selection class, but the function can hide that (complexity) from the caller

for file_path in instance.iteration:
    yield file_path
'''

# pipenv shell
# pipenv run pylint count_parts.py

# standard library imports
import os
import posix
import argparse

# local application/library specific imports
# from myutilities import ExistingDir

YIELD_PARTS_VERSION = '0.0.1'


def scan_directory_files(
        directory_path: [str, posix.DirEntry]) -> posix.DirEntry:
    '''return one file at a time from a specified directory'''
    if isinstance(directory_path, str):
        start_path = directory_path
    else:
        start_path = directory_path.path
    with os.scandir(start_path) as directory_files:
        for set_file_spec in directory_files:
            # print('scan_directory_files: next file "{0}"'.format(set_file_spec)) # DEBUG
            yield set_file_spec
# end def scan_directory_files:


class PseudoDirEntry:
    '''A fake posix.DirEntry instantiation'''
    def __init__(self, name, path):
        '''constructor'''
        self.name = name
        self.path = path
        self._is_dir = None
        self._is_file = None
        self._stat = None

    def is_dir(self):
        '''getter function to emulate DirEntry'''
        return self._is_dir

    def is_file(self):
        '''getter function to emulate DirEntry'''
        return self._is_file

    def stat(self):
        '''getter function to emulate DirEntry'''
        return self._stat
# end class PseudoDirEntry:


class PartFinder:
    '''create a generator that will iterate over the specified part files'''
    PART_SOURCE_FOLDERS = ('contrib', 'core', 'obsolete', 'user')
    PART_IMAGE_FOLDER = 'svg'
    PART_VIEW_FOLDERS = ('breadboard', 'icon', 'pcb', 'schematic')
    PART_FILE_TYPE = ('.fzp')
    IMAGE_FILE_TYPE = ('.svg')

    def __init__(self, cmd_args: argparse.Namespace):
        # self.command_arguments = cmd_args
        self.criteria = {
            'match_suffix': None,
            'folder': None,
            'single_folder': None,
            'svg': None,
            'part_library': None
        }
        # hpd setup folder nest/filter criteria
        self.process_command_arguments(cmd_args)
    # end def __init__:

    def process_command_arguments(self, cmd_args: argparse.Namespace) -> None:
        '''analyze configuration options, and setup processing criteria'''
        # print('start process_command_arguments {0}'.format(cmd_args)) # DEBUG
        if not cmd_args.folder is None:
            self.criteria['single_folder'] = True
            self.criteria['part_library'] = False
            self.criteria['folder'] = PseudoDirEntry('root', cmd_args.folder)
            self.criteria['match_suffix'] = self.PART_FILE_TYPE
        elif not cmd_args.part_library is None:
            self.criteria['single_folder'] = False
            self.criteria['part_library'] = True
            self.criteria['folder'] = PseudoDirEntry('root', cmd_args.part_library)
        else:
            raise NotImplementedError(
                'handling not written yet for additional configuration option')

        self.criteria['svg'] = cmd_args.svg
    # end def process_command_arguments:

    def folder_sources(self) -> posix.DirEntry:
        '''provide single source folder for processing'''
        root = self.criteria['folder']
        yield root
        if self.criteria['svg']:
            self.criteria['match_suffix'] = self.IMAGE_FILE_TYPE
            yield root
    # end def folder_sources:

    def library_sources(self) -> posix.DirEntry:
        '''sequence through the part source folders in the library'''
        image_folder = None
        with os.scandir(self.criteria['folder'].path) as library_root:
            self.criteria['match_suffix'] = self.PART_FILE_TYPE
            for source_candidate in library_root:
                if self.is_source_folder(source_candidate):
                    yield source_candidate
                elif self.is_image_folder(source_candidate):
                    image_folder = source_candidate
        if self.criteria['svg'] and not image_folder is None:
            self.criteria['match_suffix'] = self.IMAGE_FILE_TYPE
            for source_candidate in image_folder:
                if self.is_source_folder(source_candidate):
                    for view_candidate in source_candidate:
                        if self.is_view_folder(view_candidate):
                            yield view_candidate
    # end def library_sources(self, root: posix.DirEntry) ->posix.DirEntry:

    def is_source_folder(self, candidate_folder: posix.DirEntry) -> bool:
        '''decide when a folder contains part definition files'''
        return candidate_folder.is_dir() and candidate_folder.name in self.PART_SOURCE_FOLDERS

    def is_image_folder(self, candidate_folder: posix.DirEntry) -> bool:
        '''decide when a folder contains part image file (folders)'''
        return candidate_folder.is_dir() and candidate_folder.name == self.PART_IMAGE_FOLDER

    def is_view_folder(self, candidate_folder: posix.DirEntry) -> bool:
        '''decide when a folder contains part view image files'''
        return candidate_folder.is_dir() and candidate_folder.name in self.PART_VIEW_FOLDERS

    def matching_folders(self) -> posix.DirEntry:
        '''sequence through the directories that match the selection conditions'''
        # print('start matching_folders') # DEBUG
        matching_sources = None
        if self.criteria['single_folder']:
            matching_sources = self.folder_sources
        elif self.criteria['part_library']:
            matching_sources = self.library_sources
        else:
            raise NotImplementedError('handling not written yet for other sources')

        for source in matching_sources():
            yield source
    # end def matching_folders:

    def filtered_files(self) -> posix.DirEntry:
        '''select part files based on selection criteria'''
        # print('start filtered_files') # DEBUG
        for folder_path in self.matching_folders():
            # print('start folder "{0}"'.format(type(folder_path))) # DEBUG
            for file_path in self.matching_files(folder_path):
                yield file_path
    # end def filtered_files:

    def matching_files(self, source: posix.DirEntry) -> posix.DirEntry:
        '''sequence through the files that match the selection criteria'''
        # print('matching_files for : {0}'.format(source)) # DEBUG
        for entry in scan_directory_files(source):
            if self.is_matched_file(entry):
                yield entry
    # end def matching_files:

    def is_matched_file(self, offered: posix.DirEntry) -> bool:
        '''choose whether a file should be processed (True) or skipped (False)'''
        # Use the current folder information to inform the choice logic
        return offered.name.endswith(self.criteria['match_suffix'])
    # end def is_matched_file:

    # def __iter__(self):
    #     self.state = "create iter"
    #     self.folder = self.command_arguments.folder
    #     self.limit = 0
    #     return self
    # # end def __iter__:

    # def __next__(self):
    #     '''next'''
    #     for folder_path in self.matching_folders():
    #         print('start folder "{0}"'.format(folder_path))
    #         for file_path in self.matching_files(folder_path):
    #             yield file_path
    # # end def __next:
# end class PartFinder:


def my_main() -> None:
    '''wrapper for test/start code so that variables do not look like constants'''
    print('\n\n') # DEBUG
    # for entry in scan_directory_files('/home/phil/development/fritzing-lint'):
    #     print(entry) # DEBUG
    # for entry in scan_directory_files('./'):
    #     print(entry) # DEBUG
    args = argparse.Namespace()
    args.folder = None
    args.svg = False
    args.part_library = None
    args.pattern = None

    # args.folder = './'
    # args.folder = '/home/phil/Documents/data_files/fritzing-parts/core/'

    args.part_library = '/home/phil/Documents/data_files/fritzing-parts/'

    for part_file in PartFinder(args).filtered_files():
        print(part_file.name)
        # print(part_file.path, part_file.name)

    # print(dir(part_file)) # DEBUG
    # ['__class__', '__delattr__', '__dir__', '__doc__', '__eq__', '__format__', '__fspath__',
    #  '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__',
    #  '__le__', '__lt__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__',
    #  '__setattr__', '__sizeof__', '__str__', '__subclasshook__',
    #  'inode', 'is_dir', 'is_file', 'is_symlink', 'name', 'path', 'stat']
    # for test in PartFinder(args):
    #     print(test)
# end def my_main:

# Standalone module execution
if __name__ == "__main__":
    my_main()

# variables
#   cSpell:words
