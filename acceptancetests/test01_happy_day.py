#!/usr/bin/env python3.2
from os import chdir, getcwd, listdir
from os.path import dirname, isdir, join
from shutil import copytree, rmtree
from subprocess import PIPE, Popen
from tempfile import mkdtemp
from unittest import TestCase
from contextlib import contextmanager


TEST_DATA = join(dirname(__file__), 'test_data')


@contextmanager
def create_temp_dir():
    temp_dir = mkdtemp()
    yield temp_dir
    rmtree(temp_dir)


@contextmanager
def cd(dest):
    orig = getcwd()
    chdir(dest)
    yield
    chdir(orig)


@contextmanager
def create_test_project(projname):
    with create_temp_dir() as temp_dir:
        project_dir = join(temp_dir, projname)
        copytree(join(TEST_DATA, 'project'), project_dir)
        with cd(temp_dir):
            yield project_dir


class GenesisTest(TestCase):

    def run_process(self, command, cwd):
        process = Popen(
            command,
            shell=True,
            cwd=cwd,
            stdout=PIPE,
            stderr=PIPE,
        )
        out, err = process.communicate()
        self.assertEqual(
            process.returncode, 0,
                '\n' + err.decode('unicode_escape') +
                '\n' + out.decode('unicode_escape'))
        self.assertEqual(err, b'', '\n' + err.decode('unicode_escape'))
        self.assertEqual(out, b'')


    def assert_tags_replaced_in_file(self, filename):
        with open(filename) as fp:
            content = fp.read()
        self.assertEqual(content, 'name=myproj\n\n')


    def assert_tags_replaced_in_dirname(self, project_dir):
        self.assertIn('dir-myproj', listdir(project_dir))
        self.assertTrue(isdir(join(project_dir, 'dir-myproj')))


    def test_tags_are_replaced(self):
        with create_test_project('project') as project_dir:
            self.run_process('genesis name=myproj', project_dir)
            self.assert_tags_replaced_in_file(join(project_dir, 'file1'))
            self.assert_tags_replaced_in_dirname(project_dir)
            self.assert_tags_replaced_in_file(
                join(project_dir, 'dir-myproj', 'file2'))

