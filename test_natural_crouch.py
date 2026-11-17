import os
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")
anim_dir = os.path.join(scratch_dir, "animations", "sheets")

# Load reference idle images for exact color palette
idle_std = Image.open(os.path.join(godot_assets, "robot_standard_idle_strip4.png"))
f0_std = idle_std.crop((0, 0, 32, 32))

C_TRANS = (0, 0, 0, 0)
C_OUTLINE = (14, 18, 25, 255)
C_SLATE = (51, 65, 85, 255)
C_DARK_SLATE = (30, 41, 59, 255)
C_WHITE = (248, 250, 252, 255)
C_WHITE_SHADE = (203, 213, 225, 255)
C_CYAN_GLOW = (0, 245, 255, 255)
C_CYAN_HI = (170, 245, 255, 255)
C_COPPER = (217, 119, 6, 255)
C_COPPER_HI = (245, 158, 11, 255)

def draw_natural_crouch(is_damaged=False, frame=0):
    im = Image.new("RGBA", (32, 32), C_TRANS)
    d = ImageDraw.Draw(im)
    bob = 1 if frame == 1 else 0

    # 1. FAR / BACK LEG (Tucked back, knee low, toe on ground)
    # Thigh from hip (11, 18+bob) down-back to knee (6, 23+bob)
    d.line([(11, 18 + bob), (6, 23 + bob)], fill=C_DARK_SLATE, width=3)
    # Shin from knee (6, 23+bob) to heel/toe (5, 28)
    d.line([(6, 23 + bob), (5, 28)], fill=C_DARK_SLATE, width=3)
    # Back foot pad resting on toe (cyan sole)
    d.rectangle([3, 28, 8, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

    # 2. PELVIS & HIPS (Low center of gravity at y=17..20)
    d.rectangle([9, 16 + bob, 16, 20 + bob], fill=C_DARK_SLATE, outline=C_OUTLINE)
    d.line([(11, 17 + bob), (14, 19 + bob)], fill=C_WHITE_SHADE, width=1)

    # 3. NEAR / FRONT LEG (Bent forward in athletic runner's crouch: thigh angled forward, knee forward at x=19)
    # Thigh from hip (14, 17+bob) to front knee (19, 21+bob)
    d.line([(14, 17 + bob), (19, 21 + bob)], fill=C_WHITE, width=4)
    d.line([(14, 17 + bob), (19, 21 + bob)], fill=C_WHITE_SHADE, width=2)
    # Front knee joint
    d.rectangle([18, 20 + bob, 21, 23 + bob], fill=C_SLATE, outline=C_OUTLINE)
    # Front shin coming straight down from knee (19, 23+bob) to front foot (17, 28)
    d.line([(19, 23 + bob), (17, 28)], fill=C_WHITE_SHADE, width=3)
    # Front foot pad flat on ground with glowing cyan sole
    d.rectangle([13, 28, 20, 30], fill=C_CYAN_GLOW, outline=C_OUTLINE)

    # 4. TORSO (Leaning forward aerodynamically over front knee, y=10..17+bob)
    tx = 10
    ty = 10 + bob
    # Dark chassis back
    d.polygon([(tx, ty + 2), (tx + 10, ty), (tx + 11, ty + 7), (tx + 1, ty + 8)], fill=C_SLATE, outline=C_OUTLINE)
    # White chest armor plate
    d.polygon([(tx + 3, ty + 1), (tx + 9, ty + 1), (tx + 10, ty + 6), (tx + 4, ty + 6)], fill=C_WHITE)
    d.line([(tx + 4, ty + 6), (tx + 9, ty + 6)], fill=C_WHITE_SHADE, width=1)
    # Glowing Cyan Core Reactor angled forward
    d.rectangle([tx + 7, ty + 2, tx + 9, ty + 4], fill=C_CYAN_GLOW)
    d.point((tx + 8, ty + 3), fill=(255, 255, 255, 255))

    # 5. HEAD (Alert, looking forward, sleek curved helmet at y=4..9+bob)
    hx = 13
    hy = 4 + bob
    # Curved helmet dome (white + shade)
    d.polygon([(hx, hy + 2), (hx + 4, hy), (hx + 8, hy), (hx + 8, hy + 5), (hx + 1, hy + 5)], fill=C_WHITE, outline=C_OUTLINE)
    d.line([(hx + 1, hy + 2), (hx + 4, hy + 1)], fill=C_WHITE_SHADE, width=1)
    # Cyan Optic Visor peering forward low
    d.rectangle([hx + 7, hy + 2, hx + 10, hy + 4], fill=C_CYAN_GLOW, outline=C_OUTLINE)
    d.point((hx + 8, hy + 3), fill=(255, 255, 255, 255))
    # Neck joint
    d.rectangle([hx - 1, hy + 5, hx + 2, hy + 7], fill=C_DARK_SLATE)

    # 6. RIGHT ARM (Resting forward across the front knee, ready to strike!)
    if is_damaged:
        # Loose copper wires hanging over front knee
        d.line([(tx + 6, ty + 3), (tx + 10, ty + 7)], fill=C_SLATE, width=2)
        d.point((tx + 11, ty + 8), fill=C_COPPER)
        d.point((tx + 10, ty + 9), fill=C_COPPER_HI)
        d.point((tx + 12, ty + 9), fill=C_CYAN_GLOW)
    else:
        # Sleek white pauldron & arm resting on knee
        d.line([(tx + 6, ty + 3), (tx + 11, ty + 8)], fill=C_WHITE_SHADE, width=3)
        d.rectangle([tx + 10, ty + 7, tx + 13, ty + 10], fill=C_SLATE, outline=C_OUTLINE) # Hand

    return im

def build_natural_crouch_strip(is_damaged=False):
    sheet = Image.new("RGBA", (64, 32), C_TRANS)
    f0 = draw_natural_crouch(is_damaged, frame=0)
    f1 = draw_natural_crouch(is_damaged, frame=1)
    sheet.paste(f0, (0, 0))
    sheet.paste(f1, (32, 0))
    return sheet

crouch_std_nat = build_natural_crouch_strip(False)
crouch_dmg_nat = build_natural_crouch_strip(True)

crouch_std_nat.save(os.path.join(godot_assets, "robot_standard_crouch_strip2.png"))
crouch_dmg_nat.save(os.path.join(godot_assets, "robot_damaged_crouch_strip2.png"))
crouch_std_nat.save(os.path.join(anim_dir, "robot_standard_crouch_strip2.png"))
crouch_dmg_nat.save(os.path.join(anim_dir, "robot_damaged_crouch_strip2.png"))
crouch_std_nat.save(os.path.join(godot_copy_assets, "robot_standard_crouch_strip2.png"))
crouch_dmg_nat.save(os.path.join(godot_copy_assets, "robot_damaged_crouch_strip2.png"))

# Zoom in and save preview for inspection
zoom = crouch_std_nat.resize((128, 64), Image.NEAREST)
zoom.save(r'c:\Users\cozy1\.gemini\antigravity\scratch\natural_crouch_zoom.png')
print("Saved natural crouch sprites.")
