extends CharacterBody2D
class_name Player
# player.gd - V9 Metroidvania Player Controller with Low Ceiling Crouch Lock, Item Pickup & Safe Damage

@export var walk_speed: float = 145.0
@export var sprint_speed: float = 230.0
@export var crouch_speed: float = 60.0
@export var jump_velocity: float = -380.0
@export var double_jump_velocity: float = -330.0
@export var dash_speed: float = 420.0
@export var dash_duration: float = 0.22
@export var gravity: float = 980.0
@export var wall_slide_speed: float = 75.0
@export var wall_jump_h_force: float = 270.0
@export var wall_jump_v_velocity: float = -370.0
@export var wall_slide_stamina_drain: float = 10.0
@export var wall_jump_stamina_cost: float = 12.0
@export var safe_fall_height: float = 175.0
@export var fall_damage_per_pixel: float = 0.14

# Strict I-Frames
var i_frame_timer: float = 0.0
const I_FRAME_DURATION: float = 1.2

# Movement states
var is_sprinting: bool = false
var is_crouching: bool = false
var is_dashing: bool = false
var dash_timer: float = 0.0
var dash_cooldown: float = 0.0
var dash_ghost_timer: float = 0.0
const DASH_GHOST_INTERVAL: float = 0.038
var can_double_jump: bool = true
var has_double_jumped: bool = false
var is_wall_sliding: bool = false
var wall_direction: int = 0
var wall_jump_lock_timer: float = 0.0
var wall_coyote_timer: float = 0.0

# Input Overwrite Buffers (allows pressing Space while holding W, A while holding D, etc.)
var _queued_jump_press: bool = false
var _last_horizontal_dir: float = 0.0

# Energy Shield
var is_shield_raised: bool = false

# Grappling Hook (True Cartesian Velocity-Projection Pendulum - Zero Teleportation)
var is_grappling: bool = false
var grapple_anchor: Vector2 = Vector2.ZERO
var grapple_length: float = 0.0
var grapple_angle: float = 0.0
var grapple_angular_vel: float = 0.0
var current_grapple_ring: Node2D = null
var closest_available_ring: Node2D = null
const GRAPPLE_RANGE: float = 330.0
const GRAPPLE_IDEAL_MAX_LEN: float = 185.0
const GRAPPLE_MIN_LEN: float = 75.0

# Grenade Slingshot Aiming
var is_aiming_grenade: bool = false
var grenade_launch_velocity: Vector2 = Vector2.ZERO
var grenade_trajectory_points: Array[Vector2] = []

# Grenade Status Effects on Player (Cryo Freeze, EMP Overload, Fire Burn, Frag Blast)
var freeze_timer: float = 0.0
var chill_timer: float = 0.0
var emp_timer: float = 0.0
var burn_timer: float = 0.0
var burn_tick_timer: float = 0.0
var blast_stun_timer: float = 0.0
var heal_flash_timer: float = 0.0
var fall_flash_timer: float = 0.0
var last_fall_damage: int = 0
var _is_tracking_fall: bool = false
var _fall_start_y: float = 0.0
var camera_shake_timer: float = 0.0
var camera_shake_intensity: float = 0.0

# Checkpoints & Respawn
var respawn_position: Vector2 = Vector2(80, 750)
const SWING_CHECKPOINT: Vector2 = Vector2(2720, 750)

# Combat
var attack_timer: float = 0.0
var attack_duration: float = 0.24
var current_attack_type: String = "" # "melee" or "ranged"
var facing_direction: int = 1
var is_firing_flamethrower: bool = false
var flame_tick_timer: float = 0.0

# Node references
@onready var sprite: Sprite2D = $Sprite2D
@onready var weapon_sprite: Sprite2D = $WeaponSprite
@onready var shield_sprite: Sprite2D = $ShieldSprite
@onready var melee_hitbox: Area2D = $MeleeHitbox
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var dash_particles: CPUParticles2D = get_node_or_null("DashParticles")
@onready var cam: Camera2D = get_node_or_null("Camera2D")

const DashGhostClass = preload("res://scripts/dash_ghost.gd")
const AirJumpEffectScene = preload("res://scenes/air_jump_effect.tscn")

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
var tex_jump = preload("res://assets/robot_jump_strip3.png")
var tex_dash = preload("res://assets/robot_dash_strip2.png")
var tex_standard_wallslide = preload("res://assets/robot_standard_wallslide_strip2.png")
var tex_damaged_wallslide = preload("res://assets/robot_damaged_wallslide_strip2.png")

var anim_timer: float = 0.0
var sprite_scale_mod: Vector2 = Vector2.ONE

func _ready() -> void:
	add_to_group("player")
	if weapon_sprite: weapon_sprite.visible = false
	if shield_sprite:
		shield_sprite.visible = false
		shield_sprite.texture = tex_shield
	if melee_hitbox:
		melee_hitbox.monitoring = false
		melee_hitbox.area_entered.connect(_on_melee_hit)
	if not GameManager.pending_load_data.is_empty():
		var loaded_pos = GameManager.pending_load_data.get("player_pos", global_position)
		var loaded_respawn = GameManager.pending_load_data.get("respawn_pos", respawn_position)
		if loaded_pos is Vector2:
			global_position = Vector2(max(loaded_pos.x, 80.0), loaded_pos.y)
		if loaded_respawn is Vector2:
			respawn_position = Vector2(max(loaded_respawn.x, 80.0), loaded_respawn.y)
		GameManager.pending_load_data.clear()
	if cam:
		cam.make_current()
		cam.reset_smoothing()
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
	GameManager.player_shield_changed.emit(GameManager.player_shield, GameManager.player_max_shield)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("jump", false):
		_queued_jump_press = true
	if event.is_action_pressed("move_left", false):
		_last_horizontal_dir = -1.0
	elif event.is_action_pressed("move_right", false):
		_last_horizontal_dir = 1.0

func _get_horizontal_input() -> float:
	var left_held: bool = Input.is_action_pressed("move_left")
	var right_held: bool = Input.is_action_pressed("move_right")
	if left_held and right_held:
		return _last_horizontal_dir
	elif left_held:
		return -1.0
	elif right_held:
		return 1.0
	return 0.0

func _physics_process(dt: float) -> void:
	var jump_just_pressed: bool = _queued_jump_press or Input.is_action_just_pressed("jump")
	_queued_jump_press = false
	# Update checkpoint when approaching swing section
	if global_position.x >= 2650.0 and respawn_position.x < 2650.0:
		respawn_position = SWING_CHECKPOINT
		GameManager.save_game(GameManager.current_save_slot, "Prăpastia de Acid")

	# Fall death safety check: strictly if fallen into the toxic green acid chasm or fell out of the world
	if global_position.y > 890.0 and global_position.x > 2810.0 and global_position.x < 3590.0:
		die_in_hazard("acid")
		return
	elif global_position.y > 1050.0:
		die_in_hazard("void")
		return

	# 0. Camera Shake & Closest Grapple Ring Detection
	if camera_shake_timer > 0.0:
		camera_shake_timer -= dt
		if cam:
			cam.offset = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)) * camera_shake_intensity * clamp(camera_shake_timer * 4.0, 0.0, 1.0)
	elif cam and cam.offset != Vector2.ZERO:
		cam.offset = Vector2.ZERO

	closest_available_ring = _find_closest_grapple_ring(is_grappling)

	# 1. Update I-Frames, Movement Timers & Grenade Status Effects
	if i_frame_timer > 0.0:
		i_frame_timer -= dt

	if wall_jump_lock_timer > 0.0:
		wall_jump_lock_timer -= dt
	if wall_coyote_timer > 0.0:
		wall_coyote_timer -= dt
	if blast_stun_timer > 0.0:
		blast_stun_timer -= dt
	if chill_timer > 0.0:
		chill_timer -= dt
	if emp_timer > 0.0:
		emp_timer -= dt
		queue_redraw()
	if heal_flash_timer > 0.0:
		heal_flash_timer -= dt
		queue_redraw()
	if fall_flash_timer > 0.0:
		fall_flash_timer -= dt
		queue_redraw()

	# Thermite / Fire Burning DoT
	if burn_timer > 0.0:
		burn_timer -= dt
		burn_tick_timer += dt
		if burn_tick_timer >= 0.5:
			burn_tick_timer = 0.0
			take_grenade_damage(5.0)
		queue_redraw()

	# Sprite tinting for Status Effects & I-Frames
	var base_tint = Color(1.0, 1.0, 1.0, 1.0)
	if freeze_timer > 0.0:
		base_tint = Color(0.35, 0.92, 1.65, 1.0)
	elif chill_timer > 0.0:
		base_tint = Color(0.55, 0.9, 1.35, 1.0)
	elif emp_timer > 0.0:
		base_tint = Color(0.5, 0.9, 1.5, 1.0) if fmod(Time.get_ticks_msec() / 45.0, 2.0) > 1.0 else Color(1.1, 1.1, 0.5, 1.0)
	elif burn_timer > 0.0:
		base_tint = Color(1.4, 0.65, 0.35, 1.0)
	if i_frame_timer > 0.0 and freeze_timer <= 0.0:
		base_tint.a = 0.35 if fmod(Time.get_ticks_msec() / 70.0, 2.0) > 1.0 else 1.0
	sprite.modulate = base_tint

	# CRYO FREEZE SOLID LOCK: While frozen in an ice block, player is immobilized!
	if freeze_timer > 0.0:
		freeze_timer -= dt
		if is_grappling:
			_release_grapple()
		is_dashing = false
		is_firing_flamethrower = false
		is_aiming_grenade = false
		if shield_sprite:
			shield_sprite.visible = false
		if not is_on_floor():
			velocity.y += gravity * dt
		velocity.x = move_toward(velocity.x, 0.0, 900.0 * dt)
		move_and_slide()
		queue_redraw()
		return

	# 2. Quick-Swap Weapons [Q] & Grenade Type Selection [T / 1-4]
	if Input.is_action_just_pressed("switch_weapon"):
		GameManager.swap_weapons()
	if Input.is_action_just_pressed("cycle_grenade"):
		GameManager.cycle_active_grenade()
	elif Input.is_action_just_pressed("grenade_1"):
		GameManager.set_active_grenade("frag")
	elif Input.is_action_just_pressed("grenade_2"):
		GameManager.set_active_grenade("emp")
	elif Input.is_action_just_pressed("grenade_3"):
		GameManager.set_active_grenade("cryo")
	elif Input.is_action_just_pressed("grenade_4"):
		GameManager.set_active_grenade("fire")
	if Input.is_action_just_pressed("heal"):
		_try_use_bandage()

	# 3. Handle [E] (Pick Up nearby dropped item or Grappling Hook)
	if Input.is_action_just_pressed("interact"):
		var items = get_tree().get_nodes_in_group("dropped_items")
		var picked = false
		for it in items:
			if global_position.distance_to(it.global_position) < 65.0:
				it._pickup()
				picked = true
				break
		if not picked:
			if is_grappling:
				# Pressing [E] while grappling cleanly releases the hook!
				_release_grapple()
			else:
				_try_grapple()

	if is_grappling:
		_reset_fall_tracking()
		_process_grapple_physics(dt, jump_just_pressed)
		move_and_slide()
		return

	# 4. Energy Shield [F] / [Right Click] (Disabled during EMP malfunction!)
	is_shield_raised = Input.is_action_pressed("shield") and GameManager.player_shield > 0.0 and emp_timer <= 0.0
	if shield_sprite:
		shield_sprite.visible = is_shield_raised
		shield_sprite.position = Vector2(16 * facing_direction, 0)
		shield_sprite.scale.x = facing_direction

	# 5. Handle Dash [C] (Disabled during EMP malfunction!)
	if dash_cooldown > 0.0:
		dash_cooldown -= dt
	if is_dashing:
		_reset_fall_tracking()
		dash_timer -= dt
		velocity.y = 0.0
		velocity.x = dash_speed * facing_direction

		# Dynamic Dash Animation & Orientation
		sprite.texture = tex_dash
		sprite.hframes = 2
		sprite.frame = 1 if dash_timer < (dash_duration * 0.5) else 0
		sprite.scale.x = facing_direction
		sprite.offset = Vector2(0, 0)

		# Spawn ghost trail while dashing
		dash_ghost_timer -= dt
		if dash_ghost_timer <= 0.0:
			dash_ghost_timer = DASH_GHOST_INTERVAL
			_spawn_dash_ghost()

		move_and_slide()
		if dash_timer <= 0.0:
			is_dashing = false
			dash_cooldown = 0.45
			velocity.x = 0.0
			if dash_particles:
				dash_particles.emitting = false
		return

	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and not is_dashing and emp_timer <= 0.0 and GameManager.consume_ep(15.0):
		var dash_input_dir: float = _get_horizontal_input()
		if dash_input_dir != 0.0:
			facing_direction = 1 if dash_input_dir > 0.0 else -1
		is_dashing = true
		dash_timer = dash_duration
		dash_ghost_timer = DASH_GHOST_INTERVAL
		velocity = Vector2(dash_speed * facing_direction, 0.0)

		sprite.texture = tex_dash
		sprite.hframes = 2
		sprite.frame = 0
		sprite.scale.x = facing_direction
		sprite.offset = Vector2(0, 0)

		if dash_particles:
			dash_particles.direction = Vector2(-facing_direction, 0)
			dash_particles.emitting = true

		_spawn_dash_ghost()
		return

	# 6. Handle Crouch [S] / [DOWN] with Low Ceiling Lock
	var wants_crouch = Input.is_action_pressed("crouch") and is_on_floor()
	var can_stand = true
	if is_crouching and not wants_crouch:
		# Multi-ray ceiling clearance check across full body width (-9 to +9)
		# Prevents getting stuck or clipped on the exit pixel!
		var space_state = get_world_2d().direct_space_state
		var check_x_offsets = [-9.0, -4.5, 0.0, 4.5, 9.0]
		for ox in check_x_offsets:
			var query = PhysicsRayQueryParameters2D.create(
				global_position + Vector2(ox, 0),
				global_position + Vector2(ox, -20.0)
			)
			query.exclude = [self]
			query.collision_mask = 1
			var res = space_state.intersect_ray(query)
			if not res.is_empty():
				can_stand = false
				break

	is_crouching = (wants_crouch or not can_stand)

	if collision_shape:
		var rect = collision_shape.shape as RectangleShape2D
		if rect:
			if is_crouching:
				rect.size = Vector2(18, 16)
				collision_shape.position = Vector2(0, 6)
			else:
				rect.size = Vector2(18, 28)
				collision_shape.position = Vector2(0, 0)

	# 7. Gravity & Wall Slide Friction
	if not is_on_floor():
		velocity.y += gravity * dt
	else:
		can_double_jump = true
		has_double_jumped = false

	# Detect Wall Slide (ONLY on walls tagged climbable = true!)
	var on_climbable_wall: bool = false
	var wall_dir: int = 0
	if is_on_wall() and not is_on_floor():
		for i in range(get_slide_collision_count()):
			var col: KinematicCollision2D = get_slide_collision(i)
			var n: Vector2 = col.get_normal()
			if abs(n.x) > 0.5 and _is_collider_climbable(col.get_collider()):
				on_climbable_wall = true
				wall_dir = -1 if n.x > 0.5 else 1
				break

	var input_dir: float = _get_horizontal_input()
	var pushing_wall: bool = (on_climbable_wall and input_dir != 0.0 and signf(input_dir) == float(wall_dir))

	var was_wall_sliding: bool = is_wall_sliding
	if on_climbable_wall and pushing_wall and not is_crouching and not is_dashing and not is_grappling and GameManager.player_ep > 0.0:
		wall_direction = wall_dir
		wall_coyote_timer = 0.12
		if velocity.y > 0.0:
			is_wall_sliding = true
			_reset_fall_tracking()
			velocity.y = min(velocity.y, wall_slide_speed)
			can_double_jump = true
			has_double_jumped = false
			GameManager.pause_ep_regen(0.6)
			GameManager.player_ep = max(0.0, GameManager.player_ep - wall_slide_stamina_drain * dt)
			GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
		else:
			is_wall_sliding = false
	else:
		is_wall_sliding = false
	if was_wall_sliding != is_wall_sliding:
		queue_redraw()

	# 8. Jump, Wall Jump & Double Jump
	var speed_debuff_mult: float = 1.0
	if chill_timer > 0.0:
		speed_debuff_mult *= 0.55
	if emp_timer > 0.0:
		speed_debuff_mult *= 0.7

	if jump_just_pressed:
		if (is_wall_sliding or wall_coyote_timer > 0.0) and not is_on_floor():
			# Wall Jump (consumes stamina to climb walls!)
			if GameManager.consume_ep(wall_jump_stamina_cost):
				velocity.x = -wall_direction * wall_jump_h_force
				velocity.y = wall_jump_v_velocity
				facing_direction = -wall_direction
				sprite.scale.x = facing_direction
				wall_jump_lock_timer = 0.16
				is_wall_sliding = false
				wall_coyote_timer = 0.0
				can_double_jump = true
				has_double_jumped = false
				queue_redraw()
		elif is_on_floor():
			# Can only jump if not stuck under a low ceiling!
			if can_stand:
				velocity.y = jump_velocity * (0.82 if chill_timer > 0.0 else 1.0)
		elif can_double_jump and not has_double_jumped and emp_timer <= 0.0 and GameManager.consume_ep(10.0):
			velocity.y = double_jump_velocity
			has_double_jumped = true
			_trigger_air_jump_effect()

	# 9. Horizontal Movement
	if blast_stun_timer > 0.0:
		velocity.x = move_toward(velocity.x, input_dir * walk_speed, 320.0 * dt)
	elif wall_jump_lock_timer > 0.0:
		velocity.x = move_toward(velocity.x, input_dir * walk_speed, 600.0 * dt)
	else:
		is_sprinting = Input.is_action_pressed("sprint") and input_dir != 0.0 and not is_crouching and chill_timer <= 0.0

		var target_speed = walk_speed
		if is_crouching:
			target_speed = crouch_speed
		elif is_sprinting:
			target_speed = sprint_speed
		target_speed *= speed_debuff_mult

		if input_dir != 0.0:
			velocity.x = input_dir * target_speed
			facing_direction = 1 if input_dir > 0 else -1
			sprite.scale.x = facing_direction
		else:
			velocity.x = move_toward(velocity.x, 0.0, 800.0 * dt)

	# 10. Combat Attacks (Distinct Melee and Ranged handling)
	_handle_attacks(dt)

	# 11. Grenade [G] (Angry-Birds Slingshot Drag-Aiming & Trajectory)
	_handle_grenade_aiming(dt)

	# 12. Update Animations
	_update_animations(dt, input_dir)

	# 13. Fall Distance Tracking & Landing Impact Check
	var was_on_floor_before_slide: bool = is_on_floor()
	if not was_on_floor_before_slide:
		if velocity.y <= 0.0:
			_reset_fall_tracking()
		elif not _is_tracking_fall:
			_is_tracking_fall = true
			_fall_start_y = global_position.y

	move_and_slide()

	if is_on_floor():
		if not was_on_floor_before_slide and _is_tracking_fall:
			var fall_dist: float = global_position.y - _fall_start_y
			if fall_dist > safe_fall_height:
				var base_dmg: float = max(5.0, (fall_dist - safe_fall_height) * fall_damage_per_pixel)
				var final_dmg: float = GameManager.get_scaled_fall_damage(base_dmg)
				_apply_fall_damage(final_dmg)
		_reset_fall_tracking()

func _handle_attacks(dt: float) -> void:
	var weapon_item = GameManager.main_hand
	var weapon_id = weapon_item.get("id", "pan")
	var weapon_type = weapon_item.get("type", "melee")
	var sec_item = GameManager.secondary_hand
	var sec_id = sec_item.get("id", "blaster")
	var sec_type = sec_item.get("type", "ranged")
	var is_dmg = (GameManager.player_chassis == "damaged")

	# 1. Flamethrower Continuous Firing (Main hand or Secondary hand)
	var firing_flame_main = (weapon_id == "flamethrower" and Input.is_action_pressed("attack_melee"))
	var firing_flame_sec = (sec_id == "flamethrower" and Input.is_action_pressed("attack_ranged"))

	if (firing_flame_main or firing_flame_sec) and GameManager.player_ep > 0.0 and emp_timer <= 0.0:
		is_firing_flamethrower = true
		GameManager.pause_ep_regen(1.0) # Stamina regen paused while firing!
		var drain = 28.0 * dt
		GameManager.player_ep = max(0.0, GameManager.player_ep - drain)
		GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)

		var mouse_pos = get_global_mouse_position()
		if mouse_pos.x < global_position.x - 4.0:
			facing_direction = -1
		elif mouse_pos.x > global_position.x + 4.0:
			facing_direction = 1

		sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
		sprite.hframes = 4
		sprite.frame = (int(Time.get_ticks_msec() / 70) % 4)
		sprite.offset.x = 4 if facing_direction == 1 else -4
		if is_crouching:
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x * 1.06, sprite_scale_mod.y * 0.64)
			sprite.offset.y = 9.0
		else:
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
			sprite.offset.y = 0.0

		flame_tick_timer -= dt
		if flame_tick_timer <= 0.0:
			flame_tick_timer = 0.065
			_spawn_flame_puff()
		return
	else:
		if is_firing_flamethrower:
			is_firing_flamethrower = false
			GameManager.pause_ep_regen(1.0) # 1 full second cooldown AFTER releasing trigger!
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
			sprite.offset = Vector2(0, 0)

	if attack_timer > 0.0:
		attack_timer -= dt
		var progress = clamp(1.0 - (attack_timer / attack_duration), 0.0, 0.99)
		var f_idx = int(progress * 4.0)
		if is_crouching:
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x * 1.06, sprite_scale_mod.y * 0.64)
		else:
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)

		if current_attack_type == "melee":
			if weapon_id == "bat":
				sprite.texture = tex_damaged_attack_bat if is_dmg else tex_standard_attack_bat
				sprite.hframes = 4
				sprite.frame = f_idx
				sprite.offset.x = 12 if facing_direction == 1 else -12
				sprite.offset.y = 7.0 if is_crouching else -2.0
			else: # pan
				sprite.texture = tex_damaged_attack_pan if is_dmg else tex_standard_attack_pan
				sprite.hframes = 4
				sprite.frame = f_idx
				sprite.offset.x = 8 if facing_direction == 1 else -8
				sprite.offset.y = 9.0 if is_crouching else 0.0
		elif current_attack_type == "ranged":
			sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
			sprite.hframes = 4
			sprite.frame = f_idx
			sprite.offset.x = 4 if facing_direction == 1 else -4
			sprite.offset.y = 9.0 if is_crouching else 0.0

		if attack_timer <= 0.0:
			melee_hitbox.monitoring = false
			sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
			sprite.offset = Vector2(0, 0)
			current_attack_type = ""
		return

	# Primary Attack: Left Click or [X]
	if Input.is_action_just_pressed("attack_melee"):
		if weapon_type == "melee":
			current_attack_type = "melee"
			var is_bat = (weapon_id == "bat")
			attack_duration = 0.28 if is_bat else 0.22
			attack_timer = attack_duration

			var hit_y = 6 if is_crouching else 0
			melee_hitbox.monitoring = true
			melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)
		elif weapon_type == "ranged":
			_fire_ranged(weapon_id)
		elif weapon_type == "consumable":
			_try_use_bandage()
		elif sec_type == "ranged":
			_fire_ranged(sec_id)

	# Secondary Attack: [Z]
	elif Input.is_action_just_pressed("attack_ranged"):
		if sec_type == "ranged":
			_fire_ranged(sec_id)
		elif sec_type == "consumable":
			_try_use_bandage()
		elif sec_type == "melee":
			current_attack_type = "melee"
			var is_bat = (sec_id == "bat")
			attack_duration = 0.28 if is_bat else 0.22
			attack_timer = attack_duration
			var hit_y = 6 if is_crouching else 0
			melee_hitbox.monitoring = true
			melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)

func _fire_ranged(weapon_id: String) -> void:
	if emp_timer > 0.0:
		return
	var mouse_pos = get_global_mouse_position()
	if mouse_pos.x < global_position.x - 4.0:
		facing_direction = -1
	elif mouse_pos.x > global_position.x + 4.0:
		facing_direction = 1
	sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)

	if weapon_id == "flamethrower":
		if GameManager.consume_ep(8.0):
			_spawn_flame_puff()
		return

	# Default: Laser Blaster
	if not GameManager.consume_ep(12.0):
		return

	current_attack_type = "ranged"
	attack_duration = 0.20
	attack_timer = 0.20

	var hand_pos = global_position + Vector2(18 * facing_direction, 6 if is_crouching else -2)
	var aim_dir = (mouse_pos - hand_pos).normalized()
	if aim_dir.length_squared() == 0:
		aim_dir = Vector2(facing_direction, 0)

	var parent_node = get_parent()
	if parent_node:
		var proj = preload("res://scenes/projectile_laser.tscn").instantiate()
		parent_node.add_child(proj)
		proj.global_position = hand_pos
		proj.direction = aim_dir
		proj.rotation = aim_dir.angle()

func _spawn_flame_puff() -> void:
	var flame_scene = load("res://scenes/projectile_flame.tscn")
	if not flame_scene:
		return
	var mouse_pos = get_global_mouse_position()
	if mouse_pos.x < global_position.x - 4.0:
		facing_direction = -1
	elif mouse_pos.x > global_position.x + 4.0:
		facing_direction = 1
	sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)

	var spawn_pos = global_position + Vector2(20 * facing_direction, 6 if is_crouching else -2)
	var aim_dir = (mouse_pos - spawn_pos).normalized()
	if aim_dir.length_squared() == 0:
		aim_dir = Vector2(facing_direction, 0)

	aim_dir = aim_dir.rotated(randf_range(-0.14, 0.14))

	var parent_node = get_parent()
	if parent_node:
		var flame = flame_scene.instantiate()
		parent_node.add_child(flame)
		flame.global_position = spawn_pos + aim_dir * 6.0
		flame.direction = aim_dir
		flame.rotation = aim_dir.angle()

func _handle_grenade_aiming(_dt: float) -> void:
	if Input.is_action_just_pressed("grenade"):
		is_aiming_grenade = true

	if is_aiming_grenade:
		if Input.is_action_pressed("grenade"):
			var anchor_pt = global_position + Vector2(0, -6)
			var mouse_pt = get_global_mouse_position()
			var pull_vec = anchor_pt - mouse_pt # Angry-Birds style pull-back
			var pull_dist = clamp(pull_vec.length(), 15.0, 190.0)
			var launch_dir = pull_vec.normalized()
			var launch_speed = pull_dist * 4.2
			grenade_launch_velocity = launch_dir * launch_speed

			# Calculate trajectory points with gravity simulation & raycast impact
			grenade_trajectory_points.clear()
			var cur_pt = anchor_pt
			var sim_vel = grenade_launch_velocity
			var sim_dt = 0.04
			var space_state = get_world_2d().direct_space_state

			for _i in range(25):
				var next_pt = cur_pt + sim_vel * sim_dt
				sim_vel.y += 780.0 * sim_dt
				var ray = PhysicsRayQueryParameters2D.create(cur_pt, next_pt)
				ray.exclude = [self]
				ray.collision_mask = 1
				var hit = space_state.intersect_ray(ray)
				if not hit.is_empty():
					grenade_trajectory_points.append(hit.position)
					break
				grenade_trajectory_points.append(next_pt)
				cur_pt = next_pt

			queue_redraw()

		elif Input.is_action_just_released("grenade"):
			is_aiming_grenade = false
			queue_redraw()
			_fire_grenade_slingshot()

func _fire_grenade_slingshot() -> void:
	if GameManager.use_grenade():
		var grenade_scene = load("res://scenes/projectile_grenade.tscn")
		if grenade_scene:
			var inst = grenade_scene.instantiate()
			inst.global_position = global_position + Vector2(facing_direction * 14.0, -8.0)
			inst.velocity = grenade_launch_velocity
			inst.grenade_type = GameManager.active_grenade
			get_parent().add_child(inst)
			print("Launched slingshot grenade:", GameManager.active_grenade, "vel:", grenade_launch_velocity)

func _draw() -> void:
	# 1. Grappling Hook Cable
	if is_grappling:
		var local_anchor = to_local(grapple_anchor)
		var hand_offset = Vector2(8 * facing_direction, 2 if is_crouching else -2)

		# Glowing outer halo
		draw_line(hand_offset, local_anchor, Color(0.0, 0.45, 0.85, 0.55), 5.0)
		# Main glowing cyan cable
		draw_line(hand_offset, local_anchor, Color(0.22, 0.85, 1.0, 1.0), 2.5)
		# Inner white-hot energy core
		draw_line(hand_offset, local_anchor, Color(0.92, 1.0, 1.0, 0.95), 1.0)

		# Magnetic clamp / hook at ring
		draw_circle(local_anchor, 6.0, Color(0.96, 0.62, 0.04, 1.0))
		draw_circle(local_anchor, 4.0, Color(0.22, 0.85, 1.0, 1.0))
		draw_circle(local_anchor, 2.0, Color(1.0, 1.0, 1.0, 1.0))

	# 2. Slingshot Aiming & Ballistic Trajectory Arc (Angry-Birds style)
	if is_aiming_grenade:
		var anchor_pt = to_local(global_position + Vector2(0, -6))
		var mouse_pt = to_local(get_global_mouse_position())

		# Slingshot elastic band
		draw_line(anchor_pt, mouse_pt, Color(0.96, 0.62, 0.04, 0.85), 2.5)
		draw_circle(mouse_pt, 4.5, Color(1.0, 0.3, 0.2, 0.95))

		# Ballistic trajectory dots
		for i in range(grenade_trajectory_points.size()):
			var pt = to_local(grenade_trajectory_points[i])
			var alpha = clamp(1.0 - (float(i) / 28.0), 0.35, 1.0)
			draw_circle(pt, 3.2, Color(1.0, 0.75, 0.2, alpha * 0.85))
			draw_circle(pt, 1.6, Color(1.0, 1.0, 1.0, alpha))

		# Impact reticle
		if not grenade_trajectory_points.is_empty():
			var end_pt = to_local(grenade_trajectory_points.back())
			draw_arc(end_pt, 9.0, 0.0, TAU, 16, Color(1.0, 0.25, 0.25, 0.9), 2.0)
			draw_circle(end_pt, 3.0, Color(1.0, 0.25, 0.25, 0.9))

	# 3. Grenade Status Effect Visual Overlays on Player
	if freeze_timer > 0.0:
		# Crystalline Hexagonal Ice Block Encasing the Player
		var ice_poly = PackedVector2Array([
			Vector2(-13, -18),
			Vector2(0, -23),
			Vector2(13, -18),
			Vector2(15, 14),
			Vector2(-15, 14)
		])
		draw_colored_polygon(ice_poly, Color(0.32, 0.85, 1.0, 0.52))
		var outline_pts = PackedVector2Array([
			Vector2(-13, -18), Vector2(0, -23), Vector2(13, -18),
			Vector2(15, 14), Vector2(-15, 14), Vector2(-13, -18)
		])
		draw_polyline(outline_pts, Color(0.9, 0.98, 1.0, 0.95), 1.8)
		# Internal frost specular facet lines
		draw_line(Vector2(-9, -14), Vector2(8, 6), Color(1.0, 1.0, 1.0, 0.7), 1.5)
		draw_line(Vector2(6, -15), Vector2(-6, 8), Color(0.8, 0.96, 1.0, 0.6), 1.2)

	if emp_timer > 0.0:
		# Crackling Electric Lightning Arcs around Player Chassis
		var t_ms = Time.get_ticks_msec() / 40.0
		for i in range(3):
			var y_a = -12.0 + float(i) * 10.0
			var p1 = Vector2(-12.0, y_a + sin(t_ms + i) * 3.0)
			var p2 = Vector2(0.0, y_a + cos(t_ms * 1.3 + i) * 5.0)
			var p3 = Vector2(12.0, y_a - sin(t_ms * 0.9 + i) * 3.0)
			draw_polyline(PackedVector2Array([p1, p2, p3]), Color(0.25, 0.92, 1.0, 0.95), 1.8)
			draw_circle(p2, 2.0, Color(1.0, 0.95, 0.4, 0.95))

	if burn_timer > 0.0:
		# Animated Rising Flame Tongues on Player
		var t_sec = Time.get_ticks_msec() / 1000.0
		for i in range(-1, 2):
			var fx = float(i) * 6.5
			var fh = 12.0 + 5.0 * sin(t_sec * 16.0 + float(i) * 2.1)
			var base = Vector2(fx, 8.0)
			var tip = Vector2(fx + cos(t_sec * 11.0 + i) * 3.0, 8.0 - fh)
			draw_colored_polygon(PackedVector2Array([
				base + Vector2(-4.0, 0),
				base + Vector2(4.0, 0),
				tip
			]), Color(1.0, 0.38, 0.05, 0.8))
			draw_colored_polygon(PackedVector2Array([
				base + Vector2(-2.0, 0),
				base + Vector2(2.0, 0),
				base + (tip - base) * 0.6
			]), Color(1.0, 0.92, 0.3, 0.9))

	# 4. Bandage Heal Feedback (+35 HP & Emerald Pulse)
	if heal_flash_timer > 0.0:
		var progress: float = 1.0 - clamp(heal_flash_timer / 0.85, 0.0, 1.0)
		var alpha: float = clamp(1.0 - progress, 0.0, 1.0)
		draw_arc(Vector2.ZERO, 16.0 + progress * 14.0, 0.0, TAU, 24, Color(0.25, 0.96, 0.55, alpha * 0.85), 2.0)
		var font: Font = ThemeDB.fallback_font
		if font:
			var txt_pos: Vector2 = Vector2(-18.0, -24.0 - progress * 22.0)
			draw_string(font, txt_pos, "+35 HP", HORIZONTAL_ALIGNMENT_CENTER, -1, 12, Color(0.3, 1.0, 0.58, alpha))

	# 4b. Fall Damage Impact Feedback (-XX FALL & Red Ground Shock Ring)
	if fall_flash_timer > 0.0:
		var f_prog: float = 1.0 - clamp(fall_flash_timer / 0.9, 0.0, 1.0)
		var f_alpha: float = clamp(1.0 - f_prog, 0.0, 1.0)
		draw_arc(Vector2(0.0, 13.0), 10.0 + f_prog * 22.0, PI, TAU, 20, Color(1.0, 0.35, 0.2, f_alpha * 0.85), 2.0)
		var f_font: Font = ThemeDB.fallback_font
		if f_font:
			var f_txt_pos: Vector2 = Vector2(-24.0, -22.0 - f_prog * 24.0)
			draw_string(f_font, f_txt_pos, "-%d FALL" % last_fall_damage, HORIZONTAL_ALIGNMENT_CENTER, -1, 12, Color(1.0, 0.38, 0.28, f_alpha))

	# 5. Wall-Slide Friction Sparks & Magnetic Grip Glow along the wall edge
	if is_wall_sliding and wall_direction != 0:
		var t_ws: float = Time.get_ticks_msec() / 1000.0
		var wx: float = float(wall_direction) * 9.0
		# Subtle cyan magnetic grip points at upper hand (-9) and braced boot (+6)
		draw_circle(Vector2(wx, -9.0), 2.2, Color(0.22, 0.92, 1.0, 0.75))
		draw_circle(Vector2(wx, 6.0), 2.2, Color(0.22, 0.92, 1.0, 0.75))
		# Rising friction sparks scraping off the wall
		for i in range(4):
			var phase: float = fmod(t_ws * 4.5 + float(i) * 0.27, 1.0)
			var sy: float = lerpf(8.0, -14.0, phase)
			var sx: float = wx - float(wall_direction) * (1.0 + sin(phase * PI) * 4.5)
			var s_alpha: float = clamp(1.0 - phase, 0.0, 1.0)
			var col: Color = Color(1.0, 0.88, 0.35, s_alpha) if (i % 2 == 0) else Color(1.0, 0.5, 0.12, s_alpha)
			draw_line(Vector2(sx, sy), Vector2(sx + float(wall_direction) * 1.5, sy + 3.0), col, 1.4)

func _is_collider_climbable(collider: Object) -> bool:
	if collider == null:
		return false
	if "climbable" in collider:
		return bool(collider.get("climbable"))
	if collider.has_meta("climbable"):
		return bool(collider.get_meta("climbable"))
	if collider is Node:
		var node: Node = collider as Node
		return node.is_in_group("climbable_walls") or node.is_in_group("climbable")
	return false

func _try_use_bandage() -> void:
	if GameManager.use_bandage():
		heal_flash_timer = 0.85
		queue_redraw()

func _find_closest_grapple_ring(exclude_current: bool = false) -> Node2D:
	var rings = get_tree().get_nodes_in_group("grapple_rings")
	var closest_ring: Node2D = null
	var min_dist: float = GRAPPLE_RANGE
	var space_state = get_world_2d().direct_space_state

	for ring in rings:
		if not is_instance_valid(ring):
			continue
		if exclude_current and is_grappling and ring == current_grapple_ring:
			continue

		var dist = global_position.distance_to(ring.global_position)
		if dist > min_dist:
			continue

		# Raycast line of sight check: cannot grapple through solid walls/ceilings!
		var ray = PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -6), ring.global_position)
		ray.exclude = [self]
		ray.collision_mask = 1
		var hit = space_state.intersect_ray(ray)
		if not hit.is_empty():
			continue

		min_dist = dist
		closest_ring = ring

	return closest_ring

func _try_grapple() -> void:
	var target_ring = _find_closest_grapple_ring(is_grappling)
	if not target_ring:
		return

	is_grappling = true
	current_grapple_ring = target_ring
	grapple_anchor = target_ring.global_position

	# Start at exact current distance so the player NEVER teleports on latch!
	var current_dist = max(global_position.distance_to(grapple_anchor), 32.0)
	grapple_length = current_dist
	grapple_angle = (global_position - grapple_anchor).angle()

	# Project incoming linear velocity smoothly onto the pendulum tangent:
	var rope_vec = global_position - grapple_anchor
	var r_hat = rope_vec / current_dist
	# Tangent pointing rightwards at the bottom of the swing arc
	var t_right = Vector2(r_hat.y, -r_hat.x)
	var v_tan = velocity.dot(t_right)

	# If player latched from rest or low horizontal speed, give a natural swing push in facing direction
	if abs(v_tan) < 140.0:
		v_tan = 165.0 * float(facing_direction)

	velocity = t_right * v_tan
	grapple_angular_vel = -v_tan / max(grapple_length, 60.0)
	queue_redraw()

func _process_grapple_physics(dt: float, jump_just_pressed: bool = false) -> void:
	# TRUE CARTESIAN VELOCITY-PROJECTION PENDULUM (Zero Teleportation, Real Gravity & Damping)
	var rope_vec = global_position - grapple_anchor
	var dist = max(rope_vec.length(), 1.0)
	var r_hat = rope_vec / dist
	var t_right = Vector2(r_hat.y, -r_hat.x) # Unit tangent pointing right at bottom of arc

	# 1. Smoothly reel cable towards safe swing clearance (GRAPPLE_MIN_LEN..GRAPPLE_IDEAL_MAX_LEN)
	# Never snaps in 1 frame; smoothly reels at 165 px/s so player clears the acid pit!
	if grapple_length > GRAPPLE_IDEAL_MAX_LEN:
		grapple_length = move_toward(grapple_length, GRAPPLE_IDEAL_MAX_LEN, 165.0 * dt)
	elif grapple_length < GRAPPLE_MIN_LEN:
		grapple_length = move_toward(grapple_length, GRAPPLE_MIN_LEN, 140.0 * dt)

	# 2. Apply Real Gravity
	velocity.y += gravity * dt

	# 3. Player Swing Pumping with [A] / [D] (Left / Right)
	var swing_input = _get_horizontal_input()
	if swing_input != 0.0 and r_hat.y > -0.15:
		velocity += t_right * (swing_input * 310.0 * dt)
		facing_direction = 1 if swing_input > 0.0 else -1
		sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)

	# 4. Project Velocity onto Rope Tangent (Eliminate outward radial stretch)
	var radial_vel = velocity.dot(r_hat)
	velocity -= r_hat * radial_vel

	# 5. Natural Pendulum Damping ("sa isi piarda din swing cu cat sta mai mult agatat")
	var damp_rate = 0.89 if swing_input == 0.0 else 0.97
	velocity *= pow(damp_rate, dt)

	# Clamp maximum tangential swing speed so it always feels smooth and controlled
	if velocity.length() > 430.0:
		velocity = velocity.normalized() * 430.0

	# 6. Soft Radial Spring Correction to maintain rope length without ever snapping position
	var dist_error = dist - grapple_length
	var radial_correction = clamp(dist_error * 11.0, -210.0, 210.0)
	velocity -= r_hat * radial_correction

	# Prevent swinging above the ceiling anchor
	if global_position.y < grapple_anchor.y - 10.0 and velocity.y < 0.0:
		velocity.y *= 0.4

	# Update angle tracking for visual compatibility
	grapple_angle = rope_vec.angle()
	grapple_angular_vel = -velocity.dot(t_right) / max(grapple_length, 60.0)

	# 7. Redraw visible grappling hook cable
	queue_redraw()

	# 8. Manual Jump Off with [SPACE] / [W] (Catapult Launch)
	if jump_just_pressed:
		_catapult_release_grapple()

func _catapult_release_grapple() -> void:
	var launch_vel = velocity
	_release_grapple()
	velocity.x = clamp(launch_vel.x * 1.15 + facing_direction * 95.0, -390.0, 390.0)
	velocity.y = min(launch_vel.y, jump_velocity * 0.88)
	can_double_jump = true
	has_double_jumped = false

func _release_grapple() -> void:
	is_grappling = false
	current_grapple_ring = null
	queue_redraw()

func _update_animations(dt: float, input_dir: float) -> void:
	if attack_timer > 0.0 or is_firing_flamethrower:
		return

	var is_dmg = (GameManager.player_chassis == "damaged")
	anim_timer += dt

	if is_crouching:
		sprite.texture = tex_damaged_crouch if is_dmg else tex_standard_crouch
		sprite.hframes = 2
		sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
		if input_dir != 0.0:
			# Crouch Walk: animated crawl cycle synchronized with movement speed + subtle crawl bob
			var crawl_frame = int(anim_timer * 7.5) % 2
			sprite.frame = crawl_frame
			sprite.offset.x = (1 if crawl_frame == 1 else 0) * facing_direction
			sprite.offset.y = 1 if crawl_frame == 1 else 0
		else:
			# Crouch Idle: steady low-duck posture (frame 0, no twitching)
			sprite.frame = 0
			sprite.offset = Vector2.ZERO
	elif is_wall_sliding:
		sprite.texture = tex_damaged_wallslide if is_dmg else tex_standard_wallslide
		sprite.hframes = 2
		sprite.frame = int(anim_timer * 7.0) % 2
		sprite.scale = Vector2(wall_direction * sprite_scale_mod.x, sprite_scale_mod.y)
		sprite.offset = Vector2(0, 0)
		queue_redraw()
	elif not is_on_floor():
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 0 if velocity.y < 0.0 else 2
		sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
		sprite.offset = Vector2(0, 0)
	elif input_dir != 0.0:
		sprite.texture = tex_damaged_walk if is_dmg else tex_standard_walk
		sprite.hframes = 8
		var speed_mult = 12.0 if is_sprinting else 8.0
		sprite.frame = int(anim_timer * speed_mult) % 8
		sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
		sprite.offset = Vector2(0, 0)
	else:
		sprite.texture = tex_damaged_idle if is_dmg else tex_standard_idle
		sprite.hframes = 4
		sprite.frame = int(anim_timer * 4.0) % 4
		sprite.scale = Vector2(facing_direction * sprite_scale_mod.x, sprite_scale_mod.y)
		sprite.offset = Vector2(0, 0)

# SAFE MELEE HIT: PASSES BOTH (amount, knockback) TO PREVENT ENGINE CRASH!
func _on_melee_hit(area: Area2D) -> void:
	var target = area.get_parent()
	if target and target.has_method("take_damage"):
		var weapon_id = GameManager.main_hand.get("id", "pan")
		var dmg = 35.0 if weapon_id == "bat" else 25.0
		var kb = float(facing_direction)
		target.take_damage(dmg, kb)

func add_camera_shake(intensity: float, duration: float) -> void:
	var mult = clamp(GameManager.setting_screen_shake / 100.0, 0.0, 2.0)
	if mult <= 0.01:
		return
	camera_shake_intensity = max(camera_shake_intensity, intensity * mult)
	camera_shake_timer = max(camera_shake_timer, duration)

func take_grenade_damage(amount: float) -> void:
	# Direct grenade/burn damage to player (bypasses contact i-frames so grenade blasts always register!)
	if is_shield_raised and GameManager.player_shield > 0.0:
		var leftover = GameManager.damage_shield(amount)
		if leftover <= 0.0:
			return
		amount = leftover

	GameManager.player_hp = max(0.0, GameManager.player_hp - amount)
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	if GameManager.player_hp <= 0.0:
		_die()

func apply_grenade_effect(g_type: String, blast_pos: Vector2, falloff: float) -> void:
	var away_dir = (global_position - blast_pos).normalized()
	if away_dir.length_squared() < 0.01:
		away_dir = Vector2(facing_direction, -0.5).normalized()

	match g_type:
		"frag":
			# Frag Shrapnel Explosion: High self-damage + explosive radial launch!
			take_grenade_damage(35.0 * falloff)
			if is_grappling:
				_release_grapple()
			velocity = Vector2(away_dir.x * 290.0 * falloff, min(away_dir.y * 260.0, -210.0) * falloff)
			blast_stun_timer = 0.28
			i_frame_timer = 0.6

		"cryo":
			# Cryo Frost Nova: Freezes the player solid in an ice block, then chills!
			take_grenade_damage(20.0 * falloff)
			if is_grappling:
				_release_grapple()
			freeze_timer = max(freeze_timer, 1.8 * falloff)
			chill_timer = max(chill_timer, 3.2 * falloff)
			velocity.x *= 0.25

		"emp":
			# EMP Electromagnetic Blast: Short-circuits Shield & Core Stamina, disables electronics!
			take_grenade_damage(25.0 * falloff)
			GameManager.player_shield = 0.0
			GameManager.shield_regen_timer = 4.0
			GameManager.player_shield_changed.emit(GameManager.player_shield, GameManager.player_max_shield)
			GameManager.player_ep = max(0.0, GameManager.player_ep - 45.0 * falloff)
			GameManager.pause_ep_regen(3.0)
			GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
			emp_timer = max(emp_timer, 2.6 * falloff)
			velocity = Vector2(away_dir.x * 140.0, -110.0) * falloff
			blast_stun_timer = 0.18

		"fire":
			# Thermite Incendiary Blast: Initial blast damage + sets player on fire (Burning DoT)!
			take_grenade_damage(24.0 * falloff)
			burn_timer = max(burn_timer, 3.5)
			burn_tick_timer = 0.0
			velocity = Vector2(away_dir.x * 160.0, -130.0) * falloff
			blast_stun_timer = 0.18

		"fire_pool":
			# Stepping into lingering thermite fire pool
			if burn_timer <= 0.5:
				take_grenade_damage(4.0)
			burn_timer = max(burn_timer, 1.6)

	queue_redraw()

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

func _reset_fall_tracking() -> void:
	_is_tracking_fall = false
	_fall_start_y = global_position.y

func _apply_fall_damage(amount: float) -> void:
	if amount <= 0.0:
		return
	last_fall_damage = max(1, int(round(amount)))
	fall_flash_timer = 0.9
	add_camera_shake(clamp(amount * 0.25, 3.0, 12.0), 0.22)

	# Heavy landing squash-and-stretch feedback
	sprite_scale_mod = Vector2(1.32, 0.68)
	var tw = create_tween()
	if tw:
		tw.tween_property(self, "sprite_scale_mod", Vector2(1.0, 1.0), 0.16).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)

	GameManager.player_hp = max(0.0, GameManager.player_hp - amount)
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	queue_redraw()
	if GameManager.player_hp <= 0.0:
		_die()

func clear_status_effects() -> void:
	freeze_timer = 0.0
	chill_timer = 0.0
	emp_timer = 0.0
	burn_timer = 0.0
	burn_tick_timer = 0.0
	blast_stun_timer = 0.0
	_reset_fall_tracking()
	queue_redraw()

func die_in_hazard(hazard_name: String = "acid") -> void:
	if is_grappling:
		_release_grapple()
	is_dashing = false
	clear_status_effects()
	if dash_particles:
		dash_particles.emitting = false

	GameManager.clear_fire_hazards()
	if GameManager.is_boss_fight_active:
		GameManager.clear_combat_hazards()
		GameManager.restore_inventory_checkpoint()

	velocity = Vector2.ZERO
	GameManager.player_hp = GameManager.player_max_hp
	GameManager.player_ep = GameManager.player_max_ep
	GameManager.player_shield = GameManager.player_max_shield
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
	GameManager.player_shield_changed.emit(GameManager.player_shield, GameManager.player_max_shield)

	global_position = respawn_position
	i_frame_timer = 1.0
	queue_redraw()

	if sprite:
		var tween = create_tween()
		tween.tween_property(sprite, "modulate", Color(0.2, 1.4, 0.4, 1.0), 0.08)
		tween.tween_property(sprite, "modulate", Color(1.0, 1.0, 1.0, 1.0), 0.18)

	print("Player fell into ", hazard_name, "! Respawned before swing at: ", respawn_position)

func _die() -> void:
	die_in_hazard("defeated")

func _spawn_dash_ghost() -> void:
	var parent_node = get_parent()
	if not parent_node or not sprite:
		return
	var ghost = DashGhostClass.new()
	parent_node.add_child(ghost)
	ghost.init(
		sprite.texture,
		sprite.hframes,
		sprite.frame,
		sprite.scale,
		sprite.offset,
		sprite.global_position,
		Color(0.25, 0.85, 1.0, 0.75),
		0.25
	)

func _trigger_air_jump_effect() -> void:
	var parent_node = get_parent()
	if parent_node and AirJumpEffectScene:
		var fx = AirJumpEffectScene.instantiate()
		parent_node.add_child(fx)
		fx.global_position = global_position + Vector2(0, 14)

	# Spawn jump ghost at takeoff point with electric cyan tint
	if parent_node and sprite:
		var ghost = DashGhostClass.new()
		parent_node.add_child(ghost)
		ghost.init(
			sprite.texture,
			sprite.hframes,
			sprite.frame,
			sprite.scale,
			sprite.offset,
			sprite.global_position,
			Color(0.35, 0.9, 1.0, 0.65),
			0.22
		)

	# Squash & stretch impulse tween on the robot chassis
	sprite_scale_mod = Vector2(1.22, 0.78)
	var tw = create_tween()
	if tw:
		tw.tween_property(self, "sprite_scale_mod", Vector2(0.85, 1.25), 0.06).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(self, "sprite_scale_mod", Vector2(1.0, 1.0), 0.12).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN_OUT)
