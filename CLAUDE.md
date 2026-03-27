# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ТРИ ДУРАКА: Pixel Brawler** — браузерная Vampire Survivors-подобная игра. Один файл `index.html`, vanilla JS, HTML5 Canvas (800x600, масштабируется через CSS). Без сборщиков, без зависимостей.

## Running the Game

**Рекомендуемый способ** (гарантированно работает):
```bash
cd pixel-game
python3 -m http.server 8080
# Открыть http://localhost:8080
```

**Standalone** (не требует сервера, все спрайты встроены как base64):
```bash
python3 build_standalone.py
# Открыть index_standalone.html в браузере
```

**Напрямую** — `index.html` можно открыть из file://, но некоторые браузеры блокируют загрузку картинок. Есть таймаут 5 сек + кнопка "Пропустить".

## File Structure

- `index.html` — весь игровой код (~1400 строк)
- `characters/` — PNG спрайты персонажей (4 направления: front/back/left/right для каждого)
  - Игроки: rustam, kristina, artem, ely, timur
  - Враги: dima, kiril, yula, vadim, Alex, alexandr
  - `map.png` — фон карты (2752x1536)
- `enemy/` — спрайтшиты врагов (bat, slime, bone, zombie, ghost, golem, dragon)
  - Формат: `enemy_lvl{N}_{name}.png` (2816x1536, серый фон, ряды анимаций)
  - Используется: `enemy_lvl1_bat.png` (5 анимаций: idle/move/attack/hit/death)
- `build_standalone.py` — упаковщик в один файл (встраивает characters/ как base64)
- `index_standalone.html` — собранная standalone-версия (~10.7 MB)

## Architecture of index.html

Секции в порядке объявления:

1. **Input** — WASD/Arrows для движения, клик для UI, I/Tab для инвентаря, 1/2/3 для выбора навыка, Esc для пропуска.

2. **Constants** (`TW=32, MW=120, MH=68, PW=3840, PH=2176`) — мир в тайлах и пикселях. `WAVE_INTERVAL=180000` (3 мин), `BOSS_INTERVAL=180000`, `GAME_DURATION=1800000` (30 мин), `MAX_WEAPONS=6`.

3. **Sprite loading** — `loadImg(key, src)`. Загружает characters/ (5 игроков x 4 направления + 6 врагов x 4 направления + map = 45 штук) + `enemy_lvl1_bat.png`.

4. **Bat sprite sheet** — `BAT_ANIMS` описывает раскладку кадров в `enemy_lvl1_bat.png`. `processBatSprite()` удаляет серый фон через pixel-by-pixel замену на прозрачность. `drawBatFrame()` рендерит нужный кадр анимации с зеркалированием.

5. **Character data** (`CHARS[]`) — 4 класса:
   - **Рыцарь** (rustam): HP 150, медленный, пассив — реген 1HP/5с, стартовое оружие — меч
   - **Разбойник** (artem): HP 80, быстрый, пассив — 15% уклонение, стартовое — лук
   - **Маг** (ely): HP 100, средний, пассив — пробивание +1, стартовое — жезл
   - **Берсерк** (timur): HP 130, средний, пассив — +50% AtkSpd ниже 30% HP, стартовое — аура

6. **Weapon definitions** (`WEAPON_DEFS`) — 7 типов оружия: sword (мили-свип), bow (прямой снаряд), wand (наведение/HomingProj), aura (постоянный AoE), dagger (орбита), cross (отскоки), lightning (случайные цели).

7. **Skills** (`SKILLS_DEF[]`) — 14 навыков с полем `fx` (объект ключей → `player.mods`). `getSkillChoices()` возвращает до 3 случайных доступных. Выбор через `applyUpgrade()`.

8. **Classes**: `XPGem`, `Chest`, `LootDrop`, `Weapon`, `Proj`, `HomingProj`, `Player`, `Monster`.

9. **Player** — хранит `mods` (модификаторы), `weapons[]` (массив до MAX_WEAPONS=6), `skills` (Map id->level). Методы: `pickupWeapon(id)` (подбор/апгрейд дубликата), `discardWeapon(idx)`, `applySkill()`, `gainXP()` (while-цикл для множественных левелапов).

10. **Monster** — `ENEMY_BY_LVL` маппит `enemyLvl` (1-4) к спрайтам. Lvl1 нормальные враги — анимированные баты (`isBat=true`). Смерть бата проигрывает death-анимацию (`dyingAnim`). Враги дропают оружие: 3% обычные, 15% элиты, 70% боссы.

11. **Map** — `drawMapBg()` рендерит `map.png` через source-rect drawImage (viewport culling). `isSolid()` всегда false — открытый мир.

12. **Game states**: `STATE in {TITLE, SELECT, GAME, LEVELUP, CHEST, INVENTORY, GAMEOVER, WIN}`. INVENTORY открывается по I/Tab.

13. **HUD** — таймер, убийства, уровень, волна (lv), инвентарь-хинт, XP-бар, HP-бар, миникарта, слоты оружий.

14. **Game loop** — `update(ts)` через RAF. `dt = min(now-last, 100)` (ms). `enemyLvl` растёт каждые 3 мин (макс 4). Босс каждые 3 мин.

## Key Conventions

- Все координаты в **мировом пространстве**. Экранные = `worldX - cam.x`.
- `dt` в **миллисекундах**. Скорости: `px/s * dt/1000`.
- Оружия читают `player.mods` при каждом выстреле (не при добавлении).
- Спрайты персонажей: `drawCharSprite(sprName, dir, sx, sy, tgtH)` маппит game-dir (down/up/left/right) в sprite-dir (front/back/left/right).
- Бат-спрайт: `drawBatFrame(monster, sx, sy, tgtH)` читает анимацию из `batProcCanvas` (обработанный канвас без серого фона).
- `mclk` обрабатывается в draw-функциях (UI-клики). Клавиши 1/2/3/Esc обрабатываются в keydown listener.

## Build System

`build_standalone.py`:
- Собирает 45 base64 IIFE (map + 20 player sprites + 24 enemy character sprites)
- Bat sprite sheet НЕ встраивается (11MB) — в standalone bat рисуется обычным character sprite
- Regex: ищет блок от `loadImg('map',...)` до `loadImg('enemy_lvl1_bat',...)` и заменяет на IIFE-блок
- Удаляет `const P_CHARS/E_CHARS/SPR_DIRS` из standalone (уже не нужны)
