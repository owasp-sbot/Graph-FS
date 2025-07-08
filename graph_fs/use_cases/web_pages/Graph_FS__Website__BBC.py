from memory_fs.file_fs.File_FS import File_FS
from osbot_utils.utils.Http import GET

from osbot_utils.type_safe.Type_Safe import Type_Safe

WEBSITE_URL__BBC__SPORT = "https://www.bbc.co.uk/sport"

class Graph_FS__Website__BBC(Type_Safe):

    def create_file_fs_from__bbc_sport(self):
        return File_FS()

    def get__html__bbc__sport(self):
        return GET(WEBSITE_URL__BBC__SPORT)