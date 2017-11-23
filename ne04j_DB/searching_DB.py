from py2neo import Graph
import itertools
import operator

graph = Graph()  # creating a graph for a database

# кажддый "реальный" node имеет "Id", "Text_id", "text", "lemmas". Т.е. достаточно проверить, есть ли у node "text",
# если есть, по нему можно искать. Если нет - то это фиктивный node, который появился в результате объединения ЭДЕ.

nodes = graph.find('EDU')
real_edus = [node for node in nodes if 'text' in node]


def search_edus(real_edus, parameter, value):
    if parameter == 'word':
        found = [edu for edu in real_edus if value in edu['text'].split()]
    if parameter == 'lemma':
        found = [edu for edu in real_edus if value in eval(edu['lemmas'])]
    if parameter == 'pos':
        found = [edu for edu in real_edus if value in eval(edu['lemmas']).values()]
    found = found[:20]  # берем 20 просто для тестирования
    found_by_text = list()
    for key, items in itertools.groupby(found, operator.itemgetter('Text_id')):
        found_by_text.append([key, list(items)])
    for text in found_by_text:
        text_id = list(text)[0]
        edus = list(text)[1]
        print(text_id)
        print(edus, '\n\n')

search_edus(real_edus, 'pos', 'A')




