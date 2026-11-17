import os
import shutil

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dirs = [
    os.path.join(scratch_dir, "godot_project"),
    os.path.join(scratch_dir, "scrapborn-(4.0)")
]

# -------------------------------------------------------------
# 1. GDScript: Updated player.gd with 8-Frame Smooth Walk & Sprint
# -------------------------------------------------------------
player_gd_v2 = """extends CharacterBody2D
class_name Player
# player.gd (v2) - Smooth 8-frame robotic walk, dynamic sprint lean, improved metroidvania physics

@export var walk_speed: float = 140.0
@export var sprint_speed: float = 230.0
@export var jump_velocity: float = -380.0
@export var double_jump_velocity: float = -340.0
@export var dash_speed: float = 420.0
@export var dash_duration: float = 0.22
@export var gravity: float = 850.0

# Stats
var max_hp: float = 100.0
var hp: float = 100.0
var max_ep: float = 100.0
var ep: float = 100.0

# Movement states
var can_double_jump: bool = true
var has_double_jumped: bool = false
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown: float = 0.0
var invulnerable_timer: float = 0.0
var is_sprinting: bool = false

# Combat
var attack_timer: float = 0.0
var facing_direction: int = 1

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

# 8-Frame Smooth Walk Sheets (No Horse Trot!)
var tex_standard_walk_8 = preload("res://assets/robot_standard_walk_strip8.png")
var tex_damaged_walk_8 = preload("res://assets/robot_damaged_walk_strip8.png")
var tex_standard_idle = preload("res://assets/robot_standard_idle_strip4.png")
var tex_damaged_idle = preload("res://assets/robot_damaged_idle_strip4.png")
var tex_dash = preload("res://assets/robot_dash_strip2.png")
var tex_jump = preload("res://assets/robot_jump_strip3.png")

var tex_weapon_pan = preload("res://assets/weapon_pan_swing_strip4.png")
var tex_weapon_bat = preload("res://assets/weapon_bat_slam_strip4.png")
var tex_weapon_blaster = preload("res://assets/weapon_blaster_shoot_strip4.png")
var tex_weapon_flame = preload("res://assets/weapon_flamethrower_stream_strip4.png")

var anim_timer: float = 0.0

func _ready() -> void:
	melee_hitbox.monitoring = false
	melee_hitbox.area_entered.connect(_on_melee_hit)
	GameManager.player_health_changed.emit(hp, max_hp)
	GameManager.player_energy_changed.emit(ep, max_ep)

func _physics_process(dt: float) -> void:
	# Timers
	if invulnerable_timer > 0.0:
		invulnerable_timer -= dt
		modulate.a = 0.4 if fmod(Time.get_ticks_msec() / 60.0, 2.0) > 1.0 else 1.0
	else:
		modulate.a = 1.0

	if dash_cooldown > 0.0:
		dash_cooldown -= dt

	# Energy Regen
	ep = min(max_ep, ep + dt * 12.0)
	GameManager.player_energy_changed.emit(ep, max_ep)

	# Handle Dash State
	if is_dashing:
		dash_timer -= dt
		velocity.y = 0.0
		if dash_timer <= 0.0:
			is_dashing = false
		move_and_slide()
		_update_animation(dt)
		return

	# Gravity
	if not is_on_floor():
		velocity.y += gravity * dt
	else:
		has_double_jumped = false

	# Horizontal Movement & Sprint
	is_sprinting = Input.is_action_pressed("sprint")
	var current_speed = sprint_speed if is_sprinting else walk_speed
	var dir = Input.get_axis("move_left", "move_right")

	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * current_speed, current_speed * 8.0 * dt)
		facing_direction = 1 if dir > 0.0 else -1
		sprite.flip_h = (facing_direction == -1)
		melee_hitbox.position.x = 16 * facing_direction
		# Forward aerodynamic lean when sprinting
		sprite.rotation_degrees = dir * (5.0 if is_sprinting else 1.5)
	else:
		velocity.x = move_toward(velocity.x, 0.0, current_speed * 10.0 * dt)
		sprite.rotation_degrees = move_toward(sprite.rotation_degrees, 0.0, 45.0 * dt)

	# Jump & Double Jump
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and ep >= 10.0:
			velocity.y = double_jump_velocity
			has_double_jumped = true
			ep -= 10.0

	# Dash Action [C]
	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and ep >= 15.0:
		is_dashing = true
		dash_timer = dash_duration
		dash_cooldown = 0.65
		ep -= 15.0
		velocity.x = facing_direction * dash_speed
		velocity.y = 0.0

	# Weapon Inputs
	_handle_weapon_inputs()

	# Attack Trigger
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
	if attack_timer > 0.0:
		attack_timer -= dt
		if attack_timer <= 0.0:
			weapon_sprite.visible = false
			melee_hitbox.monitoring = false
		return

	var current_weapon = GameManager.unlocked_weapons[GameManager.current_weapon_idx]

	# Melee [X]
	if Input.is_action_just_pressed("attack_melee"):
		attack_timer = 0.25
		weapon_sprite.visible = true
		melee_hitbox.monitoring = true

		if current_weapon == "pan":
			weapon_sprite.texture = tex_weapon_pan
			weapon_sprite.hframes = 4
		else:
			weapon_sprite.texture = tex_weapon_bat
			weapon_sprite.hframes = 4
		weapon_sprite.flip_h = (facing_direction == -1)
		weapon_sprite.position.x = 10 * facing_direction

	# Ranged [Z]
	elif Input.is_action_pressed("attack_ranged"):
		if current_weapon == "blaster" and ep >= 12.0 and Input.is_action_just_pressed("attack_ranged"):
			ep -= 12.0
			attack_timer = 0.2
			_shoot_laser()
		elif current_weapon == "flamethrower" and ep >= 3.0:
			ep -= 3.0
			attack_timer = 0.08
			_shoot_flame()

func _shoot_laser() -> void:
	var proj_scene = load("res://scenes/projectile_laser.tscn")
	if proj_scene:
		var p = proj_scene.instantiate()
		p.position = global_position + Vector2(16 * facing_direction, -4)
		p.direction = Vector2(facing_direction, 0)
		get_parent().add_child(p)

func _shoot_flame() -> void:
	weapon_sprite.visible = true
	weapon_sprite.texture = tex_weapon_flame
	weapon_sprite.hframes = 4
	weapon_sprite.flip_h = (facing_direction == -1)

func _on_melee_hit(area: Area2D) -> void:
	if area.is_in_group("enemies") or area.is_in_group("breakable"):
		if area.has_method("take_damage"):
			var dmg = 30.0 if GameManager.unlocked_weapons[GameManager.current_weapon_idx] == "bat" else 20.0
			area.take_damage(dmg, facing_direction)

func take_damage(amount: float, knockback_dir: float = 0.0) -> void:
	if invulnerable_timer > 0.0:
		return
	hp = max(0.0, hp - amount)
	invulnerable_timer = 0.8
	velocity.x = knockback_dir * 240.0
	velocity.y = -160.0
	GameManager.player_health_changed.emit(hp, max_hp)
	if hp <= 0.0:
		GameManager.notify("CRITICAL SHUTDOWN", "Rebooting at Compactor Pit checkpoint...")
		position = Vector2(80, 720)
		hp = max_hp
		GameManager.player_health_changed.emit(hp, max_hp)

func _update_animation(dt: float) -> void:
	var frame_speed = 0.07 if is_sprinting else 0.11
	anim_timer += dt
	var frame_idx = int(anim_timer / frame_speed)

	if is_dashing:
		sprite.texture = tex_dash
		sprite.hframes = 2
		sprite.frame = frame_idx % 2
	elif not is_on_floor():
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 0 if velocity.y < 0 else (1 if abs(velocity.y) < 60 else 2)
	elif abs(velocity.x) > 10.0:
		# Use 8-frame smooth walk cycle
		sprite.texture = tex_standard_walk_8 if GameManager.player_chassis == "standard" else tex_damaged_walk_8
		sprite.hframes = 8
		sprite.frame = frame_idx % 8
	else:
		sprite.texture = tex_standard_idle if GameManager.player_chassis == "standard" else tex_damaged_idle
		sprite.hframes = 4
		sprite.frame = frame_idx % 4
"""

# -------------------------------------------------------------
# 2. GDScript: Updated enemy_drone.gd with native sprite animation
# -------------------------------------------------------------
drone_gd_v2 = """extends CharacterBody2D
class_name EnemyDrone
# enemy_drone.gd - Patrolling flying drone with animated rotors & thruster

@export var patrol_distance: float = 120.0
@export var speed: float = 55.0
@export var max_hp: float = 24.0

var hp: float = 24.0
var start_x: float = 0.0
var direction: int = 1
var shoot_timer: float = 2.0
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")

func _physics_process(dt: float) -> void:
	# Sinusoidal hover
	velocity.x = direction * speed
	velocity.y = sin(Time.get_ticks_msec() / 200.0) * 15.0

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	# Rotor blade animation cycle
	anim_timer += dt
	sprite.frame = int(anim_timer / 0.09) % 4

	move_and_slide()

	# Contact damage with player
	for i in get_slide_collision_count():
		var col = get_slide_collision(i)
		var collider = col.get_collider()
		if collider is Player:
			collider.take_damage(16.0, direction)

func take_damage(amount: float, knockback: float) -> void:
	hp -= amount
	velocity.x = knockback * 160.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

# -------------------------------------------------------------
# 3. GDScript: Scrap Crawler Enemy (Ground Mecha-Beast)
# -------------------------------------------------------------
crawler_gd = """extends CharacterBody2D
class_name EnemyCrawler
# enemy_crawler.gd - Ground patrolling scrap scuttler with animated legs & mandibles

@export var patrol_distance: float = 140.0
@export var speed: float = 45.0
@export var max_hp: float = 32.0

var hp: float = 32.0
var start_x: float = 0.0
var direction: int = 1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")

func _physics_process(dt: float) -> void:
	if not is_on_floor():
		velocity.y += 800.0 * dt

	velocity.x = direction * speed

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	# Leg scuttling cycle
	anim_timer += dt
	sprite.frame = int(anim_timer / 0.12) % 4

	move_and_slide()

	# Contact damage with player
	for i in get_slide_collision_count():
		var col = get_slide_collision(i)
		var collider = col.get_collider()
		if collider is Player:
			collider.take_damage(20.0, direction)

func take_damage(amount: float, knockback: float) -> void:
	hp -= amount
	velocity.x = knockback * 140.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

# -------------------------------------------------------------
# 4. GDScript: Updated boss_crusher.gd with native 64x64 sprite
# -------------------------------------------------------------
boss_gd_v2 = """extends CharacterBody2D
class_name BossCrusher
# boss_crusher.gd - The Crusher Compactor Boss with native animated 64x64 sprite

@export var max_hp: float = 200.0
var hp: float = 200.0
var state: String = "idle" # idle, charge, slam
var state_timer: float = 2.5
var facing: int = -1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox

func _ready() -> void:
	hp = max_hp
	hurtbox.add_to_group("enemies")
	GameManager.boss_health_changed.emit(hp, max_hp)

func _physics_process(dt: float) -> void:
	if not is_on_floor():
		velocity.y += 850.0 * dt

	state_timer -= dt
	if state_timer <= 0.0:
		state_timer = 2.8
		_choose_action()

	if state == "charge":
		velocity.x = facing * 240.0
	elif state == "slam":
		if is_on_floor():
			state = "idle"
			velocity.x = 0.0
	else:
		velocity.x = move_toward(velocity.x, 0.0, 300.0 * dt)

	# Animation cycle (compactor piston & steam vents)
	anim_timer += dt
	sprite.frame = int(anim_timer / 0.15) % 4
	sprite.flip_h = (facing == 1)

	move_and_slide()

	# Contact damage with player
	for i in get_slide_collision_count():
		var col = get_slide_collision(i)
		var collider = col.get_collider()
		if collider is Player:
			collider.take_damage(28.0, facing)

func _choose_action() -> void:
	var roll = randf()
	if roll < 0.5:
		state = "charge"
	else:
		state = "slam"
		velocity.y = -350.0

func take_damage(amount: float, _kb: float) -> void:
	hp -= amount
	GameManager.boss_health_changed.emit(hp, max_hp)
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.12)
	if hp <= 0.0:
		GameManager.notify("VICTORY!", "THE CRUSHER DEFEATED! Laser Blaster Arm permanently acquired!")
		queue_free()
"""

# -------------------------------------------------------------
# 5. GDScript: Tutorial Trigger (Floating In-World Holographic Prompt)
# -------------------------------------------------------------
tutorial_gd = """extends Area2D
class_name TutorialTrigger
# tutorial_trigger.gd - Floating holographic tutorial billboard with smooth fade

@export var prompt_key: String = "[SHIFT]"
@export var prompt_action: String = "HOLD TO SPRINT"
@export var prompt_subtitle: String = "Accelerate mechanical chassis"

@onready var panel: Panel = $Panel
@onready var key_label: Label = $Panel/KeyLabel
@onready var action_label: Label = $Panel/ActionLabel
@onready var sub_label: Label = $Panel/SubLabel

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	panel.modulate.a = 0.0
	key_label.text = prompt_key
	action_label.text = prompt_action
	sub_label.text = prompt_subtitle

func _on_body_entered(body: Node2D) -> void:
	if body is Player:
		var t = create_tween()
		t.tween_property(panel, "modulate:a", 1.0, 0.25)

func _on_body_exited(body: Node2D) -> void:
	if body is Player:
		var t = create_tween()
		t.tween_property(panel, "modulate:a", 0.0, 0.25)
"""

# -------------------------------------------------------------
# 6. Scene Updates (.tscn)
# -------------------------------------------------------------

# enemy_drone.tscn with native sprite
drone_tscn = """[gd_scene load_steps=5 format=3 uid="uid://drone_scene_02"]

[ext_resource type="Script" path="res://scripts/enemy_drone.gd" id="1_drone"]
[ext_resource type="Texture2D" path="res://assets/enemy_junk_drone_strip4.png" id="2_drone_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(20, 16)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(24, 18)

[node name="EnemyDrone" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 3
script = ExtResource("1_drone")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_drone_tex")
hframes = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_body")

[node name="Hurtbox" type="Area2D" parent="." groups=["enemies"]]
collision_layer = 8
collision_mask = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
shape = SubResource("RectangleShape2D_hurt")
"""

# enemy_crawler.tscn
crawler_tscn = """[gd_scene load_steps=5 format=3 uid="uid://crawler_scene_01"]

[ext_resource type="Script" path="res://scripts/enemy_crawler.gd" id="1_crawler"]
[ext_resource type="Texture2D" path="res://assets/enemy_scrap_crawler_strip4.png" id="2_crawler_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(24, 14)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(26, 16)

[node name="EnemyCrawler" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 1
script = ExtResource("1_crawler")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_crawler_tex")
hframes = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, 5)
shape = SubResource("RectangleShape2D_body")

[node name="Hurtbox" type="Area2D" parent="." groups=["enemies"]]
collision_layer = 8
collision_mask = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
position = Vector2(0, 5)
shape = SubResource("RectangleShape2D_hurt")
"""

# boss_crusher.tscn with native 64x64 sprite
boss_tscn = """[gd_scene load_steps=5 format=3 uid="uid://boss_scene_02"]

[ext_resource type="Script" path="res://scripts/boss_crusher.gd" id="1_boss"]
[ext_resource type="Texture2D" path="res://assets/boss_crusher_strip4.png" id="2_crusher_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_boss"]
size = Vector2(46, 52)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(50, 56)

[node name="BossCrusher" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 3
script = ExtResource("1_boss")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_crusher_tex")
hframes = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
position = Vector2(0, 4)
shape = SubResource("RectangleShape2D_boss")

[node name="Hurtbox" type="Area2D" parent="." groups=["enemies"]]
collision_layer = 8
collision_mask = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
position = Vector2(0, 4)
shape = SubResource("RectangleShape2D_hurt")
"""

# tutorial_prompt.tscn
tutorial_tscn = """[gd_scene load_steps=3 format=3 uid="uid://tutorial_prompt_01"]

[ext_resource type="Script" path="res://scripts/tutorial_trigger.gd" id="1_tut"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_area"]
size = Vector2(90, 80)

[node name="TutorialTrigger" type="Area2D"]
collision_layer = 0
collision_mask = 2
script = ExtResource("1_tut")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_area")

[node name="Panel" type="Panel" parent="."]
offset_left = -70.0
offset_top = -65.0
offset_right = 70.0
offset_bottom = -15.0

[node name="KeyLabel" type="Label" parent="Panel"]
layout_mode = 0
offset_left = 6.0
offset_top = 4.0
offset_right = 134.0
offset_bottom = 22.0
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_font_sizes/font_size = 11
text = "[SHIFT]"
horizontal_alignment = 1

[node name="ActionLabel" type="Label" parent="Panel"]
layout_mode = 0
offset_left = 6.0
offset_top = 18.0
offset_right = 134.0
offset_bottom = 34.0
theme_override_font_sizes/font_size = 10
text = "HOLD TO SPRINT"
horizontal_alignment = 1

[node name="SubLabel" type="Label" parent="Panel"]
layout_mode = 0
offset_left = 6.0
offset_top = 32.0
offset_right = 134.0
offset_bottom = 48.0
theme_override_colors/font_color = Color(0.58, 0.64, 0.72, 1)
theme_override_font_sizes/font_size = 8
text = "Accelerate mechanical chassis"
horizontal_alignment = 1
"""

# level_heap.tscn with ParallaxBackground + Enemies + Tutorial Triggers
level_tscn_v2 = """[gd_scene load_steps=12 format=3 uid="uid://level_heap_02"]

[ext_resource type="Texture2D" path="res://assets/bg_layer1_sky.png" id="1_sky"]
[ext_resource type="Texture2D" path="res://assets/bg_layer2_distant_scrap.png" id="2_scrap"]
[ext_resource type="Texture2D" path="res://assets/bg_layer3_midground_pipes.png" id="3_pipes"]
[ext_resource type="Texture2D" path="res://assets/bg_layer4_foreground_girders.png" id="4_girders"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="5_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="6_drone"]
[ext_resource type="PackedScene" path="res://scenes/enemy_crawler.tscn" id="7_crawler"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="8_boss"]
[ext_resource type="PackedScene" path="res://scenes/tutorial_prompt.tscn" id="9_tut"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_ground"]
size = Vector2(3200, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_plat"]
size = Vector2(140, 18)

[node name="LevelHeap" type="Node2D"]

[node name="ParallaxBackground" type="ParallaxBackground" parent="."]

[node name="Layer1Sky" type="ParallaxLayer" parent="ParallaxBackground"]
motion_scale = Vector2(0.05, 0.05)
motion_mirroring = Vector2(1920, 0)

[node name="Sprite2D" type="Sprite2D" parent="ParallaxBackground/Layer1Sky"]
position = Vector2(960, 270)
texture = ExtResource("1_sky")

[node name="Layer2Scrap" type="ParallaxLayer" parent="ParallaxBackground"]
motion_scale = Vector2(0.18, 0.12)
motion_mirroring = Vector2(1920, 0)

[node name="Sprite2D" type="Sprite2D" parent="ParallaxBackground/Layer2Scrap"]
position = Vector2(960, 270)
texture = ExtResource("2_scrap")

[node name="Layer3Pipes" type="ParallaxLayer" parent="ParallaxBackground"]
motion_scale = Vector2(0.45, 0.25)
motion_mirroring = Vector2(1920, 0)

[node name="Sprite2D" type="Sprite2D" parent="ParallaxBackground/Layer3Pipes"]
position = Vector2(960, 270)
texture = ExtResource("3_pipes")

[node name="Layer4Girders" type="ParallaxLayer" parent="ParallaxBackground"]
motion_scale = Vector2(0.75, 0.45)
motion_mirroring = Vector2(1920, 0)

[node name="Sprite2D" type="Sprite2D" parent="ParallaxBackground/Layer4Girders"]
position = Vector2(960, 270)
texture = ExtResource("4_girders")

[node name="StaticGeometry" type="StaticBody2D" parent="."]
collision_mask = 0

[node name="Floor" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(1600, 800)
shape = SubResource("RectangleShape2D_ground")

[node name="FloorVisual" type="ColorRect" parent="StaticGeometry/Floor"]
offset_left = -1600.0
offset_top = -20.0
offset_right = 1600.0
offset_bottom = 120.0
color = Color(0.15, 0.1, 0.08, 1)

[node name="Plat1" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(260, 680)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat1"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Plat2" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(440, 600)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat2"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Plat3" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(720, 520)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat3"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Plat4" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(1040, 440)
shape = SubResource("RectangleShape2D_plat")

[node name="ColorRect" type="ColorRect" parent="StaticGeometry/Plat4"]
offset_left = -70.0
offset_top = -9.0
offset_right = 70.0
offset_bottom = 9.0
color = Color(0.2, 0.25, 0.35, 1)

[node name="Player" parent="." instance=ExtResource("5_player")]
position = Vector2(100, 720)

[node name="TutorialMove" parent="." instance=ExtResource("9_tut")]
position = Vector2(140, 740)
prompt_key = "A / D"
prompt_action = "MOVE CHASSIS"
prompt_subtitle = "Hold [SHIFT] to Sprint"

[node name="TutorialJump" parent="." instance=ExtResource("9_tut")]
position = Vector2(240, 640)
prompt_key = "[SPACE] / [W]"
prompt_action = "JUMP & DOUBLE JUMP"
prompt_subtitle = "Tap in mid-air to engage core thrusters"

[node name="TutorialDash" parent="." instance=ExtResource("9_tut")]
position = Vector2(440, 560)
prompt_key = "[C]"
prompt_action = "HIGH SPEED DASH"
prompt_subtitle = "Phases through hazards & enemy shots"

[node name="TutorialCombat" parent="." instance=ExtResource("9_tut")]
position = Vector2(720, 480)
prompt_key = "[X] OR LEFT CLICK"
prompt_action = "MELEE STRIKE"
prompt_subtitle = "Cyber Pan clangs & deflects projectiles"

[node name="TutorialRanged" parent="." instance=ExtResource("9_tut")]
position = Vector2(1040, 400)
prompt_key = "[Z] OR RIGHT CLICK"
prompt_action = "RANGED LASER BLASTER"
prompt_subtitle = "Consumes Core Energy to fire"

[node name="TutorialWeapons" parent="." instance=ExtResource("9_tut")]
position = Vector2(1400, 740)
prompt_key = "[Q] OR [1-4]"
prompt_action = "SWITCH ARSENAL"
prompt_subtitle = "[G] Grenade · [E] Grappling Hook"

[node name="EnemyDrone1" parent="." instance=ExtResource("6_drone")]
position = Vector2(780, 450)

[node name="EnemyDrone2" parent="." instance=ExtResource("6_drone")]
position = Vector2(1360, 420)

[node name="EnemyCrawler1" parent="." instance=ExtResource("7_crawler")]
position = Vector2(520, 765)

[node name="EnemyCrawler2" parent="." instance=ExtResource("7_crawler")]
position = Vector2(980, 765)

[node name="BossCrusher" parent="." instance=ExtResource("8_boss")]
position = Vector2(2650, 720)
"""

# Apply files to all active Godot project directories
for g_dir in godot_dirs:
    if not os.path.exists(g_dir):
        continue

    # Scripts
    with open(os.path.join(g_dir, "scripts", "player.gd"), "w", encoding="utf-8") as f:
        f.write(player_gd_v2)
    with open(os.path.join(g_dir, "scripts", "enemy_drone.gd"), "w", encoding="utf-8") as f:
        f.write(drone_gd_v2)
    with open(os.path.join(g_dir, "scripts", "enemy_crawler.gd"), "w", encoding="utf-8") as f:
        f.write(crawler_gd)
    with open(os.path.join(g_dir, "scripts", "boss_crusher.gd"), "w", encoding="utf-8") as f:
        f.write(boss_gd_v2)
    with open(os.path.join(g_dir, "scripts", "tutorial_trigger.gd"), "w", encoding="utf-8") as f:
        f.write(tutorial_gd)

    # Scenes
    with open(os.path.join(g_dir, "scenes", "enemy_drone.tscn"), "w", encoding="utf-8") as f:
        f.write(drone_tscn)
    with open(os.path.join(g_dir, "scenes", "enemy_crawler.tscn"), "w", encoding="utf-8") as f:
        f.write(crawler_tscn)
    with open(os.path.join(g_dir, "scenes", "boss_crusher.tscn"), "w", encoding="utf-8") as f:
        f.write(boss_tscn)
    with open(os.path.join(g_dir, "scenes", "tutorial_prompt.tscn"), "w", encoding="utf-8") as f:
        f.write(tutorial_tscn)
    with open(os.path.join(g_dir, "scenes", "level_heap.tscn"), "w", encoding="utf-8") as f:
        f.write(level_tscn_v2)

    print(f"Updated all scenes and GDScripts in: {g_dir}")

print("Godot update completed successfully!")
