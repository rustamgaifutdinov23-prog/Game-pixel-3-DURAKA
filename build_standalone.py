#!/usr/bin/env python3
"""
Собирает standalone index.html: встраивает все спрайты из characters/ как base64.
Запуск: python3 build_standalone.py
Результат: index_standalone.html (можно отправить друзьям)
"""
import base64
import os
import re

# key -> (path, process_type)
IMAGES = {
    'p1sel': ('characters/player1_select.png', ''),
    'p2sel': ('characters/player2_select.png', ''),
    'p3sel': ('characters/player3_select.png', ''),
    'p1spr': ('characters/player1_sprite.png', 'sprite'),
    'p2spr': ('characters/player2_sprite.png', 'sprite'),
    'p3spr': ('characters/player3_sprite.png', 'sprite'),
    'e1':    ('characters/enemy1.png',          'enemy'),
    'e2':    ('characters/enemy2.png',          'enemy'),
}

def to_b64(path):
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    return f'data:image/png;base64,{data}'

# Read source HTML
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace loadImg calls with inline base64 IIFE
for key, (path, proc) in IMAGES.items():
    if not os.path.exists(path):
        print(f'[WARN] Not found: {path}')
        continue
    b64 = to_b64(path)
    print(f'[OK] {path} -> {len(b64)//1024}KB base64')

    new = (
        f"(function(){{"
        f"var im=new Image();"
        f"im.onload=function(){{"
        f"if('{proc}'==='sprite')imgs['{key}']=buildSpritesheet(im,24,32);"
        f"else if('{proc}'==='enemy')imgs['{key}']=buildSpritesheet(im,40,54);"
        f"else imgs['{key}']=im;"
        f"loaded++;}};"
        f"im.src='{b64}';"
        f"}})();"
    )

    # Use regex to handle any whitespace variations around commas
    pattern = re.escape(f"loadImg('{key}'") + r"\s*,\s*" + re.escape(f"'{path}'") + r"\s*,\s*" + re.escape(f"'{proc}'") + r"\s*\)"  + r"\s*;"
    m = re.search(pattern, html)
    if m:
        html = html[:m.start()] + new + html[m.end():]
        print(f'[OK] Embedded {key}')
    else:
        print(f'[WARN] Pattern not found for {key}')

# Write output
out = 'index_standalone.html'
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out) // 1024
print(f'\nDone! {out} ({size_kb}KB)')
print(f'Send this file to friends - opens in any browser without a server.')
