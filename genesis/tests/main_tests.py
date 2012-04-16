from argparse import Namespace
from unittest import TestCase

from mock import patch

from ..main import create_parser, parse_tags, replace_dir, update_template


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
            Namespace()
        )


    def test_replace_file_replaces_file_contents(self):
        self.fail()


    def test_replace_dir_returns_unchanged_dir_names(self):
        self.assertEqual(replace_dir('abc', {}), 'abc')


    @patch('genesis.main.replace_file')
    @patch('genesis.main.walk')
    def test_update_template_replaces_each_file(
        self, mock_walk, mock_replace_file
    ):
        mock_walk.return_value = [(
            'root',
            [],
            ['file1', 'file2']
        )]
        tags = {}

        update_template(tags, Namespace())

        self.assertEqual(
            mock_replace_file.call_args_list,
            [(('file1', tags), {}), (('file2', tags), {})]
        )


    @patch('genesis.main.replace_dir')
    @patch('genesis.main.walk')
    def test_update_template_replaces_each_dir(
        self, mock_walk, mock_replace_dir
    ):
        mock_walk.return_value = [(
            'root',
            ['dir1', 'dir2'],
            []
        )]
        tags = {}

        update_template(tags, Namespace())

        self.assertEqual(
            mock_replace_dir.call_args_list,
            [(('dir1', tags), {}), (('dir2', tags), {})]
        )


    @patch('genesis.main.replace_dir')
    @patch('genesis.main.walk')
    def test_update_template_tells_os_walk_about_updated_dirs(
        self, mock_walk, mock_replace_dir
    ):
        mock_replace_dir.side_effect = lambda dirname, _: 'new' + dirname
        subdirs = ['dir1', 'dir2']
        mock_walk.return_value = [(
            'root',
            subdirs,
            ['file1', 'file2']
        )]

        update_template({}, Namespace())

        self.assertEqual(subdirs, ['newdir1', 'newdir2'])


