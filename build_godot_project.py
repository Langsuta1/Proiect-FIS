import os
import shutil

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")

# 1. Create Directories
dirs = [
    godot_dir,
    os.path.join(godot_dir, "assets"),
    os.path.join(godot_dir, "scripts"),
    os.path.join(godot_dir, "scenes"),
    os.path.join(godot_dir, "autoload")
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# 2. Copy all Sprite Assets
source_dirs = [
    os.path.join(scratch_dir, "animations", "sheets"),
    os.path.join(scratch_dir, "weapons"),
    os.path.join(scratch_dir, "characters"),
    os.path.join(scratch_dir, "grenades"),
    os.path.join(scratch_dir, "new_weapons"),
    os.path.join(scratch_dir, "upgrades")
]

copied = 0
for sdir in source_dirs:
    if not os.path.exists(sdir):
        continue
    for f in os.listdir(sdir):
        if f.endswith(".png") and not "_hd" in f and not "showcase" in f:
            src = os.path.join(sdir, f)
            dst = os.path.join(godot_dir, "assets", f)
            shutil.copy2(src, dst)
            copied += 1

print(f"Copied {copied} sprite assets to godot_project/assets/")

# 3. Create project.godot
project_godot = """; Engine configuration file for Godot Engine 4.x
; Project: SCRAPBORN (Cyber Metroidvania)

config_version=5

[application]

config/name="SCRAPBORN"
config/description="Cyber Metroidvania with modular robot upgrades and seamless world"
run/main_scene="res://scenes/main.tscn"
config/features=PackedStringArray("4.0", "4.1", "4.2", "4.3", "Forward Plus", "GL Compatibility")
boot_splash/bg_color=Color(0.035, 0.043, 0.063, 1)

[autoload]

GameManager="*res://autoload/game_manager.gd"

[display]

window/size/viewport_width=960
window/size/viewport_height=540
window/size/window_width_override=1280
window/size/window_height_override=720
window/stretch/mode="canvas_items"
window/stretch/aspect="keep"

[rendering]

textures/canvas_textures/default_texture_filter=0
renderer/rendering_method="gl_compatibility"
environment/defaults/default_clear_color=Color(0.04, 0.05, 0.08, 1)
"""

with open(os.path.join(godot_dir, "project.godot"), "w", encoding="utf-8") as f:
    f.write(project_godot)

# 4. Create GameManager Autoload (Singleton in GDScript)
game_manager_gd = """extends Node
# GameManager.gd - Central coordinator for SCRAPBORN
# Manages input mappings, global state, audio synthesis, and transitions

signal player_health_changed(new_hp, max_hp)
signal player_energy_changed(new_ep, max_ep)
signal weapon_switched(weapon_name, weapon_data)
signal boss_health_changed(current_hp, max_hp)
signal notification_posted(title, text)

var current_zone: String = "The Heap"
var player_chassis: String = "damaged" # 'damaged' or 'standard'

# Discovered items
var unlocked_weapons: Array = ["pan", "bat", "blaster", "flamethrower"]
var current_weapon_idx: int = 0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_setup_default_inputs()
	print("[SCRAPBORN] GameManager initialized. Welcome to Godot Engine!")

func _setup_default_inputs() -> void:
	# Programmatic fail-safe input mapping for any Godot version
	var key_mappings = {
		"move_left": [KEY_A, KEY_LEFT],
		"move_right": [KEY_D, KEY_RIGHT],
		"move_up": [KEY_W, KEY_UP],
		"move_down": [KEY_S, KEY_DOWN],
		"jump": [KEY_SPACE, KEY_W, KEY_UP],
		"sprint": [KEY_SHIFT],
		"dash": [KEY_C, KEY_K],
		"attack_melee": [KEY_X, KEY_J],
		"attack_ranged": [KEY_Z, KEY_L],
		"grenade": [KEY_G],
		"grapple": [KEY_E],
		"switch_weapon": [KEY_Q],
		"toggle_chassis": [KEY_F],
		"weapon_1": [KEY_1],
		"weapon_2": [KEY_2],
		"weapon_3": [KEY_3],
		"weapon_4": [KEY_4]
	}

	for action in key_mappings:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
			for keycode in key_mappings[action]:
				var ev = InputEventKey.new()
				ev.physical_keycode = keycode
				InputMap.action_add_event(action, ev)

func notify(title: String, text: String) -> void:
	notification_posted.emit(title, text)
"""

with open(os.path.join(godot_dir, "autoload", "game_manager.gd"), "w", encoding="utf-8") as f:
    f.write(game_manager_gd)

# 5. Create Player GDScript (CharacterBody2D Metroidvania Controller)
player_gd = """extends CharacterBody2D
class_name Player
# player.gd - Core Metroidvania Player Controller for SCRAPBORN
# Supports Damaged/Standard chassis, Melee swings, Blaster/Flamethrower, Double Jump, Dash

@export var walk_speed: float = 140.0
@export var sprint_speed: float = 220.0
@export var jump_velocity: float = -380.0
@export var double_jump_velocity: float = -340.0
@export var dash_speed: float = 400.0
@export var dash_duration: float = 0.22
@export var gravity: float = 850.0

# Stats
var max_hp: float = 100.0
var hp: float = 100.0
var max_ep: float = 100.0
var ep: float = 100.0

# Abilities
var can_double_jump: bool = true
var has_double_jumped: bool = false
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown: float = 0.0
var invulnerable_timer: float = 0.0

# Combat
var attack_timer: float = 0.0
var facing_direction: int = 1

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

# Sprite sheet textures preloaded from assets
var tex_damaged_idle = preload("res://assets/robot_damaged_idle_strip4.png")
var tex_damaged_walk = preload("res://assets/robot_damaged_walk_strip6.png")
var tex_standard_idle = preload("res://assets/robot_standard_idle_strip4.png")
var tex_standard_walk = preload("res://assets/robot_standard_walk_strip6.png")
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

	# Core Energy Regen
	ep = min(max_ep, ep + dt * 12.0)
	GameManager.player_energy_changed.emit(ep, max_ep)

	# Handle Dash Mode
	if is_dashing:
		dash_timer -= dt
		velocity.y = 0.0
		if dash_timer <= 0.0:
			is_dashing = false
		move_and_slide()
		_update_animation()
		return

	# Gravity
	if not is_on_floor():
		velocity.y += gravity * dt
	else:
		has_double_jumped = false

	# Horizontal Movement & Sprint
	var is_sprinting = Input.is_action_pressed("sprint")
	var current_speed = sprint_speed if is_sprinting else walk_speed
	var dir = Input.get_axis("move_left", "move_right")

	if dir != 0.0:
		velocity.x = dir * current_speed
		facing_direction = 1 if dir > 0.0 else -1
		sprite.flip_h = (facing_direction == -1)
		melee_hitbox.position.x = 16 * facing_direction
	else:
		velocity.x = move_toward(velocity.x, 0.0, current_speed * 6.0 * dt)

	# Jump & Double Jump
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and ep >= 10.0:
			velocity.y = double_jump_velocity
			has_double_jumped = true
			ep -= 10.0

	# Dash Action
	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and ep >= 15.0:
		is_dashing = true
		dash_timer = dash_duration
		dash_cooldown = 0.65
		ep -= 15.0
		velocity.x = facing_direction * dash_speed
		velocity.y = 0.0

	# Weapon Switching
	_handle_weapon_inputs()

	# Attack Trigger
	_handle_attacks(dt)

	move_and_slide()
	_update_animation()

func _handle_weapon_inputs() -> void:
	if Input.is_action_just_pressed("switch_weapon"):
		GameManager.current_weapon_idx = (GameManager.current_weapon_idx + 1) % GameManager.unlocked_weapons.size()
		GameManager.weapon_switched.emit(GameManager.unlocked_weapons[GameManager.current_weapon_idx], {})
	if Input.is_action_just_pressed("toggle_chassis"):
		GameManager.player_chassis = "standard" if GameManager.player_chassis == "damaged" else "damaged"
		GameManager.notify("CHASSIS RECONFIGURED", "Active: " + GameManager.player_chassis.to_upper())

func _handle_attacks(dt: float) -> void:
	if attack_timer > 0.0:
		attack_timer -= dt
		if attack_timer <= 0.0:
			weapon_sprite.visible = false
			melee_hitbox.monitoring = false
		return

	var current_weapon = GameManager.unlocked_weapons[GameManager.current_weapon_idx]

	# Melee Attack [X]
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

	# Ranged Attack [Z]
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
	velocity.x = knockback_dir * 220.0
	velocity.y = -150.0
	GameManager.player_health_changed.emit(hp, max_hp)
	if hp <= 0.0:
		GameManager.notify("CRITICAL FAILURE", "Scraps core depleted. Respawning at Heap Compactor...")
		position = Vector2(80, 720)
		hp = max_hp
		GameManager.player_health_changed.emit(hp, max_hp)

func _update_animation() -> void:
	anim_timer += get_physics_process_delta_time()
	var frame_idx = int(anim_timer / 0.12)

	if is_dashing:
		sprite.texture = tex_dash
		sprite.hframes = 2
		sprite.frame = frame_idx % 2
	elif not is_on_floor():
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 0 if velocity.y < 0 else (1 if abs(velocity.y) < 60 else 2)
	elif abs(velocity.x) > 10.0:
		sprite.texture = tex_standard_walk if GameManager.player_chassis == "standard" else tex_damaged_walk
		sprite.hframes = 6
		sprite.frame = frame_idx % 6
	else:
		sprite.texture = tex_standard_idle if GameManager.player_chassis == "standard" else tex_damaged_idle
		sprite.hframes = 4
		sprite.frame = frame_idx % 4
"""

with open(os.path.join(godot_dir, "scripts", "player.gd"), "w", encoding="utf-8") as f:
    f.write(player_gd)

# 6. Create Enemy Drone GDScript (Flying Drone AI)
drone_gd = """extends CharacterBody2D
class_name EnemyDrone
# enemy_drone.gd - Patrolling flying drone with optic laser

@export var patrol_distance: float = 120.0
@export var speed: float = 55.0
@export var max_hp: float = 24.0

var hp: float = 24.0
var start_x: float = 0.0
var direction: int = 1
var shoot_timer: float = 2.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")

func _physics_process(dt: float) -> void:
	velocity.x = direction * speed
	velocity.y = sin(Time.get_ticks_msec() / 200.0) * 15.0

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)
	move_and_slide()

	# Contact damage with player
	for i in get_slide_collision_count():
		var col = get_slide_collision(i)
		var collider = col.get_collider()
		if collider is Player:
			collider.take_damage(15.0, direction)

func take_damage(amount: float, knockback: float) -> void:
	hp -= amount
	velocity.x = knockback * 140.0
	modulate = Color(1, 0.2, 0.2)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

with open(os.path.join(godot_dir, "scripts", "enemy_drone.gd"), "w", encoding="utf-8") as f:
    f.write(drone_gd)

# 7. Create Boss Crusher GDScript (The Crusher Boss Controller)
boss_gd = """extends CharacterBody2D
class_name BossCrusher
# boss_crusher.gd - The Crusher Compactor Boss in The Heap

@export var max_hp: float = 200.0
var hp: float = 200.0
var state: String = "idle" # idle, charge, slam
var state_timer: float = 2.5
var facing: int = -1
var target_player: Player = null

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

	# Face towards player
	if target_player:
		facing = -1 if target_player.global_position.x < global_position.x else 1

	move_and_slide()

	# Contact damage with player
	for i in get_slide_collision_count():
		var col = get_slide_collision(i)
		var collider = col.get_collider()
		if collider is Player:
			collider.take_damage(25.0, facing)

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

with open(os.path.join(godot_dir, "scripts", "boss_crusher.gd"), "w", encoding="utf-8") as f:
    f.write(boss_gd)

# 8. Create Projectile Laser GDScript
laser_gd = """extends Area2D
# projectile_laser.gd - Cyan plasma pulse beam

@export var speed: float = 480.0
@export var damage: float = 24.0
var direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(dt: float) -> void:
	position += direction * speed * dt

func _on_body_entered(body: Node2D) -> void:
	if not body is Player:
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("enemies"):
		if area.get_parent().has_method("take_damage"):
			area.get_parent().take_damage(damage, direction.x)
		queue_free()
"""

with open(os.path.join(godot_dir, "scripts", "projectile_laser.gd"), "w", encoding="utf-8") as f:
    f.write(laser_gd)

# 9. Create HUD GDScript
hud_gd = """extends CanvasLayer
# hud.gd - Metroidvania On-Screen Display

@onready var hp_bar: ProgressBar = $HUDContainer/Bars/HPBar
@onready var ep_bar: ProgressBar = $HUDContainer/Bars/EPBar
@onready var weapon_label: Label = $HUDContainer/WeaponCard/WeaponName
@onready var notify_box: Panel = $NotificationBox
@onready var notify_title: Label = $NotificationBox/Title
@onready var notify_text: Label = $NotificationBox/Text
@onready var boss_hud: Panel = $BossHUD
@onready var boss_bar: ProgressBar = $BossHUD/BossBar

var notify_timer: float = 0.0

func _ready() -> void:
	GameManager.player_health_changed.connect(_on_hp_changed)
	GameManager.player_energy_changed.connect(_on_ep_changed)
	GameManager.weapon_switched.connect(_on_weapon_switched)
	GameManager.boss_health_changed.connect(_on_boss_health)
	GameManager.notification_posted.connect(_on_notification)
	notify_box.visible = false
	boss_hud.visible = false

func _process(dt: float) -> void:
	if notify_timer > 0.0:
		notify_timer -= dt
		if notify_timer <= 0.0:
			notify_box.visible = false

func _on_hp_changed(current: float, max_val: float) -> void:
	hp_bar.value = (current / max_val) * 100.0

func _on_ep_changed(current: float, max_val: float) -> void:
	ep_bar.value = (current / max_val) * 100.0

func _on_weapon_switched(w_name: String, _data: Dictionary) -> void:
	weapon_label.text = w_name.to_upper()

func _on_boss_health(current: float, max_val: float) -> void:
	boss_hud.visible = (current > 0.0)
	boss_bar.value = (current / max_val) * 100.0

func _on_notification(title: String, text: String) -> void:
	notify_title.text = title
	notify_text.text = text
	notify_box.visible = true
	notify_timer = 4.0
"""

with open(os.path.join(godot_dir, "scripts", "hud.gd"), "w", encoding="utf-8") as f:
    f.write(hud_gd)

# 10. Generate Godot Scenes (.tscn format)
# A. player.tscn
player_tscn = """[gd_scene load_steps=5 format=3 uid="uid://player_scene_01"]

[ext_resource type="Script" path="res://scripts/player.gd" id="1_player"]
[ext_resource type="Texture2D" path="res://assets/robot_damaged_idle_strip4.png" id="2_sprite"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_box"]
size = Vector2(18, 28)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hitbox"]
size = Vector2(28, 28)

[node name="Player" type="CharacterBody2D"]
collision_layer = 2
collision_mask = 1
script = ExtResource("1_player")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_sprite")
hframes = 4

[node name="WeaponSprite" type="Sprite2D" parent="."]
visible = false
position = Vector2(10, 0)

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_box")

[node name="MeleeHitbox" type="Area2D" parent="."]
position = Vector2(16, 0)
collision_layer = 4
collision_mask = 8

[node name="CollisionShape2D" type="CollisionShape2D" parent="MeleeHitbox"]
shape = SubResource("RectangleShape2D_hitbox")

[node name="Camera2D" type="Camera2D" parent="."]
limit_left = 0
limit_top = 0
limit_right = 3200
limit_bottom = 900
position_smoothing_enabled = true
"""
with open(os.path.join(godot_dir, "scenes", "player.tscn"), "w", encoding="utf-8") as f:
    f.write(player_tscn)

# B. projectile_laser.tscn
proj_tscn = """[gd_scene load_steps=3 format=3 uid="uid://laser_scene_01"]

[ext_resource type="Script" path="res://scripts/projectile_laser.gd" id="1_laser"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_proj"]
size = Vector2(14, 6)

[node name="Laser" type="Area2D"]
collision_layer = 4
collision_mask = 9
script = ExtResource("1_laser")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_proj")

[node name="ColorRect" type="ColorRect" parent="."]
offset_left = -7.0
offset_top = -3.0
offset_right = 7.0
offset_bottom = 3.0
color = Color(0.22, 0.74, 0.97, 1)
"""
with open(os.path.join(godot_dir, "scenes", "projectile_laser.tscn"), "w", encoding="utf-8") as f:
    f.write(proj_tscn)

# C. enemy_drone.tscn
drone_tscn = """[gd_scene load_steps=4 format=3 uid="uid://drone_scene_01"]

[ext_resource type="Script" path="res://scripts/enemy_drone.gd" id="1_drone"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(22, 16)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(24, 18)

[node name="EnemyDrone" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 3
script = ExtResource("1_drone")

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="ColorRect" type="ColorRect" parent="."]
offset_left = -11.0
offset_top = -8.0
offset_right = 11.0
offset_bottom = 8.0
color = Color(0.39, 0.45, 0.55, 1)

[node name="Eye" type="ColorRect" parent="."]
offset_left = 3.0
offset_top = -2.0
offset_right = 9.0
offset_bottom = 2.0
color = Color(0.93, 0.27, 0.27, 1)

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_body")

[node name="Hurtbox" type="Area2D" parent="." groups=["enemies"]]
collision_layer = 8
collision_mask = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
shape = SubResource("RectangleShape2D_hurt")
"""
with open(os.path.join(godot_dir, "scenes", "enemy_drone.tscn"), "w", encoding="utf-8") as f:
    f.write(drone_tscn)

# D. boss_crusher.tscn
boss_tscn = """[gd_scene load_steps=4 format=3 uid="uid://boss_scene_01"]

[ext_resource type="Script" path="res://scripts/boss_crusher.gd" id="1_boss"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_boss"]
size = Vector2(46, 54)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(50, 58)

[node name="BossCrusher" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 3
script = ExtResource("1_boss")

[node name="Sprite2D" type="Sprite2D" parent="."]

[node name="Body" type="ColorRect" parent="."]
offset_left = -23.0
offset_top = -27.0
offset_right = 23.0
offset_bottom = 27.0
color = Color(0.86, 0.15, 0.15, 1)

[node name="Fist" type="ColorRect" parent="."]
offset_left = 8.0
offset_top = -8.0
offset_right = 28.0
offset_bottom = 20.0
color = Color(0.96, 0.62, 0.04, 1)

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("RectangleShape2D_boss")

[node name="Hurtbox" type="Area2D" parent="." groups=["enemies"]]
collision_layer = 8
collision_mask = 4

[node name="CollisionShape2D" type="CollisionShape2D" parent="Hurtbox"]
shape = SubResource("RectangleShape2D_hurt")
"""
with open(os.path.join(godot_dir, "scenes", "boss_crusher.tscn"), "w", encoding="utf-8") as f:
    f.write(boss_tscn)

# E. hud.tscn
hud_tscn = """[gd_scene load_steps=2 format=3 uid="uid://hud_scene_01"]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_hud"]

[node name="HUD" type="CanvasLayer"]
script = ExtResource("1_hud")

[node name="HUDContainer" type="Control" parent="."]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Bars" type="VBoxContainer" parent="HUDContainer"]
layout_mode = 0
offset_left = 16.0
offset_top = 16.0
offset_right = 216.0
offset_bottom = 60.0

[node name="HPBar" type="ProgressBar" parent="HUDContainer/Bars"]
custom_minimum_size = Vector2(180, 14)
layout_mode = 2
value = 100.0
show_percentage = false

[node name="EPBar" type="ProgressBar" parent="HUDContainer/Bars"]
custom_minimum_size = Vector2(180, 14)
layout_mode = 2
value = 100.0
show_percentage = false

[node name="WeaponCard" type="Panel" parent="HUDContainer"]
layout_mode = 0
offset_left = 16.0
offset_top = 480.0
offset_right = 220.0
offset_bottom = 524.0

[node name="WeaponName" type="Label" parent="HUDContainer/WeaponCard"]
layout_mode = 0
offset_left = 10.0
offset_top = 10.0
offset_right = 200.0
offset_bottom = 34.0
text = "CYBER FRYING PAN"

[node name="NotificationBox" type="Panel" parent="."]
visible = false
offset_left = 280.0
offset_top = 440.0
offset_right = 680.0
offset_bottom = 510.0

[node name="Title" type="Label" parent="NotificationBox"]
layout_mode = 0
offset_left = 12.0
offset_top = 8.0
offset_right = 388.0
offset_bottom = 30.0
text = "SYSTEM MESSAGE"

[node name="Text" type="Label" parent="NotificationBox"]
layout_mode = 0
offset_left = 12.0
offset_top = 32.0
offset_right = 388.0
offset_bottom = 62.0
text = "Scraps activated."

[node name="BossHUD" type="Panel" parent="."]
visible = false
offset_left = 320.0
offset_top = 20.0
offset_right = 640.0
offset_bottom = 65.0

[node name="BossTitle" type="Label" parent="BossHUD"]
layout_mode = 0
offset_left = 10.0
offset_top = 4.0
offset_right = 310.0
offset_bottom = 24.0
text = "THE CRUSHER — COMPACTOR TITAN"

[node name="BossBar" type="ProgressBar" parent="BossHUD"]
layout_mode = 0
offset_left = 10.0
offset_top = 26.0
offset_right = 310.0
offset_bottom = 38.0
value = 100.0
show_percentage = false
"""
with open(os.path.join(godot_dir, "scenes", "hud.tscn"), "w", encoding="utf-8") as f:
    f.write(hud_tscn)

# F. level_heap.tscn (The Zone 1 Level Geometry)
level_tscn = """[gd_scene load_steps=6 format=3 uid="uid://level_heap_01"]

[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="1_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="2_drone"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="3_boss"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_ground"]
size = Vector2(3200, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_plat"]
size = Vector2(140, 18)

[node name="LevelHeap" type="Node2D"]

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

[node name="LeftWall" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(10, 400)
shape = SubResource("RectangleShape2D_plat")

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

[node name="Player" parent="." instance=ExtResource("1_player")]
position = Vector2(120, 720)

[node name="EnemyDrone1" parent="." instance=ExtResource("2_drone")]
position = Vector2(680, 460)

[node name="EnemyDrone2" parent="." instance=ExtResource("2_drone")]
position = Vector2(1400, 480)

[node name="BossCrusher" parent="." instance=ExtResource("3_boss")]
position = Vector2(2600, 730)
"""
with open(os.path.join(godot_dir, "scenes", "level_heap.tscn"), "w", encoding="utf-8") as f:
    f.write(level_tscn)

# G. main.tscn (Root scene that instantiates HUD and Level)
main_tscn = """[gd_scene load_steps=3 format=3 uid="uid://main_root_01"]

[ext_resource type="PackedScene" path="res://scenes/level_heap.tscn" id="1_level"]
[ext_resource type="PackedScene" path="res://scenes/hud.tscn" id="2_hud"]

[node name="Main" type="Node"]

[node name="LevelHeap" parent="." instance=ExtResource("1_level")]

[node name="HUD" parent="." instance=ExtResource("2_hud")]
"""
with open(os.path.join(godot_dir, "scenes", "main.tscn"), "w", encoding="utf-8") as f:
    f.write(main_tscn)

print("Godot 4 Project successfully built at:", godot_dir)
