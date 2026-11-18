import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

hud_tscn = """[gd_scene load_steps=2 format=3 uid="uid://hud_v8_reference_inv"]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_hud"]

[node name="HUD" type="CanvasLayer"]
layer = 100
script = ExtResource("1_hud")

[node name="HUDPanel" type="Panel" parent="."]
offset_left = 16.0
offset_top = 16.0
offset_right = 240.0
offset_bottom = 100.0

[node name="VBox" type="VBoxContainer" parent="HUDPanel"]
layout_mode = 0
offset_left = 8.0
offset_top = 6.0
offset_right = 216.0
offset_bottom = 90.0

[node name="HPContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="HPTrack" type="ColorRect" parent="HUDPanel/VBox/HPContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="HPFill" type="ColorRect" parent="HUDPanel/VBox/HPContainer/HPTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.93, 0.27, 0.27, 1)

[node name="HPLabel" type="Label" parent="HUDPanel/VBox/HPContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "ARMOR: 100 / 100"

[node name="EPContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="EPTrack" type="ColorRect" parent="HUDPanel/VBox/EPContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="EPFill" type="ColorRect" parent="HUDPanel/VBox/EPContainer/EPTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.22, 0.74, 0.97, 1)

[node name="EPLabel" type="Label" parent="HUDPanel/VBox/EPContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "CORE STAMINA: 100 / 100"

[node name="ShieldContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="ShieldTrack" type="ColorRect" parent="HUDPanel/VBox/ShieldContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="ShieldFill" type="ColorRect" parent="HUDPanel/VBox/ShieldContainer/ShieldTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.02, 0.71, 0.83, 1)

[node name="ShieldLabel" type="Label" parent="HUDPanel/VBox/ShieldContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "SHIELD: 50 / 50"

[node name="WeaponCard" type="Panel" parent="."]
offset_left = 16.0
offset_top = 450.0
offset_right = 260.0
offset_bottom = 530.0

[node name="VBox" type="VBoxContainer" parent="WeaponCard"]
layout_mode = 0
offset_left = 8.0
offset_top = 6.0
offset_right = 236.0
offset_bottom = 74.0

[node name="PrimaryLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_font_sizes/font_size = 12
text = "MAIN HAND: CYBER PAN"

[node name="SecondaryLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.7, 0.75, 0.85, 1)
theme_override_font_sizes/font_size = 12
text = "SECONDARY: BLASTER"

[node name="GrenadeLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_font_sizes/font_size = 11
text = "GRENADE: FRAG (x3)"

[node name="BossPanel" type="Panel" parent="."]
visible = false
offset_left = 300.0
offset_top = 20.0
offset_right = 760.0
offset_bottom = 70.0

[node name="BossBar" type="ProgressBar" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 24.0
offset_right = 450.0
offset_bottom = 40.0
value = 100.0
show_percentage = false

[node name="PhaseLabel" type="Label" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 4.0
offset_right = 450.0
offset_bottom = 22.0
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_font_sizes/font_size = 11
text = "PHASE 1 - COMPACTOR OVERLOAD"

[node name="InventoryModal" type="Control" parent="."]
visible = false
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Dimmer" type="ColorRect" parent="InventoryModal"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
color = Color(0.04, 0.06, 0.09, 0.8)

[node name="Panel" type="Panel" parent="InventoryModal"]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -310.0
offset_top = -210.0
offset_right = 310.0
offset_bottom = 210.0
grow_horizontal = 2
grow_vertical = 2

[node name="HBox" type="HBoxContainer" parent="InventoryModal/Panel"]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -280.0
offset_top = -180.0
offset_right = 280.0
offset_bottom = 160.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/separation = 40

[node name="LeftCol" type="VBoxContainer" parent="InventoryModal/Panel/HBox"]
custom_minimum_size = Vector2(170, 320)
layout_mode = 2
theme_override_constants/separation = 10

[node name="HotbarBanner" type="Label" parent="InventoryModal/Panel/HBox/LeftCol"]
layout_mode = 2
theme_override_colors/font_color = Color(0.9, 0.95, 1, 1)
theme_override_font_sizes/font_size = 14
text = "-- HOTBAR --"
horizontal_alignment = 1

[node name="MainHandBanner" type="Label" parent="InventoryModal/Panel/HBox/LeftCol"]
layout_mode = 2
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_font_sizes/font_size = 11
text = "MAIN HAND"
horizontal_alignment = 1

[node name="SlotMain" type="Button" parent="InventoryModal/Panel/HBox/LeftCol"]
custom_minimum_size = Vector2(160, 70)
layout_mode = 2
text = "Cyber Pan"

[node name="SecHandBanner" type="Label" parent="InventoryModal/Panel/HBox/LeftCol"]
layout_mode = 2
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_font_sizes/font_size = 11
text = "SECONDARY HAND"
horizontal_alignment = 1

[node name="SlotSec" type="Button" parent="InventoryModal/Panel/HBox/LeftCol"]
custom_minimum_size = Vector2(160, 70)
layout_mode = 2
text = "Laser Blaster"

[node name="RightCol" type="VBoxContainer" parent="InventoryModal/Panel/HBox"]
custom_minimum_size = Vector2(300, 320)
layout_mode = 2
theme_override_constants/separation = 10

[node name="BackpackBanner" type="Label" parent="InventoryModal/Panel/HBox/RightCol"]
layout_mode = 2
theme_override_colors/font_color = Color(0.9, 0.95, 1, 1)
theme_override_font_sizes/font_size = 14
text = "-- BACKPACK (3x3) --"
horizontal_alignment = 1

[node name="BackpackGrid" type="GridContainer" parent="InventoryModal/Panel/HBox/RightCol"]
layout_mode = 2
columns = 3
theme_override_constants/h_separation = 8
theme_override_constants/v_separation = 8

[node name="HelpLabel" type="Label" parent="InventoryModal/Panel"]
layout_mode = 1
anchors_preset = 7
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -270.0
offset_top = -28.0
offset_right = 270.0
offset_bottom = -10.0
grow_horizontal = 2
grow_vertical = 0
theme_override_colors/font_color = Color(0.6, 0.7, 0.8, 1)
theme_override_font_sizes/font_size = 10
text = "Click a slot to select, then click another slot to swap! Press [I] to close."
horizontal_alignment = 1
"""

for d in [godot_dir, godot_copy_dir]:
    path = os.path.join(d, "scenes", "hud.tscn")
    with open(path, "w", encoding="utf-8") as f:
        f.write(hud_tscn)

print("hud.tscn updated successfully.")
