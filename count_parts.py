#!/usr/bin/env python
# coding=utf-8

'''
counting the Fritzing part files in a library or user parts folder structure

explore the code to accurately walk the Fritzing part folder structure
'''

# pipenv shell
# pipenv run pylint count_parts.py

# standard library imports
import os
import posix
from typing import Dict, List, NewType, Callable
import argparse

# local application/library specific imports
from myutilities import ExistingDir

PART_COUNT_VERSION = '0.0.1'
CountDict = NewType('CountDict', Dict[str, int])


def scan_directory_files(
        directory_path: posix.DirEntry,
        processing: Callable[[posix.DirEntry, dict], None],
        data: object) -> None:
    '''execute a function for each file in a directory'''
    with os.scandir(directory_path.path) as directory_files:
        for set_file_spec in directory_files:
            # ?yield? processing(…)
            processing(set_file_spec, directory_path, data)
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


class PartCounter:
    '''count and report part files in the selected directories'''
    PART_FILE_TYPE = ('.fzp')
    IMAGE_FILE_TYPE = ('.svg')
    LIB_DIR_DESC = 'parts library'
    USER_DIR_DESC = 'user parts'
    PLACEHOLDER_NAME = 'placeholder.txt'
    LICENSE_NAME = 'LICENSE.txt'

    def __init__(self, cmd_args: argparse.Namespace):
        '''count and report part files in the selected directories'''
        count_totals = self.empty_part_folder_counts()
        user_counts = None
        self.command_arguments = cmd_args
        self._report_folder_processing(cmd_args.parts_library, self.LIB_DIR_DESC)
        lib_counts = self.count_nested_parts('parts_library')
        if cmd_args.user is not None:
            self.accumulate_count_fields(count_totals, lib_counts)
            self._report_folder_processing(cmd_args.user, self.USER_DIR_DESC)
            user_counts = self.count_nested_parts('user')
            self.accumulate_count_fields(count_totals, user_counts)
            self._report_parts_grand_totals(count_totals)
    # end def __init__:

    def _report_folder_processing(self, folder: str, description: str) -> None:
        '''Show information about the folder to be processed depending on verbosity setting'''
        if self.command_arguments.verbose > 1:
            print('processing {0} folder "{1}"'.format(description, folder))
        elif self.command_arguments.verbose > 0:
            print('processing {0}'.format(description))
    # end def _report_folder_processing:

    def _report_counted_content(
            self, report_formats: List[str], counts: CountDict, folder: posix.DirEntry) -> None:
        '''show information about collected counts using passed format strings and cli verbosity'''
        target_format_index = min(self.command_arguments.verbose, len(report_formats) - 1)
        while target_format_index > 0 and not report_formats[target_format_index]:
            target_format_index -= 1
        counts_fmt = report_formats[target_format_index]
        if counts_fmt:
            if folder is None:
                print(counts_fmt.format(**counts))
            else:
                print(counts_fmt.format(folder.name, **counts))
    # end def _report_counted_content:

    def _report_single_folder_content(self, counts: CountDict, folder: posix.DirEntry) -> None:
        '''show information about the contents of the part folder'''
        verbosity_formats = [
            "",
            '"{0}" {parts} parts',
            '"{0}" Parts: {parts}, Dirs: {dirs}, Other: {other}, Weird: {weird}',
            '"{0}" Parts: {parts}, Dirs: {dirs}, Other: {other}, ' \
            'Weird: {weird} in folder {source[name]}'
        ]
        self._report_counted_content(verbosity_formats, counts, folder)
    # end def _report_single_folder_content:

    def _report_source_image_counts(self, counts: CountDict, folder: posix.DirEntry) -> None:
        '''show information about part images from a single source (folder)'''
        counts_fmt_base = 'Breadboard = {breadboard}, Schematic = {schematic}, PCB = {pcb}, ' \
            'Icon = {icon}'
        verbosity_formats = [
            "",
            '"{0}" ' + counts_fmt_base,
            '"{0}" Images: ' + counts_fmt_base,
            '"{0}" Images: ' + counts_fmt_base + ', Dirs: {dirs}, Other: {other}, Weird: {weird}'
        ]
        self._report_counted_content(verbosity_formats, counts, folder)
    # end def _report_source_image_counts:

    def _report_part_set_images(self, counts: CountDict, folder: posix.DirEntry) -> None:
        counts_fmt_base = 'Breadboard = {breadboard}, Schematic = {schematic}, PCB = {pcb}, ' \
            'Icon = {icon}'
        verbosity_formats = [
            'Total images: ' + counts_fmt_base,
            'Total images: ' + counts_fmt_base + ', Dirs: {dirs}, Other: {other}, Weird: {weird}'
        ]
        self._report_counted_content(verbosity_formats, counts, folder)
    # end def _report_part_set_images:

    def _report_root_folder_content(self, counts: CountDict) -> None:
        '''show information about the root part folder contents'''
        verbosity_formats = [
            'Total Parts = {parts}',
            'Total: Parts: {parts}, Dirs: {dirs}, Other: {other}, Weird: {weird}'
        ]
        self._report_counted_content(verbosity_formats, counts, None)
    # end def _report_root_folder_content:

    def _report_parts_grand_totals(self, counts: CountDict) -> None:
        '''show the grand total information from the counting run'''
        verbosity_formats = [
            'Grand Total Parts = {parts}',
            'Grand Total Parts = {parts}, Dirs: {dirs}, Other: {other}, Weird: {weird}'
        ]
        self._report_counted_content(verbosity_formats, counts, None)
    # end def _report_parts_grand_totals:

    def _report_dir_file_details(self, file: posix.DirEntry, folder: posix.DirEntry) -> None:
        '''show information about a directory file found with parts'''
        if self.command_arguments.exceptions: # hpd full verbosity only
            print('directory "{0}" found in {1} folder'.format(file.name, folder.path))
    # end def _report_dir_file_details:

    def _report_weird_file_details(self, file: posix.DirEntry, folder: posix.DirEntry) -> None:
        '''show information about a weird (type of) file found with parts'''
        raise NotImplementedError('_report_weird_file_details method not written yet')
        # higher verbosity (? or exception?) levels show stat information about the file
    # end def _report_weird_file_details:

    def _report_part_other_file_details(
            self, other_file: posix.DirEntry, folder: posix.DirEntry) -> None:
        '''show information about a non-part file in parts folder'''
        if other_file.name != self.PLACEHOLDER_NAME and self.command_arguments.exceptions:
            if self.command_arguments.verbose > 0:
                print('other file "{0}" found in {1} parts folder'.format(
                    other_file.name, folder.name))
            else:
                print('other file "{0}" found in parts folder'.format(other_file.name))
    # end def _report_part_other_file_details:

    def _report_image_other_file_details(
            self, other_file: posix.DirEntry, folder: posix.DirEntry) -> None:
        '''show information about a non-image file in an image view folder'''
        if other_file.name != self.LICENSE_NAME \
                and other_file.name != self.PLACEHOLDER_NAME \
                and self.command_arguments.exceptions:
            if self.command_arguments.verbose > 0:
                print('other file "{0}" found in {1} image folder'.format(
                    other_file.name, folder.name))
            else:
                print('other file "{0}" found in image folder'.format(other_file.name))
    # end def _report_image_other_file_details:

    @staticmethod
    def _report_image_definition_mismatch(def_folders: List[str], img_folders: List[str]) -> None:
        '''report information about folders to hold part definitions and images that do not match'''
        # should be an image category sub folder in svg for each part category in set
        for name in def_folders:
            if name not in img_folders:
                print('No svg folder associated with {0} parts'.format(name))
        # should be a part category folder for each image category subfolder in set
        for name in img_folders:
            if name not in def_folders:
                print('Found svg folder for {0} parts, but no {0} part definitions'.format(name))
    # end def _report_image_definition_mismatch:

    # def count_nested_parts(self, folders: list) -> dict:
    def count_nested_parts(self, arg_key: str) -> Dict[str, int]:
        '''Count the number of Fritzing part definition files in each folder'''
        folders = getattr(self.command_arguments, arg_key + "_sub")
        count_totals = self.empty_part_folder_counts()
        part_sub_folders = []
        for one_folder in folders:
            part_sub_folders.append(one_folder.name)
            counts = self.count_folder_parts(one_folder)
            self._report_single_folder_content(counts, one_folder)
            self.accumulate_count_fields(count_totals, counts)
        if self.command_arguments.svg:
            self.count_images_for_parts(arg_key, part_sub_folders)
        self._report_root_folder_content(count_totals)
        return count_totals
    # end def count_nested_parts:

    def count_images_for_parts(self, arg_key: str, part_folders: List[str]) -> Dict[str, int]:
        '''Count the number of svg image files useable for parts'''
        folders = getattr(self.command_arguments, arg_key + "_svg")
        if folders:
            counts = self.count_part_set_images(folders[0], part_folders)
            self._report_part_set_images(counts, folders[0])
        else:
            print('no svg folder found in {0}'.format(getattr(self.command_arguments, arg_key)))
    # end def count_images_for_parts:

    def count_part_set_images(
            self, svg_root: posix.DirEntry, part_folders: List[str]) -> Dict[str, int]:
        '''count svg image files associated with a set (library) of part files'''
        context_data = {
            'svg_part_sets': [],
            'root_svg_counts': self.empty_image_folder_counts(),
            'svg_root': svg_root
        }
        scan_directory_files(svg_root, self.process_part_set_source_folders, context_data)
        self._report_image_definition_mismatch(part_folders, context_data['svg_part_sets'])
        return context_data['root_svg_counts']
    # end def count_part_set_images:

    def process_part_set_source_folders(
            self, source_file_spec: posix.DirEntry,
            set_root_folder: posix.DirEntry,
            context_data: dict) -> None:
        '''process image view folders in a single part source folder'''
        if source_file_spec.is_dir():
            if source_file_spec.name in PartsLibraryDir.SUB_PART_FOLDERS:
                context_data['svg_part_sets'].append(source_file_spec.name)
                set_counts = self.count_part_source_images(source_file_spec)
                self.accumulate_count_fields(context_data['root_svg_counts'], set_counts)
            else: # unexpected directory name for parts svg
                context_data['root_svg_counts']['dirs'] += 1
                self._report_dir_file_details(source_file_spec, set_root_folder)
        elif source_file_spec.is_file():
            context_data['root_svg_counts']['other'] += 1
            self._report_image_other_file_details(source_file_spec, set_root_folder)
        else:
            context_data['root_svg_counts']['weird'] += 1
    # end def process_part_set_set_root_folders:

    def count_part_source_images(self, source_folder: posix.DirEntry) -> Dict[str, int]:
        '''count the image files for a part (definition) set'''
        context_data = {
            'total_counts': self.empty_image_folder_counts(),
            'source_counts': self.empty_image_folder_counts()
        }
        scan_directory_files(source_folder, self.process_part_source_view_folders, context_data)
        self._report_source_image_counts(context_data['total_counts'], source_folder)
        self.accumulate_count_fields(context_data['total_counts'], context_data['source_counts'])
        return context_data['total_counts']
    # end def count_part_source_images:

    def process_part_source_view_folders(
            self, view_file_spec: posix.DirEntry,
            source_folder: posix.DirEntry,
            context_data: dict) -> None:
        '''process image view folders in a single part source folder'''
        if view_file_spec.is_dir():
            if view_file_spec.name in PartsLibraryDir.SVG_VIEW_FOLDERS:
                view_counts = self.count_view_images(view_file_spec)
                self.accumulate_count_fields(context_data['total_counts'], view_counts)
            else:
                context_data['source_counts']['dirs'] += 1
                self._report_dir_file_details(view_file_spec, source_folder)
        elif view_file_spec.is_file():
            context_data['source_counts']['other'] += 1
            self._report_image_other_file_details(view_file_spec, source_folder)
        else:
            context_data['source_counts']['weird'] += 1
    # end def process_part_source_view_folders:

    def count_view_images(self, view_folder: posix.DirEntry) -> dict:
        '''count the part image files for a single view folder'''
        raw_counts = self.empty_image_folder_counts()
        scan_directory_files(view_folder, self.process_view_image_folder, raw_counts)
        raw_counts['source'] = {
            'path': view_folder.path,
            'name': view_folder.name
        }
        return raw_counts
    # end def count_view_images:

    def process_view_image_folder(
            self, image_file: posix.DirEntry,
            view_folder: posix.DirEntry,
            raw_counts: Dict[str, int]) -> None:
        '''process a file found in an svg view specific folder'''
        if image_file.is_dir():
            raw_counts['dirs'] += 1
            self._report_dir_file_details(image_file, view_folder)
        elif not image_file.is_file():
            raw_counts['weird'] += 1
            self._report_weird_file_details(image_file, view_folder)
        elif image_file.name.endswith(PartCounter.IMAGE_FILE_TYPE):
            raw_counts[view_folder.name] += 1
        else:
            raw_counts['other'] += 1
            self._report_image_other_file_details(image_file, view_folder)
    # end def process_view_image_folder:

    def count_folder_parts(self, parts_folder: posix.DirEntry) -> dict:
        '''Count the number of Fritzing part definition files in a folder'''
        raw_counts = self.empty_part_folder_counts()
        with os.scandir(parts_folder.path) as parts:
            for part_file in parts:
                if part_file.is_dir():
                    raw_counts['dirs'] += 1
                    self._report_dir_file_details(part_file, parts_folder)
                elif not part_file.is_file():
                    raw_counts['weird'] += 1
                    self._report_weird_file_details(part_file, parts_folder)
                elif part_file.name.endswith(PartCounter.PART_FILE_TYPE):
                    raw_counts['parts'] += 1
                else:
                    raw_counts['other'] += 1
                    self._report_part_other_file_details(part_file, parts_folder)
        raw_counts['source'] = {
            'path': parts_folder.path,
            'name': parts_folder.name
        }
        return raw_counts
    # end def count_folder_parts:

    @staticmethod
    def accumulate_count_fields(target: dict, source: dict) -> None:
        '''update count attributes in target with those in source'''
        for count in target.keys():
            target[count] += source[count]
    # end def accumulate_count_fields:

    @staticmethod
    def empty_part_folder_counts() -> Dict[str, int]:
        '''create a safe to modify copy of an empty set of counts'''
        return dict({
            'parts': 0,
            'dirs': 0,
            'other': 0,
            'weird': 0
        })
    # end def empty_part_folder_counts:

    @staticmethod
    def empty_image_folder_counts() -> Dict[str, int]:
        '''create a safe to modify copy of an empty set of counts'''
        return dict({
            'breadboard': 0,
            'icon': 0,
            'pcb': 0,
            'schematic': 0,
            'dirs': 0,
            'other': 0,
            'weird': 0
        })
    # end def empty_image_folder_counts:
# end class PartCounter:


class PartsLibraryDir(argparse.Action):
    '''verify passed argument is a path to a Fritzing Parts Library directory'''
    # pylint: disable=too-few-public-methods
    SUB_PART_FOLDERS = ('contrib', 'core', 'obsolete', 'user')
    SUB_IMAGE_FOLDER = 'svg'
    SVG_VIEW_FOLDERS = ('breadboard', 'icon', 'pcb', 'schematic')

    def __call__(
            self, parser: argparse.ArgumentParser, namespace: argparse.Namespace,
            src_path: str, option_string: str = None) -> None:
        '''verify that the path references a Fritzing Parts Library folder'''
        # start by making sure that the source is actually an existing directory
        ex_dir = ExistingDir(
            self.option_strings, self.dest, self.nargs, self.const,
            self.default, self.choices, self.required, self.help, self.metavar)
        ex_dir(parser, namespace, src_path, option_string)
        # have path to an existing directory: is it a parts library?
        self._find_child_folders(namespace)
    # end def __call__()

    def _find_child_folders(self, namespace: argparse.Namespace) -> None:
        '''determine if the directory is likely to be a Fritzing Parts Library'''
        # match_count = 0
        # part_folders = []
        # svg_folders = []
        namespace_path = getattr(namespace, self.dest)
        if namespace_path is None:
            return
        context_data = {
            'part_folders': [],
            'svg_folders': [],
            'match_count': 0
        }
        root_path = PseudoDirEntry('root', namespace_path)
        scan_directory_files(root_path, self._process_possible_parts_library, context_data)
        if context_data['match_count'] < 1:
            msg = "%r does not contain Fritzing part information " % root_path
            raise argparse.ArgumentError(self, msg)
        setattr(namespace, self.dest + '_sub', context_data['part_folders'])
        setattr(namespace, self.dest + '_svg', context_data['svg_folders'])
    # end def _find_child_folders:

    def _process_possible_parts_library(
            self, file_spec: posix.DirEntry,
            _source_folder: posix.DirEntry,
            context_data: dict) -> None:
        '''check if a file is the name of a folder matches a Fritzing parts source'''
        if file_spec.is_dir():
            if file_spec.name in self.SUB_PART_FOLDERS:
                context_data['match_count'] += 1
                context_data['part_folders'].append(file_spec) # save detected child folders
            if file_spec.name == self.SUB_IMAGE_FOLDER:
                context_data['svg_folders'].append(file_spec)
# end class PartsLibraryDir:


class CommandLineParser:
    '''handle command line argument parsing'''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        self.parser = CommandLineParser.build_parser()
        self.command_arguments = self.parser.parse_args()

    @staticmethod
    def build_parser() -> argparse.ArgumentParser:
        '''create command line argument parser'''
        parser = argparse.ArgumentParser(description='Fritzing part counter')
        parser.add_argument('--version', action='version',
                            version='%(prog)s ' + PART_COUNT_VERSION)
        parser.add_argument('-u', '--user', metavar='user-parts',
                            action=PartsLibraryDir, # action=ExistingDir,
                            help='path to folder containing user parts')
        parser.add_argument('parts_library', metavar='Part Library',
                            action=PartsLibraryDir, default='./',
                            help='path to top folder for Fritzing Parts library')
        parser.add_argument('-v', '--verbose', action='count', default=0,
                            help='increase verbosity')
        parser.add_argument('-e', '--exceptions', action='store_true',
                            help='report exceptions while counting')
        parser.add_argument('-s', '--svg', action='store_true',
                            help='report svg image file counts')
        return parser
    # end def build_parser:
# end class CommandLineParser:


def my_main() -> None:
    '''wrapper for test/start code so that variables do not look like constants'''
    cli_parser = CommandLineParser()
    PartCounter(cli_parser.command_arguments)
# end def my_main:

# Standalone module execution
if __name__ == "__main__":
    my_main()

# variables
#   cSpell:words
