import os
import shutil
import json
import base64

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

# 1. Copy the updated melee weapon sheets into Godot asset directories
for dest in [os.path.join(godot_dir, "assets"), os.path.join(godot_copy_dir, "assets")]:
    os.makedirs(dest, exist_ok=True)
    shutil.copy2(
        os.path.join(scratch_dir, "animations", "sheets", "weapon_pan_swing_strip4.png"),
        os.path.join(dest, "weapon_pan_swing_strip4.png")
    )
    shutil.copy2(
        os.path.join(scratch_dir, "animations", "sheets", "weapon_bat_slam_strip4.png"),
        os.path.join(dest, "weapon_bat_slam_strip4.png")
    )

print("Updated weapon sheets copied to Godot asset folders.")

# 2. Update player.gd for both Godot projects
player_gd_code = """extends CharacterBody2D
class_name Player
# player.gd - Metroidvania Player Controller with Clean 8-Frame Humanoid Walk & Dynamic Melee Swing

# Movement physics parameters
@export var walk_speed: float = 145.0
@export var sprint_speed: float = 230.0
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
		# Aerodynamic lean when sprinting
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
	var current_weapon = GameManager.unlocked_weapons[GameManager.current_weapon_idx]

	if attack_timer > 0.0:
		attack_timer -= dt
		# Update frame dynamically across attack duration (0 -> 1 -> 2 -> 3)
		var progress = clamp(1.0 - (attack_timer / attack_duration), 0.0, 0.99)
		weapon_sprite.frame = int(progress * 4.0)

		# Keep weapon orientation and position synchronized with player facing direction
		weapon_sprite.scale.x = facing_direction
		weapon_sprite.position = Vector2(2 * facing_direction, 0)

		if attack_timer <= 0.0:
			weapon_sprite.visible = false
			melee_hitbox.monitoring = false
		return

	# Melee [X] / attack_melee
	if Input.is_action_just_pressed("attack_melee"):
		var is_bat = (current_weapon == "bat")
		attack_duration = 0.30 if is_bat else 0.22
		attack_timer = attack_duration

		weapon_sprite.visible = true
		weapon_sprite.texture = tex_weapon_bat if is_bat else tex_weapon_pan
		weapon_sprite.hframes = 4
		weapon_sprite.frame = 0

		# Pivot from robot's hand, flipping cleanly with facing_direction
		weapon_sprite.scale.x = facing_direction
		weapon_sprite.position = Vector2(2 * facing_direction, 0)
		weapon_sprite.offset = Vector2(-10, -18 if is_bat else -16)

		# Melee Hitbox reach and size
		melee_hitbox.monitoring = true
		melee_hitbox.position = Vector2((32 if is_bat else 24) * facing_direction, 0)
		var shape_node = melee_hitbox.get_node_or_null("CollisionShape2D")
		if shape_node and shape_node.shape is RectangleShape2D:
			shape_node.shape.size = Vector2(56, 36) if is_bat else Vector2(44, 32)

	# Ranged [Z] / attack_ranged
	elif Input.is_action_pressed("attack_ranged"):
		if current_weapon == "blaster" and ep >= 12.0 and Input.is_action_just_pressed("attack_ranged"):
			ep -= 12.0
			attack_duration = 0.2
			attack_timer = 0.2
			_shoot_laser()
		elif current_weapon == "flamethrower" and ep >= 3.0:
			ep -= 3.0
			attack_duration = 0.08
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
	weapon_sprite.scale.x = facing_direction
	weapon_sprite.position = Vector2(12 * facing_direction, 0)
	weapon_sprite.offset = Vector2(0, -16)

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
		return # Completely immune during i-frames!

	i_frame_timer = I_FRAME_DURATION
	hp = max(0.0, hp - amount)

	# Launch player away from the attacker
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

for target_dir in [godot_dir, godot_copy_dir]:
    p_path = os.path.join(target_dir, "scripts", "player.gd")
    with open(p_path, "w", encoding="utf-8") as f:
        f.write(player_gd_code)

print("Updated player.gd in both Godot projects.")

# 3. Update level_heap.tscn to lock background layers vertically (cranes, fence, tires do not move when jumping!)
for target_dir in [godot_dir, godot_copy_dir]:
    scene_path = os.path.join(target_dir, "scenes", "level_heap.tscn")
    with open(scene_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Set motion_scale.y = 1.0 for midground and foreground layers so they remain locked to the world ground!
    # And position sprites to ground horizon (y = 530)
    content = content.replace(
        'motion_scale = Vector2(0.45, 0.25)',
        'motion_scale = Vector2(0.45, 1.0)'
    )
    content = content.replace(
        'motion_scale = Vector2(0.75, 0.45)',
        'motion_scale = Vector2(0.75, 1.0)'
    )
    content = content.replace(
        'motion_scale = Vector2(0.18, 0.12)',
        'motion_scale = Vector2(0.18, 0.1)'
    )
    content = content.replace(
        'motion_scale = Vector2(0.05, 0.05)',
        'motion_scale = Vector2(0.05, 0.02)'
    )

    with open(scene_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated level_heap.tscn parallax in both Godot projects.")
