import json
import re
import os
from pymystem3 import Mystem
from py2neo import Graph

m = Mystem()


def create_real_nodes(data, text_id):
    """This function receives text json ('rst' element)
    and parses json and gets all "real" nodes that correspond to EDUs and NOT groups of EDUs."""
    text_id = str(text_id)
    nodes_to_create = dict()
    edus = data['body']['segment']
    for edu in edus:
        nodes_to_create[edu['@id']] = edu['$']
    neo4j_nodes_command = ''
    punct = list('.,?!%:;[]()"@$&*«»–#,')
    num = list('0123456789')
    for node in sorted(nodes_to_create.keys()):
        edu_text = nodes_to_create[node]
        edu_lemmas = re.sub('[,\.:;!\?\(\)\[\]"@\$&\*«»–#-\+%—]', '', edu_text)
        edu_lemmas = [l for l in m.lemmatize(edu_lemmas) if l not in [' ', ' ', '\n']+punct+num]
        # edu_lemmas = [l for l in edu_lemmas if l.split(' ')[0] not in [' ', '\n']+punct+num]

        # edu_lemmas = ('|'.join(edu_lemmas))
        lemma_pos_dict = '"{'
        for lemma in edu_lemmas:
            # print(lemma)
            lemma_pos_dict += "'" + lemma + "': "
            try:
                lemma_pos_dict += "'" + m.analyze(lemma)[0]['analysis'][0]['gr'].split(',')[0].split('=')[0] + "'"
            except:
                lemma_pos_dict += "'NONE'"
            lemma_pos_dict += ', '
        lemma_pos_dict += '}"'
        # print(lemma_pos_dict)
        neo4j_nodes_command += 'CREATE (edu' + node + ':EDU { Id: ' + node + ", text: '" + edu_text +\
                               "', lemmas: " + lemma_pos_dict + ", Text_id: " + text_id + "})\n"

    print(neo4j_nodes_command)
    graph.run(neo4j_nodes_command)


def create_multi_or_span_rels(relations, text_id):
    """This function creates new grouping nodes for multineclear relations or "span" relations and the
    corresponding relations of these nodes.
    Its input should be a list of json objects of RST-relations between EDUs ('body' 'segment' elements).
    It parses relations that require creating new nodes (span- or group- relations).
    It creates the needed nodes and these relations between them."""
    text_id = str(text_id)
    rels_with_new_nodes = ['span', 'comparison', 'contrast', 'joint', 'restatement', 'same-unit', 'sequence']
    for rel in relations:
        if '@parent' in rel:
            if rel['@relname'] in rels_with_new_nodes:
                # print(rel)
                parent_id = rel['@parent']
                child_id = rel['@id']
                relation = rel['@relname']
                if len(list(graph.run('MERGE (edu' + parent_id + ':EDU {Id: ' + parent_id +
                        ', Text_id:' + text_id + '}) RETURN edu' + parent_id))) == 0:
                    graph.run('CREATE (edu' + parent_id + ':EDU {Id: ' + parent_id + ", Text_id: " + text_id + "})")
                    print('CREATE (edu' + parent_id + ':EDU {Id: ' + parent_id + ", Text_id: " + text_id + "})")
                span_multi_rels_command = 'MERGE (edu' + child_id + ':EDU {Id: ' + child_id + ', Text_id: ' + text_id + '})\n' +\
                             'MERGE (edu' + parent_id + ':EDU {Id: ' + parent_id + ', Text_id: ' + text_id + '})\n' +\
                             'CREATE (edu' + child_id + ')-' + '[r:' + relation + ']->(edu' + parent_id + ')\n'
                span_multi_rels_command = re.sub('same-unit', 'sameunit', span_multi_rels_command)
                span_multi_rels_command = re.sub('cause-effect', 'causeeffect', span_multi_rels_command)
                span_multi_rels_command = re.sub('interpretation-evaluation', 'interpretationevaluation', span_multi_rels_command)
                print(span_multi_rels_command)
                graph.run(span_multi_rels_command)


def create_ordinary_rels(relations, text_id):
    """This function creates ordinary relations between EDUs.
    Its input should be a list of json objects of RST-relations between EDUs (['body']['segment'] elements)."""
    text_id = str(text_id)
    rels_with_new_nodes = ['span', 'comparison', 'contrast', 'joint', 'restatement', 'same-unit', 'sequence']
    rels_to_create = list()
    for rel in relations:
        if '@parent' in rel:
            if rel['@relname'] not in rels_with_new_nodes:
                rels_to_create.append((rel['@id'], rel['@parent'], rel['@relname']))
    for rel in rels_to_create:
        child_id = rel[0]
        parent_id = rel[1]
        relation = rel[2]
        neo4j_rels_command = 'MERGE (edu' + child_id + ':EDU {Id: ' + child_id + ', Text_id: ' + text_id + '})\n' +\
                             'MERGE (edu' + parent_id + ':EDU {Id: ' + parent_id + ', Text_id: ' + text_id + '})\n' +\
                             'CREATE (edu' + child_id + ')-' + '[r:' + relation + ']->(edu' + parent_id + ')\n'
        neo4j_rels_command = re.sub('same-unit', 'sameunit', neo4j_rels_command)
        neo4j_rels_command = re.sub('cause-effect', 'causeeffect', neo4j_rels_command)
        neo4j_rels_command = re.sub('interpretation-evaluation', 'interpretationevaluation', neo4j_rels_command)
        print(neo4j_rels_command)
        graph.run(neo4j_rels_command)


def create_group_relations(group_rels, text_id):
    """This function creates new nodes and relations for relations involving grouped EDUs.
    Its input should be a list of json objects of RST-relations involving grouped EDUs (['body']['group'] elements)."""
    text_id = str(text_id)
    for rel in group_rels:
        if '@parent' in rel:
            parent_id = rel['@parent']
            child_id = rel['@id']
            relation = rel['@relname']
            if len(list(graph.run('MATCH (edu' + parent_id + ':EDU) WHERE edu' + parent_id +
                        '.id = ' + parent_id + ' RETURN edu' + parent_id))) == 0:
                    graph.run('CREATE (edu' + parent_id + ':EDU {Id: ' + parent_id + ", Text_id: " + text_id + "})")
                    print('CREATE (edu' + parent_id + ':EDU {Id: ' + parent_id + ", Text_id: " + text_id + "})")
            group_rels_command = 'MERGE (edu' + child_id + ':EDU {Id: ' + child_id + ', Text_id: ' + text_id + '})\n' +\
                                 'MERGE (edu' + parent_id + ':EDU {Id: ' + parent_id + ', Text_id: ' + text_id + '})\n' +\
                                 'CREATE (edu' + child_id + ')-' +\
                                 '[r:' + relation +']->(edu' + parent_id + ')\n'
            group_rels_command = re.sub('same-unit', 'same_unit', group_rels_command)
            group_rels_command = re.sub('cause-effect', 'cause_effect', group_rels_command)
            group_rels_command = re.sub('interpretation-evaluation', 'interpretation_evaluation', group_rels_command)
            print(group_rels_command)
            graph.run(group_rels_command)


graph = Graph()  # creating a graph for a database

graph.run('MATCH (n) DETACH DELETE n')  # making sure the DB is empty

for file in os.listdir('./corpus_of_jsons_test/'):  # directory with texts in .rs3 format
    if file.endswith('.json'):
        n = file.split('.json')[0] # text_id value
        data_file = open('./corpus_of_jsons_test/' + file)
        text_json = json.load(data_file)
        text_json = text_json['rst']  # json root element
        rels = text_json['body']['segment']  # list of json 'segment' elements
        group_rels = text_json['body']['group']  # list of json 'group' elements

        create_real_nodes(text_json, n)
        create_multi_or_span_rels(rels, n)
        create_ordinary_rels(rels, n)
        create_group_relations(group_rels, n)



