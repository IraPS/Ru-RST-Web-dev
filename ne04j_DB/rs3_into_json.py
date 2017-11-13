"""This program allows you to run through the corpus (folder) of files annotated in .rs3 format
and get a folder "corpus_of_ jsons" with json-files of your annotated texts."""
import json
from xmljson import BadgerFish
from xml.etree.ElementTree import fromstring
import os


def create_json(path, file):
    text_name = file.split('.rs3')[0]
    text = open(path + file, 'r', encoding='utf-8').read()
    bf_str = BadgerFish(xml_fromstring=False)
    made_json = json.dumps(bf_str.data(fromstring(text)))
    o = open('./corpus_of_jsons/' + text_name + '.json', 'w')
    o.write(made_json)
    o.close()

for file in os.listdir('./corpus/'):
    if file.endswith('.rs3'):
        create_json('./corpus/', file)