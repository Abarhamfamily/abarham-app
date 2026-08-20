import sys
with open('main.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
lines[38:41] = [
    '    \"\"\"\n',
    '    Safe migration to add car option columns and transport_type column.\n',
    '    \"\"\"\n'
]
with open('main.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)