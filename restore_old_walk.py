import os
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")
anim_dir = os.path.join(scratch_dir, "animations", "sheets")

# Colors from generate_apocalyptic_assets.py
CLR_TRANS = (0, 0, 0, 0)
CLR_OUTLINE = (14, 18, 25, 255)
CLR_TITANIUM = (248, 250, 252, 255)
CLR_TITANIUM_SHADOW = (203, 213, 225, 255)
CLR_FRAME_MID = (51, 65, 85, 255)
CLR_FRAME_DARK = (30, 41, 59, 255)
CLR_FRAME_LIGHT = (100, 116, 139, 255)
CLR_CYAN_GLOW = (0, 245, 255, 255)
CLR_CYAN_DARK = (2, 132, 199, 255)
CLR_COPPER = (217, 119, 6, 255)
CLR_COPPER_DARK = (180, 83, 9, 255)
CLR_YELLOW_WIRE = (250, 204, 21, 255)

def draw_scraps_humanoid_frame(f_idx, is_damaged=False):
    im = Image.new("RGBA", (32, 32), CLR_TRANS)
    d = ImageDraw.Draw(im)

    body_bob = [0, 1, 0, -1, 0, 1, 0, -1]
    body_y = body_bob[f_idx]
    arm_swings = [-4, -2, 0, 3, 5, 2, -1, -3]
    arm_swing = arm_swings[f_idx]

    # --- FAR ARM ---
    if not is_damaged:
        far_arm_x = 16 - arm_swing
        far_arm_y = 9 + body_y
        d.line([(16, 8 + body_y), (far_arm_x, far_arm_y + 4)], fill=CLR_FRAME_DARK, width=2)
        d.line([(far_arm_x, far_arm_y + 4), (far_arm_x + 1, far_arm_y + 7)], fill=CLR_FRAME_MID, width=2)

    # --- FAR LEG ---
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
    d.line([(14, 16 + body_y), ((14 + flx) // 2, (18 + fly) // 2)], fill=CLR_FRAME_DARK, width=3)
    d.line([((14 + flx) // 2, (18 + fly) // 2), (flx, fly)], fill=CLR_FRAME_MID, width=3)
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

    # --- NEAR LEG ---
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
    d.line([(15, 16 + body_y), (knee_x, knee_y)], fill=CLR_TITANIUM, width=4)
    d.line([(15, 16 + body_y), (knee_x, knee_y)], fill=CLR_OUTLINE, width=1)
    d.line([(knee_x, knee_y), (nlx, nly)], fill=CLR_TITANIUM_SHADOW, width=3)
    d.point((knee_x, knee_y), fill=CLR_FRAME_LIGHT)
    d.rectangle([nlx - 2, nly, nlx + 3, nly + 2], fill=CLR_CYAN_GLOW, outline=CLR_OUTLINE)

    # --- NEAR ARM ---
    if is_damaged:
        stump_x = 16 + arm_swing
        stump_y = 8 + body_y
        d.line([(16, 8 + body_y), (stump_x, stump_y + 3)], fill=CLR_FRAME_MID, width=3)
        d.point((stump_x, stump_y + 4), fill=CLR_COPPER)
        d.point((stump_x + (1 if f_idx % 2 == 0 else -1), stump_y + 5), fill=CLR_YELLOW_WIRE)
        d.point((stump_x, stump_y + 6), fill=CLR_COPPER_DARK)
        if f_idx in [0, 4]:
            d.point((stump_x + 1, stump_y + 5), fill=CLR_CYAN_GLOW)
    else:
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

strip_std_8 = build_smooth_8frame_walk_strip(is_damaged=False)
strip_dmg_8 = build_smooth_8frame_walk_strip(is_damaged=True)

for p in [godot_assets, godot_copy_assets, anim_dir]:
    strip_std_8.save(os.path.join(p, "robot_standard_walk_strip8.png"))
    strip_dmg_8.save(os.path.join(p, "robot_damaged_walk_strip8.png"))

print("Restored old smooth 8-frame humanoid walk strips successfully.")
