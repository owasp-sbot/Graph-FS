import json
from unittest import TestCase

import graph_fs
from osbot_utils.utils.Misc import str_md5

from osbot_utils.helpers.html.Html__To__Html_Dict import Html__To__Html_Dict, STRING__SCHEMA_TEXT, STRING__SCHEMA_NODES

from osbot_utils.helpers.html.Html_Dict__To__Html import Html_Dict__To__Html

from osbot_utils.helpers.html.schemas.Schema__Html_Document import Schema__Html_Document

from osbot_utils.helpers.html.Html_Document__To__Html_Dict import Html_Document__To__Html_Dict
from osbot_utils.utils.Files                                import file_save, path_combine, load_file
from osbot_utils.utils.Json                                 import json_save, json_save_file_pretty, json_load_file, json_loads, json_file_load
from osbot_utils.helpers.duration.decorators.print_duration import print_duration
from osbot_utils.helpers.html.Html__To__Html_Document       import Html__To__Html_Document
from memory_fs.file_fs.File_FS                              import File_FS
from graph_fs.use_cases.web_pages.Graph_FS__Website__BBC    import Graph_FS__Website__BBC

base_dir      = path_combine(graph_fs.path, '../_data')

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
            with print_duration(action_name='fetch'):
                html = self.website_bbc.get__html__bbc__sport()
                file_save(html, path=path_combine(base_dir, '1) bbc-sports.html'))
            assert "BBC Sport - Scores, Fixtures" in html
            with print_duration(action_name='convert'):
                html_document = Html__To__Html_Document(html=html).convert()
            with print_duration(action_name='save to disk'):
                json_code     = html_document.json()
                json_save_file_pretty(json_code, path=path_combine(base_dir, '2) bbc-sports.json'))
            with print_duration(action_name='save_lines'):
                html_dict = Html__To__Html_Dict(html=html)
                html_dict.convert()
                lines     = "/n".join(html_dict.print(just_return_lines=True))
                file_save(lines, path=path_combine(base_dir, '3) bbc-sports.lines.json'))

    # def test_get__html__bbc__sport_roundtrip(self):
    #     with print_duration(action_name='load from disk'):
    #         json_code     = json_load_file(path='./1.bbc-sports.json')
    #     with print_duration(action_name='convert to html_document'):
    #         html_document = Schema__Html_Document.from_json(json_code)
    #     with print_duration(action_name='convert to html_dict'):
    #         html_dict = Html_Document__To__Html_Dict(html__document=html_document).convert()
    #     with print_duration(action_name='create html'):
    #         html      = Html_Dict__To__Html(html_dict).convert()
            #file_save(html, path='bbc-sports-2.html')

    def test_get__html__bbc__sport__extract_content(self):
        text_elements      = {}
        text_elements__raw = {}
        hash_size          = 10
        captures           = 0
        def capture_text(text):
            nonlocal captures
            hash                     = str_md5(text)[:hash_size]
            text_elements__raw[hash] = text
            text_elements[hash]      = dict(original_text = text,
                                           rating        = None,
                                           new_text      = None)
            captures += 1
            return hash

        def extract_text_nodes(html_dict, max_depth=5):
            #text_nodes = []

            def traverse(node, depth, parent_tag):
                if depth > max_depth:
                    return

                if not isinstance(node, dict):
                    return

                if parent_tag in ['script', 'style']:
                    data = node.get("data", "").strip()
                    if 'window.__INITIAL_DATA__' in data:
                        raw_data = data[len('window.__INITIAL_DATA__')+2: -2].replace('\\"', '"')
                        json_data = json.loads(raw_data)
                        #print(json_data)
                        area = "hierarchical-promo-collection?enableFetchPriority=false&enablePrimaryActions=false&enablePromoTimestamps=true&home=sport&isUk=true&language=en-GB&lazyLoadImages=true&path=%2Fsport&promoAttributionsToSuppress=%5B%22%2Fsport%22%2C%22%2Fsport%2Ffront_page%22%2C%22%2Fsport%2Ffront-page%22%5D&title=Also%20in%20Sport&tracking=%7B%22groupName%22%3A%22Also%20in%20Sport%22%2C%22groupType%22%3A%22hierarchical%20promo%20collection%22%2C%22groupResourceId%22%3A%22urn%3Abbc%3Atipo%3Alist%3A5afd0cb0-f60e-41a5-9e72-829f9715db55%22%2C%22groupPosition%22%3A3%7D&urn=urn%3Abbc%3Atipo%3Alist%3A5afd0cb0-f60e-41a5-9e72-829f9715db55&withContainedPromos=false&withPromoHeadings=true"
                        for area_name, area in json_data.get('data').items():
                        #area_data = json_data.get('data').get(area).get('data')
                            area_data = area.get('data')
                            promos = area_data.get('promos')
                            if promos:
                                for promo in promos:
                                    #promo['contentTitle'] = capture_text(promo['contentTitle'])
                                    promo['headline'] = capture_text(promo.get('headline'))
                                    if promo.get('description'):
                                        promo['description'] = capture_text(promo.get('description'))

                        new_code ='window.__INITIAL_DATA__="' + json.dumps(json_data).replace('"','\\"') +'";'
                        node["data"] = new_code
                        # pprint(json_data.get('page')
                        #                     .get('entry')
                        #                     .get('pageContent')
                        #                     .get('zones'))
                    return  # Skip script tags entirely

                if node.get("type") == STRING__SCHEMA_TEXT:
                    data = node.get("data", "").strip()
                    if data:
                        if parent_tag in ['span', 'p']:
                            #text_nodes.append((parent_tag,data))
                            node['data'] = capture_text(node['data'])

                node_tag = node.get('tag')
                for child in node.get(STRING__SCHEMA_NODES, []):
                    traverse(child, depth + 1, node_tag)

            traverse(html_dict, depth=0, parent_tag=None)
            #return text_nodes
        print()
        html = self.website_bbc.get__html__bbc__sport()
        html_dict = Html__To__Html_Dict(html).convert()
        extract_text_nodes(html_dict, max_depth=35)
        #pprint(all_text_nodes)
        html = Html_Dict__To__Html(html_dict).convert()
        file_save(html, path=path_combine(base_dir, '4) bbc-sports.raw-hashes.html'))
        json_save_file_pretty(text_elements__raw, path=path_combine(base_dir, '5) bbc-sports.text-elements-raw.json'))
        json_save_file_pretty(text_elements, path=path_combine(base_dir, '6) bbc-sports.text-elements.json'))
        print("file saved")

    def test_get__html__bbc__sport_rebuild_from_hashes(self):
        file_hashes           = path_combine(base_dir, '6) bbc-sports.text-elements.json')
        file_html_with_hashes = path_combine(base_dir, '4) bbc-sports.raw-hashes.html'   )
        text_elements         = json_file_load(file_hashes)
        html                  = load_file(file_html_with_hashes)
        for text_hash, text_element in text_elements.items():
            original_text = text_element.get('original_text')
            html          = html.replace(text_hash, original_text)

        file_save(html, path=path_combine(base_dir, '7) bbc-sports.roundtrip-from-hashes.html'))

    def test_get__html__bbc__sport_replace_with_X(self):
        file_hashes           = path_combine(base_dir, '6) bbc-sports.text-elements.json')
        file_html_with_hashes = path_combine(base_dir, '4) bbc-sports.raw-hashes.html'   )
        text_elements         = json_file_load(file_hashes)
        html                  = load_file(file_html_with_hashes)
        for text_hash, text_element in text_elements.items():
            original_text   = text_element.get('original_text')
            text_to_replace = ''.join('x' if c != ' ' else ' ' for c in original_text)
            html            = html.replace(text_hash, text_to_replace)

        file_save(html, path=path_combine(base_dir, '8) bbc-sports.replaced-with-X.html'))


    def test_get__html__bbc__sport_replace_with_positivity_ratings(self):
        file_hashes           = path_combine(base_dir, '9) bbc-sports.text-elements-with-ratings.json')
        file_html_with_hashes = path_combine(base_dir, '4) bbc-sports.raw-hashes.html'   )
        text_elements         = json_file_load(file_hashes)
        html                  = load_file(file_html_with_hashes)
        for text_hash, text_element in text_elements.items():
            original_text   = text_element.get('original_text')
            rating          = str(text_element.get('rating'))
            text_to_replace = ''.join(rating if c != ' ' else ' ' for c in original_text)
            html            = html.replace(text_hash, text_to_replace)

        file_save(html, path=path_combine(base_dir, '10) bbc-sports.replaced-with-ratings.html'))

    def test_get__html__bbc__sport_replace_with_filter(self):
        file_hashes           = path_combine(base_dir, '9) bbc-sports.text-elements-with-ratings.json')
        file_html_with_hashes = path_combine(base_dir, '4) bbc-sports.raw-hashes.html'   )
        text_elements         = json_file_load(file_hashes)
        html                  = load_file(file_html_with_hashes)
        for text_hash, text_element in text_elements.items():
            original_text   = text_element.get('original_text')
            rating          = text_element.get('rating')
            if rating < 0:
                text_to_replace = ''.join('▒' if c != ' ' else ' ' for c in original_text)
            else:
                text_to_replace = original_text
            html            = html.replace(text_hash, text_to_replace)


        file_save(html, path=path_combine(base_dir, '11) bbc-sports.filtered.html'))


    def test_get__html__bbc__sport_replace_only_positivity(self):
        file_hashes           = path_combine(base_dir, '9) bbc-sports.text-elements-with-ratings.json')
        file_html_with_hashes = path_combine(base_dir, '4) bbc-sports.raw-hashes.html'   )
        text_elements         = json_file_load(file_hashes)
        html                  = load_file(file_html_with_hashes)
        for text_hash, text_element in text_elements.items():
            original_text   = text_element.get('original_text')
            rating          = text_element.get('rating')
            if rating < 1:
                text_to_replace = ''.join('▒' if c != ' ' else ' ' for c in original_text)
            else:
                text_to_replace = original_text
            html            = html.replace(text_hash, text_to_replace)


        file_save(html, path=path_combine(base_dir, '12) bbc-sports.only-positive.html'))

