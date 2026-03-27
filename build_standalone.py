#!/usr/bin/env python3
"""
Собирает standalone index.html: встраивает все спрайты из characters/ как base64.
Запуск: python3 build_standalone.py
Результат: index_standalone.html (можно отправить друзьям без папки characters/)
"""
import base64
import os
import re

P_CHARS = ['rustam', 'kristina', 'artem', 'ely', 'timur']
E_CHARS = ['dima', 'kiril', 'yula', 'vadim', 'Alex', 'alexandr']
DIRS    = ['front', 'back', 'left', 'right']

ALL_KEYS = {'map': 'characters/map.png'}
for n in P_CHARS:
    for d in DIRS:
        ALL_KEYS[f'{n}_{d}'] = f'characters/{n}_{d}.png'
for n in E_CHARS:
    for d in DIRS:
        ALL_KEYS[f'{n}_{d}'] = f'characters/{n}_{d}.png'


def to_b64(path):
    with open(path, 'rb') as f:
        return 'data:image/png;base64,' + base64.b64encode(f.read()).decode()


with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Строим блок с base64 IIFEs вместо цикловых loadImg
lines = []
ok, skip = 0, 0
for key, path in ALL_KEYS.items():
    if not os.path.exists(path):
        print(f'[WARN] Not found: {path}')
        skip += 1
        continue
    b64 = to_b64(path)
    print(f'[OK] {path} -> {len(b64)//1024} KB')
    lines.append(
        f"(function(){{total++;var im=new Image();"
        f"im.onload=function(){{imgs['{key}']=im;loaded++;}};"
        f"im.onerror=function(){{loaded++;}};"
        f"im.src='{b64}';}})()"
    )
    ok += 1

inline_block = ';\n'.join(lines) + ';'

# Находим блок загрузки спрайтов в HTML и заменяем его целиком.
# Блок начинается с loadImg('map'... и заканчивается на строке for(const n of E_CHARS)...
BLOCK_START = r"loadImg\('map','characters/map\.png'\);"
BLOCK_END   = r"for \(const n of E_CHARS\)[^\n]+\n"

pattern = BLOCK_START + r".*?" + BLOCK_END
m = re.search(pattern, html, re.DOTALL)
if m:
    html = html[:m.start()] + inline_block + '\n' + html[m.end():]
    print(f'[OK] Блок loadImg заменён на {ok} base64 IIFEs')
else:
    print('[WARN] Блок загрузки не найден — проверь структуру index.html')

# Удаляем также строки с P_CHARS/E_CHARS/SPR_DIRS объявлениями, которые остались
html = re.sub(r"const P_CHARS=\[.*?\];\n", '', html)
html = re.sub(r"const E_CHARS=\[.*?\];\n", '', html)
html = re.sub(r"const SPR_DIRS=\[.*?\];\n", '', html)

out = 'index_standalone.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out) // 1024
print(f'\nГотово! {out} ({size_kb} KB)')
print(f'Заменено: {ok}, пропущено: {skip}')
print(f'Открывается в браузере без папки characters/')
