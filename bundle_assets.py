import os
import base64
import json

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
sheets_dir = os.path.join(scratch_dir, "animations", "sheets")
godot_assets = os.path.join(scratch_dir, "godot_project", "assets")
weapons_dir = os.path.join(scratch_dir, "weapons")
chars_dir = os.path.join(scratch_dir, "characters")
grenades_dir = os.path.join(scratch_dir, "grenades")

assets = {}

for path in [sheets_dir, godot_assets, weapons_dir, chars_dir, grenades_dir]:
    if not os.path.exists(path):
        continue
    for f in os.listdir(path):
        if not f.endswith(".png"):
            continue
        if "_hd" in f or "showcase" in f:
            continue
        name = os.path.splitext(f)[0]
        full_path = os.path.join(path, f)
        with open(full_path, "rb") as fp:
            b64 = base64.b64encode(fp.read()).decode("utf-8")
            assets[name] = f"data:image/png;base64,{b64}"

print(f"Collected {len(assets)} pixel assets for SCRAPBORN Demo.")
with open(os.path.join(scratch_dir, "assets_bundle.json"), "w", encoding="utf-8") as fp:
    json.dump(assets, fp)

print("Saved assets_bundle.json successfully.")
