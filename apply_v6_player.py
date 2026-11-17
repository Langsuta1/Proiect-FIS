import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

player_gd = """extends CharacterBody2D
class_name Player
# player.gd - Metroidvania Player Controller with Flamethrower, Low Crouch Attacks & Natural Poses

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

# Unified Attack Textures (Character visibly swings arm holding weapon from hand level!)
var tex_standard_attack_pan = preload("res://assets/robot_standard_attack_pan_strip4.png")
var tex_damaged_attack_pan = preload("res://assets/robot_damaged_attack_pan_strip4.png")
var tex_standard_attack_bat = preload("res://assets/robot_standard_attack_bat_strip4.png")
var tex_damaged_attack_bat = preload("res://assets/robot_damaged_attack_bat_strip4.png")
var tex_standard_shoot = preload("res://assets/robot_standard_shoot_strip4.png")
var tex_damaged_shoot = preload("res://assets/robot_damaged_shoot_strip4.png")
var tex_weapon_flame = preload("res://assets/weapon_flamethrower_stream_strip4.png")

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

	# 5. Handle Crouch [S] / [DOWN] (Stays low even when attacking from crouch!)
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
		sprite.rotation_degrees = dir * (4.5 if is_sprinting else (0.5 if is_crouching else 1.0))
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

		# If crouching, keep sprite lowered by 6 pixels so player stays crouched!
		var y_off = 6 if is_crouching else 0

		if current_weapon == "pan":
			sprite.texture = tex_damaged_attack_pan if is_dmg else tex_standard_attack_pan
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 8 if facing_direction == 1 else -8
			sprite.offset.y = y_off
		elif current_weapon == "bat":
			sprite.texture = tex_damaged_attack_bat if is_dmg else tex_standard_attack_bat
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 12 if facing_direction == 1 else -12
			sprite.offset.y = -2 + y_off
		elif current_weapon == "blaster":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = y_off
		elif current_weapon == "flamethrower":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = y_off

		if attack_timer <= 0.0:
			melee_hitbox.monitoring = false
			weapon_sprite.visible = false
			sprite.offset = Vector2(0, 0)
		return

	# Melee [X] / attack_melee
	if Input.is_action_just_pressed("attack_melee"):
		var is_bat = (current_weapon == "bat")
		attack_duration = 0.30 if is_bat else 0.22
		attack_timer = attack_duration

		# Low attack hitbox if crouching!
		var hit_y = 6 if is_crouching else 0
		melee_hitbox.monitoring = true
		melee_hitbox.position = Vector2((32 if is_bat else 24) * facing_direction, hit_y)
		var shape_node = melee_hitbox.get_node_or_null("CollisionShape2D")
		if shape_node and shape_node.shape is RectangleShape2D:
			shape_node.shape.size = Vector2(58, 28) if is_bat else Vector2(48, 24)

	# Ranged [Z] / attack_ranged
	elif Input.is_action_pressed("attack_ranged"):
		# Laser Blaster: High damage semi-auto shot
		if current_weapon == "blaster" and ep >= 12.0 and Input.is_action_just_pressed("attack_ranged"):
			ep -= 12.0
			attack_duration = 0.2
			attack_timer = 0.2
			_shoot_laser()
		# Flamethrower: Continuous streaming fire
		elif current_weapon == "flamethrower" and ep >= 1.5:
			ep -= 18.0 * dt
			attack_duration = 0.12
			attack_timer = 0.12
			_shoot_flame(dt)

func _shoot_laser() -> void:
	var proj_scene = load("res://scenes/projectile_laser.tscn")
	if proj_scene:
		var p = proj_scene.instantiate()
		var spawn_y = 4 if is_crouching else -2
		p.position = global_position + Vector2(20 * facing_direction, spawn_y)
		p.direction = Vector2(facing_direction, 0)
		get_parent().add_child(p)

func _shoot_flame(dt: float) -> void:
	weapon_sprite.visible = true
	weapon_sprite.texture = tex_weapon_flame
	weapon_sprite.hframes = 4
	weapon_sprite.scale.x = facing_direction
	var hand_y = 6 if is_crouching else 0
	weapon_sprite.position = Vector2(28 * facing_direction, hand_y)
	weapon_sprite.offset = Vector2(0, 0)
	weapon_sprite.frame = int(Time.get_ticks_msec() / 70.0) % 4

	# Flamethrower melee hitbox damage in front
	melee_hitbox.monitoring = true
	melee_hitbox.position = Vector2(36 * facing_direction, hand_y)
	var shape_node = melee_hitbox.get_node_or_null("CollisionShape2D")
	if shape_node and shape_node.shape is RectangleShape2D:
		shape_node.shape.size = Vector2(48, 28)

func _on_melee_hit(area: Area2D) -> void:
	var target = area.owner if area.owner else area.get_parent()
	if not target:
		target = area

	if target.has_method("take_damage"):
		var cur_w = GameManager.unlocked_weapons[GameManager.current_weapon_idx]
		var dmg = 45.0 if cur_w == "bat" else (14.0 if cur_w == "flamethrower" else 28.0)
		var kb = (360.0 if cur_w == "bat" else (80.0 if cur_w == "flamethrower" else 220.0)) * facing_direction
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
print("Updated player.gd with flamethrower and low crouch attacks.")
