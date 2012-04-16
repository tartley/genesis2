from argparse import Namespace
from io import IOBase
from os.path import join
from unittest import TestCase

from mock import patch, MagicMock

from ..main import (
    create_parser, parse_tags, read_content, transform, update_project,
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
            Namespace()
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
        new_text, changed = transform('aG{name}z', {'name': 'value'})
        self.assertEqual(new_text, 'avaluez')
        self.assertTrue(changed)


    def test_transform_does_nothing_if_no_recognised_tags(self):
        new_text, changed = transform('aG{unrecognised}z', {'name': 'value'})
        self.assertEqual(new_text, 'aG{unrecognised}z')
        self.assertFalse(changed)


    @patch('genesis.main.update_file')
    @patch('genesis.main.os.walk')
    def test_update_project_updates_each_file(
        self, mock_walk, mock_update_file,
    ):
        mock_walk.return_value = [(
            'root',
            [],
            ['file1', 'file2']
        )]
        tags = {}

        update_project(tags, Namespace())

        self.assertEqual(
            mock_update_file.call_args_list,
            [
                ((join('root', 'file1'), tags), {}),
                ((join('root', 'file2'), tags), {}),
            ]
        )


    @patch('genesis.main.rename_dir')
    @patch('genesis.main.os.walk')
    def test_update_template_renames_each_dir(
        self, mock_walk, mock_rename_dir
    ):
        mock_walk.return_value = [(
            'root',
            ['dir1', 'dir2'],
            []
        )]
        tags = {}

        update_project(tags, Namespace())

        self.assertEqual(
            mock_rename_dir.call_args_list,
            [
                ((join('root', 'dir1'), tags), {}),
                ((join('root', 'dir2'), tags), {}),
            ]
        )


    #@patch('genesis.main.replace_dir')
    #@patch('genesis.main.walk')
    #def test_update_template_tells_os_walk_about_updated_dirs(
        #self, mock_walk, mock_replace_dir
    #):
        #mock_replace_dir.side_effect = lambda dirname, _: 'new' + dirname
        #subdirs = ['dir1', 'dir2']
        #mock_walk.return_value = [(
            #'root',
            #subdirs,
            #['file1', 'file2']
        #)]

        #update_template({}, Namespace())

        #self.assertEqual(subdirs, ['newdir1', 'newdir2'])


