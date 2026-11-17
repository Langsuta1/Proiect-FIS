extends CharacterBody2D
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
