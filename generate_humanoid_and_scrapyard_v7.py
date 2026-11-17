import os
import math
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")
anim_dir = os.path.join(scratch_dir, "animations", "sheets")
os.makedirs(godot_assets, exist_ok=True)
os.makedirs(godot_copy_assets, exist_ok=True)
os.makedirs(anim_dir, exist_ok=True)

# ---------------------------------------------------------------------------
# COLOR PALETTE (Strictly cohesive with Scraps' iconic design)
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
C_COPPER_SHADE = (180, 83, 9, 255)

# Weapon & Effects Colors
C_PAN_HANDLE = (71, 85, 105, 255)
C_PAN_IRON = (30, 41, 59, 255)
C_PAN_RIM = (148, 163, 184, 255)
C_PAN_CORE = (251, 191, 36, 255)
C_WIND_CORE = (255, 255, 255, 245)
C_WIND_CYAN = (56, 189, 248, 220)
C_WIND_FADE = (14, 165, 233, 110)

C_BAT_GRIP = (180, 83, 9, 255)
C_BAT_STEEL = (156, 163, 175, 255)
C_BAT_SPIKE = (254, 240, 138, 255)
C_BAT_WIND = (245, 158, 11, 210)

# Load base idle images to extract head and chest
idle_std = Image.open(os.path.join(godot_assets, "robot_standard_idle_strip4.png"))
idle_dmg = Image.open(os.path.join(godot_assets, "robot_damaged_idle_strip4.png"))
f0_std = idle_std.crop((0, 0, 32, 32))
f0_dmg = idle_dmg.crop((0, 0, 32, 32))

def extract_part(src, rect):
    # rect: (x1, y1, x2, y2)
    part = Image.new("RGBA", (rect[2] - rect[0] + 1, rect[3] - rect[1] + 1), C_TRANS)
    for y in range(rect[1], rect[3] + 1):
        for x in range(rect[0], rect[2] + 1):
            part.putpixel((x - rect[0], y - rect[1]), src.getpixel((x, y)))
    return part

head_std = extract_part(f0_std, (10, 1, 20, 6))
head_dmg = extract_part(f0_dmg, (10, 1, 20, 6))
torso_core_std = extract_part(f0_std, (7, 7, 18, 13))
torso_core_dmg = extract_part(f0_dmg, (7, 7, 18, 13))

print("Base parts extracted successfully.")

# ---------------------------------------------------------------------------
# 1. AUTHENTIC HUMANOID BIPEDAL LEG RENDERER (Inspired by User References 2 & 3)
# ---------------------------------------------------------------------------
def draw_humanoid_leg(draw, hip_x, hip_y, knee_x, knee_y, foot_x, foot_y, is_near=True, is_damaged=False):
    """
    Renders a solid, armored humanoid bipedal leg with distinct thigh, knee joint, shin, and magnetic boot.
    Near leg: bright white/copper armor plating with cyan accents.
    Far leg: shaded darker slate/bronze for proper depth perception.
    """
    c_armor = (C_COPPER if is_damaged else C_WHITE) if is_near else (C_COPPER_SHADE if is_damaged else C_SLATE)
    c_shade = (C_COPPER_SHADE if is_damaged else C_WHITE_SHADE) if is_near else C_DARK_SLATE
    c_joint = C_DARK_SLATE if is_near else (20, 26, 38, 255)
    c_glow = C_CYAN_CORE if is_near else C_CYAN_DEEP

    # 1. Thigh: from hip to knee (thick 3-4px armored segment)
    draw.line([(hip_x, hip_y), (knee_x, knee_y)], fill=C_OUTLINE, width=4)
    draw.line([(hip_x, hip_y), (knee_x, knee_y)], fill=c_armor, width=2)
    draw.point([(hip_x, hip_y), (knee_x, knee_y - 1)], fill=c_shade)

    # 2. Knee Joint: circular armored knee cap
    draw.rectangle([knee_x - 1, knee_y - 1, knee_x + 1, knee_y + 1], fill=C_OUTLINE)
    draw.point([(knee_x, knee_y)], fill=c_glow if is_near else c_joint)

    # 3. Shin: from knee to foot ankle
    ankle_x = foot_x
    ankle_y = foot_y - 2
    draw.line([(knee_x, knee_y), (ankle_x, ankle_y)], fill=C_OUTLINE, width=4)
    draw.line([(knee_x, knee_y), (ankle_x, ankle_y)], fill=c_armor, width=2)
    draw.point([(ankle_x, ankle_y)], fill=c_shade)

    # 4. Magnetic Boot: flat solid sole resting on floor, with bright cyan thruster strip
    draw.rectangle([foot_x - 2, foot_y - 2, foot_x + 3, foot_y], fill=C_OUTLINE)
    draw.rectangle([foot_x - 1, foot_y - 2, foot_x + 2, foot_y - 1], fill=c_armor)
    # Cyan sole light
    draw.line([(foot_x - 1, foot_y), (foot_x + 2, foot_y)], fill=c_glow)

# ---------------------------------------------------------------------------
# 2. HUMANOID WALK CYCLE (8 Frames, 32x32)
# Strictly following natural human locomotion (Images 2 & 3):
# Contact -> Down -> Passing -> High -> Contact (Opposite) -> Down -> Passing -> High
# ---------------------------------------------------------------------------
def build_humanoid_walk(is_damaged=False):
    sheet = Image.new("RGBA", (256, 32), C_TRANS)
    draw = ImageDraw.Draw(sheet)
    h = head_dmg if is_damaged else head_std
    t = torso_core_dmg if is_damaged else torso_core_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    # Keyframe poses for (far_foot, far_knee, near_foot, near_knee, pelvis_bob, arm_angle)
    # Standard ground is at y=30.
    poses = [
        # Frame 0: Contact (Near leg reaching forward, far leg trailing back)
        {"near_foot": (17, 30), "near_knee": (15, 22), "far_foot": (6, 29), "far_knee": (8, 22), "bob": 0, "arm_f": -1},
        # Frame 1: Down / Cushion (Near foot planted, knees bend slightly, center of mass drops 1px)
        {"near_foot": (15, 30), "near_knee": (14, 23), "far_foot": (7, 28), "far_knee": (9, 23), "bob": 1, "arm_f": 0},
        # Frame 2: Passing (Near leg upright supporting, far leg swinging forward past knee)
        {"near_foot": (12, 30), "near_knee": (12, 22), "far_foot": (11, 27), "far_knee": (12, 21), "bob": 0, "arm_f": 1},
        # Frame 3: High / Up (Near leg pushes off with toe, far leg reaches forward)
        {"near_foot": (9, 29), "near_knee": (10, 21), "far_foot": (15, 28), "far_knee": (14, 21), "bob": -1, "arm_f": 2},
        # Frame 4: Opposite Contact (Far leg reaching forward, near leg trailing back)
        {"near_foot": (6, 29), "near_knee": (8, 22), "far_foot": (17, 30), "far_knee": (15, 22), "bob": 0, "arm_f": 1},
        # Frame 5: Opposite Down (Far foot planted, knees bend, body drops 1px)
        {"near_foot": (7, 28), "near_knee": (9, 23), "far_foot": (15, 30), "far_knee": (14, 23), "bob": 1, "arm_f": 0},
        # Frame 6: Opposite Passing (Far leg supporting, near leg swinging forward)
        {"near_foot": (11, 27), "near_knee": (12, 21), "far_foot": (12, 30), "far_knee": (12, 22), "bob": 0, "arm_f": -1},
        # Frame 7: Opposite High (Far leg pushes off, near leg reaches forward)
        {"near_foot": (15, 28), "near_knee": (14, 21), "far_foot": (9, 29), "far_knee": (10, 21), "bob": -1, "arm_f": -2},
    ]

    for f in range(8):
        ox = f * 32
        p = poses[f]
        bob = p["bob"]
        hip_y = 15 + bob
        near_hip_x = ox + 12
        far_hip_x = ox + 14

        # 1. Draw Far Leg first (behind torso)
        draw_humanoid_leg(draw, far_hip_x, hip_y, ox + p["far_knee"][0], p["far_knee"][1] + bob, ox + p["far_foot"][0], p["far_foot"][1], is_near=False, is_damaged=is_damaged)

        # 2. Draw Torso and Head with bob
        sheet.paste(t, (ox + 7, 7 + bob), t)
        sheet.paste(h, (ox + 10, 1 + bob), h)

        # 3. Draw Near Leg (in front of torso)
        draw_humanoid_leg(draw, near_hip_x, hip_y, ox + p["near_knee"][0], p["near_knee"][1] + bob, ox + p["near_foot"][0], p["near_foot"][1], is_near=True, is_damaged=is_damaged)

        # 4. Draw Natural Swinging Human Arm (near arm, shoulder at ox+18, 8+bob)
        sh_x = ox + 18
        sh_y = 8 + bob
        arm_f = p["arm_f"]
        elbow_x = sh_x + arm_f
        elbow_y = sh_y + 4
        hand_x = sh_x + arm_f * 2
        hand_y = sh_y + 7
        draw.line([(sh_x, sh_y), (elbow_x, elbow_y)], fill=C_OUTLINE, width=3)
        draw.line([(sh_x, sh_y), (elbow_x, elbow_y)], fill=copper_color, width=1)
        draw.line([(elbow_x, elbow_y), (hand_x, hand_y)], fill=C_OUTLINE, width=3)
        draw.line([(elbow_x, elbow_y), (hand_x, hand_y)], fill=C_SLATE, width=1)
        draw.rectangle([hand_x - 1, hand_y - 1, hand_x + 1, hand_y + 1], fill=C_OUTLINE)

    return sheet

# ---------------------------------------------------------------------------
# 3. HUMANOID CROUCH SPRITES (2 Frames, 32x32)
# Natural tactical runner crouch: Hips drop 6px, knees bend forward, feet stay flat!
# ---------------------------------------------------------------------------
def build_humanoid_crouch(is_damaged=False):
    sheet = Image.new("RGBA", (64, 32), C_TRANS)
    draw = ImageDraw.Draw(sheet)
    h = head_dmg if is_damaged else head_std
    t = torso_core_dmg if is_damaged else torso_core_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    for f in range(2):
        ox = f * 32
        bob = f # 1px breathing bob

        hip_y = 19 + bob
        near_hip_x = ox + 11
        far_hip_x = ox + 13

        # Far leg: kneeling slightly behind
        draw_humanoid_leg(draw, far_hip_x, hip_y, ox + 8, 25 + bob, ox + 5, 30, is_near=False, is_damaged=is_damaged)

        # Torso & Head lowered by 6 pixels
        sheet.paste(t, (ox + 7, 13 + bob), t)
        sheet.paste(h, (ox + 10, 7 + bob), h)

        # Near leg: bent forward at 90 degrees (knee at x=17, y=23, foot flat at x=16, y=30)
        draw_humanoid_leg(draw, near_hip_x, hip_y, ox + 16, 23 + bob, ox + 16, 30, is_near=True, is_damaged=is_damaged)

        # Arm bracing forward on thigh/knee
        sh_x = ox + 18
        sh_y = 14 + bob
        draw.line([(sh_x, sh_y), (ox + 16, 22 + bob)], fill=C_OUTLINE, width=3)
        draw.line([(sh_x, sh_y), (ox + 16, 22 + bob)], fill=copper_color, width=1)
        draw.rectangle([ox + 15, 21 + bob, ox + 17, 23 + bob], fill=C_SLATE)

    return sheet

# ---------------------------------------------------------------------------
# 4. FIXED MELEE PAN ATTACK (4 Frames, 48x32)
# Fixes Image 10: Weapon is held at HAND/CHEST LEVEL (y=14..16), NOT AT THE VISOR!
# The swing sweeps forward in front of the chest, creating a magnificent wind trail ahead.
# ---------------------------------------------------------------------------
def build_fixed_pan_attack(is_damaged=False):
    sheet = Image.new("RGBA", (192, 32), C_TRANS)
    draw = ImageDraw.Draw(sheet)
    h = head_dmg if is_damaged else head_std
    t = torso_core_dmg if is_damaged else torso_core_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    for f in range(4):
        ox = f * 48

        # 1. Combat Stance Legs (solid bipedal footing)
        draw_humanoid_leg(draw, ox + 14, 15, ox + 10, 22, ox + 7, 30, is_near=False, is_damaged=is_damaged)
        sheet.paste(t, (ox + 7, 7), t)
        sheet.paste(h, (ox + 10, 1), h)
        draw_humanoid_leg(draw, ox + 12, 15, ox + 15, 23, ox + 16, 30, is_near=True, is_damaged=is_damaged)

        sh_x = ox + 18
        sh_y = 9 # Shoulder socket

        # Frame 0: Windup (arm cocked back at CHEST LEVEL y=13..15)
        if f == 0:
            hand_x = sh_x - 3
            hand_y = 13
            draw.line([(sh_x, sh_y), (sh_x - 1, 11), (hand_x, hand_y)], fill=C_OUTLINE, width=3)
            draw.line([(sh_x, sh_y), (sh_x - 1, 11), (hand_x, hand_y)], fill=copper_color, width=1)
            # Pan tilted back behind arm at chest level
            draw.line([(hand_x, hand_y), (hand_x - 5, hand_y - 2)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([hand_x - 10, hand_y - 6, hand_x - 4, hand_y], fill=C_PAN_IRON, outline=C_PAN_RIM)
            draw.point([(hand_x - 7, hand_y - 3)], fill=C_PAN_CORE)

        # Frame 1: Forward Swing Starts (Arm thrusting forward at chest level y=14)
        elif f == 1:
            hand_x = sh_x + 5
            hand_y = 14
            draw.line([(sh_x, sh_y), (sh_x + 2, 11), (hand_x, hand_y)], fill=C_OUTLINE, width=3)
            draw.line([(sh_x, sh_y), (sh_x + 2, 11), (hand_x, hand_y)], fill=copper_color, width=1)
            # Pan swinging across chest (handle at hand_x, head at hand_x + 7)
            draw.line([(hand_x, hand_y), (hand_x + 6, hand_y - 1)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([hand_x + 5, hand_y - 5, hand_x + 12, hand_y + 1], fill=C_PAN_IRON, outline=C_PAN_RIM)
            draw.point([(hand_x + 8, hand_y - 2)], fill=C_PAN_CORE)
            # Wind arc 1 (ahead of chest)
            draw.arc([hand_x + 2, 8, hand_x + 16, 22], start=270, end=350, fill=C_WIND_CYAN, width=2)

        # Frame 2: FULL EXTENSION MELEE IMPACT (Hand at x=28, y=14; Pan at x=34..42; Wind slash sweeping ahead at x=30..46, y=6..24)
        elif f == 2:
            hand_x = sh_x + 8
            hand_y = 14
            draw.line([(sh_x, sh_y), (sh_x + 4, 11), (hand_x, hand_y)], fill=C_OUTLINE, width=4)
            draw.line([(sh_x, sh_y), (sh_x + 4, 11), (hand_x, hand_y)], fill=copper_color, width=2)

            # Cyber Pan extended straight forward at hand level (y=14)
            draw.line([(hand_x, hand_y), (hand_x + 8, hand_y)], fill=C_PAN_HANDLE, width=3)
            # Pan circular head
            draw.ellipse([hand_x + 7, hand_y - 4, hand_x + 15, hand_y + 4], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.ellipse([hand_x + 9, hand_y - 2, hand_x + 13, hand_y + 2], fill=C_PAN_CORE)

            # GLORIOUS WIND SLASH ARC ("dara de vant") sweeping in front of Scraps!
            # Arc extends cleanly from y=7 down to y=25, out to x = hand_x + 18!
            draw.arc([hand_x + 4, 6, hand_x + 18, 24], start=290, end=70, fill=C_WIND_FADE, width=4)
            draw.arc([hand_x + 6, 8, hand_x + 17, 22], start=305, end=55, fill=C_WIND_CYAN, width=2)
            draw.arc([hand_x + 8, 10, hand_x + 16, 20], start=315, end=45, fill=C_WIND_CORE, width=1)
            # Forward cutting speed lines
            draw.line([(hand_x + 14, 10), (hand_x + 20, 12)], fill=C_WIND_CORE, width=1)
            draw.line([(hand_x + 16, 14), (hand_x + 22, 14)], fill=C_WIND_CORE, width=2)
            draw.line([(hand_x + 14, 18), (hand_x + 20, 16)], fill=C_WIND_CORE, width=1)

        # Frame 3: Follow-through / Recovery (Arm lowered forward at waist level y=16)
        elif f == 3:
            hand_x = sh_x + 4
            hand_y = 16
            draw.line([(sh_x, sh_y), (sh_x + 2, 12), (hand_x, hand_y)], fill=C_OUTLINE, width=3)
            draw.line([(sh_x, sh_y), (sh_x + 2, 12), (hand_x, hand_y)], fill=copper_color, width=1)
            # Pan resting low
            draw.line([(hand_x, hand_y), (hand_x + 5, hand_y + 3)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([hand_x + 4, hand_y + 1, hand_x + 10, hand_y + 7], fill=C_PAN_IRON, outline=C_PAN_RIM)
            # Lingering cyan wind sparkles
            draw.point([(hand_x + 12, 12), (hand_x + 15, 15)], fill=C_WIND_CYAN)

    return sheet

# ---------------------------------------------------------------------------
# 5. FIXED BAT ATTACK (4 Frames, 56x36)
# ---------------------------------------------------------------------------
def build_fixed_bat_attack(is_damaged=False):
    sheet = Image.new("RGBA", (224, 36), C_TRANS)
    draw = ImageDraw.Draw(sheet)
    h = head_dmg if is_damaged else head_std
    t = torso_core_dmg if is_damaged else torso_core_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    for f in range(4):
        ox = f * 56
        # Feet ground at y=34
        draw_humanoid_leg(draw, ox + 14, 19, ox + 10, 26, ox + 7, 34, is_near=False, is_damaged=is_damaged)
        sheet.paste(t, (ox + 7, 11), t)
        sheet.paste(h, (ox + 10, 5), h)
        draw_humanoid_leg(draw, ox + 12, 19, ox + 15, 27, ox + 16, 34, is_near=True, is_damaged=is_damaged)

        sh_x = ox + 18
        sh_y = 13

        if f == 0:
            hand_x = sh_x - 3
            hand_y = 17
            draw.line([(sh_x, sh_y), (hand_x, hand_y)], fill=copper_color, width=2)
            draw.line([(hand_x, hand_y), (hand_x - 8, hand_y - 6)], fill=C_BAT_GRIP, width=3)
            draw.line([(hand_x - 8, hand_y - 6), (hand_x - 14, hand_y - 12)], fill=C_BAT_STEEL, width=4)
        elif f == 1:
            hand_x = sh_x + 6
            hand_y = 18
            draw.line([(sh_x, sh_y), (hand_x, hand_y)], fill=copper_color, width=2)
            draw.line([(hand_x, hand_y), (hand_x + 8, hand_y - 4)], fill=C_BAT_GRIP, width=3)
            draw.line([(hand_x + 8, hand_y - 4), (hand_x + 16, hand_y - 8)], fill=C_BAT_STEEL, width=4)
            draw.arc([hand_x + 4, 8, hand_x + 22, 26], start=270, end=350, fill=C_BAT_WIND, width=2)
        elif f == 2:
            hand_x = sh_x + 10
            hand_y = 18
            draw.line([(sh_x, sh_y), (hand_x, hand_y)], fill=copper_color, width=3)
            draw.line([(hand_x, hand_y), (hand_x + 10, hand_y)], fill=C_BAT_GRIP, width=3)
            draw.line([(hand_x + 10, hand_y), (hand_x + 22, hand_y)], fill=C_BAT_STEEL, width=5)
            # Spikes
            draw.point([(hand_x + 14, hand_y - 3), (hand_x + 18, hand_y - 3), (hand_x + 14, hand_y + 3), (hand_x + 18, hand_y + 3)], fill=C_BAT_SPIKE)
            # Wind arc
            draw.arc([hand_x + 6, 8, hand_x + 26, 28], start=290, end=70, fill=C_BAT_WIND, width=4)
            draw.line([(hand_x + 20, 14), (hand_x + 28, 14)], fill=C_BAT_SPIKE, width=2)
        elif f == 3:
            hand_x = sh_x + 5
            hand_y = 20
            draw.line([(sh_x, sh_y), (hand_x, hand_y)], fill=copper_color, width=2)
            draw.line([(hand_x, hand_y), (hand_x + 8, hand_y + 4)], fill=C_BAT_STEEL, width=3)

    return sheet

# ---------------------------------------------------------------------------
# 6. RANGED BLASTER SHOOT (4 Frames, 32x32)
# ---------------------------------------------------------------------------
def build_humanoid_shoot(is_damaged=False):
    sheet = Image.new("RGBA", (128, 32), C_TRANS)
    draw = ImageDraw.Draw(sheet)
    h = head_dmg if is_damaged else head_std
    t = torso_core_dmg if is_damaged else torso_core_std
    copper_color = C_COPPER if is_damaged else C_WHITE

    for f in range(4):
        ox = f * 32
        recoil = 1 if f in [1, 2] else 0

        draw_humanoid_leg(draw, ox + 14, 15, ox + 10, 22, ox + 7, 30, is_near=False, is_damaged=is_damaged)
        sheet.paste(t, (ox + 7 - recoil, 7), t)
        sheet.paste(h, (ox + 10 - recoil, 1), h)
        draw_humanoid_leg(draw, ox + 12, 15, ox + 15, 23, ox + 16, 30, is_near=True, is_damaged=is_damaged)

        # Right arm transformed into plasma cannon thrust straight forward at chest level y=12
        sh_x = ox + 18 - recoil
        sh_y = 9
        draw.line([(sh_x, sh_y), (sh_x + 5, 12)], fill=copper_color, width=3)
        draw.rectangle([sh_x + 4, 10, sh_x + 10, 14], fill=C_SLATE, outline=C_OUTLINE)
        draw.rectangle([sh_x + 8, 11, sh_x + 11, 13], fill=C_CYAN_CORE)

        # Muzzle flash on frame 1
        if f == 1:
            draw.ellipse([sh_x + 11, 9, sh_x + 17, 15], fill=C_CYAN_HI)
            draw.line([(sh_x + 12, 12), (sh_x + 20, 12)], fill=C_WHITE, width=2)
            draw.line([(sh_x + 14, 9), (sh_x + 14, 15)], fill=C_CYAN_CORE, width=1)

    return sheet

# ---------------------------------------------------------------------------
# 7. GENERATE ALL SPRITES & SAVE
# ---------------------------------------------------------------------------
print("Generating humanoid walk cycles...")
walk_std = build_humanoid_walk(False)
walk_dmg = build_humanoid_walk(True)

print("Generating humanoid crouch cycles...")
crouch_std = build_humanoid_crouch(False)
crouch_dmg = build_humanoid_crouch(True)

print("Generating fixed pan attack animations...")
pan_atk_std = build_fixed_pan_attack(False)
pan_atk_dmg = build_fixed_pan_attack(True)

print("Generating fixed bat attack animations...")
bat_atk_std = build_fixed_bat_attack(False)
bat_atk_dmg = build_fixed_bat_attack(True)

print("Generating blaster shoot animations...")
shoot_std = build_humanoid_shoot(False)
shoot_dmg = build_humanoid_shoot(True)

def save_both(img, filename):
    img.save(os.path.join(godot_assets, filename))
    img.save(os.path.join(godot_copy_assets, filename))
    img.save(os.path.join(anim_dir, filename))

save_both(walk_std, "robot_standard_walk_strip8.png")
save_both(walk_dmg, "robot_damaged_walk_strip8.png")
save_both(crouch_std, "robot_standard_crouch_strip2.png")
save_both(crouch_dmg, "robot_damaged_crouch_strip2.png")
save_both(pan_atk_std, "robot_standard_attack_pan_strip4.png")
save_both(pan_atk_dmg, "robot_damaged_attack_pan_strip4.png")
save_both(bat_atk_std, "robot_standard_attack_bat_strip4.png")
save_both(bat_atk_dmg, "robot_damaged_attack_bat_strip4.png")
save_both(shoot_std, "robot_standard_shoot_strip4.png")
save_both(shoot_dmg, "robot_damaged_shoot_strip4.png")

print("All robot humanoid sprites saved successfully!")
