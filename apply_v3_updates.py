import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dirs = [
    os.path.join(scratch_dir, "godot_project"),
    os.path.join(scratch_dir, "scrapborn-(4.0)")
]

# -------------------------------------------------------------------------
# 1. GDScript: Updated player.gd with Solid I-Frames & Humanoid Walk (v3)
# -------------------------------------------------------------------------
player_gd_v3 = """extends CharacterBody2D
class_name Player
# player.gd (v3) - Strict I-Frames, Solid Enemy Collisions, Clean Humanoid Walk

@export var walk_speed: float = 145.0
@export var sprint_speed: float = 230.0
@export var jump_velocity: float = -385.0
@export var double_jump_velocity: float = -340.0
@export var dash_speed: float = 420.0
@export var dash_duration: float = 0.22
@export var gravity: float = 880.0

# Stats
var max_hp: float = 100.0
var hp: float = 100.0
var max_ep: float = 100.0
var ep: float = 100.0

# I-Frames (Invulnerability Frames)
const I_FRAME_DURATION: float = 1.2
var i_frame_timer: float = 0.0

# Movement states
var can_double_jump: bool = true
var has_double_jumped: bool = false
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown: float = 0.0
var is_sprinting: bool = false

# Combat
var attack_timer: float = 0.0
var facing_direction: int = 1

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

# 8-Frame Humanoid Walk Textures
var tex_standard_walk = preload("res://assets/robot_standard_walk_strip8.png")
var tex_damaged_walk = preload("res://assets/robot_damaged_walk_strip8.png")
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
	add_to_group("player")
	melee_hitbox.monitoring = false
	melee_hitbox.area_entered.connect(_on_melee_hit)
	GameManager.player_health_changed.emit(hp, max_hp)
	GameManager.player_energy_changed.emit(ep, max_ep)

func _physics_process(dt: float) -> void:
	# 1. Update I-Frames & Visual Flashing
	if i_frame_timer > 0.0:
		i_frame_timer -= dt
		# Rapid flicker between semi-transparent and visible
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

	# 5. Horizontal Movement & Sprint
	is_sprinting = Input.is_action_pressed("sprint")
	var current_speed = sprint_speed if is_sprinting else walk_speed
	var dir = Input.get_axis("move_left", "move_right")

	if dir != 0.0:
		velocity.x = move_toward(velocity.x, dir * current_speed, current_speed * 9.0 * dt)
		facing_direction = 1 if dir > 0.0 else -1
		sprite.flip_h = (facing_direction == -1)
		melee_hitbox.position.x = 16 * facing_direction
		# Subtle forward aerodynamic lean when sprinting
		sprite.rotation_degrees = dir * (4.5 if is_sprinting else 1.0)
	else:
		velocity.x = move_toward(velocity.x, 0.0, current_speed * 12.0 * dt)
		sprite.rotation_degrees = move_toward(sprite.rotation_degrees, 0.0, 40.0 * dt)

	# 6. Jump & Double Jump
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and ep >= 10.0:
			velocity.y = double_jump_velocity
			has_double_jumped = true
			ep -= 10.0

	# 7. Dash Trigger [C]
	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and ep >= 15.0:
		is_dashing = true
		dash_timer = dash_duration
		dash_cooldown = 0.65
		ep -= 15.0
		velocity.x = facing_direction * dash_speed
		velocity.y = 0.0

	# 8. Weapon Actions
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

# STRICT I-FRAMES & KNOCKBACK TO PREVENT HEALTH MELT
func take_damage(amount: float, knockback_dir: float = 0.0) -> void:
	if i_frame_timer > 0.0:
		return # Completely immune during i-frames!

	i_frame_timer = I_FRAME_DURATION
	hp = max(0.0, hp - amount)

	# Launch player away from the attacker so they don't stay inside the hitbox
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
	var frame_speed = 0.075 if is_sprinting else 0.115
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
		# 8-Frame Clean Humanoid Gait
		sprite.texture = tex_standard_walk if GameManager.player_chassis == "standard" else tex_damaged_walk
		sprite.hframes = 8
		sprite.frame = frame_idx % 8
	else:
		sprite.texture = tex_standard_idle if GameManager.player_chassis == "standard" else tex_damaged_idle
		sprite.hframes = 4
		sprite.frame = frame_idx % 4
"""

# -------------------------------------------------------------------------
# 2. GDScript: Updated enemy_drone.gd with Safe Hitbox & No Continuous Melt
# -------------------------------------------------------------------------
drone_gd_v3 = """extends CharacterBody2D
class_name EnemyDrone
# enemy_drone.gd - Patrolling flying drone with dedicated damage Area2D (No per-frame melt!)

@export var patrol_distance: float = 120.0
@export var speed: float = 55.0
@export var max_hp: float = 24.0

var hp: float = 24.0
var start_x: float = 0.0
var direction: int = 1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox
@onready var damage_area: Area2D = $DamageArea

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")
	damage_area.body_entered.connect(_on_damage_body_entered)

func _physics_process(dt: float) -> void:
	velocity.x = direction * speed
	velocity.y = sin(Time.get_ticks_msec() / 200.0) * 15.0

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	anim_timer += dt
	sprite.frame = int(anim_timer / 0.09) % 4

	move_and_slide()

func _on_damage_body_entered(body: Node2D) -> void:
	if body is Player:
		var kb_dir = 1.0 if body.global_position.x > global_position.x else -1.0
		body.take_damage(16.0, kb_dir)

func take_damage(amount: float, knockback: float) -> void:
	hp -= amount
	velocity.x = knockback * 160.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

# -------------------------------------------------------------------------
# 3. GDScript: Updated enemy_crawler.gd with Safe Hitbox & No Melt
# -------------------------------------------------------------------------
crawler_gd_v3 = """extends CharacterBody2D
class_name EnemyCrawler
# enemy_crawler.gd - Ground patrolling scrap crawler with dedicated damage Area2D

@export var patrol_distance: float = 140.0
@export var speed: float = 45.0
@export var max_hp: float = 32.0

var hp: float = 32.0
var start_x: float = 0.0
var direction: int = 1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox
@onready var damage_area: Area2D = $DamageArea

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")
	damage_area.body_entered.connect(_on_damage_body_entered)

func _physics_process(dt: float) -> void:
	if not is_on_floor():
		velocity.y += 850.0 * dt

	velocity.x = direction * speed

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	anim_timer += dt
	sprite.frame = int(anim_timer / 0.12) % 4

	move_and_slide()

func _on_damage_body_entered(body: Node2D) -> void:
	if body is Player:
		var kb_dir = 1.0 if body.global_position.x > global_position.x else -1.0
		body.take_damage(20.0, kb_dir)

func take_damage(amount: float, knockback: float) -> void:
	hp -= amount
	velocity.x = knockback * 140.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

# -------------------------------------------------------------------------
# 4. GDScript: Updated boss_crusher.gd with Safe Hitbox & No Melt
# -------------------------------------------------------------------------
boss_gd_v3 = """extends CharacterBody2D
class_name BossCrusher
# boss_crusher.gd - The Crusher Compactor Boss with native animated 64x64 sprite

@export var max_hp: float = 200.0
var hp: float = 200.0
var state: String = "idle"
var state_timer: float = 2.5
var facing: int = -1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox
@onready var damage_area: Area2D = $DamageArea

func _ready() -> void:
	hp = max_hp
	hurtbox.add_to_group("enemies")
	damage_area.body_entered.connect(_on_damage_body_entered)
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

	anim_timer += dt
	sprite.frame = int(anim_timer / 0.15) % 4
	sprite.flip_h = (facing == 1)

	move_and_slide()

func _on_damage_body_entered(body: Node2D) -> void:
	if body is Player:
		var kb_dir = 1.0 if body.global_position.x > global_position.x else -1.0
		body.take_damage(28.0, kb_dir)

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

# -------------------------------------------------------------------------
# 5. GDScript: Rock-Solid High-Contrast HUD (Always Visible!)
# -------------------------------------------------------------------------
hud_gd_v3 = """extends CanvasLayer
# hud.gd (v3) - High-visibility Metroidvania HUD with Armor (HP) & Core Stamina (Energy)

@onready var hp_fill: ColorRect = $HUDPanel/VBox/HPContainer/HPTrack/HPFill
@onready var hp_label: Label = $HUDPanel/VBox/HPContainer/HPLabel
@onready var ep_fill: ColorRect = $HUDPanel/VBox/EPContainer/EPTrack/EPFill
@onready var ep_label: Label = $HUDPanel/VBox/EPContainer/EPLabel
@onready var weapon_label: Label = $WeaponCard/WeaponLabel
@onready var notify_panel: Panel = $NotifyPanel
@onready var notify_title: Label = $NotifyPanel/Title
@onready var notify_text: Label = $NotifyPanel/Text
@onready var boss_panel: Panel = $BossPanel
@onready var boss_bar: ProgressBar = $BossPanel/BossBar

var target_hp: float = 100.0
var max_hp: float = 100.0
var target_ep: float = 100.0
var max_ep: float = 100.0
var notify_timer: float = 0.0

func _ready() -> void:
	layer = 100 # Topmost layer so it is NEVER hidden!
	notify_panel.visible = false
	boss_panel.visible = false

	GameManager.player_health_changed.connect(_on_hp_changed)
	GameManager.player_energy_changed.connect(_on_ep_changed)
	GameManager.weapon_switched.connect(_on_weapon_switched)
	GameManager.boss_health_changed.connect(_on_boss_health)
	GameManager.notification_posted.connect(_on_notification)

	_update_bars()

func _process(dt: float) -> void:
	# Continuous fail-safe poll to ensure bars match player exactly
	var player = get_tree().get_first_node_in_group("player")
	if player:
		target_hp = player.hp
		max_hp = player.max_hp
		target_ep = player.ep
		max_ep = player.max_ep
		_update_bars()

	if notify_timer > 0.0:
		notify_timer -= dt
		if notify_timer <= 0.0:
			notify_panel.visible = false

func _update_bars() -> void:
	var hp_pct = clamp(target_hp / max_hp, 0.0, 1.0)
	var ep_pct = clamp(target_ep / max_ep, 0.0, 1.0)

	# 180px track width
	hp_fill.size.x = 180.0 * hp_pct
	hp_label.text = "ARMOR: " + str(int(target_hp)) + " / " + str(int(max_hp))

	ep_fill.size.x = 180.0 * ep_pct
	ep_label.text = "CORE STAMINA: " + str(int(target_ep)) + " / " + str(int(max_ep))

func _on_hp_changed(curr: float, mx: float) -> void:
	target_hp = curr
	max_hp = mx
	_update_bars()

func _on_ep_changed(curr: float, mx: float) -> void:
	target_ep = curr
	max_ep = mx
	_update_bars()

func _on_weapon_switched(w_name: String, _data: Dictionary) -> void:
	weapon_label.text = w_name.to_upper()

func _on_boss_health(curr: float, mx: float) -> void:
	boss_panel.visible = (curr > 0.0)
	boss_bar.value = (curr / mx) * 100.0

func _on_notification(title: String, text: String) -> void:
	notify_title.text = title
	notify_text.text = text
	notify_panel.visible = true
	notify_timer = 4.0
"""

# -------------------------------------------------------------------------
# 6. Scene Updates (.tscn)
# -------------------------------------------------------------------------

# hud.tscn with direct ColorRect progress fills (100% visible, no theme collapse)
hud_tscn_v3 = """[gd_scene load_steps=2 format=3 uid="uid://hud_v3_solid"]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_hud"]

[node name="HUD" type="CanvasLayer"]
layer = 100
script = ExtResource("1_hud")

[node name="HUDPanel" type="Panel" parent="."]
offset_left = 16.0
offset_top = 16.0
offset_right = 240.0
offset_bottom = 76.0

[node name="VBox" type="VBoxContainer" parent="HUDPanel"]
layout_mode = 0
offset_left = 8.0
offset_top = 6.0
offset_right = 216.0
offset_bottom = 54.0

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

[node name="WeaponCard" type="Panel" parent="."]
offset_left = 16.0
offset_top = 480.0
offset_right = 220.0
offset_bottom = 524.0

[node name="WeaponLabel" type="Label" parent="WeaponCard"]
layout_mode = 0
offset_left = 10.0
offset_top = 10.0
offset_right = 200.0
offset_bottom = 34.0
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
text = "CYBER FRYING PAN"

[node name="NotifyPanel" type="Panel" parent="."]
visible = false
offset_left = 280.0
offset_top = 440.0
offset_right = 680.0
offset_bottom = 510.0

[node name="Title" type="Label" parent="NotifyPanel"]
layout_mode = 0
offset_left = 12.0
offset_top = 8.0
offset_right = 388.0
offset_bottom = 30.0
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
text = "SYSTEM MESSAGE"

[node name="Text" type="Label" parent="NotifyPanel"]
layout_mode = 0
offset_left = 12.0
offset_top = 32.0
offset_right = 388.0
offset_bottom = 62.0
text = "Scraps activated."

[node name="BossPanel" type="Panel" parent="."]
visible = false
offset_left = 320.0
offset_top = 20.0
offset_right = 640.0
offset_bottom = 65.0

[node name="BossTitle" type="Label" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 4.0
offset_right = 310.0
offset_bottom = 24.0
theme_override_colors/font_color = Color(0.93, 0.27, 0.27, 1)
text = "THE CRUSHER — COMPACTOR TITAN"

[node name="BossBar" type="ProgressBar" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 26.0
offset_right = 310.0
offset_bottom = 38.0
value = 100.0
show_percentage = false
"""

# enemy_drone.tscn with DamageArea Hitbox
drone_tscn_v3 = """[gd_scene load_steps=6 format=3 uid="uid://drone_v3_safe"]

[ext_resource type="Script" path="res://scripts/enemy_drone.gd" id="1_drone"]
[ext_resource type="Texture2D" path="res://assets/enemy_junk_drone_strip4.png" id="2_drone_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(20, 16)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(24, 18)

[sub_resource type="CircleShape2D" id="CircleShape2D_dmg"]
radius = 14.0

[node name="EnemyDrone" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 1
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

[node name="DamageArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 2

[node name="CollisionShape2D" type="CollisionShape2D" parent="DamageArea"]
shape = SubResource("CircleShape2D_dmg")
"""

# enemy_crawler.tscn with DamageArea Hitbox
crawler_tscn_v3 = """[gd_scene load_steps=6 format=3 uid="uid://crawler_v3_safe"]

[ext_resource type="Script" path="res://scripts/enemy_crawler.gd" id="1_crawler"]
[ext_resource type="Texture2D" path="res://assets/enemy_scrap_crawler_strip4.png" id="2_crawler_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_body"]
size = Vector2(24, 14)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(26, 16)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_dmg"]
size = Vector2(28, 16)

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

[node name="DamageArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 2

[node name="CollisionShape2D" type="CollisionShape2D" parent="DamageArea"]
position = Vector2(0, 5)
shape = SubResource("RectangleShape2D_dmg")
"""

# boss_crusher.tscn with DamageArea Hitbox
boss_tscn_v3 = """[gd_scene load_steps=6 format=3 uid="uid://boss_v3_safe"]

[ext_resource type="Script" path="res://scripts/boss_crusher.gd" id="1_boss"]
[ext_resource type="Texture2D" path="res://assets/boss_crusher_strip4.png" id="2_crusher_tex"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_boss"]
size = Vector2(46, 52)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_hurt"]
size = Vector2(50, 56)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_dmg"]
size = Vector2(52, 54)

[node name="BossCrusher" type="CharacterBody2D"]
collision_layer = 8
collision_mask = 1
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

[node name="DamageArea" type="Area2D" parent="."]
collision_layer = 0
collision_mask = 2

[node name="CollisionShape2D" type="CollisionShape2D" parent="DamageArea"]
position = Vector2(0, 4)
shape = SubResource("RectangleShape2D_dmg")
"""

# level_heap.tscn with Crushed Car obstacle, Parallax & Tutorial Prompt
level_tscn_v3 = """[gd_scene load_steps=14 format=3 uid="uid://level_heap_v3_interactive"]

[ext_resource type="Texture2D" path="res://assets/bg_layer1_sky.png" id="1_sky"]
[ext_resource type="Texture2D" path="res://assets/bg_layer2_distant_scrap.png" id="2_scrap"]
[ext_resource type="Texture2D" path="res://assets/bg_layer3_midground_pipes.png" id="3_pipes"]
[ext_resource type="Texture2D" path="res://assets/bg_layer4_foreground_girders.png" id="4_girders"]
[ext_resource type="Texture2D" path="res://assets/crushed_car_obstacle.png" id="5_car_tex"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="6_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="7_drone"]
[ext_resource type="PackedScene" path="res://scenes/enemy_crawler.tscn" id="8_crawler"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="9_boss"]
[ext_resource type="PackedScene" path="res://scenes/tutorial_prompt.tscn" id="10_tut"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_ground"]
size = Vector2(3200, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_plat"]
size = Vector2(140, 18)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_car"]
size = Vector2(56, 24)

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
position = Vector2(280, 768)

[node name="Sprite2D" type="Sprite2D" parent="CrushedCarObstacle"]
texture = ExtResource("5_car_tex")

[node name="CollisionShape2D" type="CollisionShape2D" parent="CrushedCarObstacle"]
position = Vector2(0, 4)
shape = SubResource("RectangleShape2D_car")

[node name="TutorialJumpCar" parent="." instance=ExtResource("10_tut")]
position = Vector2(280, 710)
prompt_key = "[SPACE] OR [W]"
prompt_action = "JUMP OVER THE CRUSHED CAR"
prompt_subtitle = "Tap in mid-air to Double Jump"

[node name="TutorialMove" parent="." instance=ExtResource("10_tut")]
position = Vector2(100, 740)
prompt_key = "A / D"
prompt_action = "MOVE CHASSIS"
prompt_subtitle = "Hold [SHIFT] to Sprint"

[node name="TutorialDash" parent="." instance=ExtResource("10_tut")]
position = Vector2(460, 630)
prompt_key = "[C]"
prompt_action = "DASH THROUGH HAZARDS"
prompt_subtitle = "Phases through enemy shots"

[node name="TutorialCombat" parent="." instance=ExtResource("10_tut")]
position = Vector2(680, 530)
prompt_key = "[X] OR LEFT CLICK"
prompt_action = "MELEE STRIKE"
prompt_subtitle = "Cyber Pan clangs & deflects shots"

[node name="TutorialRanged" parent="." instance=ExtResource("10_tut")]
position = Vector2(980, 450)
prompt_key = "[Z] OR RIGHT CLICK"
prompt_action = "RANGED LASER BLASTER"
prompt_subtitle = "Consumes Core Stamina to fire"

[node name="Player" parent="." instance=ExtResource("6_player")]
position = Vector2(70, 720)

[node name="EnemyCrawler1" parent="." instance=ExtResource("8_crawler")]
position = Vector2(420, 765)

[node name="EnemyDrone1" parent="." instance=ExtResource("7_drone")]
position = Vector2(760, 450)

[node name="EnemyCrawler2" parent="." instance=ExtResource("8_crawler")]
position = Vector2(1050, 765)

[node name="EnemyDrone2" parent="." instance=ExtResource("7_drone")]
position = Vector2(1450, 430)

[node name="BossCrusher" parent="." instance=ExtResource("9_boss")]
position = Vector2(2650, 720)
"""

for g_dir in godot_dirs:
    if not os.path.exists(g_dir):
        continue

    # Write scripts
    with open(os.path.join(g_dir, "scripts", "player.gd"), "w", encoding="utf-8") as f:
        f.write(player_gd_v3)
    with open(os.path.join(g_dir, "scripts", "enemy_drone.gd"), "w", encoding="utf-8") as f:
        f.write(drone_gd_v3)
    with open(os.path.join(g_dir, "scripts", "enemy_crawler.gd"), "w", encoding="utf-8") as f:
        f.write(crawler_gd_v3)
    with open(os.path.join(g_dir, "scripts", "boss_crusher.gd"), "w", encoding="utf-8") as f:
        f.write(boss_gd_v3)
    with open(os.path.join(g_dir, "scripts", "hud.gd"), "w", encoding="utf-8") as f:
        f.write(hud_gd_v3)

    # Write scenes
    with open(os.path.join(g_dir, "scenes", "hud.tscn"), "w", encoding="utf-8") as f:
        f.write(hud_tscn_v3)
    with open(os.path.join(g_dir, "scenes", "enemy_drone.tscn"), "w", encoding="utf-8") as f:
        f.write(drone_tscn_v3)
    with open(os.path.join(g_dir, "scenes", "enemy_crawler.tscn"), "w", encoding="utf-8") as f:
        f.write(crawler_tscn_v3)
    with open(os.path.join(g_dir, "scenes", "boss_crusher.tscn"), "w", encoding="utf-8") as f:
        f.write(boss_tscn_v3)
    with open(os.path.join(g_dir, "scenes", "level_heap.tscn"), "w", encoding="utf-8") as f:
        f.write(level_tscn_v3)

    print(f"Successfully applied v3 changes to Godot project: {g_dir}")

print("Godot v3 updates completed!")
