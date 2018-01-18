import re
import os

for file in os.listdir('./corpus/'):
    if file.endswith('.rs3'):
        text = open('./corpus/' + file, 'r', encoding='utf-8').read()
        real_text = str()
        edus_text = re.findall('<segment id=".*?" relname=".*?">(.*?)</segment>', text)
        for edu in edus_text:
            real_text += edu + ' '
        real_text = re.sub('##### ', '\n', real_text)
        real_text = re.sub('\n\n', '\n', real_text)
        new_text = open('./corpus_of_txts/' + file.split('.rs3')[0] + '.txt', 'w', encoding='utf-8')
        new_text.write(real_text)
        new_text.close()