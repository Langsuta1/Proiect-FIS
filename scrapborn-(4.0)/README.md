# 🤖 SCRAPBORN — Godot Engine 4.x Project

Acesta este proiectul complet nativ dezvoltat în **Godot Engine 4.x** folosind **GDScript** (limbajul de programare nativ Godot).

---

## 🚀 Cum deschizi proiectul în Godot:

1. Descarcă sau deschide **Godot Engine 4** (de pe [godotengine.org](https://godotengine.org) sau prin Steam).
2. În fereastra **Project Manager**, apasă butonul **Import**.
3. Selectează fișierul `project.godot` din acest folder:
   `C:\Users\cozy1\.gemini\antigravity\scratch\godot_project\project.godot`
4. Apasă **Import & Edit**.
5. În editorul Godot, apasă tasta **F5** (sau butonul **Play** din dreapta-sus) pentru a rula jocul!

---

## 📦 Cum exporți ca aplicație de sine stătătoare (.exe pe Windows):

1. În Godot, mergi în meniul de sus: **Project** -> **Export...**
2. Apasă **Add...** -> alege **Windows Desktop**.
3. Dacă nu ai template-urile descărcate, Godot îți oferă un buton cu un singur click: *Manage Export Templates* -> *Download and Install*.
4. Apasă **Export Project...** și alege unde vrei să salvezi fișierul `Scrapborn.exe`.
5. Vei avea un executabil `.exe` independent, care rulează pe orice PC fără să necesite browser sau Godot instalat!

---

## 📁 Structura proiectului:

```
godot_project/
├── project.godot               # Configurația motorului Godot 4.x (viewport, scale, pixel art filter)
├── autoload/
│   └── game_manager.gd         # Singleton global (input maps, stări, semnale, notificări)
├── scripts/
│   ├── player.gd               # Controller CharacterBody2D (walk, sprint, double jump, dash, combat)
│   ├── boss_crusher.gd         # AI Mini-boss The Crusher (charge, slam, health signals)
│   ├── enemy_drone.gd          # AI Junk Drone (patrulă orizontală, floating sinewave)
│   ├── projectile_laser.gd     # Fascicul laser tras din Blaster Arm
│   └── hud.gd                  # Manager interfață (Armor bar, Core energy bar, Boss bar)
├── scenes/
│   ├── main.tscn               # Scena rădăcină (încarcă LevelHeap + HUD)
│   ├── level_heap.tscn         # Nivelul Zone 1 (geometrie, compactor pit, platforme, inamici)
│   ├── player.tscn             # Scena jucătorului (CharacterBody2D + Camera2D + Hitboxes)
│   ├── enemy_drone.tscn        # Scena inamicului zburător
│   ├── boss_crusher.tscn       # Scena boss-ului The Crusher
│   ├── projectile_laser.tscn   # Scena glonțului laser
│   └── hud.tscn                # Scena CanvasLayer (HUD + alerte + bară boss)
└── assets/                     # Toate cele 36 de sprite-uri PNG 32x32 native din proiect
```

---

## 🕹️ Mapare Taste în GDScript (`InputMap`):

- **Mers**: `A` / `D` sau `Săgeți`
- **Sprint**: `Shift`
- **Salt / Double Jump**: `Space` sau `W`
- **Dash**: `C` sau `K`
- **Atac Melee (Tigaie / Bâtă)**: `X` sau `J`
- **Atac Ranged (Laser / Foc)**: `Z` sau `L`
- **Grenadă**: `G`
- **Grapple**: `E`
- **Schimbă Armă**: `Q` sau tastele `1` - `4`
- **Toggle Chassis**: `F` (Damaged Robot ↔ Standard Chassis)
