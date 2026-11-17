import os
import shutil
import json

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

# ---------------------------------------------------------------------------
# 1. Update GameManager with "crouch" input action
# ---------------------------------------------------------------------------
gm_path = os.path.join(godot_dir, "autoload", "game_manager.gd")
with open(gm_path, "r", encoding="utf-8") as f:
    gm_text = f.read()

if '"crouch"' not in gm_text:
    gm_text = gm_text.replace(
        '"sprint": [KEY_SHIFT],',
        '"sprint": [KEY_SHIFT],\n\t\t"crouch": [KEY_S, KEY_DOWN],'
    )
    for d in [godot_dir, godot_copy_dir]:
        with open(os.path.join(d, "autoload", "game_manager.gd"), "w", encoding="utf-8") as f:
            f.write(gm_text)
    print("Updated game_manager.gd with crouch action.")

# ---------------------------------------------------------------------------
# 2. Update player.gd with Unified Attack (Arm Swing from Hand Level) & Crouch
# ---------------------------------------------------------------------------
player_gd = """extends CharacterBody2D
class_name Player
# player.gd - Metroidvania Player Controller with Arm Swing Attack, Hand Shooting & Crouch

# Movement physics parameters
@export var walk_speed: float = 145.0
@export var sprint_speed: float = 230.0
@export var crouch_speed: float = 55.0
@export var jump_velocity: float = -380.0
@export var double_jump_velocity: float = -330.0
@export var dash_speed: float = 420.0
@export var dash_duration: float = 0.22
@export var gravity: float = 980.0

# Stats
@export var max_hp: float = 100.0
@export var max_ep: float = 100.0

var hp: float = 100.0
var ep: float = 100.0

# Strict I-Frames (Prevents Health Melt on enemy collision!)
var i_frame_timer: float = 0.0
const I_FRAME_DURATION: float = 1.2

# Movement states
var is_sprinting: bool = false
var is_crouching: bool = false
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown: float = 0.0
var can_double_jump: bool = true
var has_double_jumped: bool = false

# Combat
var attack_timer: float = 0.0
var attack_duration: float = 0.24
var facing_direction: int = 1

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

# 8-Frame Humanoid Walk & Idle Textures
var tex_standard_walk = preload("res://assets/robot_standard_walk_strip8.png")
var tex_damaged_walk = preload("res://assets/robot_damaged_walk_strip8.png")
var tex_standard_idle = preload("res://assets/robot_standard_idle_strip4.png")
var tex_damaged_idle = preload("res://assets/robot_damaged_idle_strip4.png")
var tex_standard_crouch = preload("res://assets/robot_standard_crouch_strip2.png")
var tex_damaged_crouch = preload("res://assets/robot_damaged_crouch_strip2.png")

# Unified Attack Textures (Character swings his arm holding weapon from hand level!)
var tex_standard_attack_pan = preload("res://assets/robot_standard_attack_pan_strip4.png")
var tex_damaged_attack_pan = preload("res://assets/robot_damaged_attack_pan_strip4.png")
var tex_standard_attack_bat = preload("res://assets/robot_standard_attack_bat_strip4.png")
var tex_damaged_attack_bat = preload("res://assets/robot_damaged_attack_bat_strip4.png")
var tex_standard_shoot = preload("res://assets/robot_standard_shoot_strip4.png")
var tex_damaged_shoot = preload("res://assets/robot_damaged_shoot_strip4.png")

var tex_dash = preload("res://assets/robot_dash_strip2.png")
var tex_jump = preload("res://assets/robot_jump_strip3.png")

var anim_timer: float = 0.0

func _ready() -> void:
	add_to_group("player")
	weapon_sprite.visible = false
	melee_hitbox.monitoring = false
	melee_hitbox.area_entered.connect(_on_melee_hit)
	GameManager.player_health_changed.emit(hp, max_hp)
	GameManager.player_energy_changed.emit(ep, max_ep)

func _physics_process(dt: float) -> void:
	# 1. Update I-Frames & Visual Flashing
	if i_frame_timer > 0.0:
		i_frame_timer -= dt
		sprite.modulate.a = 0.35 if fmod(Time.get_ticks_msec() / 70.0, 2.0) > 1.0 else 1.0
	else:
		sprite.modulate.a = 1.0

	if dash_cooldown > 0.0:
		dash_cooldown -= dt

	# 2. Core Stamina / Energy Regeneration
	ep = min(max_ep, ep + dt * 14.0)
	GameManager.player_energy_changed.emit(ep, max_ep)

	# 3. Handle Dash Action
	if is_dashing:
		dash_timer -= dt
		velocity.y = 0.0
		if dash_timer <= 0.0:
			is_dashing = false
		move_and_slide()
		_update_animation(dt)
		return

	# 4. Gravity & Ground Check
	if not is_on_floor():
		velocity.y += gravity * dt
	else:
		has_double_jumped = false

	# 5. Handle Crouch [S] / [DOWN]
	if is_on_floor() and Input.is_action_pressed("crouch") and not is_dashing:
		is_crouching = true
		if collision_shape and collision_shape.shape is RectangleShape2D:
			collision_shape.shape.size = Vector2(18, 16)
			collision_shape.position = Vector2(0, 6)
	else:
		is_crouching = false
		if collision_shape and collision_shape.shape is RectangleShape2D:
			collision_shape.shape.size = Vector2(18, 28)
			collision_shape.position = Vector2(0, 0)

	# 6. Horizontal Movement & Sprint
	is_sprinting = Input.is_action_pressed("sprint") and not is_crouching
	var current_speed = sprint_speed if is_sprinting else (crouch_speed if is_crouching else walk_speed)
	var dir = Input.get_axis("move_left", "move_right")

	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * current_speed, current_speed * 9.0 * dt)
		facing_direction = 1 if dir > 0.0 else -1
		sprite.flip_h = (facing_direction == -1)
		sprite.rotation_degrees = dir * (4.5 if is_sprinting else 1.0)
	else:
		velocity.x = move_toward(velocity.x, 0.0, current_speed * 12.0 * dt)
		sprite.rotation_degrees = move_toward(sprite.rotation_degrees, 0.0, 40.0 * dt)

	# 7. Jump & Double Jump (Cannot jump while crouching)
	if Input.is_action_just_pressed("jump") and not is_crouching:
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and ep >= 10.0:
			velocity.y = double_jump_velocity
			has_double_jumped = true
			ep -= 10.0

	# 8. Dash Trigger [C]
	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and ep >= 15.0 and not is_crouching:
		is_dashing = true
		dash_timer = dash_duration
		dash_cooldown = 0.65
		ep -= 15.0
		velocity.x = facing_direction * dash_speed
		velocity.y = 0.0

	# 9. Weapon Inputs & Actions
	_handle_weapon_inputs()
	_handle_attacks(dt)

	move_and_slide()
	_update_animation(dt)

func _handle_weapon_inputs() -> void:
	if Input.is_action_just_pressed("switch_weapon"):
		GameManager.current_weapon_idx = (GameManager.current_weapon_idx + 1) % GameManager.unlocked_weapons.size()
		GameManager.weapon_switched.emit(GameManager.unlocked_weapons[GameManager.current_weapon_idx], {})
	if Input.is_action_just_pressed("toggle_chassis"):
		GameManager.player_chassis = "standard" if GameManager.player_chassis == "damaged" else "damaged"
		GameManager.notify("CHASSIS RECONFIGURED", "Active Form: " + GameManager.player_chassis.to_upper())

func _handle_attacks(dt: float) -> void:
	var current_weapon = GameManager.unlocked_weapons[GameManager.current_weapon_idx]
	var is_dmg = (GameManager.player_chassis == "damaged")

	if attack_timer > 0.0:
		attack_timer -= dt
		var progress = clamp(1.0 - (attack_timer / attack_duration), 0.0, 0.99)
		var f_idx = int(progress * 4.0)

		# The robot's own arm dynamically swings holding the weapon from hand level!
		if current_weapon == "pan":
			sprite.texture = tex_damaged_attack_pan if is_dmg else tex_standard_attack_pan
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 8 if facing_direction == 1 else -8
			sprite.offset.y = 0
		elif current_weapon == "bat":
			sprite.texture = tex_damaged_attack_bat if is_dmg else tex_standard_attack_bat
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 12 if facing_direction == 1 else -12
			sprite.offset.y = -2
		elif current_weapon == "blaster":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = 0

		if attack_timer <= 0.0:
			melee_hitbox.monitoring = false
			sprite.offset = Vector2(0, 0)
		return

	# Melee [X] / attack_melee
	if Input.is_action_just_pressed("attack_melee"):
		var is_bat = (current_weapon == "bat")
		attack_duration = 0.30 if is_bat else 0.22
		attack_timer = attack_duration

		# Configure Melee Hitbox reach right in front of hand level (y = 0)
		melee_hitbox.monitoring = true
		melee_hitbox.position = Vector2((32 if is_bat else 24) * facing_direction, 0)
		var shape_node = melee_hitbox.get_node_or_null("CollisionShape2D")
		if shape_node and shape_node.shape is RectangleShape2D:
			shape_node.shape.size = Vector2(58, 34) if is_bat else Vector2(48, 28)

	# Ranged [Z] / attack_ranged (Shoots straight from hand level!)
	elif Input.is_action_pressed("attack_ranged"):
		if current_weapon == "blaster" and ep >= 12.0 and Input.is_action_just_pressed("attack_ranged"):
			ep -= 12.0
			attack_duration = 0.2
			attack_timer = 0.2
			_shoot_laser()

func _shoot_laser() -> void:
	var proj_scene = load("res://scenes/projectile_laser.tscn")
	if proj_scene:
		var p = proj_scene.instantiate()
		# Fires directly from blaster cannon at hand level (y = -2)
		p.position = global_position + Vector2(20 * facing_direction, -2)
		p.direction = Vector2(facing_direction, 0)
		get_parent().add_child(p)

func _on_melee_hit(area: Area2D) -> void:
	var target = area.owner if area.owner else area.get_parent()
	if not target:
		target = area

	if target.has_method("take_damage"):
		var is_bat = (GameManager.unlocked_weapons[GameManager.current_weapon_idx] == "bat")
		var dmg = 45.0 if is_bat else 28.0
		var kb = (360.0 if is_bat else 220.0) * facing_direction
		target.take_damage(dmg, kb)

# STRICT I-FRAMES & KNOCKBACK TO PREVENT HEALTH MELT
func take_damage(amount: float, knockback_dir: float = 0.0) -> void:
	if i_frame_timer > 0.0:
		return

	i_frame_timer = I_FRAME_DURATION
	hp = max(0.0, hp - amount)

	velocity.x = knockback_dir * 320.0
	velocity.y = -220.0

	GameManager.player_health_changed.emit(hp, max_hp)

	if hp <= 0.0:
		GameManager.notify("CRITICAL SHUTDOWN", "Rebooting at Compactor Pit checkpoint...")
		position = Vector2(80, 720)
		hp = max_hp
		i_frame_timer = 1.5
		GameManager.player_health_changed.emit(hp, max_hp)

func _update_animation(dt: float) -> void:
	if attack_timer > 0.0:
		return # Handled in _handle_attacks!

	anim_timer += dt
	var is_dmg = (GameManager.player_chassis == "damaged")
	sprite.offset = Vector2(0, 0)

	if is_crouching:
		sprite.texture = tex_damaged_crouch if is_dmg else tex_standard_crouch
		sprite.hframes = 2
		sprite.frame = 1 if abs(velocity.x) > 5.0 else 0
	elif is_dashing:
		sprite.texture = tex_dash
		sprite.hframes = 2
		sprite.frame = int(anim_timer / 0.08) % 2
	elif not is_on_floor():
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 0 if velocity.y < 0 else (1 if abs(velocity.y) < 60 else 2)
	elif abs(velocity.x) > 10.0:
		# 8-Frame Clean Humanoid Gait
		sprite.texture = tex_damaged_walk if is_dmg else tex_standard_walk
		sprite.hframes = 8
		var frame_speed = 0.075 if is_sprinting else 0.115
		sprite.frame = int(anim_timer / frame_speed) % 8
	else:
		sprite.texture = tex_damaged_idle if is_dmg else tex_standard_idle
		sprite.hframes = 4
		sprite.frame = int(anim_timer / 0.14) % 4
"""

for target_dir in [godot_dir, godot_copy_dir]:
    p_path = os.path.join(target_dir, "scripts", "player.gd")
    with open(p_path, "w", encoding="utf-8") as f:
        f.write(player_gd)
print("Updated player.gd in both Godot projects.")

# ---------------------------------------------------------------------------
# 3. Update level_heap.tscn with 100% STATIC 3200x900 BACKDROP (No midair hovering!)
# ---------------------------------------------------------------------------
level_heap_tscn = """[gd_scene load_steps=12 format=3 uid="uid://level_heap_v5_static"]

[ext_resource type="Texture2D" path="res://assets/level_heap_backdrop_3200x900.png" id="1_backdrop"]
[ext_resource type="Texture2D" path="res://assets/crushed_car_obstacle.png" id="2_car_tex"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="3_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="4_drone"]
[ext_resource type="PackedScene" path="res://scenes/enemy_crawler.tscn" id="5_crawler"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="6_boss"]
[ext_resource type="PackedScene" path="res://scenes/tutorial_prompt.tscn" id="7_tut"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_ground"]
size = Vector2(3200, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_plat"]
size = Vector2(140, 18)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_car"]
size = Vector2(56, 24)

[node name="LevelHeap" type="Node2D"]

[node name="StaticBackdrop" type="Sprite2D" parent="."]
z_index = -10
position = Vector2(1600, 450)
texture = ExtResource("1_backdrop")

[node name="StaticGeometry" type="StaticBody2D" parent="."]
collision_mask = 0

[node name="Floor" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(1600, 800)
shape = SubResource("RectangleShape2D_ground")

[node name="FloorVisual" type="ColorRect" parent="StaticGeometry/Floor"]
offset_left = -1600.0
offset_top = -20.0
offset_right = 1600.0
offset_bottom = 100.0
color = Color(0.1, 0.08, 0.07, 1)

[node name="Plat1" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(460, 680)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat1"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Plat2" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(680, 580)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat2"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Plat3" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(980, 500)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat3"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="CrushedCarObstacle" type="StaticBody2D" parent="."]
position = Vector2(300, 768)
collision_layer = 1
collision_mask = 0

[node name="Sprite2D" type="Sprite2D" parent="CrushedCarObstacle"]
texture = ExtResource("2_car_tex")

[node name="CollisionShape2D" type="CollisionShape2D" parent="CrushedCarObstacle"]
shape = SubResource("RectangleShape2D_car")

[node name="Player" parent="." instance=ExtResource("3_player")]
position = Vector2(80, 750)

[node name="TutorialJumpCar" parent="." instance=ExtResource("7_tut")]
position = Vector2(295, 715)
tutorial_title = "[SPACE] TO JUMP"
tutorial_desc = "Leap over the crushed car obstacle"
detection_radius = 160.0

[node name="TutorialMove" parent="." instance=ExtResource("7_tut")]
position = Vector2(100, 715)
tutorial_title = "A / D"
tutorial_desc = "MOVE CHASSIS\\nHold [SHIFT] to Sprint\\nPress [S] to Crouch"
detection_radius = 140.0

[node name="TutorialAttack" parent="." instance=ExtResource("7_tut")]
position = Vector2(500, 715)
tutorial_title = "[X] SWING MELEE"
tutorial_desc = "Cyber Frying Pan Strike\\n[Z] Fire Blaster Arm"
detection_radius = 140.0

[node name="EnemyCrawler1" parent="." instance=ExtResource("5_crawler")]
position = Vector2(520, 768)

[node name="EnemyDrone1" parent="." instance=ExtResource("4_drone")]
position = Vector2(740, 520)

[node name="BossCrusher" parent="." instance=ExtResource("6_boss")]
position = Vector2(2850, 740)
"""

for target_dir in [godot_dir, godot_copy_dir]:
    scene_path = os.path.join(target_dir, "scenes", "level_heap.tscn")
    with open(scene_path, "w", encoding="utf-8") as f:
        f.write(level_heap_tscn)

    # Also fix main.tscn to make sure LevelHeap position is Vector2(0, 0)
    main_path = os.path.join(target_dir, "scenes", "main.tscn")
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    main_content = main_content.replace('position = Vector2(2, -47)', 'position = Vector2(0, 0)')
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

print("Updated level_heap.tscn with 100% static backdrop and main.tscn position.")
