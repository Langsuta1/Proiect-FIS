import os
import math
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")
anim_dir = os.path.join(scratch_dir, "animations", "sheets")

print("Building complete Level Heap 5200x900 Apocalyptic Backdrop & Gameplay Assets...")

# ---------------------------------------------------------------------------
# 1. 5200x900 CONTINUOUS APOCALYPTIC SCRAPYARD BACKDROP
# Directly inspired by Images 4, 5, 6, 7:
# - Smoggy orange/sepia industrial sky with distant mountain heaps and suspension bridges
# - Midground: Towering crane with dangling hydraulic claw (Image 6), massive Junkertown-style gates (Image 5), crushed car pyramids (Image 7)
# - Chasm at x=2800..3600 with bottomless depth and hanging anchor rings
# - Boss Hangar at x=4100..5200 with heavy gantry rail and industrial hazard warning walls
# ---------------------------------------------------------------------------
WIDTH = 5200
HEIGHT = 900
FLOOR_Y = 780

bg = Image.new("RGBA", (WIDTH, HEIGHT), (12, 10, 14, 255))
d = ImageDraw.Draw(bg)

# A. ATMOSPHERIC SKY GRADIENT (y = 0 to 450)
for y in range(450):
    t = y / 450.0
    # Sepia / toxic industrial sunset gradient
    r = int(24 + (58 - 24) * t)
    g = int(20 + (42 - 20) * t)
    b = int(22 + (30 - 22) * t)
    d.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

# Smog / chemical haze clouds
for cx in range(0, WIDTH, 280):
    d.ellipse([cx, 120, cx + 380, 280], fill=(42, 32, 28, 110))
    d.ellipse([cx + 120, 150, cx + 480, 320], fill=(32, 24, 26, 90))

# Distant Transmission Towers & Colossal Bridges on Horizon (Image 4)
for tx in range(160, WIDTH, 540):
    # Transmission tower
    d.polygon([(tx + 40, 180), (tx + 15, 460), (tx + 65, 460)], fill=(22, 18, 24, 255))
    for cy in range(210, 450, 40):
        d.line([(tx + 5, cy), (tx + 75, cy)], fill=(22, 18, 24, 255), width=2)
        d.line([(tx + 5, cy), (tx + 75, cy + 40)], fill=(22, 18, 24, 255), width=1)

# Distant Suspension Bridge Cables across the sky (Image 4)
for bx in range(300, WIDTH, 900):
    d.arc([bx, 140, bx + 600, 480], start=0, end=180, fill=(30, 24, 30, 180), width=2)

# B. MASSIVE MOUNTAINS OF CRUSHED COMPACTED CARS (Images 6 & 7)
for sx in range(0, WIDTH, 340):
    peak_h = 320 + (sx % 160)
    d.polygon([(sx - 80, FLOOR_Y), (sx + 80, peak_h), (sx + 260, peak_h + 80), (sx + 400, FLOOR_Y)], fill=(26, 22, 26, 255))

# Midground crushed car silhouettes layered on mountains
for cx in range(40, WIDTH, 180):
    cy = 520 + (cx % 120)
    # Crushed vehicle rectangles stacked
    for stack in range(3):
        sy = cy + stack * 28
        d.rectangle([cx, sy, cx + 90, sy + 22], fill=(36, 30, 32, 255), outline=(18, 14, 18, 255), width=2)
        # Tires
        d.ellipse([cx + 10, sy + 12, cx + 28, sy + 26], fill=(18, 14, 18, 255))
        d.ellipse([cx + 62, sy + 12, cx + 80, sy + 26], fill=(18, 14, 18, 255))

# C. KEY MONUMENTAL SCRAP STRUCTURES (Images 5 & 6)
# 1. Giant Excavator Crane with Hanging Hydraulic Claw (Image 6) at x = 850
crane_x = 850
d.rectangle([crane_x - 22, 200, crane_x + 22, FLOOR_Y], fill=(42, 32, 28, 255))
for ty in range(200, FLOOR_Y, 40):
    d.line([(crane_x - 22, ty), (crane_x + 22, ty + 40)], fill=(65, 48, 40, 255), width=2)
    d.line([(crane_x + 22, ty), (crane_x - 22, ty + 40)], fill=(65, 48, 40, 255), width=2)
# Yellow Crane Arm & Boom
boom_end_x = crane_x + 240
boom_end_y = 90
d.polygon([(crane_x - 30, 220), (crane_x + 30, 190), (boom_end_x, boom_end_y), (boom_end_x - 24, boom_end_y + 30)], fill=(180, 83, 9, 255))
d.line([(crane_x, 210), (boom_end_x - 12, boom_end_y + 15)], fill=(245, 158, 11, 255), width=3)
# Steel hoist cable hanging down
d.line([(boom_end_x - 12, boom_end_y + 15), (boom_end_x - 12, 480)], fill=(120, 130, 145, 255), width=3)
# Heavy 4-tine hydraulic compactor claw
claw_x = boom_end_x - 12
d.rectangle([claw_x - 24, 480, claw_x + 24, 515], fill=(30, 36, 44, 255), outline=(15, 20, 26, 255), width=2)
for tine_x in [-20, -7, 7, 20]:
    d.line([(claw_x + tine_x, 515), (claw_x + tine_x * 1.3, 565)], fill=(51, 65, 85, 255), width=4)
    d.polygon([(claw_x + tine_x * 1.3, 565), (claw_x + tine_x * 1.3 - 4, 575), (claw_x + tine_x * 1.3 + 4, 575)], fill=(180, 83, 9, 255))

# 2. "Junkertown" Fortified Scrap Gate (Image 5 & 7) at x = 1600 (Entrance to Safe Combat Arena)
gate_x = 1600
# Massive towering scrap metal pillars with corrugated panels
d.rectangle([gate_x - 60, 280, gate_x + 60, FLOOR_Y], fill=(50, 40, 38, 255), outline=(24, 18, 18, 255), width=3)
d.rectangle([gate_x + 480, 280, gate_x + 600, FLOOR_Y], fill=(50, 40, 38, 255), outline=(24, 18, 18, 255), width=3)
# Massive overhead iron crossbeam with giant cog gears
d.rectangle([gate_x - 70, 260, gate_x + 610, 320], fill=(70, 52, 46, 255), outline=(24, 18, 18, 255), width=3)
# Giant rotating gears mounted on gate (Image 5)
for gx in [gate_x + 120, gate_x + 420]:
    d.ellipse([gx - 45, 220, gx + 45, 310], fill=(38, 30, 32, 255), outline=(100, 75, 60, 255), width=4)
    d.ellipse([gx - 18, 247, gx + 18, 283], fill=(70, 52, 46, 255))

# 3. Colossal Scrap Chasm ("Groapa de Gunoi") at x = 2800 to 3600
# The ground drops away into darkness, with toxic acid vapors and rusty girders
chasm_start = 2800
chasm_end = 3600
# Acid glow and bottomless mist
for ay in range(FLOOR_Y, HEIGHT):
    p = (ay - FLOOR_Y) / float(HEIGHT - FLOOR_Y)
    d.line([(chasm_start, ay), (chasm_end, ay)], fill=(int(18 + 10 * p), int(35 + 40 * p), int(22 + 15 * p), 255))
# Jagged broken metal girders protruding into chasm
for gy in range(FLOOR_Y + 20, HEIGHT - 20, 35):
    d.line([(chasm_start, gy), (chasm_start + 120, gy + 30)], fill=(45, 35, 30, 255), width=6)
    d.line([(chasm_end, gy), (chasm_end - 120, gy + 30)], fill=(45, 35, 30, 255), width=6)

# Overhead Grappling Cable Suspension Girders across Chasm (y = 480)
d.line([(chasm_start - 60, 480), (chasm_end + 60, 480)], fill=(45, 52, 65, 255), width=8)
for rx in [3000, 3200, 3400]:
    # Cable hanging down
    d.line([(rx, 480), (rx, 570)], fill=(148, 163, 184, 255), width=3)
    # Glowing Anchor Ring for Grappling Hook!
    d.ellipse([rx - 16, 570, rx + 16, 602], fill=(20, 30, 45, 255), outline=(0, 245, 255, 255), width=3)
    d.ellipse([rx - 6, 580, rx + 6, 592], fill=(170, 245, 255, 255))

# 4. Boss Hangar Industrial Complex at x = 4000 to 5200
# Heavy steel riveted blast walls, yellow hazard warning stripes, heavy crane gantry rail
hangar_x = 4000
# Dividing fortified security bulkhead
d.rectangle([hangar_x, 140, hangar_x + 80, FLOOR_Y], fill=(32, 38, 48, 255), outline=(16, 20, 28, 255), width=4)
# Yellow hazard stripes
for hy in range(160, FLOOR_Y, 40):
    d.polygon([(hangar_x + 5, hy), (hangar_x + 75, hy + 30), (hangar_x + 75, hy + 45), (hangar_x + 5, hy + 15)], fill=(234, 179, 8, 255))

# Arena ceiling gantry crane rail (y = 180 to 220)
d.rectangle([hangar_x + 80, 180, WIDTH, 220], fill=(45, 55, 72, 255), outline=(20, 25, 35, 255), width=3)
for gx in range(hangar_x + 100, WIDTH, 60):
    d.line([(gx, 180), (gx + 40, 220)], fill=(71, 85, 105, 255), width=3)
    d.line([(gx + 40, 180), (gx, 220)], fill=(71, 85, 105, 255), width=3)

# D. SOLID FLOOR (y = 780 to 900) - EXCEPT AT THE CHASM!
for fx in range(0, WIDTH, 120):
    if chasm_start <= fx < chasm_end:
        continue # Gap for the death pit!
    # Fence and tire piles along the floor
    d.rectangle([fx, 710, fx + 6, 780], fill=(90, 100, 115, 255))
    d.line([(fx, 715), (fx + 120, 715)], fill=(120, 135, 155, 255), width=2)
    d.line([(fx, 775), (fx + 120, 775)], fill=(70, 80, 95, 255), width=2)
    # Mesh
    for mx in range(fx, fx + 120, 16):
        d.line([(mx, 715), (mx + 16, 775)], fill=(60, 70, 85, 120), width=1)
        d.line([(mx + 16, 715), (mx, 775)], fill=(60, 70, 85, 120), width=1)
    # Tire piles
    if (fx // 120) % 2 == 0:
        tx = fx + 30
        for ty in [764, 752, 740]:
            d.ellipse([tx, ty, tx + 36, ty + 15], fill=(24, 20, 24, 255), outline=(10, 8, 10, 255), width=2)
            d.ellipse([tx + 8, ty + 3, tx + 28, ty + 12], fill=(42, 34, 38, 255))

# Subterranean industrial foundation (y = 780 to 900)
# Segment 1: x = 0 to chasm_start
d.rectangle([0, FLOOR_Y, chasm_start, HEIGHT], fill=(24, 18, 16, 255))
d.line([(0, FLOOR_Y), (chasm_start, FLOOR_Y)], fill=(75, 55, 45, 255), width=3)
# Segment 2: x = chasm_end to WIDTH
d.rectangle([chasm_end, FLOOR_Y, WIDTH, HEIGHT], fill=(24, 18, 16, 255))
d.line([(chasm_end, FLOOR_Y), (WIDTH, FLOOR_Y)], fill=(75, 55, 45, 255), width=3)

# Floor steel plates and rivets
for gx in list(range(0, chasm_start, 40)) + list(range(chasm_end, WIDTH, 40)):
    d.rectangle([gx, FLOOR_Y, gx + 38, FLOOR_Y + 18], fill=(36, 28, 24, 255), outline=(18, 14, 12, 255), width=1)
    d.point([(gx + 8, FLOOR_Y + 4), (gx + 30, FLOOR_Y + 4)], fill=(120, 95, 80, 255))

bg.save(os.path.join(godot_assets, "level_heap_backdrop_5200x900.png"))
bg.save(os.path.join(godot_copy_assets, "level_heap_backdrop_5200x900.png"))
bg.save(os.path.join(anim_dir, "level_heap_backdrop_5200x900.png"))
print("Saved 5200x900 complete static level backdrop successfully.")

# ---------------------------------------------------------------------------
# 2. ENERGY SHIELD SPRITE (64x64)
# Glowing hexagonal energy barrier with pulsing cyber honeycomb pattern
# ---------------------------------------------------------------------------
shield_img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
sd = ImageDraw.Draw(shield_img)
# Hexagonal shield arc
poly_outer = [(28, 4), (46, 16), (54, 32), (46, 48), (28, 60), (22, 56), (40, 44), (46, 32), (40, 20), (22, 8)]
sd.polygon(poly_outer, fill=(0, 215, 255, 80), outline=(0, 245, 255, 240))
# Inner bright core
poly_inner = [(32, 12), (44, 22), (48, 32), (44, 42), (32, 52), (30, 48), (40, 40), (44, 32), (40, 24), (30, 16)]
sd.polygon(poly_inner, fill=(170, 245, 255, 140), outline=(255, 255, 255, 255))
# Honeycomb lines
for hy in [20, 32, 44]:
    sd.line([(24, hy), (46, hy)], fill=(170, 245, 255, 180), width=1)

shield_img.save(os.path.join(godot_assets, "shield_energy_barrier_64x64.png"))
shield_img.save(os.path.join(godot_copy_assets, "shield_energy_barrier_64x64.png"))
print("Saved Energy Shield sprite.")

# ---------------------------------------------------------------------------
# 3. 4 GRENADE TYPES (32x32 each)
# Frag, EMP, Cryo, Fire
# ---------------------------------------------------------------------------
def make_grenade(color_body, color_glow, label):
    img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    gd = ImageDraw.Draw(img)
    # Body oval
    gd.ellipse([9, 9, 23, 27], fill=color_body, outline=(14, 18, 25, 255), width=2)
    # Fuse collar
    gd.rectangle([13, 5, 19, 9], fill=(71, 85, 105, 255), outline=(14, 18, 25, 255), width=1)
    # Pin ring
    gd.ellipse([18, 3, 24, 9], outline=(203, 213, 225, 255), width=1)
    # Energy core band
    gd.line([(10, 17), (22, 17)], fill=color_glow, width=2)
    gd.line([(11, 21), (21, 21)], fill=color_glow, width=2)
    return img

g_frag = make_grenade((180, 83, 9, 255), (251, 191, 36, 255), "FRAG")
g_emp = make_grenade((14, 165, 233, 255), (0, 245, 255, 255), "EMP")
g_cryo = make_grenade((56, 189, 248, 255), (224, 242, 254, 255), "CRYO")
g_fire = make_grenade((220, 38, 38, 255), (249, 115, 22, 255), "FIRE")

g_frag.save(os.path.join(godot_assets, "grenade_frag_32x32.png"))
g_frag.save(os.path.join(godot_copy_assets, "grenade_frag_32x32.png"))
g_emp.save(os.path.join(godot_assets, "grenade_emp_32x32.png"))
g_emp.save(os.path.join(godot_copy_assets, "grenade_emp_32x32.png"))
g_cryo.save(os.path.join(godot_assets, "grenade_cryo_32x32.png"))
g_cryo.save(os.path.join(godot_copy_assets, "grenade_cryo_32x32.png"))
g_fire.save(os.path.join(godot_assets, "grenade_fire_32x32.png"))
g_fire.save(os.path.join(godot_copy_assets, "grenade_fire_32x32.png"))
print("Saved 4 grenade sprites.")

# ---------------------------------------------------------------------------
# 4. GRAPPLING HOOK ANCHOR RING & CABLE (32x32)
# ---------------------------------------------------------------------------
ring_img = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
rd = ImageDraw.Draw(ring_img)
rd.rectangle([13, 0, 19, 8], fill=(71, 85, 105, 255), outline=(14, 18, 25, 255), width=1)
rd.ellipse([4, 6, 28, 30], fill=(15, 23, 42, 255), outline=(0, 245, 255, 255), width=3)
rd.ellipse([10, 12, 22, 24], fill=(0, 0, 0, 0), outline=(170, 245, 255, 255), width=2)
ring_img.save(os.path.join(godot_assets, "grapple_ring_32x32.png"))
ring_img.save(os.path.join(godot_copy_assets, "grapple_ring_32x32.png"))
print("Saved Grappling Ring sprite.")

# ---------------------------------------------------------------------------
# 5. THE CRUSHER TITAN BOSS & COMPACTOR SLAM (128x128 Boss, 80x160 Piston)
# Multi-phase Behemoth with massive industrial hydraulic arm, red sensor eye, and diesel smokestacks
# ---------------------------------------------------------------------------
boss_img = Image.new("RGBA", (512, 128), (0, 0, 0, 0)) # 4 frames: Idle, Slam Windup, Phase 2 Rage, Stunned
bd = ImageDraw.Draw(boss_img)

for f in range(4):
    bx = f * 128
    is_rage = (f == 2)
    is_stun = (f == 3)
    c_armor = (185, 28, 28, 255) if is_rage else (51, 65, 85, 255)
    c_eye = (255, 50, 50, 255) if is_rage else ((251, 191, 36, 255) if not is_stun else (100, 116, 139, 255))

    # Heavy caterpillar treads / reinforced legs at y=90..122
    bd.rectangle([bx + 16, 92, bx + 112, 122], fill=(20, 25, 35, 255), outline=(10, 12, 18, 255), width=3)
    for tx in range(bx + 24, bx + 106, 16):
        bd.ellipse([tx, 96, tx + 14, 118], fill=(38, 48, 64, 255), outline=(15, 20, 28, 255), width=2)

    # Massive industrial armored chassis (x=24..104, y=36..92)
    bd.rectangle([bx + 24, 36, bx + 104, 92], fill=c_armor, outline=(14, 18, 25, 255), width=3)
    # Hazard warning stripes on bottom skirt
    for hx in range(bx + 26, bx + 102, 16):
        bd.polygon([(hx, 88), (hx + 10, 78), (hx + 14, 78), (hx + 4, 88)], fill=(234, 179, 8, 255))

    # Dual Diesel Smokestacks on back
    bd.rectangle([bx + 30, 12, bx + 42, 36], fill=(30, 41, 59, 255), outline=(14, 18, 25, 255), width=2)
    bd.rectangle([bx + 46, 16, bx + 56, 36], fill=(30, 41, 59, 255), outline=(14, 18, 25, 255), width=2)

    # Monolithic Central Eye Visor
    bd.rectangle([bx + 64, 46, bx + 94, 58], fill=(15, 23, 42, 255), outline=(14, 18, 25, 255), width=2)
    bd.rectangle([bx + 68, 49, bx + 90, 55], fill=c_eye)

    # Giant Hydraulic Compactor Fist / Crusher Arm
    if f == 1: # Slam windup (raised high)
        bd.rectangle([bx + 80, 8, bx + 120, 46], fill=(180, 83, 9, 255), outline=(14, 18, 25, 255), width=3)
        bd.line([(bx + 85, 27), (bx + 115, 27)], fill=(245, 158, 11, 255), width=3)
    elif is_stun: # Stunned (collapsed low, sparks flying)
        bd.rectangle([bx + 80, 68, bx + 120, 106], fill=(71, 85, 105, 255), outline=(14, 18, 25, 255), width=3)
        # Spark particles
        bd.point([(bx + 75, 40), (bx + 82, 34), (bx + 95, 38)], fill=(251, 191, 36, 255))
    else: # Normal forward reach
        bd.rectangle([bx + 80, 48, bx + 124, 84], fill=(180, 83, 9, 255), outline=(14, 18, 25, 255), width=3)
        bd.line([(bx + 85, 66), (bx + 119, 66)], fill=(245, 158, 11, 255), width=3)

boss_img.save(os.path.join(godot_assets, "boss_crusher_titan_strip4.png"))
boss_img.save(os.path.join(godot_copy_assets, "boss_crusher_titan_strip4.png"))

# Ceiling Hydraulic Compactor Piston (80x160)
piston_img = Image.new("RGBA", (80, 160), (0, 0, 0, 0))
pd = ImageDraw.Draw(piston_img)
# Hydraulic chrome cylinder
pd.rectangle([24, 0, 56, 120], fill=(148, 163, 184, 255), outline=(30, 41, 59, 255), width=3)
pd.line([(32, 0), (32, 120)], fill=(241, 245, 249, 255), width=4)
# Heavy steel compactor head at bottom
pd.rectangle([4, 120, 76, 158], fill=(180, 83, 9, 255), outline=(14, 18, 25, 255), width=4)
pd.line([(10, 139), (70, 139)], fill=(245, 158, 11, 255), width=4)
piston_img.save(os.path.join(godot_assets, "boss_compactor_piston_80x160.png"))
piston_img.save(os.path.join(godot_copy_assets, "boss_compactor_piston_80x160.png"))
print("Saved Boss Crusher Titan & Compactor Piston sprites.")

print("All level & gameplay assets built successfully!")
