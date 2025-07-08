from unittest import TestCase

from memory_fs.file_fs.File_FS import File_FS
from osbot_utils.utils.Dev import pprint

from graph_fs.use_cases.web_pages.Graph_FS__Website__BBC import Graph_FS__Website__BBC


class test_Graph_FS__Website__BBC(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.website_bbc = Graph_FS__Website__BBC()

    def test__init__(self):
        with self.website_bbc as _:
            assert type(_) is Graph_FS__Website__BBC

    def test_create_file_fs_from__bbc_sport(self):
        with self.website_bbc as _:
            file_fs = _.create_file_fs_from__bbc_sport()
            assert type(file_fs) is File_FS

    def test_get__html__bbc__sport(self):
        with self.website_bbc as _:
            html = self.website_bbc.get__html__bbc__sport()
            assert "BBC Sport - Scores, Fixtures" in html