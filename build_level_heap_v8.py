import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

level_heap_tscn = """[gd_scene load_steps=14 format=3 uid="uid://level_heap_v8_visible_conduit"]

[ext_resource type="Texture2D" path="res://assets/level_heap_backdrop_5200x900.png" id="1_backdrop"]
[ext_resource type="Texture2D" path="res://assets/crushed_car_obstacle.png" id="2_car_tex"]
[ext_resource type="Texture2D" path="res://assets/scrap_conduit_tunnel.png" id="3_conduit_tex"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="4_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="5_drone"]
[ext_resource type="PackedScene" path="res://scenes/enemy_crawler.tscn" id="6_crawler"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="7_boss"]
[ext_resource type="PackedScene" path="res://scenes/tutorial_prompt.tscn" id="8_tut"]
[ext_resource type="Texture2D" path="res://assets/grapple_ring_32x32.png" id="9_ring"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_floor1"]
size = Vector2(2800, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_floor2"]
size = Vector2(1600, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_conduit_roof"]
size = Vector2(240, 140)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_car"]
size = Vector2(56, 24)

[node name="LevelHeap" type="Node2D"]

[node name="StaticBackdrop" type="Sprite2D" parent="."]
z_index = -10
position = Vector2(2600, 450)
texture = ExtResource("1_backdrop")

[node name="StaticGeometry" type="StaticBody2D" parent="."]
collision_mask = 0

[node name="Floor1" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(1400, 800)
shape = SubResource("RectangleShape2D_floor1")

[node name="Floor2" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(4400, 800)
shape = SubResource("RectangleShape2D_floor2")

[node name="CrushedCarObstacle" type="StaticBody2D" parent="."]
position = Vector2(320, 768)
collision_layer = 1
collision_mask = 0

[node name="Sprite2D" type="Sprite2D" parent="CrushedCarObstacle"]
texture = ExtResource("2_car_tex")

[node name="CollisionShape2D" type="CollisionShape2D" parent="CrushedCarObstacle"]
shape = SubResource("RectangleShape2D_car")

[node name="ScrapConduitTunnel" type="StaticBody2D" parent="."]
position = Vector2(860, 690)
collision_layer = 1
collision_mask = 0

[node name="Sprite2D" type="Sprite2D" parent="ScrapConduitTunnel"]
texture = ExtResource("3_conduit_tex")

[node name="CollisionShape2D" type="CollisionShape2D" parent="ScrapConduitTunnel"]
position = Vector2(0, -40)
shape = SubResource("RectangleShape2D_conduit_roof")

[node name="GrappleRing1" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3000, 560)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing1"]
texture = ExtResource("9_ring")

[node name="GrappleRing2" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3200, 540)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing2"]
texture = ExtResource("9_ring")

[node name="GrappleRing3" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3400, 560)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing3"]
texture = ExtResource("9_ring")

[node name="Player" parent="." instance=ExtResource("4_player")]
position = Vector2(80, 750)

[node name="TutorialMove" parent="." instance=ExtResource("8_tut")]
position = Vector2(100, 715)
tutorial_title = "A / D"
tutorial_desc = "MOVE CHASSIS\\nHold [SHIFT] to Sprint"
detection_radius = 140.0

[node name="TutorialJumpCar" parent="." instance=ExtResource("8_tut")]
position = Vector2(310, 715)
tutorial_title = "[SPACE] TO JUMP"
tutorial_desc = "Leap over crushed car obstacle"
detection_radius = 160.0

[node name="TutorialCrouch" parent="." instance=ExtResource("8_tut")]
position = Vector2(720, 715)
tutorial_title = "[S] / [DOWN] CROUCH"
tutorial_desc = "Crawl through low scrap conduit\\n(Clearance 20px - crouch to pass!)"
detection_radius = 160.0

[node name="TutorialMelee" parent="." instance=ExtResource("8_tut")]
position = Vector2(1300, 715)
tutorial_title = "[X] / [LEFT CLICK]"
tutorial_desc = "Swing Cyber Frying Pan\\nto shatter scrap barricade"
detection_radius = 160.0

[node name="TutorialSafeCombat" parent="." instance=ExtResource("8_tut")]
position = Vector2(1700, 715)
tutorial_title = "SAFE COMBAT ARENA"
tutorial_desc = "Defeat isolated Scrap Crawler\\nand Junk Drone to advance"
detection_radius = 180.0

[node name="TutorialShield" parent="." instance=ExtResource("8_tut")]
position = Vector2(2450, 715)
tutorial_title = "HOLD [F] / [RIGHT CLICK]"
tutorial_desc = "Deploy Energy Shield\\n(Regens 15%/s after 3s non-use)"
detection_radius = 180.0

[node name="TutorialGrapple" parent="." instance=ExtResource("8_tut")]
position = Vector2(2750, 715)
tutorial_title = "[E] GRAPPLING HOOK"
tutorial_desc = "Latch onto overhead rings\\nSwing across colossal death chasm!"
detection_radius = 200.0

[node name="TutorialGrenade" parent="." instance=ExtResource("8_tut")]
position = Vector2(3750, 715)
tutorial_title = "[G] FRAG GRENADE"
tutorial_desc = "Blast open reinforced steel bulkhead"
detection_radius = 180.0

[node name="TutorialPreBoss" parent="." instance=ExtResource("8_tut")]
position = Vector2(3980, 715)
tutorial_title = "[I] INVENTORY & [Q] SWAP"
tutorial_desc = "Configure 3x3 Arsenal Matrix\\nPrepare for The Crusher Titan!"
detection_radius = 180.0

[node name="EnemyCrawler1" parent="." instance=ExtResource("6_crawler")]
position = Vector2(1900, 768)

[node name="EnemyDrone1" parent="." instance=ExtResource("5_drone")]
position = Vector2(2100, 580)

[node name="BossCrusher" parent="." instance=ExtResource("7_boss")]
position = Vector2(4600, 740)
"""

for d in [godot_dir, godot_copy_dir]:
    path = os.path.join(d, "scenes", "level_heap.tscn")
    with open(path, "w", encoding="utf-8") as f:
        f.write(level_heap_tscn)

print("level_heap.tscn updated with visible Scrap Conduit Tunnel.")
