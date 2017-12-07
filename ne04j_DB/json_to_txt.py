import json
import re
import os
from pymystem3 import Mystem
from py2neo import Graph
from pandas import DataFrame


def create_real_nodes(data):
    text = str()
    nodes_to_create = dict()
    edus = data['body']['segment']
    for edu in edus:
        nodes_to_create[edu['@id']] = edu['$']
    for node in sorted(nodes_to_create.keys()):
        edu_text = nodes_to_create[node]
        text += edu_text + ' '
    return text

for file in os.listdir('./corpus_of_jsons/'):  # directory with texts in .rs3 format
    if file.endswith('.json'):
        n = file.split('.json')[0]  # text_id value
        print(n)
        data_file = open('./corpus_of_jsons/' + file)
        text_json = json.load(data_file)
        text_json = text_json['rst']  # json root element
        rels = text_json['body']['segment']  # list of json 'segment' elements
        group_rels = text_json['body']['group']  # list of json 'group' elements
        write_text = open('./raw_corpus_texts/' + n + '.txt', 'w', encoding='utf-8')
        text = create_real_nodes(text_json)
        text = re.sub('##### ', '\n', text)
        text = re.sub('\n\n', '\n', text)
        write_text.write(text)
        write_text.close()
