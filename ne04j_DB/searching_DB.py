from py2neo import Graph
import itertools
import operator
import re

graph = Graph()  # creating a graph for a database

# кажддый "реальный" node имеет "Id", "Text_id", "text", "lemmas". Т.е. достаточно проверить, есть ли у node "text",
# если есть, по нему можно искать. Если нет - то это фиктивный node, который появился в результате объединения ЭДЕ.

# nodes = graph.find('EDU')
# real_edus = [node for node in nodes if 'text' in node]


def search_edus(parameter, value):
    found = None
    if parameter == 'word':
        found = graph.run("MATCH (n) WHERE '" + value + "' in split(n.text, ' ')\n RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'lemma':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'pos':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    # print([n for n in found if n[0] == 20], '\n\n')
    if found:
        found.sort(key=operator.itemgetter(0))
        found_by_text = itertools.groupby(found, lambda x: x[0])
        found = found_by_text
    return found

# search_result = search_edus('lemma', 'как')

real_query = '{"data":[{"type":"word","searched_for":"и","ro":["any"],"add_type":"next_edu_and"},' \
    '{"type":"word","searched_for":"и","ro":["any"],"add_type":"next_edu_and"},' \
             '{"type":"word","searched_for":"и","ro":["any"],"add_type":"none"}]}'


def parse_query(query):
    query = eval(query)
    query = query['data']
    new_edu_indices = [i+1 for i, _ in enumerate(query) if _['add_type'] == 'next_edu_and']
    slices = list()
    start = 0
    for i in new_edu_indices:
        end = i
        slices.append(query[start:end])
        start = i
    slices.append(query[start::])
    return slices


def create_DB_requests(query):
    requests = list()
    conditions = {'same_edu_and': 'AND', 'same_edu_or': 'OR', 'next_edu_and': '', 'none': ''}
    parsed_query = parse_query(query)
    # print(parsed_query)
    for i in parsed_query:

        request = str()
        request += 'MATCH (n)\nWHERE'

        if len(i) > 1:
            for el in i:
                cond = conditions[el['add_type']]
                if el['type'] == 'word':
                    request += " '{0}' IN split(n.text, ' ') {1}".format(el['searched_for'], cond)
                else:
                    request += ' n.lemmas CONTAINS "\'{0}\'" {1}'.format(el['searched_for'], cond)

        else:
            el = i[0]
            if el['type'] == 'word':
                request += " '{0}' IN split(n.text, ' ')".format(el['searched_for'])
            else:
                request += ' n.lemmas CONTAINS "\'{0}\'"'.format(el['searched_for'])

        request += "\nRETURN n.Text_id, n.Id, n.text"

        requests.append(request)

    '''
    i = 0
    while i < len(requests):
        found1 = graph.run(requests[i])
        found1 = [[n[0], n[1], n[2]] for n in found1]
    '''

    return requests

'''
for i in create_DB_requests(real_query):
    print(i)
    # print(len(create_DB_requests(real_query)), 'edus to search.\n')
    found = graph.run(i)
    found = [[n[0], n[1], n[2]] for n in found]
    found.sort(key=operator.itemgetter(0))
    found_by_text = itertools.groupby(found, lambda x: x[0])
    found = found_by_text
    for i, l in found_by_text:
        print(i, list(l))
        print('\n')
'''


def get_found(DB_requests):
    all_found = list()
    for i in DB_requests:
        found = graph.run(i)
        found = [[n[0], n[1], n[2]] for n in found]
        all_found.append(found)
    return all_found


def process_multi_edus_search(all_found):
    all_ids = list()
    for i in all_found:
        ids = [n[0] for n in i]
        all_ids.append(ids)
    num_of_edus = len(all_found)
    compare = all_ids[0]
    for n in range(num_of_edus - 1):
        a = all_ids[n+1]
        out = [x for x in compare if x in a]
        compare = out
        n += 1
    out = set(out)

    all_text_edus = list()
    for q in all_found:
        request_edus = dict()
        for i in out:
            text_edus = list()
            for k in q:
                if k[0] == i:
                    text_edus.append(k)
            request_edus[i] = text_edus

        all_text_edus.append(request_edus)


    all_text_edus_filtred = list()

    '''
    for text in all_text_edus:
        text_edus_filtered = list()
        start_edu = text[0]
        for edu in text[0::]:
            if edu[1] == start_edu[1] + 1:
                text_edus_filtered.append(start_edu)
                text_edus_filtered.append(edu)
            start_edu = edu
        all_text_edus_filtred.append(text_edus_filtered)
    '''

    return out, all_text_edus


def find_seq(texts_ids, result):
    text_result = dict()
    for i in texts_ids:
        texts_results = {i: [n[i] for n in result]}
        for text in texts_results.keys():
            text_result[text] = []
            res = ''
            queries = texts_results[text]
            first_q = queries[0]
            #print(first_q)
            for i in range(len(first_q)):
                res_edus = []
                n = first_q[i][1]
                res_edus.append(first_q[i])
                found_all = True
                for j in range(1, len(queries)):
                    goal = n+j
                    ids = [q[1] for q in queries[j]]
                    if goal not in ids:
                        found_all = False
                        break
                    else:
                        res_edus.append([n for n in queries[1] if n[1] == goal][0])
                res_edus = [n[2] for n in res_edus]
                if found_all:
                    # res += '<p>Текст № {0}'.format(text) + '</p>\n'
                    text_result[text].append(str(' '. join(res_edus)))
                    #res += str(' '. join(res_edus))
                    #res += '\n'
            #print(text_result[text])
        #if res != '':
            #print(res)
    return text_result


def return_multiedu_search_res_html(all_found):
    result = process_multi_edus_search(all_found)[1]
    texts_ids = process_multi_edus_search(all_found)[0]
    text_result = find_seq(texts_ids, result)
    res = str()
    for text in text_result:
        if len(text_result[text]) > 0:
            res += '<p>Текст № {0}'.format(text) + '</p>\n<ul>\n'
            for i in text_result[text]:
                res += '<li>'
                res += i
                res += '</li>\n'
            res += '</ul>\n'
    return res


def return_singleedu_search_res_html(all_found):
    res = str()
    all_found = all_found[0]
    all_found.sort(key=operator.itemgetter(0))
    found_by_text = itertools.groupby(all_found, lambda x: x[0])
    for i, l in found_by_text:
        edus = [(n[1], n[2]) for n in list(l)]
        res += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
        for edu in edus:
            edu_id = edu[0]
            edu_text = edu[1]
            res += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id)+'">' + str(edu_text) + '</a></li>'
        res += '</ul>'
    return res


def return_search_res_html(query):
    DB_requests = create_DB_requests(query)
    all_found = get_found(DB_requests)
    if len(all_found) > 1:
        return return_multiedu_search_res_html(all_found)
    else:
        return return_singleedu_search_res_html(all_found)

print(return_search_res_html(real_query))

# print({3: [i[3] for i in result]})


'''
if num_of_edus > 1:
    print(process_multi_edus_search(all_found))
    #print([i[1] for i in process_multi_edus_search(all_found)])
else:
    all_found
'''















"""
res = ''
for i, l in search_result:
    edus = [(n[1], ' '.join(n[2])) for n in list(l)]
    res += '<p><a href="tree/{0}.html">Текст № {0}</a>'.format(i) + '</p>\n\n<ul>'
    for edu in edus:
        res += '<li><a href="tree/{0}.html">Текст № {0}</a>'.format(i) + 'EDU id: ' + str(edu[0]) + '<br>EDU text:' + str(edu[1]) + '</li>'
        res += '</ul>'
            # res += '<p>' + str(i) + '</p>\n\n<p>' + str([n[1] for n in list(l)]) + '</p>\n\n\n\n'
    if res == '':
        res = '<p>По запросу ничего не найдено.</p>'
    print(res)
"""


