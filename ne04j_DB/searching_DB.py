from py2neo import Graph


graph = Graph()  # creating a graph for a database

# кажддый "реальный" node имеет "Id", "Text_id", "text", "lemmas". Т.е. достаточно проверить, есть ли у node "text",
# если есть, по нему можно искать. Если нет - то это фиктивный node, который появился в результате объединения ЭДЕ.

nodes = graph.find('EDU')
real_edus = [node for node in nodes if 'text' in node]

word = 'а'
lemma = 'благодаря'
pos = 'V'

found_word = [edu for edu in real_edus if word in edu['text'].split()]
print(found_word[:10], '\n\n')

found_lemma = [edu for edu in real_edus if lemma in eval(edu['lemmas'])]  # eval нужен, чтобы сделать из строки словарь
print(found_lemma[:10], '\n\n')

found_pos = [edu for edu in real_edus if pos in eval(edu['lemmas']).values()]
print(found_pos[:10], '\n\n')

