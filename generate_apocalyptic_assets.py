import os
import math
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
sheets_dir = os.path.join(scratch_dir, "animations", "sheets")
godot_assets_dir = os.path.join(scratch_dir, "godot_project", "assets")
godot_40_assets_dir = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")

target_dirs = [sheets_dir, godot_assets_dir, godot_40_assets_dir]

def save_asset(im, filename):
    for d in target_dirs:
        if d and os.path.exists(d):
            im.save(os.path.join(d, filename), "PNG")
    print(f"Saved {filename} ({im.size})")

# -------------------------------------------------------------------------
# PALETTE DEFINITION (Accurate to Scraps & Apocalyptic Scrapyard)
# -------------------------------------------------------------------------
CLR_TRANS = (0, 0, 0, 0)
CLR_TITANIUM = (248, 250, 252, 255)
CLR_TITANIUM_SHADOW = (203, 213, 225, 255)
CLR_FRAME_LIGHT = (100, 116, 139, 255)
CLR_FRAME_MID = (51, 65, 85, 255)
CLR_FRAME_DARK = (30, 41, 59, 255)
CLR_OUTLINE = (14, 18, 25, 255)

CLR_CYAN_GLOW = (0, 245, 255, 255)
CLR_CYAN_MID = (0, 215, 255, 255)
CLR_CYAN_DARK = (2, 132, 199, 255)

CLR_COPPER = (245, 158, 11, 255)
CLR_COPPER_DARK = (180, 83, 9, 255)
CLR_YELLOW_WIRE = (250, 204, 21, 255)

# -------------------------------------------------------------------------
# 1. PERFECT 8-FRAME HUMANOID BIPEDAL WALK CYCLE
# Designed strictly from the user's reference images (media_1794933203970 & media_1794933194079)
# -------------------------------------------------------------------------
# Dimensions: 8 frames of 32x32 -> 256x32 strip
# Structure of Scraps in each frame:
# - Head: x=11..19, y=1..6 (Visor facing right at x=17..20)
# - Torso: x=9..21, y=7..13 (Chest reactor at x=14..16, y=9..10)
# - Pelvis: x=12..18, y=14..17
# - Near Leg (Left - fully lit) & Far Leg (Right - shaded 30% darker for clear depth)

def draw_scraps_humanoid_frame(f_idx, is_damaged=False):
    im = Image.new("RGBA", (32, 32), CLR_TRANS)
    d = ImageDraw.Draw(im)

    # Humanoid gait offsets based on 8-frame cycle:
    # 0: L Contact (L forward, R back)
    # 1: L Down (L foot flat, knee flexes, R leg lifts)
    # 2: L Passing (L straight carrying weight, R knee passing under hip)
    # 3: L Push-off (L toe push, R leg extends forward)
    # 4: R Contact (R forward, L back)
    # 5: R Down (R foot flat, knee flexes, L leg lifts)
    # 6: R Passing (R straight carrying weight, L knee passing under hip)
    # 7: R Push-off (R toe push, L leg extends forward)

    # Vertical torso bob: subtle mechanical 1px cushion on down frames (1 and 5)
    body_y = 1 if f_idx in [1, 5] else 0

    # Arm swing offsets: opposite to leading leg
    # In frames 0-3 (L leg forward), Near arm swings back, Far arm swings forward
    # In frames 4-7 (R leg forward), Near arm swings forward, Far arm swings back
    arm_swing = [ -3, -2, 0, 2, 3, 2, 0, -2 ][f_idx]

    # --- FAR ARM (Behind torso) ---
    if not is_damaged:
        far_arm_x = 11 - arm_swing
        far_arm_y = 9 + body_y
        d.rectangle([far_arm_x, far_arm_y, far_arm_x + 3, far_arm_y + 7], fill=CLR_FRAME_DARK, outline=CLR_OUTLINE)

    # --- FAR LEG (Behind) ---
    # Shaded darker so the player clearly sees which leg is front and back!
    # Positions of far foot (x, y) across 8 frames
    far_leg_pos = [
        (8, 28),   # 0: trailing back
        (10, 27),  # 1: lifting
        (14, 25),  # 2: passing high
        (18, 27),  # 3: reaching forward
        (20, 29),  # 4: forward contact
        (18, 29),  # 5: down flat
        (15, 29),  # 6: passing weight
        (11, 29)   # 7: push off
    ]
    flx, fly = far_leg_pos[f_idx]
    # Far hip to knee
    d.line([(14, 16 + body_y), ((14 + flx) // 2, (18 + fly) // 2)], fill=CLR_FRAME_DARK, width=3)
    # Far knee to foot
    d.line([((14 + flx) // 2, (18 + fly) // 2), (flx, fly)], fill=CLR_FRAME_MID, width=3)
    # Far foot pad
    d.rectangle([flx - 2, fly, flx + 3, fly + 2], fill=CLR_CYAN_DARK, outline=CLR_OUTLINE)

    # --- HEAD ---
    hx = 13
    hy = 1 + body_y
    d.rectangle([hx, hy, hx + 8, hy + 5], fill=CLR_TITANIUM, outline=CLR_OUTLINE)
    d.rectangle([hx + 1, hy + 1, hx + 5, hy + 4], fill=CLR_TITANIUM_SHADOW)
    # Cyan Optic Visor
    d.rectangle([hx + 6, hy + 2, hx + 9, hy + 4], fill=CLR_CYAN_GLOW, outline=CLR_OUTLINE)
    d.point((hx + 7, hy + 3), fill=(255, 255, 255, 255))

    # --- TORSO ---
    tx = 11
    ty = 7 + body_y
    d.rectangle([tx, ty, tx + 9, ty + 6], fill=CLR_FRAME_MID, outline=CLR_OUTLINE)
    d.rectangle([tx + 1, ty + 1, tx + 4, ty + 5], fill=CLR_TITANIUM)
    d.rectangle([tx + 5, ty + 1, tx + 8, ty + 5], fill=CLR_TITANIUM_SHADOW)
    # Cyan Core Reactor
    d.rectangle([tx + 6, ty + 2, tx + 8, ty + 4], fill=CLR_CYAN_GLOW)
    d.point((tx + 7, ty + 3), fill=(255, 255, 255, 255))

    # --- PELVIS ---
    d.rectangle([13, 14 + body_y, 18, 16 + body_y], fill=CLR_FRAME_DARK, outline=CLR_OUTLINE)

    # --- NEAR LEG (In front - full brightness) ---
    near_leg_pos = [
        (20, 29),  # 0: forward contact
        (18, 29),  # 1: down flat
        (15, 29),  # 2: passing weight
        (11, 29),  # 3: push off
        (8, 28),   # 4: trailing back
        (10, 27),  # 5: lifting
        (14, 25),  # 6: passing high
        (18, 27)   # 7: reaching forward
    ]
    nlx, nly = near_leg_pos[f_idx]
    knee_x = (15 + nlx) // 2 + (1 if f_idx in [0, 7] else -1)
    knee_y = (16 + nly) // 2
    # Thigh
    d.line([(15, 16 + body_y), (knee_x, knee_y)], fill=CLR_TITANIUM, width=4)
    d.line([(15, 16 + body_y), (knee_x, knee_y)], fill=CLR_OUTLINE, width=1)
    # Shin
    d.line([(knee_x, knee_y), (nlx, nly)], fill=CLR_TITANIUM_SHADOW, width=3)
    # Knee cap bolt
    d.point((knee_x, knee_y), fill=CLR_FRAME_LIGHT)
    # Near Foot Pad (Cyan power sole)
    d.rectangle([nlx - 2, nly, nlx + 3, nly + 2], fill=CLR_CYAN_GLOW, outline=CLR_OUTLINE)

    # --- NEAR ARM ---
    if is_damaged:
        # Damaged right arm: severed forearm stump with sparking loose wires!
        stump_x = 16 + arm_swing
        stump_y = 8 + body_y
        d.line([(16, 8 + body_y), (stump_x, stump_y + 3)], fill=CLR_FRAME_MID, width=3)
        # Copper & yellow wires hanging
        d.point((stump_x, stump_y + 4), fill=CLR_COPPER)
        d.point((stump_x + (1 if f_idx % 2 == 0 else -1), stump_y + 5), fill=CLR_YELLOW_WIRE)
        d.point((stump_x, stump_y + 6), fill=CLR_COPPER_DARK)
        if f_idx in [0, 4]: # Occasional electric spark
            d.point((stump_x + 1, stump_y + 5), fill=CLR_CYAN_GLOW)
    else:
        # Full titanium arm swinging
        near_arm_x = 16 + arm_swing
        near_arm_y = 9 + body_y
        d.line([(16, 8 + body_y), (near_arm_x, near_arm_y + 4)], fill=CLR_TITANIUM, width=3)
        d.line([(near_arm_x, near_arm_y + 4), (near_arm_x + 1, near_arm_y + 7)], fill=CLR_TITANIUM_SHADOW, width=2)
        d.point((near_arm_x + 1, near_arm_y + 8), fill=CLR_FRAME_MID)

    return im

def build_smooth_8frame_walk_strip(is_damaged=False):
    strip = Image.new("RGBA", (256, 32), CLR_TRANS)
    for i in range(8):
        frame = draw_scraps_humanoid_frame(i, is_damaged)
        strip.paste(frame, (i * 32, 0))
    return strip

# Generate and save both walk strips
strip_std_8 = build_smooth_8frame_walk_strip(is_damaged=False)
save_asset(strip_std_8, "robot_standard_walk_strip8.png")

strip_dmg_8 = build_smooth_8frame_walk_strip(is_damaged=True)
save_asset(strip_dmg_8, "robot_damaged_walk_strip8.png")

# Also update the strip6 files with the first 6 frames of this new clean gait
strip_std_6 = Image.new("RGBA", (192, 32), CLR_TRANS)
for i, idx in enumerate([0, 1, 2, 4, 5, 6]):
    f = strip_std_8.crop((idx * 32, 0, (idx + 1) * 32, 32))
    strip_std_6.paste(f, (i * 32, 0))
save_asset(strip_std_6, "robot_standard_walk_strip6.png")

strip_dmg_6 = Image.new("RGBA", (192, 32), CLR_TRANS)
for i, idx in enumerate([0, 1, 2, 4, 5, 6]):
    f = strip_dmg_8.crop((idx * 32, 0, (idx + 1) * 32, 32))
    strip_dmg_6.paste(f, (i * 32, 0))
save_asset(strip_dmg_6, "robot_damaged_walk_strip6.png")

print("Generated clean humanoid 8-frame walk cycles!")

# -------------------------------------------------------------------------
# 2. INTERACTIVE PLATFORMING PROPS: CRUSHED CAR OBSTACLE & BARREL STACK
# -------------------------------------------------------------------------
# Crushed Car: 64x32 pixel art prop (Rusty, smashed sedan chassis with blown tires)
car_im = Image.new("RGBA", (64, 32), CLR_TRANS)
cd = ImageDraw.Draw(car_im)

# Car body outline & rusty base
cd.polygon([(6, 26), (10, 14), (22, 8), (42, 8), (56, 16), (58, 26)], fill=(120, 53, 15, 255), outline=(40, 20, 10, 255))
# Dented hood & roof
cd.polygon([(11, 15), (22, 9), (41, 9), (54, 17)], fill=(180, 83, 9, 255))
# Crushed cabin dent (collapsed roof)
cd.line([(28, 9), (34, 13), (40, 9)], fill=(60, 30, 15, 255), width=2)
# Shattered front windshield
cd.polygon([(42, 10), (52, 17), (42, 17)], fill=(100, 116, 139, 200), outline=(51, 65, 85, 255))
cd.line([(45, 12), (48, 16)], fill=(203, 213, 225, 255)) # Glass crack
# Flat flattened tires
cd.ellipse([10, 22, 22, 30], fill=(24, 24, 27, 255), outline=(9, 9, 11, 255)) # Front tire
cd.ellipse([42, 22, 54, 30], fill=(24, 24, 27, 255), outline=(9, 9, 11, 255)) # Rear tire
cd.ellipse([13, 24, 19, 28], fill=(63, 63, 70, 255)) # Wheel rim
cd.ellipse([45, 24, 51, 28], fill=(63, 63, 70, 255))
# Rust streaks & scratches
cd.line([(18, 16), (18, 22)], fill=(90, 40, 10, 255))
cd.line([(32, 14), (32, 24)], fill=(90, 40, 10, 255))

save_asset(car_im, "crushed_car_obstacle.png")

# -------------------------------------------------------------------------
# 3. HIGH-DETAIL APOCALYPTIC PARALLAX BACKGROUNDS (1920x540)
# Strictly inspired by user reference photos:
# - Canyon of scrap cars & aircraft wings
# - Colossal cranes & excavator claws
# - Chainlink fence & caution signs
# - Gloomy somber overcast sky
# -------------------------------------------------------------------------
P_W = 1920
P_H = 540

# --- LAYER 1: Deep Somber Overcast Sky & Horizon Smog Spires ---
bg1 = Image.new("RGBA", (P_W, P_H), (18, 16, 20, 255))
d1 = ImageDraw.Draw(bg1)
# Atmospheric dark stormy gradient with sickly yellow toxic horizon
for y in range(P_H):
    t = y / P_H
    # Top: dark stormy slate charcoal -> Bottom: sickly mustard smog haze
    r = int(24 * (1 - t) + 48 * t)
    g = int(20 * (1 - t) + 36 * t)
    b = int(26 * (1 - t) + 20 * t)
    d1.line([(0, y), (P_W, y)], fill=(r, g, b, 255))

# Heavy gloomy cloud silhouettes
for cx in range(0, P_W, 280):
    d1.ellipse([cx - 40, 40, cx + 220, 140], fill=(30, 24, 32, 120))
    d1.ellipse([cx + 60, 60, cx + 340, 160], fill=(26, 20, 28, 140))

# Distant colossal industrial cranes & suspension bridge on horizon (media_1794933393413)
for bx in range(0, P_W, 480):
    # Bridge towers
    d1.rectangle([bx + 80, 180, bx + 95, 380], fill=(38, 30, 36, 180))
    d1.rectangle([bx + 320, 180, bx + 335, 380], fill=(38, 30, 36, 180))
    # Suspension span & cables
    d1.line([(bx + 40, 280), (bx + 380, 280)], fill=(44, 35, 42, 200), width=4)
    d1.arc([bx + 80, 200, bx + 335, 360], start=0, end=180, fill=(40, 32, 38, 180), width=2)
    # Distant towering crane boom
    d1.line([(bx + 200, 360), (bx + 260, 160)], fill=(42, 34, 40, 160), width=5)
    d1.line([(bx + 260, 160), (bx + 310, 180)], fill=(42, 34, 40, 160), width=3)

save_asset(bg1, "bg_layer1_sky.png")

# --- LAYER 2: Colossal Scrap Mountains & Crushed Car Pyramids ---
bg2 = Image.new("RGBA", (P_W, P_H), (0, 0, 0, 0))
d2 = ImageDraw.Draw(bg2)

# Jagged, towering mounds of crushed vehicles, chassis, and metal plates
for sx in range(-60, P_W + 120, 140):
    peak_y = 200 + ((sx * 31) % 110)
    # Mountain base
    d2.polygon([(sx, P_H), (sx + 70, peak_y), (sx + 150, P_H)], fill=(42, 32, 36, 240), outline=(28, 20, 24, 255))
    # Terraced crushed car silhouettes inside the scrap mountain
    for cy in range(peak_y + 40, P_H, 45):
        cx = sx + 20 + ((cy * 13) % 40)
        d2.rectangle([cx, cy, cx + 55, cy + 18], fill=(55, 40, 42, 220), outline=(32, 24, 28, 255), width=2)
        # Small window aperture on crushed car
        d2.rectangle([cx + 10, cy + 4, cx + 24, cy + 10], fill=(25, 20, 25, 200))
    # Giant collapsed jet aircraft wing or girder sticking out
    if sx % 280 == 0:
        d2.polygon([(sx + 50, peak_y + 10), (sx + 110, peak_y - 70), (sx + 125, peak_y - 65), (sx + 65, peak_y + 30)],
                   fill=(60, 48, 52, 245), outline=(35, 26, 30, 255))

save_asset(bg2, "bg_layer2_distant_scrap.png")

# --- LAYER 3: Midground Scaffolding, Excavator Booms & Dangling Claws ---
bg3 = Image.new("RGBA", (P_W, P_H), (0, 0, 0, 0))
d3 = ImageDraw.Draw(bg3)

for mx in range(40, P_W, 360):
    # Giant yellow/rusty excavator crane arm (media_1794933424885)
    d3.polygon([(mx, 420), (mx + 25, 420), (mx + 90, 140), (mx + 70, 135)], fill=(120, 75, 20, 245), outline=(40, 25, 10, 255), width=2)
    d3.polygon([(mx + 80, 140), (mx + 160, 160), (mx + 155, 175), (mx + 75, 150)], fill=(140, 85, 22, 245), outline=(40, 25, 10, 255), width=2)
    # Cable hanging from crane tip
    d3.line([(mx + 158, 168), (mx + 158, 270)], fill=(60, 50, 55, 255), width=2)
    # Dangling 3-pronged scrap grab claw!
    claw_x, claw_y = mx + 158, 270
    d3.polygon([(claw_x - 8, claw_y), (claw_x + 8, claw_y), (claw_x, claw_y + 8)], fill=(80, 65, 70, 255))
    d3.line([(claw_x - 6, claw_y + 8), (claw_x - 14, claw_y + 24)], fill=(80, 65, 70, 255), width=3)
    d3.line([(claw_x + 6, claw_y + 8), (claw_x + 14, claw_y + 24)], fill=(80, 65, 70, 255), width=3)
    d3.line([(claw_x, claw_y + 8), (claw_x, claw_y + 26)], fill=(80, 65, 70, 255), width=3)

    # Corrugated iron wall / Junkertown barrier (media_1794933402801)
    d3.rectangle([mx + 220, 260, mx + 310, P_H], fill=(65, 50, 45, 240), outline=(35, 25, 20, 255), width=2)
    # Industrial pipe conduit running across
    d3.rectangle([mx + 180, 310, mx + 340, 325], fill=(50, 40, 45, 255), outline=(25, 20, 25, 255), width=2)

save_asset(bg3, "bg_layer3_midground_pipes.png")

# --- LAYER 4: Foreground Chainlink Fences, Hazard Signs & Tire Piles ---
bg4 = Image.new("RGBA", (P_W, P_H), (0, 0, 0, 0))
d4 = ImageDraw.Draw(bg4)

for fx in range(0, P_W, 240):
    # Chainlink fence posts & mesh (media_1794933447619)
    d4.line([(fx, 340), (fx, P_H)], fill=(75, 65, 70, 255), width=4)
    d4.line([(fx + 120, 340), (fx + 120, P_H)], fill=(75, 65, 70, 255), width=4)
    d4.line([(fx, 350), (fx + 120, 350)], fill=(60, 50, 55, 255), width=2)
    d4.line([(fx, 420), (fx + 120, 420)], fill=(60, 50, 55, 255), width=2)

    # Fence criss-cross wires
    for fy in range(350, 440, 15):
        d4.line([(fx, fy), (fx + 120, fy + 12)], fill=(50, 42, 48, 160), width=1)
        d4.line([(fx, fy + 12), (fx + 120, fy)], fill=(50, 42, 48, 160), width=1)

    # Yellow / Black Warning Sign ("DANGER", "KEEP OUT")
    if fx % 480 == 0:
        d4.rectangle([fx + 30, 365, fx + 85, 395], fill=(234, 179, 8, 255), outline=(15, 23, 42, 255), width=2)
        d4.rectangle([fx + 33, 368, fx + 82, 392], outline=(15, 23, 42, 255), width=1)
        # Skull or hazard symbol lines
        d4.line([(fx + 40, 380), (fx + 75, 380)], fill=(15, 23, 42, 255), width=2)
        d4.line([(fx + 45, 385), (fx + 70, 385)], fill=(15, 23, 42, 255), width=1)

    # Stack of weathered black tires
    tire_x = fx + 150
    for ty in [430, 442, 454]:
        d4.ellipse([tire_x, ty, tire_x + 36, ty + 16], fill=(28, 25, 28, 255), outline=(12, 10, 12, 255), width=2)
        d4.ellipse([tire_x + 8, ty + 4, tire_x + 28, ty + 12], fill=(45, 38, 42, 255))

save_asset(bg4, "bg_layer4_foreground_girders.png")

print("All apocalyptic background layers and crushed car prop generated successfully!")
