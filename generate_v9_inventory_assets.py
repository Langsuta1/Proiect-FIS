import os
from PIL import Image, ImageDraw, ImageFont

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
godot_copy_assets = os.path.join(scratch_dir, "scrapborn-(4.0)", "assets")

print("Generating V9 high-fidelity inventory UI assets matching user reference...")

def save_both(img, name):
    img.save(os.path.join(godot_assets, name))
    img.save(os.path.join(godot_copy_assets, name))

# 1. SLOT BACKGROUND (76x76) - Dark smoky stone/metal with inset bevel
slot_bg = Image.new("RGBA", (76, 76), (0, 0, 0, 0))
sd = ImageDraw.Draw(slot_bg)
# Outer subtle border
sd.rectangle([0, 0, 75, 75], fill=(16, 22, 32, 240), outline=(45, 55, 72, 255), width=2)
# Inset bevel & smoke gradient
for i in range(1, 10):
    alpha = int(140 - i * 12)
    sd.rectangle([i, i, 75 - i, 75 - i], outline=(10, 14, 20, alpha), width=1)
# Center dark smoke texture
for sx in range(12, 64, 4):
    for sy in range(12, 64, 4):
        noise = (sx * 17 + sy * 31) % 15
        sd.point([(sx, sy)], fill=(22 + noise, 30 + noise, 44 + noise, 255))
save_both(slot_bg, "inv_slot_bg.png")

# Slot Hover (Cyan glow)
slot_hover = slot_bg.copy()
shd = ImageDraw.Draw(slot_hover)
shd.rectangle([0, 0, 75, 75], outline=(56, 189, 248, 255), width=2)
save_both(slot_hover, "inv_slot_hover.png")

# Slot Selected (Gold / Amber glow)
slot_sel = slot_bg.copy()
ssd = ImageDraw.Draw(slot_sel)
ssd.rectangle([0, 0, 75, 75], outline=(245, 158, 11, 255), width=2)
save_both(slot_sel, "inv_slot_selected.png")

# 2. BANNERS (Matching the icy/slate grunge brush banners in user reference)
def make_banner(width, text, text_color):
    b = Image.new("RGBA", (width, 32), (0, 0, 0, 0))
    bd = ImageDraw.Draw(b)
    # Brush stroke white/slate gradient
    for x in range(width):
        t = x / float(width)
        fade = 1.0 - 4.0 * (t - 0.5) ** 2
        fade = max(0.4, min(1.0, fade))
        r = int(220 * fade)
        g = int(230 * fade)
        b_c = int(242 * fade)
        bd.line([(x, 4), (x, 27)], fill=(r, g, b_c, 240), width=1)
    # Dark bevel border
    bd.rectangle([2, 4, width - 3, 27], outline=(30, 41, 59, 200), width=1)
    # Text centered
    bbox = bd.textbbox((0, 0), text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = (32 - th) // 2 - 1
    bd.text((tx, ty), text, fill=text_color)
    return b

save_both(make_banner(180, "HOTBAR", (15, 23, 42, 255)), "inv_banner_hotbar.png")
save_both(make_banner(180, "MAIN HAND", (14, 116, 144, 255)), "inv_banner_mainhand.png")
save_both(make_banner(180, "SECONDARY HAND", (180, 83, 9, 255)), "inv_banner_sechand.png")
save_both(make_banner(270, "BACKPACK", (15, 23, 42, 255)), "inv_banner_backpack.png")

# 3. CONDUIT TUNNEL ENHANCED (Spanning from y=400 to y=760 so player CANNOT jump over it!)
w_c, h_c = 280, 360
conduit_img = Image.new("RGBA", (w_c, h_c), (0, 0, 0, 0))
cd = ImageDraw.Draw(conduit_img)
# Giant vertical wall of scrap, girders, and pipes reaching from top (y=0) all the way down to bottom (y=360)
cd.rectangle([0, 0, w_c, h_c - 10], fill=(42, 34, 32, 255), outline=(15, 12, 14, 255), width=3)
# Corrugated steel vertical sheets
for sx in range(10, w_c - 10, 16):
    cd.line([(sx, 10), (sx, h_c - 12)], fill=(65, 52, 48, 255), width=4)
    cd.line([(sx + 4, 10), (sx + 4, h_c - 12)], fill=(28, 22, 20, 255), width=2)
# Massive horizontal industrial pipes
for py in [60, 140, 220, 300]:
    cd.rectangle([0, py, w_c, py + 22], fill=(71, 85, 105, 255), outline=(15, 23, 42, 255), width=2)
    for px in range(15, w_c, 35):
        cd.rectangle([px, py - 2, px + 8, py + 24], fill=(100, 116, 139, 255))
# Heavy reinforced steel bottom lip with hazard stripes (y = h_c - 26 to h_c - 10)
cd.rectangle([0, h_c - 26, w_c, h_c - 10], fill=(234, 179, 8, 255), outline=(15, 23, 42, 255), width=2)
for hx in range(4, w_c, 16):
    cd.polygon([(hx, h_c - 11), (hx + 8, h_c - 25), (hx + 12, h_c - 25), (hx + 4, h_c - 11)], fill=(15, 23, 42, 255))

save_both(conduit_img, "scrap_conduit_tunnel_tall.png")
print("V9 Inventory & Tall Conduit assets generated successfully.")
