# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ТРИ ДУРАКА: Pixel Brawler** — браузерная Vampire Survivors-подобная игра. Один файл `index.html`, vanilla JS, HTML5 Canvas (800×600, масштабируется через CSS). Без сборщиков, без зависимостей.

## Running the Game

Open `index.html` directly in a browser. No server required for development (sprite images load from `characters/` via relative paths).

To build a **standalone** version (all sprites embedded as base64, shareable without the `characters/` folder):

```bash
python3 build_standalone.py
# Output: index_standalone.html
```

## File Structure

- `index.html` — весь игровой код (~1700 строк)
- `characters/` — PNG спрайты (player1-3 select/sprite, enemy1-2)
- `build_standalone.py` — упаковщик в один файл
- `index_standalone.html` — собранная standalone-версия

## Architecture of index.html

Секции в порядке объявления:

1. **Constants** (`TW=32, MW=120, MH=68, PW=3840, PH=2176`) — мир в тайлах и пикселях. Ключевые таймеры: `GAME_DURATION=1800000` (30 мин), `BOSS_INTERVAL=180000` (3 мин), `WAVE_INTERVAL=30000` (30 сек), `MAX_ENEMIES=600`.

2. **Sprite loading** — `loadImg(key, src, processType)`. Три типа обработки: `''` (raw), `'sprite'` (2×2 spritesheet 24×32 frame), `'enemy'` (2×2 spritesheet 40×54 frame). Белый фон удаляется pixel-by-pixel через `buildSpritesheet()`.

3. **Character data** (`CHARS[]`) — 5 персонажей. У первых трёх есть спрайты (`sprKey`), у mage/adventurer — процедурная отрисовка. Каждый имеет `stats: {str,agi,lck,vit,int}` (сумма=22), пассивную способность (`passiveType`), и стартовое оружие (`startWeapon`).

4. **Skills data** (`ALL_SKILLS[]`) — 14 навыков + weapon unlocks. Поле `fx` — объект с ключами, совпадающими с полями `player.mods`.

5. **Classes**: `XPGem`, `Chest`, `Proj`, `Player`, `Monster` — в таком порядке.

6. **Player** — хранит `mods` (модификаторы от скиллов), `weapons[]` (массив активных оружий), `acquiredSkills` (Map id→level). Метод `applySkill(sk)` добавляет эффект из `sk.fx` к `mods`. Метод `getSkillChoices()` возвращает 3 случайных доступных скилла.

7. **Weapon system** — не классы, а данные в `player.weapons[]`. Каждое оружие: `{type, timer, ...typeSpecificData}`. Логика обновления — `updateWeapons(dt)`. Все оружия читают `player.mods` напрямую при каждом выстреле.

8. **Map** — `genMap()` заполняет `tilemap[y][x]` (120×68). `drawTiles()` рендерит только видимые тайлы через viewport culling.

9. **Camera** — `cam={x,y}`. Обновляется в `updateGame()`. `isSolid(wx,wy)` проверяет мировые координаты.

10. **Game states**: `STATE ∈ {TITLE, SELECT, GAME, LEVELUP, CHEST, GAMEOVER, WIN}`. Game loop в `update(ts)` → `requestAnimationFrame(update)`.

11. **HUD** — `drawHUD()`: только таймер (обратный отсчёт), убито, уровень, XP-бар, HP-бар, миникарта, волна. Никакого floating text в GAME-стейте.

12. **Game loop** — `update(ts)` вызывается через RAF. `dt = ts - last` (ms). `gameTime` суммируется в GAME-стейте. Victory при `gameTime >= GAME_DURATION`.

## Key Conventions

- Все координаты в **мировом пространстве** (world coords). Экранные = `worldX - cam.x / worldY - cam.y`.
- `dt` всегда в **миллисекундах**. Скорости в пикселях/сек → умножать на `dt/1000`.
- Оружия наследуют модификаторы при каждом кадре (не при добавлении) — `player.mods` читается напрямую в `updateWeapons()`.
- Спрайт-персонажи 1-3 используют 4-направленную анимацию через `dirToFrame(dir, fw, fh)`.
- `mclk` сбрасывается в `false` каждый кадр в конце `update()` — кликать можно обрабатывать в любом месте draw-функций.
