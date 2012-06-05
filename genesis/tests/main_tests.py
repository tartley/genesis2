from argparse import Namespace
from io import IOBase
from os.path import join
from textwrap import dedent
from unittest import TestCase

from mock import call, MagicMock, Mock, patch

from .. import __version__
from ..main import (
    create_parser, parse_tags, read_content, rename_dir, transform,
    update_project,
)


class MainTest(TestCase):

    def test_parse_tags_extracts_name_value_pairs(self):
        self.assertEqual(
            parse_tags(['name=value', 'aaa=bbb']),
            ({'name': 'value', 'aaa':'bbb'}, [])
        )

    def test_parse_tags_preserves_remaining_args(self):
        self.assertEqual(
            parse_tags(['--aaa=123', '-b', 'ccc']),
            ({}, ['--aaa=123', '-b', 'ccc'])
        )

    def test_parse_tags_preserves_arg_space_value(self):
        self.assertEqual(
            parse_tags(['--option', 'value']),
            ({}, ['--option', 'value'])
        )


    def test_create_parser(self):
        self.assertEqual(
            create_parser().parse_args([]),
            Namespace(target='.')
        )

    def test_create_parser_handles_target(self):
        self.assertEqual(
            create_parser().parse_args(['target']),
            Namespace(target='target')
        )

    @patch('sys.stderr', Mock())
    def test_create_parser_errors_on_two_targets(self):
        with self.assertRaises(SystemExit):
            create_parser().parse_args(['t1', 't2'])

    @patch('sys.stdout')
    def test_create_parser_handles_help(self, mock_stdout):
        EXPECTED_HELP_TEXT = dedent("""\
        usage: python -m unittest [-h] [--version] [target]
        
        positional arguments:
          target
          
        optional arguments:
          -h, --help  show this help message and exit
          --version   show program's version number and exit
        """)
        with self.assertRaises(SystemExit):
            create_parser().parse_args(['--help'])

        self.assertEqual(mock_stdout.write.call_args[0][0], EXPECTED_HELP_TEXT)

    @patch('sys.stderr')
    def test_create_parser_handles_version(self, mock_stderr):
        with self.assertRaises(SystemExit):
            create_parser().parse_args(['--version'])

        self.assertEqual(
            mock_stderr.write.call_args,
            call('Genesis v{}\n'.format(__version__))
        )


    @patch('genesis.main.open', create=True)
    def test_read_content(self, mock_open):
        mock_open.return_value = MagicMock(spec=IOBase)

        content = read_content('filename')

        self.assertEqual(
            content,
            mock_open.return_value.__enter__.return_value.read.return_value
        )


    def test_transform_replaces_tags(self):
        new_text, changed = transform('aG{name}c', {'name': 'b'})
        self.assertEqual(new_text, 'abc')
        self.assertTrue(changed)


    def test_transform_does_nothing_to_recognised_tags(self):
        new_text, changed = transform('aG{unrecognised}z', {'name': 'value'})
        self.assertEqual(new_text, 'aG{unrecognised}z')
        self.assertFalse(changed)


    @patch('genesis.main.os.rename')
    def test_rename_dir(self, mock_rename):

        new_dirname = rename_dir('root', 'dirG{name}', {'name':'newname'})

        self.assertEqual(new_dirname, 'dirnewname')
        self.assertEqual(
            mock_rename.call_args,
            call('root/dirG{name}', 'root/dirnewname')
        )


    @patch('genesis.main.os.rename')
    def test_rename_dir_does_nothing_if_no_known_tags_in_dirname(self, mock_rename):

        new_dirname = rename_dir('root', 'dirG{name}', {})

        self.assertEqual(new_dirname, 'dirG{name}')
        self.assertIsNone(mock_rename.call_args)


    @patch('genesis.main.update_file')
    @patch('genesis.main.os.walk')
    def test_update_project_updates_each_file(
        self, mock_walk, mock_update_file,
    ):
        mock_walk.return_value = [('root', [], ['file1', 'file2'])]
        tags = {}

        update_project(tags, Namespace(target='.'))

        self.assertEqual(
            mock_update_file.call_args_list,
            [
                ((join('root', 'file1'), tags), {}),
                ((join('root', 'file2'), tags), {}),
            ]
        )


    @patch('genesis.main.rename_dir')
    @patch('genesis.main.os.walk')
    def test_update_project_renames_each_dir(
        self, mock_walk, mock_rename_dir
    ):
        mock_walk.return_value = [('root', ['dir1', 'dir2'], [])]
        tags = {}

        update_project(tags, Namespace(target='.'))

        self.assertEqual(
            mock_rename_dir.call_args_list,
            [
                (('root', 'dir1', tags), {}),
                (('root', 'dir2', tags), {}),
            ]
        )


    @patch('genesis.main.rename_dir')
    @patch('genesis.main.os.walk')
    def test_update_project_tells_os_walk_about_updated_dirs(
        self, mock_walk, mock_rename_dir
    ):
        mock_rename_dir.side_effect = lambda _, dirname, __:\
            dirname.replace('dir', 'newdir')
        subdirs = ['dir1', 'dir2']
        mock_walk.return_value = [('root', subdirs, [])]

        update_project({}, Namespace(target='.'))

        self.assertEqual(subdirs, ['newdir1', 'newdir2'])

