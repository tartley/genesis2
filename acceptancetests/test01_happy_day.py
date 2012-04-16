#!/usr/bin/env python3.2
from os import chdir, getcwd
from os.path import dirname, isdir, join
from shutil import copytree, rmtree
from subprocess import PIPE, Popen
from tempfile import mkdtemp
from unittest import TestCase


TEST_DATA = join(dirname(__file__), 'test_data')


class GenesisTest(TestCase):

    def create_temp_dir(self):
        self.orig_cwd = getcwd()
        self.temp_dir = mkdtemp()
        copytree(
            join(TEST_DATA, 'project'),
            join(self.temp_dir, 'project'),
        )


    def run_process(self, command):
        process = Popen(
            command,
            cwd=join(self.temp_dir, 'project'),
            shell=True,
            stdout=PIPE,
            stderr=PIPE,
        )
        out, err = process.communicate()
        self.assertEqual(process.returncode, 0, err)
        self.assertEqual(err, b'', err)
        self.assertEqual(out, b'')
        return process.returncode, out, err


    def assert_tags_replaced_in_file(self, filename):
        with open(join(self.temp_dir, 'project', filename)) as fp:
            content = fp.read()
        self.assertEqual(content, 'name=myproj\n\n')


    def assert_tags_replaced_in_dirname(self):
        self.assertTrue(isdir('dir-myproj'))


    def test_tags_are_replaced(self):
        self.create_temp_dir()
        try:
            self.run_process('genesis name=myproj')
            self.assert_tags_replaced_in_file('file1')
            self.assert_tags_replaced_in_dirname()
            self.assert_tags_replaced_in_file(join('dir-myproj', 'file2'))
        finally:
            rmtree(self.temp_dir)


