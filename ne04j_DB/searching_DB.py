from py2neo import Graph
import itertools
import operator
import re

graph = Graph()  # calling a graph for a database

# кажддый "реальный" node имеет "Id", "Text_id", "text", "lemmas". Т.е. достаточно проверить, есть ли у node "text",
# если есть, по нему можно искать. Если нет - то это фиктивный node, который появился в результате объединения ЭДЕ.

# nodes = graph.find('EDU')
# real_edus = [node for node in nodes if 'text' in node]

'''
def search_edus(parameter, value):
    found = None
    if parameter == 'word':
        found = graph.run("MATCH (n) WHERE '" + value + "' in split(n.text_norm, ' ')\n RETURN n.Text_id, n.Id, split(n.text, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'lemma':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text_norm, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    if parameter == 'pos':
        found = graph.run('MATCH (n) WHERE n.lemmas CONTAINS "' + "'" + value + "'" + '"' +
                          " RETURN n.Text_id, n.Id, split(n.text_norm, ' ')")
        found = [[n[0], n[1], n[2]] for n in found]
    # print([n for n in found if n[0] == 20], '\n\n')
    if found:
        found.sort(key=operator.itemgetter(0))
        found_by_text = itertools.groupby(found, lambda x: x[0])
        found = found_by_text
    return found

# search_result = search_edus('lemma', 'как')
'''


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


messages = {'ro_s_in_edu_dont_match': 'Пожалуйста, выберите одинаковые риторические отношения внутри одной ЭДЕ.',
            'no_input_for_word': 'Пожалуйста, введите значение в поле "слово".',
            'no_input_for_lemma': 'Пожалуйста, введите значение в поле "лемма".',
            'no_input_for_pos': 'Пожалуйста, выберите часть речи.',
            'not_equal_parenth_amount': 'Пожалуйста, проверьте корректность запроса, количество открывающих и закрывающих скобок не совпадает.',
            'split_your_request': 'Ваш запрос необходимо разбить на несколько отдельных запросов. Подробности см. в инструкции по поиску.'}


def check_query(parsed_query):
    outer_parenth = True
    inner_parenth = True
    open_parenthesis_outer = list()
    close_parenthesis_outer = list()
    for edu in parsed_query:
        chosen_ro_s = set([' '.join(d['ro']) for d in edu])
        if len(chosen_ro_s) > 1:
            return messages['ro_s_in_edu_dont_match']
        searched_for_word = [d['searched_for'] for d in edu if d['type'] == 'word']
        if '' in searched_for_word or ' ' in searched_for_word:
            return messages['no_input_for_word']
        searched_for_lemma = [d['searched_for'] for d in edu if d['type'] == 'lemma']
        if '' in searched_for_lemma or ' ' in searched_for_lemma:
            return messages['no_input_for_lemma']
        searched_for_pos = [d['searched_for'] for d in edu if d['type'] == 'pos']
        if '' in searched_for_pos or ' ' in searched_for_pos:
            return messages['no_input_for_pos']
        open_parenthesis_inner = ''.join([d['open_parenth'] for d in edu])
        close_parenthesis_inner = ''.join([d['close_parenth'] for d in edu])
        open_parenthesis_outer += [d['open_parenth'] for d in edu]
        close_parenthesis_outer += [d['close_parenth'] for d in edu]
        if len(open_parenthesis_inner) != len(close_parenthesis_inner):
            inner_parenth = False
    open_parenthesis_outer = ''.join(open_parenthesis_outer)
    close_parenthesis_outer = ''.join(close_parenthesis_outer)
    if len(open_parenthesis_outer) != len(close_parenthesis_outer):
        outer_parenth = False
    if not outer_parenth and not inner_parenth:
        return messages['not_equal_parenth_amount']
    if not inner_parenth and outer_parenth:
        return messages['split_your_request']
    return True


markers = {"a":"a", "bezuslovno":"безусловно", "buduchi":"будучи", "budeto":"будь это",
           "vitoge":"в итоге", "vosobennosti":"в особенности", "vramkah":"в рамках",
           "vrezultate":"в результате", "vsamomdele":"в самом деле", "vsvojyochered":"в свою очередь",
           "vsvyazis":"в связи с", "vtechenie":"в течение", "vtovremya":"в то время", "vtozhevremya":"в то же время",
           "vusloviyah":"в условиях", "vchastnosti":"в частности", "vposledstvii":"впоследствии",
           "vkluchaya":"включая", "vmestotogo":"вместо того", "vmestoetogo":"вместо этого",
           "vsezhe":"все же", "vsledstvie":"вследствие", "govoritsya":"говорится",
           "govorit_lem":"говорить", "dazhe":"даже", "dejstvitelno":"действительно",
           "dlya":"для", "dotakojstepeni":"до такой степени", "esli":"если",
           "zaverit_lem":"заверить", "zaveryat_lem":"заверять", "zayavit_lem":"заявить",
           "zayavlat_lem":"заявлять", "i":"и", "izza":"из-за", "ili":"или", "inache":"иначе",
           "ktomuzhe":"к тому же", "kogda":"когда", "kotoryj_lem":"который", "krometogo":"кроме того",
           "libo":"либо", "lishtogda":"лишь тогда", "nasamomdele":"на самом деле",
           "natotmoment":"на тот момент", "naetomfone":"на этом фоне", "napisat_lem":"написать",
           "naprimer":"например", "naprotiv":"напротив", "nesmotryana":"несмотря на", "no":"но",
           "noi":"но и", "objavit_lem":"объявить", "odnako":"однако", "osobenno":"особенно",
           "pisat_lem":"писать", "podannym":"по данным", "pomneniu":"по мнению", "poocenkam":"по оценкам",
           "posvedeniam":"по сведениям", "poslovam":"по словам", "podtverdit_lem":"подтвердить",
           "podtverzhdat_lem":"подтверждать", "podcherkivat_lem":"подчеркивать",
           "podcherknut_lem":"подчеркнуть",
           "pozdnee":"позднее", "pozzhe":"позже", "poka":"пока", "poskolku":"поскольку",
           "posle":"после", "potomuchto":"потому что", "poetomu":"поэтому",
           "prietom":"при этом", "priznavat_lem":"признавать", "priznano":"признано",
           "priznat_lem":"признать", "radi":"ради", "rasskazat_lem":"рассказать",
           "rasskazyvat_lem":"рассказывать", "sdrugojstorony":"с другой стороны",
           "scelyu":"с целью", "skazat_lem":"сказать", "skoree":"скорее",
           "sledovatelno":"следовательно", "sledomza":"следом за",
           "soobshaetsya":"сообщается", "soobshat_lem":"сообщать", "soobshit_lem":"сообщить",
           "taki":"так и", "takkak":"так как", "takchto":"так что", "takzhe":"также", "toest":"то есть",
           "utverzhdat_lem":"утверждать", "utverzhdaetsya":"утверждается", "hotya":"хотя"}


def request_with_one_cond_on_edu(query):
    requests = list()
    request = str()
    request += 'MATCH (n)\nWHERE'
    el = query[0]
    ro = el['ro']
    request += el['open_parenth']
    if ro == ['any']:
        if el['type'] == 'marker':
            marker_rus = markers[el['searched_for']]
            if '_lem' in el['searched_for']:
                request += ' n.lemmas CONTAINS \'{0}\''.format(marker_rus)
            else:
                marker_lengh = str(len(marker_rus)+1)
                if len(marker_rus.split()) > 1:
                    # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                    request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\''.format(marker_lengh, marker_rus)

                else:
                    # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                    request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}]'.format(marker_rus, marker_lengh)
        if el['type'] == 'word':
            request += " '{0}' IN split(n.text_norm, ' ')".format(el['searched_for'])
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request += ' n.lemmas CONTAINS "\'{0}\'"'.format(el['searched_for'])
        if el['type'] == '':
            request = 'MATCH (n)'
    else:
        request = re.sub('WHERE', 'WHERE (', request)
        request = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request)
        if el['type'] == 'word':
            request += " '{0}' IN split(n.text_norm, ' ')) AND type(r) IN {1}".format(el['searched_for'], ro)
        if el['type'] == 'lemma' or el['type'] == 'pos':
            request += ' n.lemmas CONTAINS "\'{0}\'") AND type(r) IN {1}'.format(el['searched_for'], ro)
        if el['type'] == '':
            request = 'MATCH (n)-[r]-()\nWHERE type(r) IN {0}'.format(ro)
    request += el['close_parenth']
    request += "\nRETURN n.Text_id, n.Id, n.text"
    #print(request, '\n')
    #requests.append(request)
    return request


def create_DB_requests(query):
    requests = list()
    conditions = {'same_edu_and': 'AND', 'same_edu_or': 'OR', 'next_edu_and': '', 'none': ''}
    parsed_query = parse_query(query)
    for i in parsed_query:
        request = str()
        request += 'MATCH (n)\nWHERE'
        if len(i) > 1:
            ro_chosen = False
            type_chosen = False
            for el in i:
                ro_chosen = False
                type_chosen = False
                request += el['open_parenth']
                cond = conditions[el['add_type']]
                ro = el['ro']
                if ro == ['any']:
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request += ' n.lemmas CONTAINS \'{0}\' {1}'.format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                                request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.format(marker_lengh, marker_rus, cond)

                            else:
                                # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                                request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.format(marker_rus, marker_lengh, cond)

                    if el['type'] == 'word':
                        type_chosen = True
                        request += " '{0}' IN split(n.text_norm, ' '){1} {2}".format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request = 'MATCH (n)'
                        request += el['close_parenth']
                else:
                    ro_chosen = True
                    if el['type'] == 'marker':
                        type_chosen = True
                        marker_rus = markers[el['searched_for']]
                        if '_lem' in el['searched_for']:
                            request += ' n.lemmas CONTAINS \'{0}\' {1}'.format(marker_rus, cond)
                        else:
                            marker_lengh = str(len(marker_rus)+1)
                            if len(marker_rus.split()) > 1:
                                # request += ' lower(n.text) CONTAINS \'{0}\''.format(marker_rus)
                                request += ' REDUCE(s = " ", w in split(n.text_norm, " ")[0..{0}]|s + " " + w) CONTAINS \'{1}\' {2}'.format(marker_lengh, marker_rus, cond)

                            else:
                                # request += " '{0}' IN split(n.text_norm, ' ')".format(marker_rus)
                                request += ' \'{0}\' IN split(n.text_norm, " ")[0..{1}] {2}'.format(marker_rus, marker_lengh, cond)
                    if el['type'] == 'word':
                        type_chosen = True
                        request += " '{0}' IN split(n.text_norm, ' '){1} {2}".format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == 'lemma' or el['type'] == 'pos':
                        type_chosen = True
                        request += ' n.lemmas CONTAINS "\'{0}\'"{1} {2}'.format(el['searched_for'], el['close_parenth'], cond)
                    if el['type'] == '':
                        type_chosen = False
                        request = 'MATCH (n)-[r]-()'
                        request += el['close_parenth']
            if ro_chosen and type_chosen:
                request = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request)
                #request += ')'
                request = re.sub("WHERE", "WHERE (", request)
                request += ') AND type(r) IN {0}'.format(ro)
            #if not ro_chosen and not type_chosen:
                #request += el['close_parenth']
            request += "\nRETURN n.Text_id, n.Id, n.text"
            #print(request, '\n')
            requests.append(request)
        else:
            requests.append(request_with_one_cond_on_edu(i))
        '''
        else:
            el = i[0]
            ro = el['ro']
            request += el['open_parenth']
            if ro == ['any']:
                if el['type'] == 'word':
                    request += " '{0}' IN split(n.text_norm, ' ')".format(el['searched_for'])
                if el['type'] == 'lemma' or el['type'] == 'pos':
                    request += ' n.lemmas CONTAINS "\'{0}\'"'.format(el['searched_for'])
                if el['type'] == '':
                    request = 'MATCH (n)'
            else:
                request = re.sub('MATCH \(n\)', 'MATCH (n)-[r]-()', request)
                if el['type'] == 'word':
                    request += " '{0}' IN split(n.text_norm, ' ') AND type(r) IN {1}".format(el['searched_for'], ro)
                if el['type'] == 'lemma' or el['type'] == 'pos':
                    request += ' n.lemmas CONTAINS "\'{0}\'" AND type(r) IN {1}'.format(el['searched_for'], ro)
                if el['type'] == '':
                    request = 'MATCH (n)-[r]-()\nWHERE type(r) IN {0}'.format(ro)
            request += el['close_parenth']
        '''
    print(requests)
    return requests


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
            queries = texts_results[text]
            first_q = queries[0]
            for i in range(len(first_q)):
                res_edus = []
                k = first_q[i][1]
                res_edus.append(first_q[i])
                found_all = True
                for j in range(1, len(queries)):
                    goal = k+j
                    ids = [q[1] for q in queries[j]]
                    if goal not in ids:
                        found_all = False
                        break
                    else:
                        if len([n for n in queries[j] if n[1] == goal]) > 0:
                            res_edus.append([n for n in queries[j] if n[1] == goal][0])
                res_edus = [n[2] for n in res_edus]
                if found_all:
                    text_result[text].append(str(' '. join(res_edus)))
    return text_result


def return_multiedu_search_res_html(all_found):
    result = process_multi_edus_search(all_found)[1]
    texts_ids = process_multi_edus_search(all_found)[0]
    # print(result)
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
        print(edus)
        res += '<p>Текст № {0}'.format(i) + '</p>\n\n<ul>'
        for edu in edus:
            edu_id = edu[0]
            edu_text = edu[1]
            res += '<li><a href="tree/{0}.html?position=edu'.format(i)+str(edu_id)+'">' + str(edu_text) + '</a></li>'
        res += '</ul>'
    return res


def return_search_res_html(query):
    checked = check_query(parse_query(query))
    if checked is True:
        try:
            DB_requests = create_DB_requests(query)
            all_found = get_found(DB_requests)
            print(len(all_found))
            if len(all_found) > 1:
                return return_multiedu_search_res_html(all_found)
            else:
                return return_singleedu_search_res_html(all_found)
        except:
            return 'failed_query'
    else:
        return checked




real_query = '{"data":[{"type":"marker","searched_for":"dazhe","ro":["any"],"add_type":"same_edu_or","open_parenth":"","close_parenth":""},{"type":"lemma","searched_for":"только","ro":["any"],"add_type":"next_edu_and","open_parenth":"(","close_parenth":""},{"type":"pos","searched_for":"V","ro":["any"],"add_type":"none","open_parenth":"","close_parenth":")"}]}'
print(return_search_res_html(real_query))

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


