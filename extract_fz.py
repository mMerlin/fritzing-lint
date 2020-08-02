#!/usr/bin/env python
# coding=utf-8

'''
exploring zip file processing in Fritzing sketch context
'''

# pipenv shell
# pipenv run pylint extract_fz.py

# standard library imports
# import os
# import sys

# related third party imports
# import tkinter.filedialog as tkf

# local application/library specific imports
import argparse
# from myutilities import ExistingDir
from myutilities import smart_filehandle
# from commontools import constant

FILE_CATALOG_VERSION = '0.0.1'
ERROR_INVALID_NAME = 123
LINK_NEST_LIMIT = 5


# class «ClassName»:
# class «ClassName»(«ParentClass»):
class FzExtractor:
    '''Get fx (xml) sketch from fzz wrapper'''
    @classmethod
    def __init__(cls):
        pass

    # def «name_of_method»(self, «[argument«: «type»»[, …]»):
    def class_method(self):
        '''method docstring'''
        raise NotImplementedError('class_method method not written yet')
        # pass

    @staticmethod
    def class_method2():
        '''method docstring'''
        raise NotImplementedError('static class_method2 method not written yet')
        # pass


def mymain():
    '''wrapper for test/start code so that variables do not look like constants'''
    instance = FzExtractor()
    instance.class_method()


class CommandLineParser:
    '''handled command line argument parsing'''
    # pylint: disable=too-few-public-methods
    def __init__(self):
        print("CommandLineParser.__init__ start")  # TRACE
        arg_parser = CommandLineParser.build_parser()
        cmd_args = arg_parser.parse_args()
        print(cmd_args)  #  DEBUG
        if cmd_args.file is not None:
            print('reading from %r' % cmd_args.file)
            # print(cmd_args.file)  # DEBUG
            print(cmd_args.file.name)  # DEBUG
            with smart_filehandle(cmd_args.file) as in_fh:
                print(in_fh.read())
            # print(cmd_args.file)  # DEBUG
            # print(cmd_args.file.read())
        self.parser = arg_parser

    @staticmethod
    def build_parser():
        """create parser"""
        # print("CommandLineParser.build_parser start")  # TRACE
        parser = argparse.ArgumentParser(description='Fritzing Sketch file data extraction.')
        parser.add_argument('-v', '--version', action='version',
                            version='%(prog)s ' + FILE_CATALOG_VERSION)
        parser.add_argument('-f', '--file', metavar='File',
                            type=argparse.FileType('r', encoding='UTF-8'),
                            help='input file to test smart file handle')
        # print("CommandLineParser.build_parser end")  # DEBUG
        # https://docs.python.org/3/library/argparse.html#action class FooAction
        # parser.add_argument('root2', metavar='Root2',
        #                     action=)
        # https://stackoverflow.com/questions/27433316/
        # how-to-get-argparse-to-read-arguments-from-a-file-with-an-option-rather-than-pre
        # https://stackoverflow.com/questions/11415570/directory-path-types-with-argparse
        return parser

# end class CommandLineParser:

# Standalone module execution
if __name__ == "__main__":
    mymain()

# variables
#   cSpell:words
