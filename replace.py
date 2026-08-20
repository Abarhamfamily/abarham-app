content = open('main.py', 'r', encoding='utf-8').read()
new = content.replace('\\\"', '\"')
open('main.py', 'w', encoding='utf-8').write(new)