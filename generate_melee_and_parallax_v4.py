import os
from PIL import Image, ImageDraw

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
anim_dir = os.path.join(scratch_dir, "animations", "sheets")
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
os.makedirs(anim_dir, exist_ok=True)
os.makedirs(godot_assets, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. GENERATE MELEE SWING STRIP: CYBER FRYING PAN (4 frames, 48x32 each)
# Designed facing RIGHT (origin at player hand x=8, y=16)
# Frame 0: Windup high behind shoulder
# Frame 1: Downward sweeping strike with initial wind arc
# Frame 2: Full horizontal slash forward with wide glowing wind trail (dara de vant)
# Frame 3: Low follow-through as wind dissipates
# ---------------------------------------------------------------------------

pan_img = Image.new("RGBA", (48 * 4, 32), (0, 0, 0, 0))
draw_pan = ImageDraw.Draw(pan_img)

# Color Palette: Cyber Frying Pan & Wind Arc
C_HANDLE = (71, 85, 105, 255)      # Slate gray grip
C_ACCENT = (0, 240, 255, 255)      # Cyan cyber glow
C_PAN_RIM = (148, 163, 184, 255)   # Metallic rim
C_PAN_BODY = (30, 41, 59, 255)     # Deep dark iron
C_PAN_GLOW = (251, 191, 36, 255)   # Amber induction heating element
C_WIND_CORE = (255, 255, 255, 240) # Pure white cutting edge
C_WIND_CYAN = (56, 189, 248, 200)  # Bright cyan wind trail
C_WIND_FADE = (14, 165, 233, 100)  # Outer fading plasma

# FRAME 0: Windup (raised behind shoulder, x=4..18, y=4..20)
ox = 0
# Handle from hand (x=12, y=18) up-left to (x=6, y=10)
draw_pan.line([(ox + 12, 18), (ox + 7, 10)], fill=C_HANDLE, width=3)
draw_pan.point([(ox + 12, 18), (ox + 11, 17)], fill=C_ACCENT)
# Pan head angled back
draw_pan.ellipse([ox + 2, 2, ox + 12, 14], fill=C_PAN_BODY, outline=C_PAN_RIM, width=2)
draw_pan.line([(ox + 4, 8), (ox + 10, 8)], fill=C_PAN_GLOW, width=1)
# Small windup aura
draw_pan.arc([ox + 1, 1, ox + 14, 15], start=180, end=320, fill=C_WIND_FADE, width=2)

# FRAME 1: Mid-downswing (slashing overhead forward, x=8..36, y=2..22)
ox = 48
# Handle from (10, 16) to (20, 10)
draw_pan.line([(ox + 10, 16), (ox + 22, 10)], fill=C_HANDLE, width=3)
draw_pan.point([(ox + 10, 16)], fill=C_ACCENT)
# Pan head overhead angled forward
draw_pan.ellipse([ox + 20, 4, ox + 32, 16], fill=C_PAN_BODY, outline=C_PAN_RIM, width=2)
draw_pan.line([(ox + 23, 10), (ox + 29, 10)], fill=C_PAN_GLOW, width=2)
# Wind Slash Trail 1: Crescent arc curving overhead
draw_pan.arc([ox + 10, 1, ox + 40, 24], start=220, end=350, fill=C_WIND_FADE, width=3)
draw_pan.arc([ox + 14, 2, ox + 38, 22], start=240, end=340, fill=C_WIND_CYAN, width=2)
draw_pan.arc([ox + 18, 3, ox + 36, 20], start=260, end=330, fill=C_WIND_CORE, width=1)

# FRAME 2: Full Extension Forward Slash (Maximum reach & large wind slash dara de vant!)
ox = 96
# Handle extending straight forward from hand (10, 16) to (26, 16)
draw_pan.line([(ox + 10, 16), (ox + 26, 16)], fill=C_HANDLE, width=3)
draw_pan.point([(ox + 10, 16), (ox + 11, 16)], fill=C_ACCENT)
# Pan head forward (24, 10) to (38, 22)
draw_pan.ellipse([ox + 24, 10, ox + 38, 22], fill=C_PAN_BODY, outline=C_PAN_RIM, width=2)
draw_pan.ellipse([ox + 27, 13, ox + 35, 19], fill=C_PAN_GLOW)
# Glorious Wind Slash Blade (Dara de vant) extending from x=20 to x=46, y=2 to y=30
# Outer fade
draw_pan.arc([ox + 16, 2, ox + 47, 30], start=290, end=70, fill=C_WIND_FADE, width=4)
# Bright cyan wind
draw_pan.arc([ox + 20, 4, ox + 46, 28], start=300, end=60, fill=C_WIND_CYAN, width=3)
# Sharp white core edge cutting ahead
draw_pan.arc([ox + 24, 6, ox + 45, 26], start=315, end=45, fill=C_WIND_CORE, width=2)
# Slash wind whisps/speedlines
draw_pan.line([(ox + 38, 7), (ox + 46, 11)], fill=C_WIND_CORE, width=1)
draw_pan.line([(ox + 40, 16), (ox + 47, 16)], fill=C_WIND_CORE, width=2)
draw_pan.line([(ox + 38, 25), (ox + 46, 21)], fill=C_WIND_CORE, width=1)

# FRAME 3: Low Follow-through & Dissipation (x=8..36, y=14..30)
ox = 144
# Handle angled down-forward from (10, 16) to (22, 24)
draw_pan.line([(ox + 10, 16), (ox + 22, 24)], fill=C_HANDLE, width=3)
# Pan head down
draw_pan.ellipse([ox + 20, 20, ox + 32, 30], fill=C_PAN_BODY, outline=C_PAN_RIM, width=2)
draw_pan.line([(ox + 23, 25), (ox + 29, 25)], fill=C_PAN_GLOW, width=1)
# Dissipating wind particles/lines
draw_pan.arc([ox + 22, 14, ox + 44, 31], start=20, end=90, fill=C_WIND_FADE, width=2)
draw_pan.point([(ox + 42, 18), (ox + 40, 22), (ox + 36, 26), (ox + 30, 29)], fill=C_WIND_CYAN)

pan_path = os.path.join(anim_dir, "weapon_pan_swing_strip4.png")
pan_img.save(pan_path)
pan_img.save(os.path.join(godot_assets, "weapon_pan_swing_strip4.png"))
print("Saved weapon_pan_swing_strip4.png successfully.")


# ---------------------------------------------------------------------------
# 2. GENERATE MELEE SWING STRIP: REINFORCED METAL BAT (4 frames, 56x36 each)
# Heavy crusher bat with industrial spikes and wide shockwave wind slash
# ---------------------------------------------------------------------------
bat_img = Image.new("RGBA", (56 * 4, 36), (0, 0, 0, 0))
draw_bat = ImageDraw.Draw(bat_img)

C_BAT_GRIP = (180, 83, 9, 255)     # Wrapped leather/tape grip
C_BAT_STEEL = (156, 163, 175, 255) # Heavy reinforced steel
C_BAT_SPIKE = (254, 240, 138, 255) # Sharp jagged spikes
C_BAT_WIND = (245, 158, 11, 200)   # Amber/kinetic shockwave
C_BAT_WIND_CORE = (255, 255, 255, 240)

# FRAME 0: High windup over shoulder
ox = 0
draw_bat.line([(ox + 12, 20), (ox + 8, 14)], fill=C_BAT_GRIP, width=3)
draw_bat.line([(ox + 8, 14), (ox + 3, 4)], fill=C_BAT_STEEL, width=5)
draw_bat.point([(ox + 2, 6), (ox + 1, 9), (ox + 5, 3)], fill=C_BAT_SPIKE)

# FRAME 1: Heavy downswing coming forward
ox = 56
draw_bat.line([(ox + 12, 18), (ox + 22, 12)], fill=C_BAT_GRIP, width=3)
draw_bat.line([(ox + 22, 12), (ox + 38, 5)], fill=C_BAT_STEEL, width=6)
# Spikes
draw_bat.point([(ox + 34, 3), (ox + 39, 4), (ox + 36, 7)], fill=C_BAT_SPIKE)
# Kinetic wind arc
draw_bat.arc([ox + 12, 2, ox + 48, 30], start=240, end=340, fill=C_BAT_WIND, width=3)

# FRAME 2: Maximum Slam / Horizontal Impact with Massive Wind Slash
ox = 112
draw_bat.line([(ox + 10, 18), (ox + 24, 18)], fill=C_BAT_GRIP, width=3)
draw_bat.line([(ox + 24, 18), (ox + 46, 18)], fill=C_BAT_STEEL, width=6)
draw_bat.point([(ox + 42, 14), (ox + 47, 18), (ox + 42, 22)], fill=C_BAT_SPIKE)
# Massive wind slash arc extending forward to 55px!
draw_bat.arc([ox + 18, 2, ox + 55, 34], start=290, end=70, fill=C_BAT_WIND, width=5)
draw_bat.arc([ox + 22, 5, ox + 54, 31], start=305, end=55, fill=C_WIND_CORE, width=2)
draw_bat.line([(ox + 46, 8), (ox + 54, 12)], fill=C_WIND_CORE, width=2)
draw_bat.line([(ox + 48, 18), (ox + 55, 18)], fill=C_WIND_CORE, width=3)
draw_bat.line([(ox + 46, 28), (ox + 54, 24)], fill=C_WIND_CORE, width=2)

# FRAME 3: Ground follow-through & shock dust
ox = 168
draw_bat.line([(ox + 10, 18), (ox + 22, 24)], fill=C_BAT_GRIP, width=3)
draw_bat.line([(ox + 22, 24), (ox + 38, 32)], fill=C_BAT_STEEL, width=6)
# Residual shockwave
draw_bat.arc([ox + 24, 18, ox + 52, 35], start=10, end=90, fill=C_BAT_WIND, width=3)

bat_path = os.path.join(anim_dir, "weapon_bat_slam_strip4.png")
bat_img.save(bat_path)
bat_img.save(os.path.join(godot_assets, "weapon_bat_slam_strip4.png"))
print("Saved weapon_bat_slam_strip4.png successfully.")
