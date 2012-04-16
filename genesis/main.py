from argparse import ArgumentParser
from os import walk
from os.path import join
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

        
def parse_options(parser, args):
    '''
    Parse command line args, returning a dict of name=value tags and an
    argparse.Namespace of command-line options.
    '''
    tags, args = parse_tags(args)
    options = parser.parse_args(args)
    return tags, options


def read_content(filename):
    with open(filename, 'rb') as pointer:
        return pointer.read()


def replace_file(filename, content, tags):
    pass


def update_project(tags, options):
    '''
    Search-and-replace all tags throughout the project
    '''
    for root, subdirs, files in walk('.'):
        for filename in files:
            fullname = join(root, filename)
            replace_file(fullname, read_content(fullname), tags)


def main():
    update_project(*parse_options(create_parser(), sys.argv[1:]))

