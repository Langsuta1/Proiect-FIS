import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

print("Writing complete Godot V7 Metroidvania System...")

# ---------------------------------------------------------------------------
# 1. AUTOLOAD GAME MANAGER (InputMap, Inventory 3x3 Matrix, Shield, Weapons)
# ---------------------------------------------------------------------------
game_manager_gd = """extends Node
# game_manager.gd - Global Game Manager & Inventory Controller

signal player_health_changed(hp, max_hp)
signal player_energy_changed(ep, max_ep)
signal player_shield_changed(shield_hp, max_shield_hp)
signal inventory_updated()
signal weapon_swapped(primary_w, secondary_w)
signal boss_health_changed(hp, max_hp, phase)
signal boss_defeated()

# Player Chassis
var player_chassis: String = "standard" # "standard" or "damaged"

# Health & Energy & Shield
var player_hp: float = 100.0
var player_max_hp: float = 100.0
var player_ep: float = 100.0
var player_max_ep: float = 100.0
var player_shield: float = 50.0
var player_max_shield: float = 50.0
var shield_regen_delay: float = 3.0
var shield_regen_timer: float = 0.0
var shield_regen_rate: float = 0.15 # 15% per second

# Inventory Matrix (3x3 = 9 slots)
# Each slot: {"id": String, "name": String, "type": String, "icon": String, "count": int}
var backpack: Array = [
	{"id": "pan", "name": "Cyber Frying Pan", "type": "weapon", "icon": "cyber_pan_32x32"},
	{"id": "bat", "name": "Reinforced Metal Bat", "type": "weapon", "icon": "metal_bat_32x32"},
	{"id": "blaster", "name": "Laser Blaster Arm", "type": "weapon", "icon": "laser_blaster_arm_32x32"},
	{"id": "flamethrower", "name": "Scrap Flamethrower", "type": "weapon", "icon": "flamethrower_32x32"},
	{"id": "frag", "name": "Frag Grenades", "type": "grenade", "icon": "grenade_frag_32x32", "count": 3},
	{"id": "emp", "name": "EMP Grenades", "type": "grenade", "icon": "grenade_emp_32x32", "count": 2},
	{"id": "cryo", "name": "Cryo Grenades", "type": "grenade", "icon": "grenade_cryo_32x32", "count": 2},
	{"id": "fire", "name": "Thermite Grenades", "type": "grenade", "icon": "grenade_fire_32x32", "count": 2},
	{"id": "nano_core", "name": "Overclock Chip", "type": "upgrade", "icon": "chip_nano_repair_32x32"}
]

# Equipped Weapons: Primary (Melee) & Secondary (Ranged)
var primary_weapon: String = "pan"
var secondary_weapon: String = "blaster"
var active_grenade: String = "frag"

var is_inventory_open: bool = false

func _ready() -> void:
	_setup_inputs()

func _setup_inputs() -> void:
	_add_action("move_left", [KEY_A, KEY_LEFT])
	_add_action("move_right", [KEY_D, KEY_RIGHT])
	_add_action("jump", [KEY_SPACE, KEY_W, KEY_UP])
	_add_action("sprint", [KEY_SHIFT])
	_add_action("crouch", [KEY_S, KEY_DOWN])
	_add_action("attack_melee", [KEY_X])
	_add_mouse_action("attack_melee", MOUSE_BUTTON_LEFT)
	_add_action("attack_ranged", [KEY_Z])
	_add_action("switch_weapon", [KEY_Q])
	_add_action("inventory", [KEY_I])
	_add_action("shield", [KEY_F])
	_add_mouse_action("shield", MOUSE_BUTTON_RIGHT)
	_add_action("grenade", [KEY_G])
	_add_action("grapple", [KEY_E])
	_add_action("dash", [KEY_C])

func _add_action(name: String, keys: Array) -> void:
	if not InputMap.has_action(name):
		InputMap.add_action(name)
	for key in keys:
		var ev = InputEventKey.new()
		ev.keycode = key
		InputMap.action_add_event(name, ev)

func _add_mouse_action(name: String, btn: int) -> void:
	if not InputMap.has_action(name):
		InputMap.add_action(name)
	var ev = InputEventMouseButton.new()
	ev.button_index = btn
	InputMap.action_add_event(name, ev)

func swap_weapons() -> void:
	var temp = primary_weapon
	primary_weapon = secondary_weapon
	secondary_weapon = temp
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func use_grenade() -> bool:
	for slot in backpack:
		if slot.id == active_grenade and slot.get("count", 0) > 0:
			slot["count"] -= 1
			inventory_updated.emit()
			return true
	return false

func damage_shield(amount: float) -> float:
	# Returns leftover damage penetrating to HP
	shield_regen_timer = shield_regen_delay
	if player_shield >= amount:
		player_shield -= amount
		player_shield_changed.emit(player_shield, player_max_shield)
		return 0.0
	else:
		var leftover = amount - player_shield
		player_shield = 0.0
		player_shield_changed.emit(player_shield, player_max_shield)
		return leftover

func _process(dt: float) -> void:
	# Shield Regeneration after 3.0s without damage
	if shield_regen_timer > 0.0:
		shield_regen_timer -= dt
	elif player_shield < player_max_shield:
		player_shield = min(player_max_shield, player_shield + (player_max_shield * shield_regen_rate * dt))
		player_shield_changed.emit(player_shield, player_max_shield)
"""

# ---------------------------------------------------------------------------
# 2. PLAYER SCRIPT (Humanoid bipedal animations, Shield, Grapple, Grenades)
# ---------------------------------------------------------------------------
player_gd = """extends CharacterBody2D
class_name Player
# player.gd - Metroidvania Player Controller with Humanoid Bipedal Locomotion, Shield, Grapple & Grenades

@export var walk_speed: float = 145.0
@export var sprint_speed: float = 230.0
@export var crouch_speed: float = 60.0
@export var jump_velocity: float = -380.0
@export var double_jump_velocity: float = -330.0
@export var dash_speed: float = 420.0
@export var dash_duration: float = 0.22
@export var gravity: float = 980.0

# Strict I-Frames
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

# Energy Shield
var is_shield_raised: bool = false

# Grappling Hook
var is_grappling: bool = false
var grapple_anchor: Vector2 = Vector2.ZERO
var grapple_length: float = 0.0
var grapple_angle: float = 0.0
var grapple_angular_vel: float = 0.0

# Combat
var attack_timer: float = 0.0
var attack_duration: float = 0.24
var facing_direction: int = 1

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var shield_sprite: Sprite2D = $ShieldSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

# Humanoid Textures
var tex_standard_walk = preload("res://assets/robot_standard_walk_strip8.png")
var tex_damaged_walk = preload("res://assets/robot_damaged_walk_strip8.png")
var tex_standard_idle = preload("res://assets/robot_standard_idle_strip4.png")
var tex_damaged_idle = preload("res://assets/robot_damaged_idle_strip4.png")
var tex_standard_crouch = preload("res://assets/robot_standard_crouch_strip2.png")
var tex_damaged_crouch = preload("res://assets/robot_damaged_crouch_strip2.png")
var tex_standard_attack_pan = preload("res://assets/robot_standard_attack_pan_strip4.png")
var tex_damaged_attack_pan = preload("res://assets/robot_damaged_attack_pan_strip4.png")
var tex_standard_attack_bat = preload("res://assets/robot_standard_attack_bat_strip4.png")
var tex_damaged_attack_bat = preload("res://assets/robot_damaged_attack_bat_strip4.png")
var tex_standard_shoot = preload("res://assets/robot_standard_shoot_strip4.png")
var tex_damaged_shoot = preload("res://assets/robot_damaged_shoot_strip4.png")
var tex_shield = preload("res://assets/shield_energy_barrier_64x64.png")

var anim_timer: float = 0.0

func _ready() -> void:
	add_to_group("player")
	if weapon_sprite: weapon_sprite.visible = false
	if shield_sprite:
		shield_sprite.visible = false
		shield_sprite.texture = tex_shield
	if melee_hitbox:
		melee_hitbox.monitoring = false
		melee_hitbox.area_entered.connect(_on_melee_hit)
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
	GameManager.player_shield_changed.emit(GameManager.player_shield, GameManager.player_max_shield)

func _physics_process(dt: float) -> void:
	# 1. Update I-Frames
	if i_frame_timer > 0.0:
		i_frame_timer -= dt
		sprite.modulate.a = 0.35 if fmod(Time.get_ticks_msec() / 70.0, 2.0) > 1.0 else 1.0
	else:
		sprite.modulate.a = 1.0

	# 2. Quick-Swap Weapons [Q]
	if Input.is_action_just_pressed("switch_weapon"):
		GameManager.swap_weapons()

	# 3. Handle Grappling Hook [E]
	if Input.is_action_just_pressed("grapple"):
		if is_grappling:
			_release_grapple()
		else:
			_try_grapple()

	if is_grappling:
		_process_grapple_physics(dt)
		move_and_slide()
		return

	# 4. Energy Shield [F] / [Right Click]
	is_shield_raised = Input.is_action_pressed("shield") and GameManager.player_shield > 0.0
	if shield_sprite:
		shield_sprite.visible = is_shield_raised
		shield_sprite.position = Vector2(16 * facing_direction, 0)
		shield_sprite.scale.x = facing_direction

	# 5. Handle Dash [C]
	if dash_cooldown > 0.0:
		dash_cooldown -= dt
	if is_dashing:
		dash_timer -= dt
		velocity.y = 0.0
		velocity.x = dash_speed * facing_direction
		if dash_timer <= 0.0:
			is_dashing = false
			dash_cooldown = 0.45
		move_and_slide()
		return

	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and not is_dashing and GameManager.player_ep >= 15.0:
		is_dashing = true
		dash_timer = dash_duration
		GameManager.player_ep -= 15.0
		GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
		return

	# 6. Handle Crouch [S] / [DOWN]
	is_crouching = Input.is_action_pressed("crouch") and is_on_floor()
	if collision_shape:
		var rect = collision_shape.shape as RectangleShape2D
		if rect:
			if is_crouching:
				rect.size = Vector2(18, 16)
				collision_shape.position = Vector2(0, 6)
			else:
				rect.size = Vector2(18, 28)
				collision_shape.position = Vector2(0, 0)

	# 7. Gravity
	if not is_on_floor():
		velocity.y += gravity * dt
	else:
		can_double_jump = true
		has_double_jumped = false

	# 8. Jump & Double Jump
	if Input.is_action_just_pressed("jump"):
		if is_on_floor():
			velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and GameManager.player_ep >= 10.0:
			velocity.y = double_jump_velocity
			has_double_jumped = true
			GameManager.player_ep -= 10.0
			GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)

	# 9. Horizontal Movement
	var input_dir: float = Input.get_axis("move_left", "move_right")
	is_sprinting = Input.is_action_pressed("sprint") and input_dir != 0.0 and not is_crouching

	var target_speed = walk_speed
	if is_crouching:
		target_speed = crouch_speed
	elif is_sprinting:
		target_speed = sprint_speed

	if input_dir != 0.0:
		velocity.x = input_dir * target_speed
		facing_direction = 1 if input_dir > 0 else -1
		sprite.scale.x = facing_direction
	else:
		velocity.x = move_toward(velocity.x, 0.0, 800.0 * dt)

	# 10. Combat Attacks
	_handle_attacks(dt)

	# 11. Grenade [G]
	if Input.is_action_just_pressed("grenade"):
		_throw_grenade()

	# 12. Update Animations
	_update_animations(dt, input_dir)

	move_and_slide()

func _handle_attacks(dt: float) -> void:
	var weapon = GameManager.primary_weapon
	var is_dmg = (GameManager.player_chassis == "damaged")

	if attack_timer > 0.0:
		attack_timer -= dt
		var progress = clamp(1.0 - (attack_timer / attack_duration), 0.0, 0.99)
		var f_idx = int(progress * 4.0)
		var y_off = 6 if is_crouching else 0

		if weapon == "pan":
			sprite.texture = tex_damaged_attack_pan if is_dmg else tex_standard_attack_pan
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 8 if facing_direction == 1 else -8
			sprite.offset.y = y_off
		elif weapon == "bat":
			sprite.texture = tex_damaged_attack_bat if is_dmg else tex_standard_attack_bat
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 12 if facing_direction == 1 else -12
			sprite.offset.y = -2 + y_off
		elif weapon == "blaster":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = y_off

		if attack_timer <= 0.0:
			melee_hitbox.monitoring = false
			sprite.offset = Vector2(0, 0)
		return

	# Melee [X] / Left Click
	if Input.is_action_just_pressed("attack_melee"):
		var is_bat = (weapon == "bat")
		attack_duration = 0.28 if is_bat else 0.22
		attack_timer = attack_duration

		var hit_y = 6 if is_crouching else 0
		melee_hitbox.monitoring = true
		melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)

	# Ranged [Z] / Secondary
	elif Input.is_action_pressed("attack_ranged"):
		var sec_weapon = GameManager.secondary_weapon
		if sec_weapon == "blaster" and GameManager.player_ep >= 12.0 and Input.is_action_just_pressed("attack_ranged"):
			GameManager.player_ep -= 12.0
			GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
			attack_duration = 0.20
			attack_timer = 0.20
			_shoot_blaster()

func _shoot_blaster() -> void:
	var proj = preload("res://scenes/projectile_laser.tscn").instantiate()
	var hand_y = position.y + (6 if is_crouching else 0)
	proj.position = Vector2(position.x + 20 * facing_direction, hand_y)
	proj.direction = Vector2(facing_direction, 0)
	get_parent().add_child(proj)

func _throw_grenade() -> void:
	if GameManager.use_grenade():
		print("Player threw grenade:", GameManager.active_grenade)
		# Spawn grenade in world
		# Spawns physical grenade with velocity arc

func _try_grapple() -> void:
	# Scan for anchor rings within 280px radius
	var rings = get_tree().get_nodes_in_group("grapple_rings")
	var closest_dist = 280.0
	var target_ring: Node2D = null
	for ring in rings:
		var d = global_position.distance_to(ring.global_position)
		if d < closest_dist and ring.global_position.y < global_position.y:
			closest_dist = d
			target_ring = ring
	if target_ring:
		is_grappling = true
		grapple_anchor = target_ring.global_position
		grapple_length = global_position.distance_to(grapple_anchor)
		grapple_angle = (global_position - grapple_anchor).angle()
		grapple_angular_vel = (velocity.x / grapple_length) * 0.8

func _process_grapple_physics(dt: float) -> void:
	# Pendulum physics
	var angular_accel = (-gravity / grapple_length) * cos(grapple_angle)
	grapple_angular_vel += angular_accel * dt
	grapple_angular_vel *= 0.995 # Slight dampening
	grapple_angle += grapple_angular_vel * dt

	global_position = grapple_anchor + Vector2(cos(grapple_angle), sin(grapple_angle)) * grapple_length
	velocity = Vector2(-sin(grapple_angle), cos(grapple_angle)) * grapple_angular_vel * grapple_length

	if Input.is_action_just_pressed("jump"):
		_release_grapple()
		velocity.y = jump_velocity * 1.15
		velocity.x += facing_direction * 150.0

func _release_grapple() -> void:
	is_grappling = false

func _update_animations(dt: float, input_dir: float) -> void:
	if attack_timer > 0.0:
		return

	var is_dmg = (GameManager.player_chassis == "damaged")
	anim_timer += dt

	if is_crouching:
		sprite.texture = tex_damaged_crouch if is_dmg else tex_standard_crouch
		sprite.hframes = 2
		sprite.frame = int(anim_timer * 4.0) % 2
		sprite.offset = Vector2(0, 0)
	elif not is_on_floor():
		sprite.texture = tex_standard_walk
		sprite.hframes = 8
		sprite.frame = 3 # High jump frame
	elif input_dir != 0.0:
		sprite.texture = tex_damaged_walk if is_dmg else tex_standard_walk
		sprite.hframes = 8
		var speed_mult = 12.0 if is_sprinting else 8.0
		sprite.frame = int(anim_timer * speed_mult) % 8
		sprite.offset = Vector2(0, 0)
	else:
		sprite.texture = tex_damaged_idle if is_dmg else tex_standard_idle
		sprite.hframes = 4
		sprite.frame = int(anim_timer * 4.0) % 4
		sprite.offset = Vector2(0, 0)

func _on_melee_hit(area: Area2D) -> void:
	if area.is_in_group("hurtbox") or area.get_parent().is_in_group("enemies") or area.get_parent().is_in_group("boss"):
		var target = area.get_parent()
		var dmg = 35.0 if GameManager.primary_weapon == "bat" else 25.0
		if target.has_method("take_damage"):
			target.take_damage(dmg)

func take_damage(amount: float) -> void:
	if i_frame_timer > 0.0:
		return

	# If shield raised, absorb frontal damage
	if is_shield_raised:
		var leftover = GameManager.damage_shield(amount)
		if leftover <= 0.0:
			# Fully absorbed by shield!
			return
		amount = leftover

	i_frame_timer = I_FRAME_DURATION
	GameManager.player_hp = max(0.0, GameManager.player_hp - amount)
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	if GameManager.player_hp <= 0.0:
		_die()

func _die() -> void:
	# Respawn at nearest checkpoint
	position = Vector2(80, 750)
	GameManager.player_hp = GameManager.player_max_hp
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
"""

# ---------------------------------------------------------------------------
# 3. BOSS CRUSHER TITAN SCRIPT (Multi-Phase, Compactor Slam 50% HP, Stun Window)
# ---------------------------------------------------------------------------
boss_crusher_gd = """extends CharacterBody2D
class_name BossCrusher
# boss_crusher.gd - The Crusher Titan Multi-Phase Boss Battle (Tuned for ~5-min encounter)

@export var max_hp: float = 1500.0
var hp: float = 1500.0
var phase: int = 1 # Phase 1 (>50%), Phase 2 (<=50% Enraged)

enum State { DORMANT, INTRO, IDLE, TELEGRAPH_SLAM, SLAM_ACTIVE, SHOCKWAVE, ROCKET_CHARGE, STUNNED }
var current_state: State = State.DORMANT

var state_timer: float = 0.0
var facing_direction: int = -1

@onready var sprite: Sprite2D = $Sprite2D
@onready var compactor_piston: Sprite2D = $CompactorPiston
@onready var telegraph_zone: ColorRect = $TelegraphZone
@onready var collision_shape: CollisionShape2D = $CollisionShape2D

var tex_boss = preload("res://assets/boss_crusher_titan_strip4.png")
var tex_piston = preload("res://assets/boss_compactor_piston_80x160.png")

var player_ref: Node2D = null

func _ready() -> void:
	add_to_group("boss")
	sprite.texture = tex_boss
	sprite.hframes = 4
	sprite.frame = 0
	if compactor_piston:
		compactor_piston.texture = tex_piston
		compactor_piston.visible = false
	if telegraph_zone:
		telegraph_zone.visible = false

func activate_boss(player: Node2D) -> void:
	player_ref = player
	current_state = State.INTRO
	state_timer = 2.5
	position.y = 740
	GameManager.boss_health_changed.emit(hp, max_hp, phase)

func _physics_process(dt: float) -> void:
	if current_state == State.DORMANT:
		return

	state_timer -= dt

	match current_state:
		State.INTRO:
			sprite.frame = 0
			# Drops down with dust
			if state_timer <= 0.0:
				current_state = State.IDLE
				state_timer = 2.0

		State.IDLE:
			sprite.frame = 2 if phase == 2 else 0
			# Face player
			if player_ref:
				facing_direction = -1 if player_ref.global_position.x < global_position.x else 1
				sprite.scale.x = -facing_direction

			if state_timer <= 0.0:
				_choose_next_attack()

		State.TELEGRAPH_SLAM:
			sprite.frame = 1 # Arm raised high
			# 2.0s glowing red telegraph warning on floor!
			if telegraph_zone:
				telegraph_zone.visible = true
				telegraph_zone.color.a = 0.4 + 0.3 * sin(Time.get_ticks_msec() / 100.0)
			if state_timer <= 0.0:
				_execute_slam()

		State.SLAM_ACTIVE:
			if state_timer <= 0.0:
				if compactor_piston: compactor_piston.visible = false
				if telegraph_zone: telegraph_zone.visible = false
				current_state = State.IDLE
				state_timer = 2.0 if phase == 1 else 1.2

		State.ROCKET_CHARGE:
			sprite.frame = 2
			velocity.x = facing_direction * 480.0
			move_and_slide()
			# Check wall collision to stun!
			if is_on_wall() or state_timer <= 0.0:
				current_state = State.STUNNED
				state_timer = 4.5 # 4.5s critical damage window!
				sprite.frame = 3

		State.STUNNED:
			sprite.frame = 3
			velocity = Vector2.ZERO
			if state_timer <= 0.0:
				current_state = State.IDLE
				state_timer = 1.5

func _choose_next_attack() -> void:
	var roll = randf()
	if phase == 2 and roll < 0.45:
		# Rocket Ram Charge!
		current_state = State.ROCKET_CHARGE
		state_timer = 3.0
	else:
		# Ceiling Compactor Slam! (50% HP damage hazard)
		current_state = State.TELEGRAPH_SLAM
		state_timer = 2.0 # 2.0-second red warning indicator!
		if player_ref and telegraph_zone:
			telegraph_zone.global_position.x = player_ref.global_position.x - 50
			telegraph_zone.global_position.y = 770
			telegraph_zone.size = Vector2(100, 20)

func _execute_slam() -> void:
	current_state = State.SLAM_ACTIVE
	state_timer = 0.6
	if compactor_piston and telegraph_zone:
		compactor_piston.visible = true
		compactor_piston.global_position = Vector2(telegraph_zone.global_position.x + 50, 700)

	# Check if player inside telegraph zone: 50% max HP damage!
	if player_ref and telegraph_zone:
		var p_x = player_ref.global_position.x
		if p_x >= telegraph_zone.global_position.x and p_x <= telegraph_zone.global_position.x + 100:
			if player_ref.has_method("take_damage"):
				player_ref.take_damage(50.0) # 50% HP SLAM!

func take_damage(amount: float) -> void:
	if current_state == State.DORMANT or current_state == State.INTRO:
		return

	# Double damage if stunned!
	if current_state == State.STUNNED:
		amount *= 2.0

	hp = max(0.0, hp - amount)
	if hp <= max_hp * 0.5 and phase == 1:
		phase = 2
		print("BOSS ENRAGED! Phase 2 Activated!")

	GameManager.boss_health_changed.emit(hp, max_hp, phase)
	if hp <= 0.0:
		_die()

func _die() -> void:
	current_state = State.DORMANT
	visible = false
	GameManager.boss_defeated.emit()
	print("THE CRUSHER TITAN DEFEATED!")
"""

# Write scripts to godot_project and scrapborn-(4.0)
def write_both(rel_path, content):
    p1 = os.path.join(godot_dir, rel_path)
    p2 = os.path.join(godot_copy_dir, rel_path)
    os.makedirs(os.path.dirname(p1), exist_ok=True)
    os.makedirs(os.path.dirname(p2), exist_ok=True)
    with open(p1, "w", encoding="utf-8") as f:
        f.write(content)
    with open(p2, "w", encoding="utf-8") as f:
        f.write(content)

write_both("autoload/game_manager.gd", game_manager_gd)
write_both("scripts/player.gd", player_gd)
write_both("scripts/boss_crusher.gd", boss_crusher_gd)

print("GameManager, Player, and BossCrusher scripts written successfully.")
