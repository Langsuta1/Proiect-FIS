import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

print("Applying V8 Fixes across Godot and Demo...")

# ---------------------------------------------------------------------------
# 1. AUTOLOAD GAME MANAGER (Main Hand, Secondary Hand, Backpack 3x3, Stamina Regen)
# ---------------------------------------------------------------------------
game_manager_gd = """extends Node
# game_manager.gd - V8 Global Game Manager & Inventory Controller

signal player_health_changed(hp, max_hp)
signal player_energy_changed(ep, max_ep)
signal player_shield_changed(shield_hp, max_shield_hp)
signal inventory_updated()
signal weapon_swapped(primary_w, secondary_w)
signal boss_health_changed(hp, max_hp, phase)
signal boss_defeated()

# Player Chassis
var player_chassis: String = "standard"

# Health, Energy (Core Stamina), Shield
var player_hp: float = 100.0
var player_max_hp: float = 100.0
var player_ep: float = 100.0
var player_max_ep: float = 100.0
var ep_regen_rate: float = 25.0 # 25 EP/s Core Stamina regeneration!

var player_shield: float = 50.0
var player_max_shield: float = 50.0
var shield_regen_delay: float = 3.0
var shield_regen_timer: float = 0.0
var shield_regen_rate: float = 0.15 # 15% per second

# Inventory Data Structure (Matching User's Reference Layout):
# Left: Main Hand (1 slot), Secondary Hand (1 slot)
# Right: Backpack (3x3 = 9 slots)
var main_hand: Dictionary = {"id": "pan", "name": "Cyber Frying Pan", "type": "melee", "icon": "cyber_pan_32x32"}
var secondary_hand: Dictionary = {"id": "blaster", "name": "Laser Blaster", "type": "ranged", "icon": "laser_blaster_arm_32x32"}

var backpack: Array = [
	{"id": "bat", "name": "Reinforced Bat", "type": "melee", "icon": "metal_bat_32x32"},
	{"id": "flamethrower", "name": "Flamethrower", "type": "ranged", "icon": "flamethrower_32x32"},
	{"id": "frag", "name": "Frag Grenades", "type": "grenade", "icon": "grenade_frag_32x32", "count": 3},
	{"id": "emp", "name": "EMP Grenades", "type": "grenade", "icon": "grenade_emp_32x32", "count": 2},
	{"id": "cryo", "name": "Cryo Grenades", "type": "grenade", "icon": "grenade_cryo_32x32", "count": 2},
	{"id": "fire", "name": "Thermite Grenades", "type": "grenade", "icon": "grenade_fire_32x32", "count": 2},
	{"id": "chip", "name": "Overclock Chip", "type": "upgrade", "icon": "chip_nano_repair_32x32"},
	{}, # Empty slot 8
	{}  # Empty slot 9
]

# Legacy string getters for weapon IDs
var primary_weapon: String:
	get:
		return main_hand.get("id", "pan")
	set(val):
		main_hand["id"] = val

var secondary_weapon: String:
	get:
		return secondary_hand.get("id", "blaster")
	set(val):
		secondary_hand["id"] = val

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

# Item Swapping Logic between Main Hand, Secondary Hand, and 9 Backpack Slots
func swap_slots(loc_a: String, idx_a: int, loc_b: String, idx_b: int) -> void:
	var item_a: Dictionary = get_slot_item(loc_a, idx_a)
	var item_b: Dictionary = get_slot_item(loc_b, idx_b)

	set_slot_item(loc_a, idx_a, item_b)
	set_slot_item(loc_b, idx_b, item_a)

	inventory_updated.emit()
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func get_slot_item(loc: String, idx: int) -> Dictionary:
	if loc == "main":
		return main_hand.duplicate()
	elif loc == "sec":
		return secondary_hand.duplicate()
	elif loc == "backpack" and idx >= 0 and idx < backpack.size():
		return backpack[idx].duplicate()
	return {}

func set_slot_item(loc: String, idx: int, item: Dictionary) -> void:
	if loc == "main":
		main_hand = item.duplicate()
	elif loc == "sec":
		secondary_hand = item.duplicate()
	elif loc == "backpack" and idx >= 0 and idx < backpack.size():
		backpack[idx] = item.duplicate()

func swap_weapons() -> void:
	var temp = main_hand.duplicate()
	main_hand = secondary_hand.duplicate()
	secondary_hand = temp
	weapon_swapped.emit(primary_weapon, secondary_weapon)
	inventory_updated.emit()

func use_grenade() -> bool:
	for slot in backpack:
		if slot.get("id", "") == active_grenade and slot.get("count", 0) > 0:
			slot["count"] -= 1
			if slot["count"] <= 0:
				slot.clear()
			inventory_updated.emit()
			return true
	return false

func damage_shield(amount: float) -> float:
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
	# 1. CORE STAMINA (EP) REGENERATION (25 EP/s) - FIXES USER POINT 5!
	if player_ep < player_max_ep:
		player_ep = min(player_max_ep, player_ep + (ep_regen_rate * dt))
		player_energy_changed.emit(player_ep, player_max_ep)

	# 2. Shield Regeneration after 3.0s without damage
	if shield_regen_timer > 0.0:
		shield_regen_timer -= dt
	elif player_shield < player_max_shield:
		player_shield = min(player_max_shield, player_shield + (player_max_shield * shield_regen_rate * dt))
		player_shield_changed.emit(player_shield, player_max_shield)
"""

# ---------------------------------------------------------------------------
# 2. ENEMY SCRIPTS - FIXES CRASH ON PAN HIT (POINT 3)
# ---------------------------------------------------------------------------
enemy_crawler_gd = """extends CharacterBody2D
class_name EnemyCrawler
# enemy_crawler.gd - Scrap Crawler with safe default parameters to prevent crash

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

func take_damage(amount: float, knockback: float = 0.0) -> void:
	hp -= amount
	velocity.x = knockback * 140.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

enemy_drone_gd = """extends CharacterBody2D
class_name EnemyDrone
# enemy_drone.gd - Patrolling flying drone with safe default parameters to prevent crash

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

func take_damage(amount: float, knockback: float = 0.0) -> void:
	hp -= amount
	velocity.x = knockback * 160.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
"""

# ---------------------------------------------------------------------------
# 3. PLAYER SCRIPT - FIXES RANGED MELEE ANIMATION & PAN CRASH (POINTS 3 & 4)
# ---------------------------------------------------------------------------
player_gd = """extends CharacterBody2D
class_name Player
# player.gd - V8 Metroidvania Player Controller with distinct Melee/Ranged handling & Safe Damage calls

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
var current_attack_type: String = "" # "melee" or "ranged"
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

	# 10. Combat Attacks (NO MELEE ANIMATION FOR RANGED WEAPONS - FIXES POINT 4!)
	_handle_attacks(dt)

	# 11. Grenade [G]
	if Input.is_action_just_pressed("grenade"):
		_throw_grenade()

	# 12. Update Animations
	_update_animations(dt, input_dir)

	move_and_slide()

func _handle_attacks(dt: float) -> void:
	var weapon_item = GameManager.main_hand
	var weapon_id = weapon_item.get("id", "pan")
	var weapon_type = weapon_item.get("type", "melee")
	var is_dmg = (GameManager.player_chassis == "damaged")

	if attack_timer > 0.0:
		attack_timer -= dt
		var progress = clamp(1.0 - (attack_timer / attack_duration), 0.0, 0.99)
		var f_idx = int(progress * 4.0)
		var y_off = 6 if is_crouching else 0

		if current_attack_type == "melee":
			if weapon_id == "bat":
				sprite.texture = tex_damaged_attack_bat if is_dmg else tex_standard_attack_bat
				sprite.hframes = 4
				sprite.frame = f_idx
				sprite.offset.x = 12 if facing_direction == 1 else -12
				sprite.offset.y = -2 + y_off
			else: # pan
				sprite.texture = tex_damaged_attack_pan if is_dmg else tex_standard_attack_pan
				sprite.hframes = 4
				sprite.frame = f_idx
				sprite.offset.x = 8 if facing_direction == 1 else -8
				sprite.offset.y = y_off
		elif current_attack_type == "ranged":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = y_off

		if attack_timer <= 0.0:
			melee_hitbox.monitoring = false
			sprite.offset = Vector2(0, 0)
			current_attack_type = ""
		return

	# Primary Attack Trigger: Left Click or [X]
	if Input.is_action_just_pressed("attack_melee"):
		if weapon_type == "melee":
			# MELEE ATTACK: ONLY for melee weapons (Pan, Bat)
			current_attack_type = "melee"
			var is_bat = (weapon_id == "bat")
			attack_duration = 0.28 if is_bat else 0.22
			attack_timer = attack_duration

			var hit_y = 6 if is_crouching else 0
			melee_hitbox.monitoring = true
			melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)
		elif weapon_type == "ranged":
			# RANGED ATTACK: Ranged weapons shoot, NO MELEE SWING!
			_fire_ranged(weapon_id)

	# Secondary Attack Trigger: [Z] (fires secondary weapon)
	elif Input.is_action_pressed("attack_ranged"):
		var sec_item = GameManager.secondary_hand
		var sec_id = sec_item.get("id", "blaster")
		var sec_type = sec_item.get("type", "ranged")

		if sec_type == "ranged" and Input.is_action_just_pressed("attack_ranged"):
			_fire_ranged(sec_id)
		elif sec_type == "melee" and Input.is_action_just_pressed("attack_ranged"):
			# If secondary is melee, execute melee
			current_attack_type = "melee"
			var is_bat = (sec_id == "bat")
			attack_duration = 0.28 if is_bat else 0.22
			attack_timer = attack_duration
			var hit_y = 6 if is_crouching else 0
			melee_hitbox.monitoring = true
			melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)

func _fire_ranged(weapon_id: String) -> void:
	if GameManager.player_ep < 12.0:
		return

	GameManager.player_ep -= 12.0
	GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)

	current_attack_type = "ranged"
	attack_duration = 0.20
	attack_timer = 0.20

	var proj = preload("res://scenes/projectile_laser.tscn").instantiate()
	var hand_y = position.y + (6 if is_crouching else 0)
	proj.position = Vector2(position.x + 20 * facing_direction, hand_y)
	proj.direction = Vector2(facing_direction, 0)
	get_parent().add_child(proj)

func _throw_grenade() -> void:
	if GameManager.use_grenade():
		print("Player threw grenade:", GameManager.active_grenade)

func _try_grapple() -> void:
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
	var angular_accel = (-gravity / grapple_length) * cos(grapple_angle)
	grapple_angular_vel += angular_accel * dt
	grapple_angular_vel *= 0.995
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
		sprite.frame = 3
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

# SAFE MELEE HIT: PASSES BOTH (amount, knockback) TO PREVENT ENGINE CRASH!
func _on_melee_hit(area: Area2D) -> void:
	var target = area.get_parent()
	if target and target.has_method("take_damage"):
		var weapon_id = GameManager.main_hand.get("id", "pan")
		var dmg = 35.0 if weapon_id == "bat" else 25.0
		var kb = float(facing_direction)
		target.take_damage(dmg, kb)

func take_damage(amount: float, knockback_dir: float = 0.0) -> void:
	if i_frame_timer > 0.0:
		return

	if is_shield_raised:
		var leftover = GameManager.damage_shield(amount)
		if leftover <= 0.0:
			return
		amount = leftover

	i_frame_timer = I_FRAME_DURATION
	GameManager.player_hp = max(0.0, GameManager.player_hp - amount)
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)

	if knockback_dir != 0.0:
		velocity.x = knockback_dir * 120.0

	if GameManager.player_hp <= 0.0:
		_die()

func _die() -> void:
	position = Vector2(80, 750)
	GameManager.player_hp = GameManager.player_max_hp
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
"""

# ---------------------------------------------------------------------------
# 4. HUD SCRIPT & INVENTORY UI - MATCHES EXACT LAYOUT FROM IMAGE (POINT 1 & 2)
# Left: HOTBAR -> MAIN HAND (1 slot), SECONDARY HAND (1 slot)
# Right: BACKPACK -> 3x3 MATRIX (9 slots)
# Full item swapping between all slots!
# ---------------------------------------------------------------------------
hud_gd = """extends CanvasLayer
# hud.gd - V8 HUD & Inventory UI matching the user's reference image

@onready var hp_fill: ColorRect = $HUDPanel/VBox/HPContainer/HPTrack/HPFill
@onready var hp_label: Label = $HUDPanel/VBox/HPContainer/HPLabel
@onready var ep_fill: ColorRect = $HUDPanel/VBox/EPContainer/EPTrack/EPFill
@onready var ep_label: Label = $HUDPanel/VBox/EPContainer/EPLabel
@onready var shield_fill: ColorRect = $HUDPanel/VBox/ShieldContainer/ShieldTrack/ShieldFill
@onready var shield_label: Label = $HUDPanel/VBox/ShieldContainer/ShieldLabel

@onready var weapon_primary_lbl: Label = $WeaponCard/VBox/PrimaryLbl
@onready var weapon_secondary_lbl: Label = $WeaponCard/VBox/SecondaryLbl
@onready var grenade_lbl: Label = $WeaponCard/VBox/GrenadeLbl

@onready var boss_panel: Panel = $BossPanel
@onready var boss_bar: ProgressBar = $BossPanel/BossBar
@onready var boss_phase_lbl: Label = $BossPanel/PhaseLabel

# Inventory Modal
@onready var inv_modal: Control = $InventoryModal
@onready var slot_main_btn: Button = $InventoryModal/Panel/HBox/LeftCol/SlotMain
@onready var slot_sec_btn: Button = $InventoryModal/Panel/HBox/LeftCol/SlotSec
@onready var backpack_grid: GridContainer = $InventoryModal/Panel/HBox/RightCol/BackpackGrid

var selected_slot_loc: String = "" # "main", "sec", "backpack"
var selected_slot_idx: int = -1

func _ready() -> void:
	layer = 100
	if boss_panel: boss_panel.visible = false
	if inv_modal: inv_modal.visible = false

	GameManager.player_health_changed.connect(_on_hp_changed)
	GameManager.player_energy_changed.connect(_on_ep_changed)
	GameManager.player_shield_changed.connect(_on_shield_changed)
	GameManager.weapon_swapped.connect(_on_weapon_swapped)
	GameManager.inventory_updated.connect(_update_inventory_ui)
	GameManager.boss_health_changed.connect(_on_boss_health)
	GameManager.boss_defeated.connect(_on_boss_defeated)

	_update_hud_display()

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory"):
		_toggle_inventory()

func _toggle_inventory() -> void:
	if inv_modal:
		inv_modal.visible = not inv_modal.visible
		selected_slot_loc = ""
		selected_slot_idx = -1
		if inv_modal.visible:
			_update_inventory_ui()

func _update_hud_display() -> void:
	var hp_pct = clamp(GameManager.player_hp / GameManager.player_max_hp, 0.0, 1.0)
	var ep_pct = clamp(GameManager.player_ep / GameManager.player_max_ep, 0.0, 1.0)
	var shield_pct = clamp(GameManager.player_shield / GameManager.player_max_shield, 0.0, 1.0)

	if hp_fill: hp_fill.size.x = 180.0 * hp_pct
	if hp_label: hp_label.text = "ARMOR: " + str(int(GameManager.player_hp)) + " / " + str(int(GameManager.player_max_hp))

	if ep_fill: ep_fill.size.x = 180.0 * ep_pct
	if ep_label: ep_label.text = "CORE STAMINA: " + str(int(GameManager.player_ep)) + " / " + str(int(GameManager.player_max_ep))

	if shield_fill: shield_fill.size.x = 180.0 * shield_pct
	if shield_label: shield_label.text = "SHIELD: " + str(int(GameManager.player_shield)) + " / " + str(int(GameManager.player_max_shield))

	var m_name = GameManager.main_hand.get("name", "EMPTY")
	var s_name = GameManager.secondary_hand.get("name", "EMPTY")
	if weapon_primary_lbl: weapon_primary_lbl.text = "MAIN HAND: " + m_name.to_upper()
	if weapon_secondary_lbl: weapon_secondary_lbl.text = "SECONDARY: " + s_name.to_upper()
	if grenade_lbl: grenade_lbl.text = "GRENADE: " + GameManager.active_grenade.to_upper()

func _on_hp_changed(_hp: float, _mx: float) -> void:
	_update_hud_display()

func _on_ep_changed(_ep: float, _mx: float) -> void:
	_update_hud_display()

func _on_shield_changed(_sh: float, _mx: float) -> void:
	_update_hud_display()

func _on_weapon_swapped(_p: String, _s: String) -> void:
	_update_hud_display()

# RENDER & INTERACT WITH INVENTORY (ITEM SWAPPING - POINT 2)
func _update_inventory_ui() -> void:
	if not inv_modal or not inv_modal.visible:
		return

	# Update Main Hand Slot
	var m_item = GameManager.main_hand
	slot_main_btn.text = m_item.get("name", "EMPTY")
	_style_slot_btn(slot_main_btn, selected_slot_loc == "main")

	# Update Secondary Hand Slot
	var s_item = GameManager.secondary_hand
	slot_sec_btn.text = s_item.get("name", "EMPTY")
	_style_slot_btn(slot_sec_btn, selected_slot_loc == "sec")

	# Update Backpack 3x3 Grid
	if backpack_grid:
		for child in backpack_grid.get_children():
			child.queue_free()

		for i in range(GameManager.backpack.size()):
			var slot_data = GameManager.backpack[i]
			var btn = Button.new()
			btn.custom_minimum_size = Vector2(80, 80)
			var item_name = slot_data.get("name", "EMPTY")
			var count_txt = (" x" + str(slot_data["count"])) if slot_data.has("count") else ""
			btn.text = item_name + count_txt
			_style_slot_btn(btn, selected_slot_loc == "backpack" and selected_slot_idx == i)

			var slot_idx = i
			btn.pressed.connect(func(): _on_slot_clicked("backpack", slot_idx))
			backpack_grid.add_child(btn)

func _style_slot_btn(btn: Button, is_selected: bool) -> void:
	if is_selected:
		btn.modulate = Color(1.0, 0.8, 0.2) # Golden active selection
	else:
		btn.modulate = Color(1.0, 1.0, 1.0)

func _on_main_slot_pressed() -> void:
	_on_slot_clicked("main", 0)

func _on_sec_slot_pressed() -> void:
	_on_slot_clicked("sec", 0)

# SWAP SYSTEM: Click slot A to select, Click slot B to swap!
func _on_slot_clicked(loc: String, idx: int) -> void:
	if selected_slot_loc == "":
		# Select first slot
		selected_slot_loc = loc
		selected_slot_idx = idx
		_update_inventory_ui()
	else:
		# Second slot clicked: SWAP!
		if selected_slot_loc == loc and selected_slot_idx == idx:
			# Deselect if clicked same slot
			selected_slot_loc = ""
			selected_slot_idx = -1
		else:
			GameManager.swap_slots(selected_slot_loc, selected_slot_idx, loc, idx)
			selected_slot_loc = ""
			selected_slot_idx = -1
		_update_inventory_ui()

func _on_boss_health(curr: float, mx: float, phase: int) -> void:
	if boss_panel:
		boss_panel.visible = true
		boss_bar.max_value = mx
		boss_bar.value = curr
		if boss_phase_lbl:
			boss_phase_lbl.text = "PHASE 2 - ENRAGED CRUSHER" if phase == 2 else "PHASE 1 - COMPACTOR OVERLOAD"

func _on_boss_defeated() -> void:
	if boss_panel:
		boss_panel.visible = false
"""

# Write script updates
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
write_both("scripts/enemy_crawler.gd", enemy_crawler_gd)
write_both("scripts/enemy_drone.gd", enemy_drone_gd)
write_both("scripts/player.gd", player_gd)
write_both("scripts/hud.gd", hud_gd)

print("GameManager, Enemies, Player, and HUD scripts updated.")
