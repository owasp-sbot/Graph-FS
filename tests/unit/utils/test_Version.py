import graph_fs
from unittest                      import TestCase
from osbot_utils.utils.Files       import parent_folder, file_name
from graph_fs.utils.Version        import Version, version__graph_fs


class test_Version(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.version = Version()

    def test_path_code_root(self):
        assert self.version.path_code_root() == graph_fs.path

    def test_path_version_file(self):
        with self.version as _:
            assert parent_folder(_.path_version_file()) == graph_fs.path
            assert file_name    (_.path_version_file()) == 'version'

    def test_value(self):
        assert self.version.value() == version__graph_fs