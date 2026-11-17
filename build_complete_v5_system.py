import os
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
anim_dir = os.path.join(scratch_dir, "animations", "sheets")
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")

for d in [anim_dir, godot_assets, godot_copy_assets]:
    os.makedirs(d, exist_ok=True)

# ---------------------------------------------------------------------------
# COLOR PALETTES
# ---------------------------------------------------------------------------
# Robot
C_OUTLINE = (14, 18, 25, 255)
C_WHITE = (241, 245, 249, 255)
C_WHITE_SHADE = (148, 163, 184, 255)
C_CYAN_GLOW = (0, 245, 255, 255)
C_DARK_JOINT = (51, 65, 85, 255)
C_COPPER = (249, 115, 22, 255) # For damaged chassis exposed wiring

# Cyber Frying Pan
C_PAN_HANDLE = (71, 85, 105, 255)
C_PAN_IRON = (30, 41, 59, 255)
C_PAN_RIM = (148, 163, 184, 255)
C_PAN_CORE = (251, 191, 36, 255) # Glowing amber induction core
C_WIND_CORE = (255, 255, 255, 245)
C_WIND_CYAN = (56, 189, 248, 220)
C_WIND_FADE = (14, 165, 233, 120)

# Metal Bat
C_BAT_GRIP = (180, 83, 9, 255)
C_BAT_STEEL = (156, 163, 175, 255)
C_BAT_SPIKE = (254, 240, 138, 255)
C_BAT_WIND = (245, 158, 11, 210)

# ---------------------------------------------------------------------------
# 1. GENERATE CROUCH SPRITES (32x32 per frame, 2 frames each)
# ---------------------------------------------------------------------------
def generate_crouch(chassis="standard"):
    img = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for f in range(2):
        ox = f * 32
        bob = 1 if f == 1 else 0

        # Crouched / ducked legs (folded low on the floor y=24..30)
        # Feet flat on ground
        draw.rectangle([ox + 6, 28, ox + 14, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
        draw.rectangle([ox + 16, 28, ox + 24, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
        # Bent knees
        draw.polygon([(ox + 8, 28), (ox + 4, 22), (ox + 12, 20), (ox + 14, 26)], fill=C_WHITE_SHADE, outline=C_OUTLINE)
        draw.polygon([(ox + 18, 28), (ox + 14, 22), (ox + 22, 20), (ox + 24, 26)], fill=C_WHITE_SHADE, outline=C_OUTLINE)

        # Lowered Torso (hunched at y=14..22 + bob)
        ty = 14 + bob
        draw.rectangle([ox + 8, ty, ox + 20, ty + 8], fill=C_WHITE, outline=C_OUTLINE)
        if chassis == "damaged":
            draw.line([(ox + 10, ty + 2), (ox + 16, ty + 5)], fill=C_COPPER, width=1)
        else:
            draw.line([(ox + 12, ty + 2), (ox + 16, ty + 2)], fill=C_CYAN_GLOW, width=1)

        # Lowered Head (y=7..13 + bob)
        hy = 7 + bob
        draw.rectangle([ox + 10, hy, ox + 22, hy + 7], fill=C_WHITE, outline=C_OUTLINE)
        # Glowing Cyan Visor looking forward low
        draw.rectangle([ox + 17, hy + 2, ox + 22, hy + 4], fill=C_CYAN_GLOW, outline=C_OUTLINE)

        # Rest arms low on knees
        draw.line([(ox + 12, ty + 2), (ox + 18, ty + 6)], fill=C_DARK_JOINT, width=2)
        draw.rectangle([ox + 17, ty + 5, ox + 20, ty + 8], fill=C_WHITE_SHADE, outline=C_OUTLINE)

    return img

img_std_crouch = generate_crouch("standard")
img_dmg_crouch = generate_crouch("damaged")
img_std_crouch.save(os.path.join(anim_dir, "robot_standard_crouch_strip2.png"))
img_dmg_crouch.save(os.path.join(anim_dir, "robot_damaged_crouch_strip2.png"))
img_std_crouch.save(os.path.join(godot_assets, "robot_standard_crouch_strip2.png"))
img_dmg_crouch.save(os.path.join(godot_assets, "robot_damaged_crouch_strip2.png"))
img_std_crouch.save(os.path.join(godot_copy_assets, "robot_standard_crouch_strip2.png"))
img_dmg_crouch.save(os.path.join(godot_copy_assets, "robot_damaged_crouch_strip2.png"))
print("Generated robot crouch strips.")

# ---------------------------------------------------------------------------
# 2. GENERATE UNIFIED ATTACK SPRITES: ROBOT SWINGING MELEE ARM
# 48x32 per frame, 4 frames total (192x32)
# The robot's arm visibly swings from shoulder through hand at hand level (y=14..16)
# ---------------------------------------------------------------------------
def generate_pan_attack(chassis="standard"):
    img = Image.new("RGBA", (48 * 4, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for f in range(4):
        ox = f * 48

        # --- FRAME 0: WINDUP (Scraps leans back, arm pulled back at shoulder, pan ready) ---
        if f == 0:
            # Legs braced back
            draw.line([(ox + 8, 22), (ox + 5, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 3, 28, ox + 7, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 14, 22), (ox + 15, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 13, 28, ox + 18, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Torso leaning slightly back
            draw.rectangle([ox + 8, 10, ox + 17, 21], fill=C_WHITE, outline=C_OUTLINE)
            if chassis == "damaged":
                draw.line([(ox + 10, 13), (ox + 14, 16)], fill=C_COPPER, width=1)
            else:
                draw.line([(ox + 12, 13), (ox + 15, 13)], fill=C_CYAN_GLOW, width=1)

            # Head
            draw.rectangle([ox + 9, 3, ox + 19, 10], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 15, 5, ox + 19, 7], fill=C_CYAN_GLOW, outline=C_OUTLINE) # Visor

            # ARM COCKED BACK: shoulder at (10, 11) -> elbow (5, 9) -> hand (6, 12)
            draw.line([(ox + 10, 11), (ox + 5, 9)], fill=C_DARK_JOINT, width=2)
            draw.line([(ox + 5, 9), (ox + 6, 12)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 5, 11, ox + 8, 14], fill=C_DARK_JOINT, outline=C_OUTLINE) # Hand

            # PAN HELD IN HAND at hand level!
            # Handle from hand (7, 12) angled up-left to (3, 6)
            draw.line([(ox + 7, 12), (ox + 3, 6)], fill=C_PAN_HANDLE, width=2)
            # Pan head
            draw.ellipse([ox + 0, 1, ox + 8, 9], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(ox + 2, 5), (ox + 6, 5)], fill=C_PAN_CORE, width=1)
            # Subtle windup aura
            draw.arc([ox + 0, 0, ox + 12, 12], start=160, end=300, fill=C_WIND_FADE, width=1)

        # --- FRAME 1: DOWNSWING (Arm swinging overhead forward at shoulder/chest level) ---
        elif f == 1:
            # Legs stepping forward
            draw.line([(ox + 7, 22), (ox + 4, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 2, 28, ox + 6, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 15, 22), (ox + 18, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 16, 28, ox + 21, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Torso leaning forward into the blow
            draw.rectangle([ox + 10, 10, ox + 19, 21], fill=C_WHITE, outline=C_OUTLINE)
            if chassis == "damaged":
                draw.line([(ox + 12, 13), (ox + 16, 16)], fill=C_COPPER, width=1)
            else:
                draw.line([(ox + 14, 13), (ox + 17, 13)], fill=C_CYAN_GLOW, width=1)

            # Head
            draw.rectangle([ox + 12, 3, ox + 22, 10], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 18, 5, ox + 22, 7], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # ARM SWINGING FORWARD: shoulder (14, 11) -> elbow (17, 8) -> hand at (20, 11)
            draw.line([(ox + 14, 11), (ox + 17, 8)], fill=C_DARK_JOINT, width=2)
            draw.line([(ox + 17, 8), (ox + 20, 11)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 19, 10, ox + 22, 13], fill=C_DARK_JOINT, outline=C_OUTLINE) # Hand

            # PAN IN HAND swinging forward! Handle from (21, 11) to (27, 8)
            draw.line([(ox + 21, 11), (ox + 27, 8)], fill=C_PAN_HANDLE, width=2)
            # Pan head at (26, 3) to (34, 11)
            draw.ellipse([ox + 26, 3, ox + 35, 12], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(ox + 28, 7), (ox + 33, 7)], fill=C_PAN_CORE, width=1)

            # Glowing Wind Slash Arc 1 (Dara de vant overhead)
            draw.arc([ox + 16, 1, ox + 40, 22], start=230, end=350, fill=C_WIND_FADE, width=3)
            draw.arc([ox + 20, 2, ox + 38, 20], start=250, end=340, fill=C_WIND_CYAN, width=2)
            draw.arc([ox + 24, 3, ox + 36, 18], start=270, end=330, fill=C_WIND_CORE, width=1)

        # --- FRAME 2: FULL EXTENSION IMPACT (Arm fully thrust forward at HAND LEVEL y=14..16, huge forward wind slash!) ---
        elif f == 2:
            # Solid forward combat lunge
            draw.line([(ox + 6, 22), (ox + 2, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 0, 28, ox + 5, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 16, 22), (ox + 22, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 20, 28, ox + 25, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Torso lunging forward
            draw.rectangle([ox + 11, 11, ox + 20, 21], fill=C_WHITE, outline=C_OUTLINE)
            if chassis == "damaged":
                draw.line([(ox + 13, 14), (ox + 17, 17)], fill=C_COPPER, width=1)
            else:
                draw.line([(ox + 15, 14), (ox + 18, 14)], fill=C_CYAN_GLOW, width=1)

            # Head
            draw.rectangle([ox + 13, 4, ox + 23, 11], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 19, 6, ox + 23, 8], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # ARM FULLY EXTENDED FORWARD AT HAND LEVEL (y=14..16):
            # Shoulder (15, 12) -> Arm (19, 14) -> Hand (23, 14)
            draw.line([(ox + 15, 12), (ox + 21, 14)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 21, 13, ox + 24, 16], fill=C_DARK_JOINT, outline=C_OUTLINE) # Hand

            # PAN HELD FIRMLY IN HAND extending straight forward at hand level!
            # Handle from hand (23, 14) to (32, 14)
            draw.line([(ox + 23, 14), (ox + 32, 14)], fill=C_PAN_HANDLE, width=3)
            # Pan head at (30, 9) to (40, 19)
            draw.ellipse([ox + 30, 9, ox + 40, 19], fill=C_PAN_IRON, outline=C_PAN_RIM, width=2)
            draw.ellipse([ox + 33, 12, ox + 37, 16], fill=C_PAN_CORE)

            # GLORIOUS WIND SLASH ARC (Dara de vant ca efect in urma) slicing forward ahead!
            # Sweeping from (30, 3) to (47, 26) right at hand impact height!
            draw.arc([ox + 26, 3, ox + 47, 26], start=290, end=70, fill=C_WIND_FADE, width=4)
            draw.arc([ox + 28, 5, ox + 46, 24], start=305, end=55, fill=C_WIND_CYAN, width=3)
            draw.arc([ox + 31, 7, ox + 45, 22], start=315, end=45, fill=C_WIND_CORE, width=2)
            # Cutting whisps
            draw.line([(ox + 39, 8), (ox + 46, 11)], fill=C_WIND_CORE, width=1)
            draw.line([(ox + 41, 14), (ox + 47, 14)], fill=C_WIND_CORE, width=2)
            draw.line([(ox + 39, 21), (ox + 46, 17)], fill=C_WIND_CORE, width=1)

        # --- FRAME 3: RECOVERY / FOLLOW-THROUGH (Arm lowering forward at waist height) ---
        elif f == 3:
            # Legs stabilizing
            draw.line([(ox + 8, 22), (ox + 5, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 3, 28, ox + 7, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 15, 22), (ox + 18, 29)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 16, 28, ox + 21, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Torso upright
            draw.rectangle([ox + 9, 10, ox + 18, 21], fill=C_WHITE, outline=C_OUTLINE)
            if chassis == "damaged":
                draw.line([(ox + 11, 13), (ox + 15, 16)], fill=C_COPPER, width=1)
            else:
                draw.line([(ox + 13, 13), (ox + 16, 13)], fill=C_CYAN_GLOW, width=1)

            # Head
            draw.rectangle([ox + 10, 3, ox + 20, 10], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 16, 5, ox + 20, 7], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Arm lowering: shoulder (13, 11) -> hand at (18, 17)
            draw.line([(ox + 13, 11), (ox + 18, 17)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 17, 16, ox + 20, 19], fill=C_DARK_JOINT, outline=C_OUTLINE)

            # Pan resting low forward: handle (19, 17) to (25, 22), head at (24, 20) to (32, 28)
            draw.line([(ox + 19, 17), (ox + 25, 22)], fill=C_PAN_HANDLE, width=2)
            draw.ellipse([ox + 24, 20, ox + 33, 29], fill=C_PAN_IRON, outline=C_PAN_RIM, width=1)
            draw.line([(ox + 26, 24), (ox + 30, 24)], fill=C_PAN_CORE, width=1)

            # Dissipating wind motes
            draw.arc([ox + 28, 14, ox + 42, 28], start=20, end=80, fill=C_WIND_FADE, width=2)
            draw.point([(ox + 40, 16), (ox + 38, 21), (ox + 35, 25)], fill=C_WIND_CYAN)

    return img

img_std_pan = generate_pan_attack("standard")
img_dmg_pan = generate_pan_attack("damaged")

img_std_pan.save(os.path.join(anim_dir, "robot_standard_attack_pan_strip4.png"))
img_dmg_pan.save(os.path.join(anim_dir, "robot_damaged_attack_pan_strip4.png"))
img_std_pan.save(os.path.join(godot_assets, "robot_standard_attack_pan_strip4.png"))
img_dmg_pan.save(os.path.join(godot_assets, "robot_damaged_attack_pan_strip4.png"))
img_std_pan.save(os.path.join(godot_copy_assets, "robot_standard_attack_pan_strip4.png"))
img_dmg_pan.save(os.path.join(godot_copy_assets, "robot_damaged_attack_pan_strip4.png"))
print("Generated robot pan attack strips with arm swinging from hand level.")

# ---------------------------------------------------------------------------
# 3. GENERATE UNIFIED BAT ATTACK SPRITES: REINFORCED METAL BAT SLAM
# 56x36 per frame, 4 frames total (224x36)
# ---------------------------------------------------------------------------
def generate_bat_attack(chassis="standard"):
    img = Image.new("RGBA", (56 * 4, 36), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for f in range(4):
        ox = f * 56

        # --- FRAME 0: High 2-handed windup over shoulder ---
        if f == 0:
            # Legs
            draw.line([(ox + 10, 26), (ox + 7, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 5, 32, ox + 9, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 16, 26), (ox + 17, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 15, 32, ox + 20, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Torso
            draw.rectangle([ox + 10, 14, ox + 19, 25], fill=C_WHITE, outline=C_OUTLINE)
            # Head
            draw.rectangle([ox + 11, 7, ox + 21, 14], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 17, 9, ox + 21, 11], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Two hands raised: (14, 13) and (16, 14)
            draw.rectangle([ox + 13, 12, ox + 17, 16], fill=C_DARK_JOINT, outline=C_OUTLINE)

            # Bat raised back over shoulder
            draw.line([(ox + 14, 14), (ox + 8, 8)], fill=C_BAT_GRIP, width=3)
            draw.line([(ox + 8, 8), (ox + 2, 2)], fill=C_BAT_STEEL, width=5)
            draw.point([(ox + 1, 4), (ox + 4, 1)], fill=C_BAT_SPIKE)

        # --- FRAME 1: Heavy Overhead Downward Arc ---
        elif f == 1:
            draw.line([(ox + 9, 26), (ox + 6, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 4, 32, ox + 8, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 17, 26), (ox + 20, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 18, 32, ox + 23, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            draw.rectangle([ox + 12, 14, ox + 21, 25], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 14, 7, ox + 24, 14], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 20, 9, ox + 24, 11], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Hands swinging overhead forward at (22, 13)
            draw.line([(ox + 16, 15), (ox + 22, 13)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 21, 12, ox + 24, 15], fill=C_DARK_JOINT, outline=C_OUTLINE)

            # Bat coming down forward
            draw.line([(ox + 23, 13), (ox + 31, 8)], fill=C_BAT_GRIP, width=3)
            draw.line([(ox + 31, 8), (ox + 43, 3)], fill=C_BAT_STEEL, width=6)
            draw.point([(ox + 40, 2), (ox + 44, 4)], fill=C_BAT_SPIKE)

            # Heavy kinetic wind arc
            draw.arc([ox + 18, 1, ox + 50, 26], start=240, end=350, fill=C_BAT_WIND, width=4)
            draw.arc([ox + 22, 2, ox + 48, 24], start=260, end=340, fill=C_WIND_CORE, width=2)

        # --- FRAME 2: Full Forward Power Slam at Hand Level (y=16..18)! ---
        elif f == 2:
            draw.line([(ox + 8, 26), (ox + 3, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 1, 32, ox + 6, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 18, 26), (ox + 24, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 22, 32, ox + 27, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            draw.rectangle([ox + 13, 15, ox + 22, 25], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 15, 8, ox + 25, 15], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 21, 10, ox + 25, 12], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Both hands fully extended forward at HAND LEVEL (24, 17)
            draw.line([(ox + 17, 16), (ox + 24, 17)], fill=C_WHITE_SHADE, width=4)
            draw.rectangle([ox + 23, 16, ox + 26, 19], fill=C_DARK_JOINT, outline=C_OUTLINE)

            # Heavy bat extended straight forward at hand level!
            draw.line([(ox + 25, 17), (ox + 35, 17)], fill=C_BAT_GRIP, width=3)
            draw.line([(ox + 35, 17), (ox + 52, 17)], fill=C_BAT_STEEL, width=6)
            draw.point([(ox + 48, 13), (ox + 53, 17), (ox + 48, 21)], fill=C_BAT_SPIKE)

            # Massive shockwave wind slash arc (Dara de vant) extending to x=55!
            draw.arc([ox + 24, 3, ox + 55, 31], start=290, end=70, fill=C_BAT_WIND, width=5)
            draw.arc([ox + 28, 5, ox + 54, 29], start=305, end=55, fill=C_WIND_CORE, width=2)
            draw.line([(ox + 47, 7), (ox + 54, 12)], fill=C_WIND_CORE, width=2)
            draw.line([(ox + 49, 17), (ox + 55, 17)], fill=C_WIND_CORE, width=3)
            draw.line([(ox + 47, 27), (ox + 54, 22)], fill=C_WIND_CORE, width=2)

        # --- FRAME 3: Low Ground Slam Follow-Through ---
        elif f == 3:
            draw.line([(ox + 10, 26), (ox + 7, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 5, 32, ox + 9, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)
            draw.line([(ox + 17, 26), (ox + 20, 33)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 18, 32, ox + 23, 34], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            draw.rectangle([ox + 11, 14, ox + 20, 25], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 12, 7, ox + 22, 14], fill=C_WHITE, outline=C_OUTLINE)
            draw.rectangle([ox + 18, 9, ox + 22, 11], fill=C_CYAN_GLOW, outline=C_OUTLINE)

            # Hands low: (19, 21)
            draw.line([(ox + 15, 15), (ox + 19, 21)], fill=C_WHITE_SHADE, width=3)
            draw.rectangle([ox + 18, 20, ox + 21, 23], fill=C_DARK_JOINT, outline=C_OUTLINE)

            # Bat head hitting low ground
            draw.line([(ox + 20, 21), (ox + 28, 26)], fill=C_BAT_GRIP, width=3)
            draw.line([(ox + 28, 26), (ox + 42, 33)], fill=C_BAT_STEEL, width=6)
            # Dust / residual kinetic arc
            draw.arc([ox + 30, 20, ox + 52, 35], start=10, end=90, fill=C_BAT_WIND, width=3)

    return img

img_std_bat = generate_bat_attack("standard")
img_dmg_bat = generate_bat_attack("damaged")

img_std_bat.save(os.path.join(anim_dir, "robot_standard_attack_bat_strip4.png"))
img_dmg_bat.save(os.path.join(anim_dir, "robot_damaged_attack_bat_strip4.png"))
img_std_bat.save(os.path.join(godot_assets, "robot_standard_attack_bat_strip4.png"))
img_dmg_bat.save(os.path.join(godot_assets, "robot_damaged_attack_bat_strip4.png"))
img_std_bat.save(os.path.join(godot_copy_assets, "robot_standard_attack_bat_strip4.png"))
img_dmg_bat.save(os.path.join(godot_copy_assets, "robot_damaged_attack_bat_strip4.png"))
print("Generated robot bat attack strips.")

# ---------------------------------------------------------------------------
# 4. GENERATE UNIFIED SHOOT SPRITES: LASER BLASTER ARM SHOOTING FROM HAND LEVEL
# 40x32 per frame, 4 frames (160x32)
# Blaster arm raised at hand level (y=13..15), charging and blasting projectile straight out!
# ---------------------------------------------------------------------------
def generate_shoot(chassis="standard"):
    img = Image.new("RGBA", (40 * 4, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for f in range(4):
        ox = f * 40
        # Legs braced
        draw.line([(ox + 8, 22), (ox + 5, 29)], fill=C_WHITE_SHADE, width=3)
        draw.rectangle([ox + 3, 28, ox + 7, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)
        draw.line([(ox + 14, 22), (ox + 16, 29)], fill=C_WHITE_SHADE, width=3)
        draw.rectangle([ox + 14, 28, ox + 19, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

        # Torso
        draw.rectangle([ox + 9, 10, ox + 18, 21], fill=C_WHITE, outline=C_OUTLINE)
        if chassis == "damaged":
            draw.line([(ox + 11, 13), (ox + 15, 16)], fill=C_COPPER, width=1)
        else:
            draw.line([(ox + 13, 13), (ox + 16, 13)], fill=C_CYAN_GLOW, width=1)

        # Head
        draw.rectangle([ox + 10, 3, ox + 20, 10], fill=C_WHITE, outline=C_OUTLINE)
        draw.rectangle([ox + 16, 5, ox + 20, 7], fill=C_CYAN_GLOW, outline=C_OUTLINE)

        # RIGHT ARM: Raised straight forward into Blaster Cannon at HAND LEVEL (y=14)!
        draw.line([(ox + 14, 12), (ox + 20, 14)], fill=C_WHITE_SHADE, width=4)
        # Cyber Blaster Cannon housing
        draw.rectangle([ox + 20, 12, ox + 28, 16], fill=C_DARK_JOINT, outline=C_OUTLINE)
        draw.rectangle([ox + 28, 13, ox + 30, 15], fill=C_CYAN_GLOW, outline=C_OUTLINE) # Muzzle

        # Frame 0: Charging cyan energy at muzzle
        if f == 0:
            draw.ellipse([ox + 29, 12, ox + 33, 16], fill=C_CYAN_GLOW)
        # Frame 1: FIRE! Bright laser muzzle flash & bolt emerging straight from muzzle!
        elif f == 1:
            draw.ellipse([ox + 28, 10, ox + 36, 18], fill=C_CYAN_GLOW)
            draw.ellipse([ox + 30, 12, ox + 34, 16], fill=C_WIND_CORE)
            draw.line([(ox + 34, 14), (ox + 39, 14)], fill=C_WIND_CORE, width=3)
        # Frame 2: Recoil, arm shifted back 1px, residual energy sparks
        elif f == 2:
            draw.line([(ox + 30, 11), (ox + 35, 13)], fill=C_CYAN_GLOW, width=1)
            draw.line([(ox + 30, 17), (ox + 35, 15)], fill=C_CYAN_GLOW, width=1)
        # Frame 3: Cooling vents smoking
        elif f == 3:
            draw.point([(ox + 30, 13), (ox + 32, 12), (ox + 31, 15)], fill=C_CYAN_GLOW)

    return img

img_std_shoot = generate_shoot("standard")
img_dmg_shoot = generate_shoot("damaged")

img_std_shoot.save(os.path.join(anim_dir, "robot_standard_shoot_strip4.png"))
img_dmg_shoot.save(os.path.join(anim_dir, "robot_damaged_shoot_strip4.png"))
img_std_shoot.save(os.path.join(godot_assets, "robot_standard_shoot_strip4.png"))
img_dmg_shoot.save(os.path.join(godot_assets, "robot_damaged_shoot_strip4.png"))
img_std_shoot.save(os.path.join(godot_copy_assets, "robot_standard_shoot_strip4.png"))
img_dmg_shoot.save(os.path.join(godot_copy_assets, "robot_damaged_shoot_strip4.png"))
print("Generated robot shoot strips originating from hand level.")

# ---------------------------------------------------------------------------
# 5. GENERATE COMPLETE 3200x900 STATIC LEVEL BACKDROP
# Perfectly aligned to ground level y=780, platforms y=680, 580, 500, cranes, fences, tires
# ---------------------------------------------------------------------------
print("Generating 3200x900 complete static level backdrop...")
bg_img = Image.new("RGBA", (3200, 900), (14, 18, 25, 255))
d = ImageDraw.Draw(bg_img)

# A. SKY GRADIENT (y = 0 to 450)
for y in range(450):
    t = y / 450.0
    r = int(22 + (45 - 22) * t)
    g = int(27 + (38 - 27) * t)
    b = int(38 + (42 - 38) * t)
    d.line([(0, y), (3200, y)], fill=(r, g, b, 255))

# Toxic smog clouds drifting on horizon
for cx in range(0, 3200, 240):
    d.ellipse([cx, 160, cx + 320, 320], fill=(52, 44, 42, 120))
    d.ellipse([cx + 100, 180, cx + 450, 350], fill=(42, 35, 36, 100))

# Distant colossal transmission towers and suspension bridge on horizon (y = 220 to 480)
for tx in range(120, 3200, 600):
    # Transmission tower
    d.polygon([(tx + 40, 220), (tx + 20, 480), (tx + 60, 480)], fill=(28, 25, 32, 255))
    # Crossbeams
    for cy in range(250, 470, 45):
        d.line([(tx + 10, cy), (tx + 70, cy)], fill=(28, 25, 32, 255), width=2)
        d.line([(tx + 10, cy), (tx + 70, cy + 45)], fill=(28, 25, 32, 255), width=1)

# B. MIDGROUND MASSIVE SCRAPYARD SILHOUETTES (y = 380 to 780)
for sx in range(0, 3200, 300):
    h = 380 + (sx % 120)
    d.polygon([(sx - 40, 780), (sx + 80, h), (sx + 220, h + 60), (sx + 340, 780)], fill=(32, 28, 34, 255))

# C. TOWERING CRANES & PIPES CONNECTING TO PLATFORMS (y = 200 to 780)
# Cranes rise directly from the ground floor (y = 780) all the way up into the sky!
crane_positions = [280, 780, 1340, 1920, 2540]
for cx in crane_positions:
    # Heavy vertical crane lattice mast rising from ground floor (y = 780) up to y = 240
    d.rectangle([cx - 16, 240, cx + 16, 780], fill=(45, 36, 32, 255))
    # Truss diagonals
    for ty in range(240, 780, 36):
        d.line([(cx - 16, ty), (cx + 16, ty + 36)], fill=(65, 52, 45, 255), width=2)
        d.line([(cx + 16, ty), (cx - 16, ty + 36)], fill=(65, 52, 45, 255), width=2)
        d.line([(cx - 16, ty), (cx + 16, ty)], fill=(80, 65, 55, 255), width=2)

    # Giant angled yellow/rusty excavator boom arm at top (y = 120..260)
    boom_end_x = cx + 160
    boom_end_y = 120
    d.polygon([(cx - 20, 260), (cx + 20, 240), (boom_end_x, boom_end_y), (boom_end_x - 16, boom_end_y + 20)], fill=(180, 83, 9, 255))
    d.line([(cx, 250), (boom_end_x - 8, boom_end_y + 10)], fill=(245, 158, 11, 255), width=2)

    # Steel hoist cable hanging down towards platforms
    d.line([(boom_end_x - 8, boom_end_y + 10), (boom_end_x - 8, 520)], fill=(100, 116, 139, 255), width=2)
    # Giant Compactor Claw / Magnet hanging
    d.rectangle([boom_end_x - 22, 520, boom_end_x + 6, 545], fill=(30, 41, 59, 255))
    d.ellipse([boom_end_x - 18, 540, boom_end_x + 2, 560], fill=(245, 158, 11, 255))

# Vertical exhaust pipes and support pillars behind platforms (x = 460, 680, 980)
platform_supports = [460, 680, 980, 1600, 2100, 2700]
for px in platform_supports:
    d.rectangle([px - 14, 450, px + 14, 780], fill=(40, 48, 60, 255), outline=(20, 25, 35, 255), width=2)
    for ry in range(480, 780, 50):
        d.rectangle([px - 16, ry, px + 16, ry + 6], fill=(71, 85, 105, 255))

# D. GROUND SCENERY: FENCES, TIRES, AND WARNING SIGNS 100% ALIGNED TO FLOOR AT Y = 780!
print("Drawing fences and tires aligned to floor line at y = 780...")
for fx in range(0, 3200, 120):
    # Chainlink fence posts (y = 700 to 780)
    d.rectangle([fx, 700, fx + 6, 780], fill=(100, 116, 139, 255), outline=(51, 65, 85, 255))
    d.line([(fx, 705), (fx + 120, 705)], fill=(148, 163, 184, 255), width=2) # Top rail
    d.line([(fx, 740), (fx + 120, 740)], fill=(71, 85, 105, 255), width=1) # Mid rail
    d.line([(fx, 775), (fx + 120, 775)], fill=(71, 85, 105, 255), width=2) # Bottom rail directly on ground

    # Fence diamond wire mesh
    for mx in range(fx, fx + 120, 12):
        d.line([(mx, 705), (mx + 12, 775)], fill=(71, 85, 105, 140), width=1)
        d.line([(mx + 12, 705), (mx, 775)], fill=(71, 85, 105, 140), width=1)

    # Barbed wire coiled along top of fence (y = 694 to 704)
    for bx in range(fx, fx + 120, 16):
        d.arc([bx, 694, bx + 16, 706], start=0, end=360, fill=(148, 163, 184, 200), width=1)

    # Weathered Tire Piles resting firmly on floor (y = 744 to 780)
    if (fx // 120) % 2 == 0:
        tire_x = fx + 30
        for ty in [764, 752, 740]:
            d.ellipse([tire_x, ty, tire_x + 38, ty + 16], fill=(28, 25, 28, 255), outline=(12, 10, 12, 255), width=2)
            d.ellipse([tire_x + 9, ty + 4, tire_x + 29, ty + 12], fill=(45, 38, 42, 255))

    # Yellow Caution Warning Signs on the fence
    if (fx // 120) % 3 == 1:
        sign_x = fx + 40
        d.rectangle([sign_x, 715, sign_x + 36, 735], fill=(234, 179, 8, 255), outline=(15, 23, 42, 255), width=2)
        # Hazard stripes
        d.line([(sign_x + 4, 731), (sign_x + 12, 719)], fill=(15, 23, 42, 255), width=2)
        d.line([(sign_x + 14, 731), (sign_x + 22, 719)], fill=(15, 23, 42, 255), width=2)
        d.line([(sign_x + 24, 731), (sign_x + 32, 719)], fill=(15, 23, 42, 255), width=2)

# E. SUBTERRANEAN FOUNDATION BENEATH FLOOR (y = 780 to 900)
d.rectangle([0, 780, 3200, 900], fill=(26, 20, 18, 255))
d.line([(0, 780), (3200, 780)], fill=(75, 55, 45, 255), width=3) # Distinct floor surface line
for gx in range(0, 3200, 40):
    d.rectangle([gx, 780, gx + 38, 800], fill=(38, 30, 26, 255), outline=(20, 16, 14, 255), width=1)
    d.line([(gx + 10, 784), (gx + 12, 784)], fill=(120, 95, 80, 255), width=1) # Rivets
    d.line([(gx + 26, 784), (gx + 28, 784)], fill=(120, 95, 80, 255), width=1)

backdrop_path = os.path.join(anim_dir, "level_heap_backdrop_3200x900.png")
bg_img.save(backdrop_path)
bg_img.save(os.path.join(godot_assets, "level_heap_backdrop_3200x900.png"))
bg_img.save(os.path.join(godot_copy_assets, "level_heap_backdrop_3200x900.png"))
print("Saved 3200x900 complete static level backdrop successfully.")
