from py2neo import Graph

graph = Graph()  # creating a graph for a database
graph.run('MATCH (n) DETACH DELETE n')  # making sure the DB is empty

commands = open('neo4j_commands.txt', 'r', encoding='utf-8').read().split('\n\n')
for command in commands:
    graph.run(command)