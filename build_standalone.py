#!/usr/bin/env python3
"""
Builds standalone index_standalone.html with all sprites embedded as base64.
Usage: python3 build_standalone.py
"""
import base64, os, re

def to_b64(path):
    with open(path,'rb') as f:
        return 'data:image/png;base64,'+base64.b64encode(f.read()).decode()

# Build key->path map: map + 20 player sprites + 24 enemy character sprites = 45
ALL_KEYS = {'map':'characters/map.png'}

P_CHARS=['rustam','kristina','artem','ely','timur']
E_CHARS=['dima','kiril','yula','vadim','Alex','alexandr']
DIRS=['front','back','left','right']
for n in P_CHARS:
    for d in DIRS:
        ALL_KEYS[f'{n}_{d}'] = f'characters/{n}_{d}.png'
for n in E_CHARS:
    for d in DIRS:
        ALL_KEYS[f'{n}_{d}'] = f'characters/{n}_{d}.png'
# enemy_lvl1_bat.png is ~11MB, too large for standalone embedding.
# In standalone, bat animation falls back to character sprites.

with open('index.html','r',encoding='utf-8') as f:
    html = f.read()

# Build inline IIFE block
lines=[]
ok=0; skip=0
for key,path in ALL_KEYS.items():
    if not os.path.exists(path):
        print(f'[WARN] Not found: {path}'); skip+=1; continue
    b64=to_b64(path)
    print(f'[OK] {path} -> {len(b64)//1024} KB')
    lines.append(
        f"(function(){{total++;var im=new Image();"
        f"im.onload=function(){{imgs['{key}']=im;loaded++;}};"
        f"im.onerror=function(){{loaded++;}};"
        f"im.src='{b64}';}})();"
    )
    ok+=1

inline_block = '\n'.join(lines)

# Replace the sprite loading block.
# Current index.html structure:
#   loadImg('map','characters/map.png');
#   const P_CHARS=...;
#   ...
#   loadImg('enemy_lvl1_bat','enemy/enemy_lvl1_bat.png');
BLOCK_START = r"loadImg\('map','characters/map\.png'\);"
BLOCK_END   = r"loadImg\('enemy_lvl1_bat','enemy/enemy_lvl1_bat\.png'\);"
pattern = BLOCK_START + r'.*?' + BLOCK_END
m = re.search(pattern, html, re.DOTALL)
if m:
    html = html[:m.start()] + inline_block + '\n' + html[m.end():]
    print(f'[OK] Block replaced with {ok} base64 IIFEs')
else:
    print('[ERROR] Could not find sprite loading block in index.html')
    print('Looking for BLOCK_START...',
          'found' if re.search(BLOCK_START, html) else 'NOT FOUND')
    print('Looking for BLOCK_END...',
          'found' if re.search(BLOCK_END, html) else 'NOT FOUND')

# Remove leftover array declarations
for pat in [r"const P_CHARS=\[.*?\];\n", r"const E_CHARS=\[.*?\];\n",
            r"const SPR_DIRS=\[.*?\];\n"]:
    html = re.sub(pat, '', html, flags=re.DOTALL)

out='index_standalone.html'
with open(out,'w',encoding='utf-8') as f:
    f.write(html)

size_kb=os.path.getsize(out)//1024
print(f'\nDone! {out} ({size_kb} KB)')
print(f'Embedded: {ok}, skipped: {skip}')
