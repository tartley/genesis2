from argparse import ArgumentParser
import os
from os.path import join
import re
import sys

from .version import __version__

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
    parser = ArgumentParser()
    parser.add_argument('--version',
        action='version', version='%(prog)s v' + __version__)
    return parser


def parse_options(parser, args):
    '''
    Parse command line args, returning a dict of name=value tags and an
    argparse.Namespace of command-line options.
    '''
    tags, args = parse_tags(args)
    options = parser.parse_args(args)
    return tags, options


def read_content(filename):
    '''
    Return the content of the given filename
    '''
    with open(filename) as pointer:
        return pointer.read()


def transform(text, tags):
    '''
    Given a body of text, replace all instances of 'G{xxx}' with the value
    of tags[xxx]. Return a tuple of the result and a boolean which is True
    if any changes were made.
    '''
    regex = re.compile('G\{(.+?)\}')
    changed = [False]

    def replace_tag(match):
        name = match.group(1)
        if name in tags:
            changed[0] = True
            return tags[name]
        return match.group(0)

    return regex.sub(replace_tag, text), changed[0]


def replace_file(filename, new_filename, content):
    '''
    Given a filename, a modified filename, and new file content,
    replace the existing file with the new content, safely.
    '''
    backup = filename + '.backup'
    os.rename(filename, backup)
    with open(new_filename, 'w') as pointer:
        pointer.write(content)
    os.remove(backup)


def update_file(filename, tags):
    try:
        content = read_content(filename)
        new_content, content_changed = transform(content, tags)
    except UnicodeDecodeError:
        # don't attempt to replace tags in binary files
        content_changed = False

    new_filename, filename_changed = transform(filename, tags)
    if content_changed:
        replace_file(filename, filename, new_content)
    elif filename_changed:
        os.rename(filename, new_filename)


def rename_dir(dirname, tags):
    new_name, changed = transform(dirname, tags)
    if changed:
        os.rename(dirname, new_name)
        return new_name
    return dirname


def update_project(tags, options):
    '''
    Search-and-replace all tags throughout the project
    '''
    for root, subdirs, files in os.walk('.'):
        for filename in files:
            update_file(join(root, filename), tags)
        subdirs[:] = [
            rename_dir(join(root, dirname), tags)
            for dirname in subdirs
        ]


def main():
    update_project(*parse_options(create_parser(), sys.argv[1:]))

