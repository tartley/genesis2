from argparse import ArgumentParser
from os import walk
import sys


def parse_tags(args):
    '''
    Given a list of command line options, return ({tags}, [remaining]), where:
    'tags' is a dict of all the 'name=value' pairs, and 'remaining' is a list
    of all the command line-args
    '''
    tags = {}
    remaining = []
    for arg in args:
        if not arg.startswith('-') and '=' in arg:
            name, value = arg.split('=')
            tags[name] = value
        else:
            remaining.append(arg)
    return tags, remaining


def create_parser():
    return ArgumentParser()


def replace_file(filename, tags):
    pass


def replace_dir(dirname, tags):
    return dirname


def update_template(tags, options):
    for root, subdirs, files in walk('.'):
        subdirs[:] = [
            replace_dir(subdir, tags)
            for subdir in subdirs
        ]
        for filename in files:
            replace_file(filename, tags)

        


def parse_options(parser, args):
    tags, args = parse_tags(args)
    options = parser.parse_args(args)
    return tags, options


def main():
    update_template(*parse_options(create_parser(), sys.argv[1:]))

