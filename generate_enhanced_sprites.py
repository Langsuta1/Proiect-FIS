import math
import random
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
sheets_dir = os.path.join(scratch_dir, "animations", "sheets") if "os" in locals() else None

import os
sheets_dir = os.path.join(scratch_dir, "animations", "sheets")
godot_assets_dir = os.path.join(scratch_dir, "godot_project", "assets")
godot_40_assets_dir = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")

target_dirs = [sheets_dir, godot_assets_dir, godot_40_assets_dir]

# Helper to save to all active asset directories
def save_asset(im, filename):
    for d in target_dirs:
        if d and os.path.exists(d):
            im.save(os.path.join(d, filename), "PNG")
    print(f"Saved {filename} ({im.size}) to active asset directories.")

# -------------------------------------------------------------------------
# 1. ENHANCED 8-FRAME WALK CYCLES (Smooth Mechanical Stride, No Gallop!)
# -------------------------------------------------------------------------
# Load original 6-frame standard walk to sample exact pixels
orig_std = Image.open(os.path.join(sheets_dir, "robot_standard_walk_strip6.png")).convert("RGBA")
orig_dmg = Image.open(os.path.join(sheets_dir, "robot_damaged_walk_strip6.png")).convert("RGBA")
orig_idle = Image.open(os.path.join(sheets_dir, "robot_standard_idle_strip4.png")).convert("RGBA")

# Extract base body components from the original sprite
# Frame 0 is contact, Frame 1 is recoil, Frame 3 is right contact...
# For 8 frames, we build:
# 0: Left Contact
# 1: Left Down (Recoil / cushion)
# 2: Left Pass (New smooth transition frame: foot rolls, knee level)
# 3: Left Push-off (Smooth lift)
# 4: Right Contact
# 5: Right Down (Recoil / cushion)
# 6: Right Pass (New smooth transition frame: foot rolls, knee level)
# 7: Right Push-off (Smooth lift)

def generate_smooth_walk_strip(is_damaged=False):
    src = orig_dmg if is_damaged else orig_std
    strip = Image.new("RGBA", (256, 32), (0, 0, 0, 0))

    # Base reference frames from the original
    f_contact_l = src.crop((0, 0, 32, 32))
    f_down_l    = src.crop((32, 0, 64, 32))
    f_up_l      = src.crop((64, 0, 96, 32))
    f_contact_r = src.crop((96, 0, 128, 32))
    f_down_r    = src.crop((128, 0, 160, 32))
    f_up_r      = src.crop((160, 0, 192, 32))

    # Create synthetic smooth passing frame 2 (between down_l and up_l)
    f_pass_l = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    # Blend torso stably at y=1 (neutral position, no jumping!)
    torso_neutral = f_contact_l.crop((0, 0, 32, 22))
    f_pass_l.paste(torso_neutral, (0, 0))
    # Passing leg: both feet under center, left passing forward, right planted
    legs_pass_l = f_down_l.crop((0, 20, 32, 32))
    f_pass_l.paste(legs_pass_l, (0, 20), legs_pass_l)

    # Create synthetic smooth passing frame 6 (between down_r and up_r)
    f_pass_r = Image.new("RGBA", (32, 32), (0, 0, 0, 0))
    f_pass_r.paste(torso_neutral, (0, 0))
    legs_pass_r = f_down_r.crop((0, 20, 32, 32))
    f_pass_r.paste(legs_pass_r, (0, 20), legs_pass_r)

    # Assemble 8 frames
    frames = [
        f_contact_l, # 0: Contact L
        f_down_l,    # 1: Cushion L
        f_pass_l,    # 2: Transition Pass L (New!)
        f_up_l,      # 3: Push-off L
        f_contact_r, # 4: Contact R
        f_down_r,    # 5: Cushion R
        f_pass_r,    # 6: Transition Pass R (New!)
        f_up_r       # 7: Push-off R
    ]

    for idx, frm in enumerate(frames):
        strip.paste(frm, (idx * 32, 0))

    return strip

strip_std_8 = generate_smooth_walk_strip(is_damaged=False)
save_asset(strip_std_8, "robot_standard_walk_strip8.png")

strip_dmg_8 = generate_smooth_walk_strip(is_damaged=True)
save_asset(strip_dmg_8, "robot_damaged_walk_strip8.png")

# Also overwrite the strip6 with stabilized frames so any code referencing strip6 also immediately looks smooth
strip_std_6_smooth = Image.new("RGBA", (192, 32), (0, 0, 0, 0))
for i, fidx in enumerate([0, 1, 2, 4, 5, 6]):
    f = strip_std_8.crop((fidx * 32, 0, (fidx + 1) * 32, 32))
    strip_std_6_smooth.paste(f, (i * 32, 0))
save_asset(strip_std_6_smooth, "robot_standard_walk_strip6.png")

strip_dmg_6_smooth = Image.new("RGBA", (192, 32), (0, 0, 0, 0))
for i, fidx in enumerate([0, 1, 2, 4, 5, 6]):
    f = strip_dmg_8.crop((fidx * 32, 0, (fidx + 1) * 32, 32))
    strip_dmg_6_smooth.paste(f, (i * 32, 0))
save_asset(strip_dmg_6_smooth, "robot_damaged_walk_strip6.png")

# -------------------------------------------------------------------------
# 2. ENEMY SPRITE SHEETS (Native 32x32 & 64x64 Pixel Art)
# -------------------------------------------------------------------------

# Palette for enemies
C_DARK_SLATE = (30, 41, 59, 255)
C_SLATE = (51, 65, 85, 255)
C_LIGHT_SLATE = (100, 116, 139, 255)
C_RUST = (120, 53, 15, 255)
C_BRONZE = (180, 83, 9, 255)
C_EYE_RED = (239, 68, 68, 255)
C_EYE_GLOW = (248, 113, 113, 255)
C_CYAN_CORE = (0, 245, 255, 255)
C_HAZARD_YELLOW = (250, 204, 21, 255)
C_HAZARD_BLACK = (15, 23, 42, 255)

# A. Junk Drone (128x32 -> 4 frames of 32x32)
drone_strip = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
d_draw = ImageDraw.Draw(drone_strip)

for i in range(4):
    ox = i * 32
    bob = int(math.sin(i * math.pi / 2) * 2)

    # 1. Main Spherical Drone Chassis
    d_draw.rectangle([ox + 8, 10 + bob, ox + 24, 24 + bob], fill=C_SLATE, outline=C_DARK_SLATE)
    d_draw.rectangle([ox + 10, 8 + bob, ox + 22, 10 + bob], fill=C_LIGHT_SLATE)
    d_draw.rectangle([ox + 10, 24 + bob, ox + 22, 26 + bob], fill=C_DARK_SLATE)

    # 2. Red Sensor Visor
    d_draw.rectangle([ox + 18, 14 + bob, ox + 24, 18 + bob], fill=C_EYE_RED)
    d_draw.point((ox + 21, 15 + bob), fill=C_EYE_GLOW)

    # 3. Overhead Dual Rotors (Cycling angles)
    rotor_angles = [0, 45, 90, 135]
    ang = rotor_angles[i]
    d_draw.line([(ox + 16, 6 + bob), (ox + 16, 8 + bob)], fill=C_LIGHT_SLATE, width=2) # Rotor shaft
    rw = int(math.cos(math.radians(ang)) * 12)
    d_draw.line([(ox + 16 - rw, 6 + bob), (ox + 16 + rw, 6 + bob)], fill=(203, 213, 225, 220), width=2)
    # Rotor motion blur tips
    d_draw.point((ox + 16 - rw, 6 + bob), fill=(248, 250, 252, 255))
    d_draw.point((ox + 16 + rw, 6 + bob), fill=(248, 250, 252, 255))

    # 4. Bottom Thruster Plasma Exhaust
    t_colors = [C_CYAN_CORE, (56, 189, 248, 255), (14, 165, 233, 255), (2, 132, 199, 255)]
    tc = t_colors[i % len(t_colors)]
    t_len = 3 + (i % 3) * 2
    d_draw.line([(ox + 16, 26 + bob), (ox + 16, 26 + bob + t_len)], fill=tc, width=2)

save_asset(drone_strip, "enemy_junk_drone_strip4.png")

# B. Scrap Crawler (128x32 -> 4 frames of 32x32)
crawler_strip = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
c_draw = ImageDraw.Draw(crawler_strip)

for i in range(4):
    ox = i * 32
    # Body chassis
    c_draw.rectangle([ox + 6, 14, ox + 26, 24], fill=C_RUST, outline=C_DARK_SLATE)
    c_draw.rectangle([ox + 8, 12, ox + 24, 14], fill=C_BRONZE)

    # Front Pincers / Hydraulic Jaws
    jaw_spread = 2 if i % 2 == 0 else 4
    c_draw.polygon([(ox + 26, 17 - jaw_spread), (ox + 30, 16), (ox + 26, 19)], fill=C_LIGHT_SLATE)
    c_draw.polygon([(ox + 26, 21 + jaw_spread), (ox + 30, 22), (ox + 26, 19)], fill=C_LIGHT_SLATE)

    # Optic Sensor
    c_draw.rectangle([ox + 22, 15, ox + 25, 17], fill=C_HAZARD_YELLOW)

    # Multi-Legs (Scuttling motion cycle)
    leg_offsets = [
        [(8, 24, 6, 30), (14, 24, 15, 30), (20, 24, 24, 30)],
        [(8, 24, 10, 30), (14, 24, 13, 30), (20, 24, 22, 30)],
        [(8, 24, 7, 30), (14, 24, 16, 30), (20, 24, 21, 30)],
        [(8, 24, 5, 30), (14, 24, 12, 30), (20, 24, 25, 30)]
    ]
    for lx1, ly1, lx2, ly2 in leg_offsets[i]:
        c_draw.line([(ox + lx1, ly1), (ox + lx2, ly2)], fill=C_DARK_SLATE, width=2)
        c_draw.point((ox + lx2, ly2), fill=C_BRONZE)

save_asset(crawler_strip, "enemy_scrap_crawler_strip4.png")

# C. Boss: The Crusher (256x64 -> 4 frames of 64x64)
crusher_strip = Image.new("RGBA", (256, 64), (0, 0, 0, 0))
b_draw = ImageDraw.Draw(crusher_strip)

for i in range(4):
    ox = i * 64

    # 1. Main Armored Hull
    b_draw.rectangle([ox + 12, 16, ox + 52, 54], fill=(69, 10, 10, 255), outline=(127, 29, 29, 255), width=2)
    b_draw.rectangle([ox + 16, 20, ox + 48, 50], fill=(185, 28, 28, 255))

    # 2. Dual Smokestacks on top
    b_draw.rectangle([ox + 18, 6, ox + 24, 16], fill=C_DARK_SLATE)
    b_draw.rectangle([ox + 40, 6, ox + 46, 16], fill=C_DARK_SLATE)
    # Smoke & Embers puffing
    smoke_h = 3 + (i % 2) * 3
    b_draw.ellipse([ox + 17, 3 - smoke_h, ox + 25, 6], fill=(100, 116, 139, 180))
    b_draw.ellipse([ox + 39, 3 - smoke_h, ox + 47, 6], fill=(249, 115, 22, 180))

    # 3. Menacing Multi-Optic Sensor Array
    b_draw.rectangle([ox + 32, 24, ox + 46, 30], fill=C_HAZARD_YELLOW)
    b_draw.rectangle([ox + 34, 25, ox + 38, 29], fill=C_EYE_RED)

    # 4. Colossal Hydraulic Compactor Arm
    fist_offset = (i % 2) * 3
    b_draw.rectangle([ox + 42, 32 + fist_offset, ox + 60, 56 + fist_offset], fill=C_DARK_SLATE, outline=C_LIGHT_SLATE)
    # Hazard warning stripes on compactor ram
    for s in range(ox + 44, ox + 58, 4):
        b_draw.line([(s, 34 + fist_offset), (s + 3, 54 + fist_offset)], fill=C_HAZARD_YELLOW, width=2)

    # 5. Heavy Tank Treads / Feet
    b_draw.rectangle([ox + 10, 52, ox + 54, 62], fill=C_DARK_SLATE)
    for tx in range(ox + 14, ox + 52, 8):
        b_draw.ellipse([tx, 54, tx + 6, 60], fill=C_LIGHT_SLATE)

save_asset(crusher_strip, "boss_crusher_strip4.png")

# -------------------------------------------------------------------------
# 3. DYNAMIC MULTI-LAYER PARALLAX BACKGROUNDS (Ori & Will of the Wisps Style)
# -------------------------------------------------------------------------
# Dimensions: 1920x540 seamless horizontal tiling
P_WIDTH = 1920
P_HEIGHT = 540

# Layer 1: Deep Sky & Atmospheric Smog Horizon (motion_scale: 0.05, 0.05)
layer1 = Image.new("RGBA", (P_WIDTH, P_HEIGHT), (12, 10, 16, 255))
l1_draw = ImageDraw.Draw(layer1)
# Atmospheric gradient
for y in range(P_HEIGHT):
    t = y / P_HEIGHT
    r = int(35 * (1 - t) + 12 * t)
    g = int(22 * (1 - t) + 10 * t)
    b = int(14 * (1 - t) + 18 * t)
    l1_draw.line([(0, y), (P_WIDTH, y)], fill=(r, g, b, 255))
# Distant factory smoke plumes & lightning glow
for px in range(0, P_WIDTH, 160):
    l1_draw.polygon([(px, P_HEIGHT), (px + 60, 180 + (px % 70)), (px + 120, P_HEIGHT)], fill=(24, 18, 22, 180))
save_asset(layer1, "bg_layer1_sky.png")

# Layer 2: Distant Mountains of Scrap & Collapsed Titans (motion_scale: 0.18, 0.12)
layer2 = Image.new("RGBA", (P_WIDTH, P_HEIGHT), (0, 0, 0, 0))
l2_draw = ImageDraw.Draw(layer2)
# Sprawling scrap mountain silhouettes
for px in range(-40, P_WIDTH + 80, 120):
    mh = 220 + (px * 37 % 140)
    l2_draw.polygon([(px, P_HEIGHT), (px + 70, P_HEIGHT - mh), (px + 140, P_HEIGHT)], fill=(32, 24, 28, 210))
    # Giant collapsed crane silhouette
    if px % 360 == 0:
        l2_draw.line([(px + 40, P_HEIGHT - mh), (px + 90, P_HEIGHT - mh - 90)], fill=(45, 34, 40, 240), width=6)
        l2_draw.line([(px + 90, P_HEIGHT - mh - 90), (px + 150, P_HEIGHT - mh - 70)], fill=(45, 34, 40, 240), width=4)
save_asset(layer2, "bg_layer2_distant_scrap.png")

# Layer 3: Midground Industrial Structures & Dangling Cables (motion_scale: 0.45, 0.25)
layer3 = Image.new("RGBA", (P_WIDTH, P_HEIGHT), (0, 0, 0, 0))
l3_draw = ImageDraw.Draw(layer3)
# Hanging high-voltage cable catenaries
for cx in range(0, P_WIDTH, 320):
    l3_draw.arc([cx - 40, 140, cx + 360, 340], start=0, end=180, fill=(50, 40, 48, 230), width=3)
    l3_draw.arc([cx, 170, cx + 320, 360], start=0, end=180, fill=(35, 28, 36, 200), width=2)
# Vertical scaffolding towers
for tx in range(60, P_WIDTH, 240):
    l3_draw.rectangle([tx, 160, tx + 24, P_HEIGHT], fill=(42, 34, 44, 240), outline=(60, 48, 62, 255), width=2)
    # Crossbeams
    for cy in range(180, P_HEIGHT, 40):
        l3_draw.line([(tx, cy), (tx + 24, cy + 20)], fill=(55, 45, 58, 220), width=2)
        l3_draw.line([(tx, cy + 20), (tx + 24, cy)], fill=(55, 45, 58, 220), width=2)
save_asset(layer3, "bg_layer3_midground_pipes.png")

# Layer 4: Near Industrial Details & Warning Beacons (motion_scale: 0.75, 0.45)
layer4 = Image.new("RGBA", (P_WIDTH, P_HEIGHT), (0, 0, 0, 0))
l4_draw = ImageDraw.Draw(layer4)
# Scrap chutes & vents
for sx in range(120, P_WIDTH, 480):
    l4_draw.polygon([(sx, 0), (sx + 40, 0), (sx + 80, 160), (sx + 20, 160)], fill=(28, 22, 30, 245), outline=(48, 38, 52, 255), width=2)
    # Flickering amber beacon light
    l4_draw.ellipse([sx + 35, 162, sx + 45, 172], fill=(245, 158, 11, 230))
    l4_draw.ellipse([sx + 30, 157, sx + 50, 177], fill=(245, 158, 11, 60))
save_asset(layer4, "bg_layer4_foreground_girders.png")

print("All enhanced sprites and parallax backgrounds successfully generated!")
