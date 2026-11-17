import os
from PIL import Image

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")
anim_dir = os.path.join(scratch_dir, "animations", "sheets")

# Load reference idle images
idle_std = Image.open(os.path.join(godot_assets, "robot_standard_idle_strip4.png"))
idle_dmg = Image.open(os.path.join(godot_assets, "robot_damaged_idle_strip4.png"))
f0_std = idle_std.crop((0, 0, 32, 32))
f0_dmg = idle_dmg.crop((0, 0, 32, 32))

# ---------------------------------------------------------------------------
# COLOR CONSTANTS FROM EXACT IDLE ROBOT
# ---------------------------------------------------------------------------
C_TRANS = (0, 0, 0, 0)
C_OUTLINE = (14, 18, 25, 255)
C_SLATE = (51, 65, 85, 255)
C_DARK_SLATE = (30, 41, 59, 255)
C_WHITE = (248, 250, 252, 255)
C_WHITE_SHADE = (203, 213, 225, 255)
C_CYAN_CORE = (0, 245, 255, 255)
C_CYAN_HI = (170, 245, 255, 255)
C_CYAN_DEEP = (0, 215, 255, 255)
C_COPPER = (217, 119, 6, 255)
C_COPPER_HI = (245, 158, 11, 255)

# Weapon colors
C_PAN_HANDLE = (71, 85, 105, 255)
C_PAN_IRON = (30, 41, 59, 255)
C_PAN_RIM = (148, 163, 184, 255)
C_PAN_CORE = (251, 191, 36, 255)
C_WIND_CORE = (255, 255, 255, 245)
C_WIND_CYAN = (56, 189, 248, 220)
C_WIND_FADE = (14, 165, 233, 120)

C_BAT_GRIP = (180, 83, 9, 255)
C_BAT_STEEL = (156, 163, 175, 255)
C_BAT_SPIKE = (254, 240, 138, 255)
C_BAT_WIND = (245, 158, 11, 210)

def extract_part(src, rect):
    # rect: (x1, y1, x2, y2) inclusive
    part = Image.new("RGBA", (rect[2] - rect[0] + 1, rect[3] - rect[1] + 1), C_TRANS)
    for y in range(rect[1], rect[3] + 1):
        for x in range(rect[0], rect[2] + 1):
            part.putpixel((x - rect[0], y - rect[1]), src.getpixel((x, y)))
    return part

# Extract exact head and torso from idle robot
# Head: x=10..22, y=1..6
head_std = extract_part(f0_std, (10, 1, 22, 6))
head_dmg = extract_part(f0_dmg, (10, 1, 22, 6))

# Torso with shoulder pauldron and glowing cyan core: x=7..24, y=7..13
torso_std = extract_part(f0_std, (7, 7, 24, 13))
torso_dmg = extract_part(f0_dmg, (7, 7, 24, 13))

# Torso without right arm (for when arm is swung or shooting):
# In idle, right arm is at x=18..24, y=8..14
torso_no_arm_std = extract_part(f0_std, (7, 7, 18, 13))
torso_no_arm_dmg = extract_part(f0_dmg, (7, 7, 18, 13))

# Pelvis & thighs base: x=8..20, y=14..18
pelvis_std = extract_part(f0_std, (8, 14, 20, 18))
pelvis_dmg = extract_part(f0_dmg, (8, 14, 20, 18))

print("Extracted exact idle components successfully.")

# ---------------------------------------------------------------------------
# 1. CROUCH SPRITES (2 frames, 32x32 each) - 100% FAITHFUL TO IDLE ROBOT
# ---------------------------------------------------------------------------
def build_faithful_crouch(is_damaged=False):
    sheet = Image.new("RGBA", (64, 32), C_TRANS)
    h = head_dmg if is_damaged else head_std
    t = torso_dmg if is_damaged else torso_std

    for frame in range(2):
        ox = frame * 32
        bob = 1 if frame == 1 else 0

        # Feet: exact same magnetic cyan boots flat on ground at y=28..30
        # Back boot at x=4..10, Front boot at x=14..20
        for bx in [ox + 4, ox + 14]:
            sheet.paste(extract_part(f0_std, (2, 28, 8, 30)), (bx, 28))

        # Bent knees / folded digitigrade shins at y=20..27
        # Back leg shin & thigh
        for y in range(20, 28):
            sheet.putpixel((ox + 6, y), C_OUTLINE)
            sheet.putpixel((ox + 7, y), C_SLATE)
            sheet.putpixel((ox + 8, y), C_WHITE_SHADE if y < 24 else C_SLATE)
            sheet.putpixel((ox + 9, y), C_OUTLINE)

        # Front leg bent forward
        for y in range(20, 28):
            sheet.putpixel((ox + 16, y), C_OUTLINE)
            sheet.putpixel((ox + 17, y), C_WHITE)
            sheet.putpixel((ox + 18, y), C_CYAN_CORE if y == 23 else C_WHITE_SHADE)
            sheet.putpixel((ox + 19, y), C_OUTLINE)

        # Torso: EXACT IDLE TORSO lowered by 6 pixels to y=13 + bob!
        # Head: EXACT IDLE HEAD lowered by 6 pixels to y=7 + bob!
        sheet.paste(t, (ox + 7, 13 + bob), t)
        sheet.paste(h, (ox + 10, 7 + bob), h)

    return sheet

crouch_std = build_faithful_crouch(False)
crouch_dmg = build_faithful_crouch(True)

crouch_std.save(os.path.join(godot_assets, "robot_standard_crouch_strip2.png"))
crouch_dmg.save(os.path.join(godot_assets, "robot_damaged_crouch_strip2.png"))
crouch_std.save(os.path.join(anim_dir, "robot_standard_crouch_strip2.png"))
crouch_dmg.save(os.path.join(anim_dir, "robot_damaged_crouch_strip2.png"))
crouch_std.save(os.path.join(godot_copy_assets, "robot_standard_crouch_strip2.png"))
crouch_dmg.save(os.path.join(godot_copy_assets, "robot_damaged_crouch_strip2.png"))
print("Saved faithful crouch sprites.")


# ---------------------------------------------------------------------------
# 2. WALK CYCLE (8 frames, 32x32 each) - 100% FAITHFUL TO IDLE ROBOT
# ---------------------------------------------------------------------------
def build_faithful_walk(is_damaged=False):
    sheet = Image.new("RGBA", (256, 32), C_TRANS)
    h = head_dmg if is_damaged else head_std
    t = torso_dmg if is_damaged else torso_std

    # 8-frame walk offsets for feet: (back_x, back_y, front_x, front_y)
    walk_poses = [
        # 0: Contact
        (2, 28, 16, 28),
        # 1: Down (bob down 1px)
        (4, 28, 14, 28),
        # 2: Passing
        (7, 27, 12, 28),
        # 3: High (front foot reaching ahead)
        (10, 26, 10, 28),
        # 4: Opposite Contact
        (16, 28, 2, 28),
        # 5: Down (bob down 1px)
        (14, 28, 4, 28),
        # 6: Passing
        (12, 28, 7, 27),
        # 7: High
        (10, 28, 10, 26)
    ]

    for f in range(8):
        ox = f * 32
        bx, by, fx, fy = walk_poses[f]
        bob = 1 if (f in [1, 5]) else 0

        # Draw Back Leg (darker shaded digitigrade)
        # Boot
        boot_back = extract_part(f0_std, (2, 28, 8, 30))
        sheet.paste(boot_back, (ox + bx, by), boot_back)
        # Shin & Thigh connecting hip (11, 14) to boot (bx+3, by)
        for step in range(14, by):
            prog = (step - 14) / float(by - 14)
            cur_x = int(11 + (bx + 3 - 11) * prog)
            sheet.putpixel((ox + cur_x - 1, step), C_OUTLINE)
            sheet.putpixel((ox + cur_x, step), C_SLATE)
            sheet.putpixel((ox + cur_x + 1, step), C_DARK_SLATE)
            sheet.putpixel((ox + cur_x + 2, step), C_OUTLINE)

        # Draw Front Leg (white armor + cyan accent)
        boot_front = extract_part(f0_std, (11, 28, 17, 30))
        sheet.paste(boot_front, (ox + fx, fy), boot_front)
        # Front shin & thigh connecting hip (14, 14) to boot (fx+3, fy)
        for step in range(14, fy):
            prog = (step - 14) / float(fy - 14)
            cur_x = int(14 + (fx + 3 - 14) * prog)
            sheet.putpixel((ox + cur_x - 1, step), C_OUTLINE)
            sheet.putpixel((ox + cur_x, step), C_WHITE if step > 20 else C_WHITE_SHADE)
            sheet.putpixel((ox + cur_x + 1, step), C_CYAN_CORE if step in [17, 18] else C_WHITE)
            sheet.putpixel((ox + cur_x + 2, step), C_OUTLINE)

        # Torso and Head: EXACT IDLE ROBOT with 1px walk bob!
        sheet.paste(t, (ox + 7, 7 + bob), t)
        sheet.paste(h, (ox + 10, 1 + bob), h)

    return sheet

walk_std = build_faithful_walk(False)
walk_dmg = build_faithful_walk(True)

walk_std.save(os.path.join(godot_assets, "robot_standard_walk_strip8.png"))
walk_dmg.save(os.path.join(godot_assets, "robot_damaged_walk_strip8.png"))
walk_std.save(os.path.join(anim_dir, "robot_standard_walk_strip8.png"))
walk_dmg.save(os.path.join(anim_dir, "robot_damaged_walk_strip8.png"))
walk_std.save(os.path.join(godot_copy_assets, "robot_standard_walk_strip8.png"))
walk_dmg.save(os.path.join(godot_copy_assets, "robot_damaged_walk_strip8.png"))
print("Saved faithful walk strips.")


# ---------------------------------------------------------------------------
# 3. PAN ATTACK SPRITES (4 frames, 48x32 each) - 100% FAITHFUL TO IDLE ROBOT
# The exact idle robot torso, head, and legs, with his arm swinging the Cyber Pan!
# ---------------------------------------------------------------------------
def build_faithful_pan_attack(is_damaged=False):
    sheet = Image.new("RGBA", (192, 32), C_TRANS)
    h = head_dmg if is_damaged else head_std
    t_no_arm = torso_no_arm_dmg if is_damaged else torso_no_arm_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    # Base legs from idle
    legs = extract_part(f0_std, (2, 14, 25, 30))

    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)

    for f in range(4):
        ox = f * 48

        # --- Base Body: EXACT IDLE LEGS, TORSO & HEAD ---
        # Legs: planted firmly in combat stance
        sheet.paste(legs, (ox + 2, 14), legs)

        # Torso (without right arm)
        sheet.paste(t_no_arm, (ox + 7, 7), t_no_arm)
        # Head
        sheet.paste(h, (ox + 10, 1), h)

        # --- DYNAMIC SWINGING RIGHT ARM & CYBER PAN ---
        # Shoulder socket is at (ox + 18, 8)
        sh_x = ox + 18
        sh_y = 8

        # Frame 0: Windup (arm cocked back at shoulder level)
        if f == 0:
            # Arm: shoulder (sh_x, 8) -> elbow (sh_x - 3, 7) -> hand (sh_x - 2, 10)
            draw.line([(sh_x, 8), (sh_x - 3, 7)], fill=C_SLATE, width=2)
            draw.line([(sh_x - 3, 7), (sh_x - 2, 10)], fill=copper_color, width=2)
            draw.rectangle([sh_x - 3, 10, sh_x - 1, 12], fill=C_OUTLINE) # Hand

            # Cyber Pan held at hand level: handle (sh_x - 2, 11) up-left to (sh_x - 7, 6)
            draw.line([(sh_x - 2, 11), (sh_x - 7, 6)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([sh_x - 13, 1, sh_x - 5, 9], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(sh_x - 11, 5), (sh_x - 7, 5)], fill=C_PAN_CORE, width=1)
            # Windup aura
            draw.arc([sh_x - 14, 0, sh_x - 4, 10], start=160, end=300, fill=C_WIND_FADE, width=1)

        # Frame 1: Downswing (arm swinging forward from shoulder)
        elif f == 1:
            # Arm: shoulder (sh_x, 8) -> elbow (sh_x + 3, 7) -> hand (sh_x + 6, 11)
            draw.line([(sh_x, 8), (sh_x + 3, 7)], fill=C_SLATE, width=2)
            draw.line([(sh_x + 3, 7), (sh_x + 6, 11)], fill=copper_color, width=2)
            draw.rectangle([sh_x + 5, 10, sh_x + 7, 12], fill=C_OUTLINE)

            # Pan swinging overhead forward: handle (sh_x + 6, 11) to (sh_x + 12, 7)
            draw.line([(sh_x + 6, 11), (sh_x + 12, 7)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([sh_x + 11, 2, sh_x + 20, 11], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(sh_x + 13, 6), (sh_x + 18, 6)], fill=C_PAN_CORE, width=1)

            # Glowing wind slash arc 1
            draw.arc([sh_x + 2, 1, sh_x + 24, 22], start=230, end=350, fill=C_WIND_FADE, width=3)
            draw.arc([sh_x + 6, 2, sh_x + 22, 20], start=250, end=340, fill=C_WIND_CYAN, width=2)
            draw.arc([sh_x + 10, 3, sh_x + 20, 18], start=270, end=330, fill=C_WIND_CORE, width=1)

        # Frame 2: Full Extension Slash (Arm thrust forward horizontally at HAND LEVEL y=13..15!)
        elif f == 2:
            # Arm: shoulder (sh_x, 8) -> forearm (sh_x + 4, 11) -> hand at (sh_x + 8, 14)
            draw.line([(sh_x, 8), (sh_x + 4, 11)], fill=C_SLATE, width=2)
            draw.line([(sh_x + 4, 11), (sh_x + 8, 14)], fill=copper_color, width=3)
            draw.rectangle([sh_x + 7, 13, sh_x + 10, 15], fill=C_OUTLINE) # Hand gripping handle!

            # Pan held horizontally straight forward at HAND LEVEL: handle (sh_x + 9, 14) to (sh_x + 18, 14)
            draw.line([(sh_x + 9, 14), (sh_x + 18, 14)], fill=C_PAN_HANDLE, width=3)
            # Pan head
            draw.ellipse([sh_x + 16, 9, sh_x + 26, 19], fill=C_PAN_IRON, outline=C_PAN_RIM, width=2)
            draw.ellipse([sh_x + 19, 12, ox + 39, 16], fill=C_PAN_CORE)

            # GLORIOUS WIND SLASH ARC (Dara de vant) extending forward ahead!
            draw.arc([sh_x + 12, 3, sh_x + 29, 26], start=290, end=70, fill=C_WIND_FADE, width=4)
            draw.arc([sh_x + 14, 5, sh_x + 28, 24], start=305, end=55, fill=C_WIND_CYAN, width=3)
            draw.arc([sh_x + 17, 7, sh_x + 27, 22], start=315, end=45, fill=C_WIND_CORE, width=2)
            # Cutting speed lines
            draw.line([(sh_x + 25, 8), (sh_x + 29, 11)], fill=C_WIND_CORE, width=1)
            draw.line([(sh_x + 26, 14), (sh_x + 30, 14)], fill=C_WIND_CORE, width=2)
            draw.line([(sh_x + 25, 20), (sh_x + 29, 17)], fill=C_WIND_CORE, width=1)

        # Frame 3: Recovery / Follow-Through (Arm lowered forward at waist)
        elif f == 3:
            # Arm: shoulder (sh_x, 8) -> hand at (sh_x + 4, 16)
            draw.line([(sh_x, 8), (sh_x + 4, 16)], fill=copper_color, width=2)
            draw.rectangle([sh_x + 3, 15, sh_x + 5, 17], fill=C_OUTLINE)

            # Pan resting low forward
            draw.line([(sh_x + 5, 16), (sh_x + 11, 21)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([sh_x + 10, 19, sh_x + 19, 28], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(sh_x + 12, 23), (sh_x + 16, 23)], fill=C_PAN_CORE, width=1)

            # Dissipating wind particles
            draw.arc([sh_x + 14, 13, sh_x + 26, 26], start=20, end=80, fill=C_WIND_FADE, width=2)
            draw.point([(sh_x + 25, 15), (sh_x + 23, 19)], fill=C_WIND_CYAN)

    return sheet

pan_atk_std = build_faithful_pan_attack(False)
pan_atk_dmg = build_faithful_pan_attack(True)

pan_atk_std.save(os.path.join(godot_assets, "robot_standard_attack_pan_strip4.png"))
pan_atk_dmg.save(os.path.join(godot_assets, "robot_damaged_attack_pan_strip4.png"))
pan_atk_std.save(os.path.join(anim_dir, "robot_standard_attack_pan_strip4.png"))
pan_atk_dmg.save(os.path.join(anim_dir, "robot_damaged_attack_pan_strip4.png"))
pan_atk_std.save(os.path.join(godot_copy_assets, "robot_standard_attack_pan_strip4.png"))
pan_atk_dmg.save(os.path.join(godot_copy_assets, "robot_damaged_attack_pan_strip4.png"))
print("Saved faithful pan attack strips.")


# ---------------------------------------------------------------------------
# 4. BAT ATTACK SPRITES (4 frames, 56x36 each) - 100% FAITHFUL TO IDLE ROBOT
# ---------------------------------------------------------------------------
def build_faithful_bat_attack(is_damaged=False):
    sheet = Image.new("RGBA", (224, 36), C_TRANS)
    h = head_dmg if is_damaged else head_std
    t_no_arm = torso_no_arm_dmg if is_damaged else torso_no_arm_std
    legs = extract_part(f0_std, (2, 14, 25, 30))
    copper_color = C_COPPER if is_damaged else C_WHITE

    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)

    for f in range(4):
        ox = f * 56
        # Offset +4 y to accommodate 36px height
        sheet.paste(legs, (ox + 2, 18), legs)
        sheet.paste(t_no_arm, (ox + 7, 11), t_no_arm)
        sheet.paste(h, (ox + 10, 5), h)

        sh_x = ox + 18
        sh_y = 12

        # Frame 0: High windup
        if f == 0:
            draw.line([(sh_x, 12), (sh_x - 3, 10)], fill=C_SLATE, width=2)
            draw.line([(sh_x - 3, 10), (sh_x - 1, 14)], fill=copper_color, width=2)
            draw.rectangle([sh_x - 2, 13, sh_x, 15], fill=C_OUTLINE)

            # Bat raised back
            draw.line([(sh_x - 1, 14), (sh_x - 7, 8)], fill=C_BAT_GRIP, width=3)
            draw.line([(sh_x - 7, 8), (sh_x - 14, 2)], fill=C_BAT_STEEL, width=5)
            draw.point([(sh_x - 15, 3), (sh_x - 13, 1)], fill=C_BAT_SPIKE)

        # Frame 1: Overhead Downward Arc
        elif f == 1:
            draw.line([(sh_x, 12), (sh_x + 3, 11)], fill=C_SLATE, width=2)
            draw.line([(sh_x + 3, 11), (sh_x + 7, 14)], fill=copper_color, width=2)
            draw.rectangle([sh_x + 6, 13, sh_x + 8, 15], fill=C_OUTLINE)

            # Bat coming down
            draw.line([(sh_x + 7, 14), (sh_x + 15, 9)], fill=C_BAT_GRIP, width=3)
            draw.line([(sh_x + 15, 9), (sh_x + 28, 4)], fill=C_BAT_STEEL, width=6)
            draw.point([(sh_x + 25, 3), (sh_x + 29, 5)], fill=C_BAT_SPIKE)

            # Kinetic arc
            draw.arc([sh_x + 2, 2, sh_x + 34, 28], start=240, end=350, fill=C_BAT_WIND, width=4)
            draw.arc([sh_x + 6, 3, sh_x + 32, 26], start=260, end=340, fill=C_WIND_CORE, width=2)

        # Frame 2: Maximum Forward Power Slam at Hand Level (y=16..18)!
        elif f == 2:
            draw.line([(sh_x, 12), (sh_x + 4, 15)], fill=C_SLATE, width=2)
            draw.line([(sh_x + 4, 15), (sh_x + 8, 18)], fill=copper_color, width=3)
            draw.rectangle([sh_x + 7, 17, sh_x + 10, 19], fill=C_OUTLINE)

            # Heavy bat horizontal slam forward
            draw.line([(sh_x + 9, 18), (sh_x + 18, 18)], fill=C_BAT_GRIP, width=3)
            draw.line([(sh_x + 18, 18), (sh_x + 35, 18)], fill=C_BAT_STEEL, width=6)
            draw.point([(sh_x + 31, 14), (sh_x + 36, 18), (sh_x + 31, 22)], fill=C_BAT_SPIKE)

            # Massive shockwave wind slash
            draw.arc([sh_x + 10, 4, sh_x + 38, 32], start=290, end=70, fill=C_BAT_WIND, width=5)
            draw.arc([sh_x + 13, 6, sh_x + 37, 30], start=305, end=55, fill=C_WIND_CORE, width=2)
            draw.line([(sh_x + 31, 8), (sh_x + 37, 13)], fill=C_WIND_CORE, width=2)
            draw.line([(sh_x + 33, 18), (sh_x + 38, 18)], fill=C_WIND_CORE, width=3)
            draw.line([(sh_x + 31, 28), (sh_x + 37, 23)], fill=C_WIND_CORE, width=2)

        # Frame 3: Low Ground Follow-Through
        elif f == 3:
            draw.line([(sh_x, 12), (sh_x + 4, 20)], fill=copper_color, width=2)
            draw.rectangle([sh_x + 3, 19, sh_x + 5, 21], fill=C_OUTLINE)

            draw.line([(sh_x + 5, 20), (sh_x + 13, 25)], fill=C_BAT_GRIP, width=3)
            draw.line([(sh_x + 13, 25), (sh_x + 28, 32)], fill=C_BAT_STEEL, width=6)
            draw.arc([sh_x + 15, 19, ox + 50, 35], start=10, end=90, fill=C_BAT_WIND, width=3)

    return sheet

bat_atk_std = build_faithful_bat_attack(False)
bat_atk_dmg = build_faithful_bat_attack(True)

bat_atk_std.save(os.path.join(godot_assets, "robot_standard_attack_bat_strip4.png"))
bat_atk_dmg.save(os.path.join(godot_assets, "robot_damaged_attack_bat_strip4.png"))
bat_atk_std.save(os.path.join(anim_dir, "robot_standard_attack_bat_strip4.png"))
bat_atk_dmg.save(os.path.join(anim_dir, "robot_damaged_attack_bat_strip4.png"))
bat_atk_std.save(os.path.join(godot_copy_assets, "robot_standard_attack_bat_strip4.png"))
bat_atk_dmg.save(os.path.join(godot_copy_assets, "robot_damaged_attack_bat_strip4.png"))
print("Saved faithful bat attack strips.")


# ---------------------------------------------------------------------------
# 5. SHOOT BLASTER (4 frames, 40x32 each) - 100% FAITHFUL TO IDLE ROBOT
# ---------------------------------------------------------------------------
def build_faithful_shoot(is_damaged=False):
    sheet = Image.new("RGBA", (160, 32), C_TRANS)
    h = head_dmg if is_damaged else head_std
    t_no_arm = torso_no_arm_dmg if is_damaged else torso_no_arm_std
    legs = extract_part(f0_std, (2, 14, 25, 30))
    copper_color = C_COPPER if is_damaged else C_WHITE

    from PIL import ImageDraw
    draw = ImageDraw.Draw(sheet)

    for f in range(4):
        ox = f * 40
        sheet.paste(legs, (ox + 2, 14), legs)
        sheet.paste(t_no_arm, (ox + 7, 7), t_no_arm)
        sheet.paste(h, (ox + 10, 1), h)

        sh_x = ox + 18
        # Blaster cannon extends straight forward at HAND LEVEL (y=14)
        draw.line([(sh_x, 8), (sh_x + 3, 11)], fill=C_SLATE, width=2)
        draw.line([(sh_x + 3, 11), (sh_x + 7, 14)], fill=copper_color, width=3)
        # Blaster housing
        draw.rectangle([sh_x + 7, 12, sh_x + 14, 16], fill=C_SLATE, outline=C_OUTLINE)
        draw.rectangle([sh_x + 14, 13, sh_x + 16, 15], fill=C_CYAN_CORE, outline=C_OUTLINE) # Muzzle

        if f == 0:
            # Charge
            draw.ellipse([sh_x + 15, 12, sh_x + 19, 16], fill=C_CYAN_CORE)
        elif f == 1:
            # Fire muzzle flash & bolt emerging straight from muzzle!
            draw.ellipse([sh_x + 14, 10, sh_x + 22, 18], fill=C_CYAN_CORE)
            draw.ellipse([sh_x + 16, 12, sh_x + 20, 16], fill=C_WIND_CORE)
            draw.line([(sh_x + 20, 14), (sh_x + 25, 14)], fill=C_WIND_CORE, width=3)
        elif f == 2:
            # Recoil
            draw.line([(sh_x + 16, 11), (sh_x + 21, 13)], fill=C_CYAN_CORE, width=1)
            draw.line([(sh_x + 16, 17), (sh_x + 21, 15)], fill=C_CYAN_CORE, width=1)
        elif f == 3:
            # Cool
            draw.point([(sh_x + 16, 13), (sh_x + 18, 12)], fill=C_CYAN_CORE)

    return sheet

shoot_std = build_faithful_shoot(False)
shoot_dmg = build_faithful_shoot(True)

shoot_std.save(os.path.join(godot_assets, "robot_standard_shoot_strip4.png"))
shoot_dmg.save(os.path.join(godot_assets, "robot_damaged_shoot_strip4.png"))
shoot_std.save(os.path.join(anim_dir, "robot_standard_shoot_strip4.png"))
shoot_dmg.save(os.path.join(anim_dir, "robot_damaged_shoot_strip4.png"))
shoot_std.save(os.path.join(godot_copy_assets, "robot_standard_shoot_strip4.png"))
shoot_dmg.save(os.path.join(godot_copy_assets, "robot_damaged_shoot_strip4.png"))
print("Saved faithful shoot strips.")
