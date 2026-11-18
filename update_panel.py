import os

for base in ['godot_project', 'scrapborn-(4.0)']:
    path = os.path.join(base, 'scenes', 'hud.tscn')
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    old_str = '[node name="Panel" type="Panel" parent="InventoryModal"]'
    new_str = '[node name="Panel" type="Panel" parent="InventoryModal"]\nscript = ExtResource("2_dimmer")'
    if old_str in c and new_str not in c:
        c = c.replace(old_str, new_str)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(c)

print("Updated Panel in hud.tscn successfully.")
