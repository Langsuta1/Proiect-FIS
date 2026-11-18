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
var is_wall_sliding: bool = false
var wall_direction: int = 0
var wall_jump_lock_timer: float = 0.0
var wall_coyote_timer: float = 0.0

# Energy Shield
var is_shield_raised: bool = false

# Grappling Hook
var is_grappling: bool = false
var grapple_anchor: Vector2 = Vector2.ZERO
var grapple_length: float = 0.0
var grapple_angle: float = 0.0
var grapple_angular_vel: float = 0.0
var grapple_has_passed_bottom: bool = false
var grapple_swing_timer: float = 0.0
const GRAPPLE_RANGE: float = 290.0

# Grenade Slingshot Aiming
var is_aiming_grenade: bool = false
var grenade_launch_velocity: Vector2 = Vector2.ZERO
var grenade_trajectory_points: Array[Vector2] = []

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
	# Update checkpoint when approaching swing section
	if global_position.x >= 2650.0 and respawn_position.x < 2650.0:
		respawn_position = SWING_CHECKPOINT

	# Fall death safety check: strictly if fallen into the toxic green acid chasm or fell out of the world
	if global_position.y > 890.0 and global_position.x > 2810.0 and global_position.x < 3590.0:
		die_in_hazard("acid")
		return
	elif global_position.y > 1050.0:
		die_in_hazard("void")
		return

	# 1. Update I-Frames & Movement Timers
	if i_frame_timer > 0.0:
		i_frame_timer -= dt
		sprite.modulate.a = 0.35 if fmod(Time.get_ticks_msec() / 70.0, 2.0) > 1.0 else 1.0
	else:
		sprite.modulate.a = 1.0

	if wall_jump_lock_timer > 0.0:
		wall_jump_lock_timer -= dt
	if wall_coyote_timer > 0.0:
		wall_coyote_timer -= dt

	# 2. Quick-Swap Weapons [Q]
	if Input.is_action_just_pressed("switch_weapon"):
		GameManager.swap_weapons()

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
				# Check if there is another ring in range to chain-swing!
				var rings = get_tree().get_nodes_in_group("grapple_rings")
				var has_next_ring = false
				for ring in rings:
					if ring.global_position.distance_to(grapple_anchor) > 15.0 and global_position.distance_to(ring.global_position) <= GRAPPLE_RANGE:
						has_next_ring = true
						break
				if has_next_ring:
					_try_grapple()
				else:
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

	if Input.is_action_just_pressed("dash") and dash_cooldown <= 0.0 and not is_dashing and GameManager.consume_ep(15.0):
		is_dashing = true
		dash_timer = dash_duration
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

	# Detect Wall Slide
	var on_wall = is_on_wall() and not is_on_floor()
	var wall_normal = get_wall_normal()
	var wall_dir = 0
	if wall_normal.x > 0.5:
		wall_dir = -1
	elif wall_normal.x < -0.5:
		wall_dir = 1

	var input_dir: float = Input.get_axis("move_left", "move_right")
	var pushing_wall = (input_dir != 0.0 and sign(input_dir) == wall_dir)

	if on_wall and pushing_wall and velocity.y > 0.0 and not is_crouching and not is_dashing and not is_grappling:
		is_wall_sliding = true
		wall_direction = wall_dir
		wall_coyote_timer = 0.12
		velocity.y = min(velocity.y, wall_slide_speed)
		can_double_jump = true
		has_double_jumped = false
	else:
		is_wall_sliding = false

	# 8. Jump, Wall Jump & Double Jump
	if Input.is_action_just_pressed("jump"):
		if (is_wall_sliding or wall_coyote_timer > 0.0) and not is_on_floor():
			# Wall Jump (Free, launches diagonally away from wall and up)
			velocity.x = -wall_direction * wall_jump_h_force
			velocity.y = wall_jump_v_velocity
			facing_direction = -wall_direction
			sprite.scale.x = facing_direction
			wall_jump_lock_timer = 0.16
			is_wall_sliding = false
			wall_coyote_timer = 0.0
			can_double_jump = true
			has_double_jumped = false
		elif is_on_floor():
			# Can only jump if not stuck under a low ceiling!
			if can_stand:
				velocity.y = jump_velocity
		elif can_double_jump and not has_double_jumped and GameManager.consume_ep(10.0):
			velocity.y = double_jump_velocity
			has_double_jumped = true

	# 9. Horizontal Movement
	if wall_jump_lock_timer > 0.0:
		velocity.x = move_toward(velocity.x, input_dir * walk_speed, 600.0 * dt)
	else:
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

	# 10. Combat Attacks (Distinct Melee and Ranged handling)
	_handle_attacks(dt)

	# 11. Grenade [G] (Angry-Birds Slingshot Drag-Aiming & Trajectory)
	_handle_grenade_aiming(dt)

	# 12. Update Animations
	_update_animations(dt, input_dir)

	move_and_slide()

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

	if (firing_flame_main or firing_flame_sec) and GameManager.player_ep > 0.0:
		is_firing_flamethrower = true
		GameManager.pause_ep_regen(1.0) # Stamina regen paused while firing!
		var drain = 28.0 * dt
		GameManager.player_ep = max(0.0, GameManager.player_ep - drain)
		GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)

		sprite.texture = tex_damaged_shoot if is_dmg else tex_standard_shoot
		sprite.hframes = 4
		sprite.frame = (int(Time.get_ticks_msec() / 70) % 4)
		var y_off = 6 if is_crouching else 0
		sprite.offset.x = 4 if facing_direction == 1 else -4
		sprite.offset.y = y_off

		flame_tick_timer -= dt
		if flame_tick_timer <= 0.0:
			flame_tick_timer = 0.065
			_spawn_flame_puff()
		return
	else:
		if is_firing_flamethrower:
			is_firing_flamethrower = false
			GameManager.pause_ep_regen(1.0) # 1 full second cooldown AFTER releasing trigger!
			sprite.offset = Vector2(0, 0)

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

	# Secondary Attack: [Z]
	elif Input.is_action_just_pressed("attack_ranged"):
		if sec_type == "ranged":
			_fire_ranged(sec_id)
		elif sec_type == "melee":
			current_attack_type = "melee"
			var is_bat = (sec_id == "bat")
			attack_duration = 0.28 if is_bat else 0.22
			attack_timer = attack_duration
			var hit_y = 6 if is_crouching else 0
			melee_hitbox.monitoring = true
			melee_hitbox.position = Vector2((30 if is_bat else 24) * facing_direction, hit_y)

func _fire_ranged(weapon_id: String) -> void:
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

	var proj = preload("res://scenes/projectile_laser.tscn").instantiate()
	var hand_y = position.y + (6 if is_crouching else 0)
	proj.position = Vector2(position.x + 20 * facing_direction, hand_y)
	proj.direction = Vector2(facing_direction, 0)
	get_parent().add_child(proj)

func _spawn_flame_puff() -> void:
	var flame_scene = load("res://scenes/projectile_flame.tscn")
	if not flame_scene:
		return
	var flame = flame_scene.instantiate()
	var hand_y = position.y + (6 if is_crouching else 0)
	flame.position = Vector2(position.x + 24 * facing_direction, hand_y + randf_range(-3.0, 3.0))
	flame.direction = Vector2(facing_direction, randf_range(-0.12, 0.12)).normalized()
	get_parent().add_child(flame)

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

func _try_grapple() -> void:
	var rings = get_tree().get_nodes_in_group("grapple_rings")
	var target_ring: Node2D = null
	var best_score: float = -999999.0
	var space_state = get_world_2d().direct_space_state

	for ring in rings:
		# If already grappling to this exact ring, skip so we can chain to a new one
		if is_grappling and ring.global_position.distance_to(grapple_anchor) < 15.0:
			continue

		var dist = global_position.distance_to(ring.global_position)
		if dist > GRAPPLE_RANGE:
			continue

		# Raycast line of sight check: cannot grapple through solid walls/ceilings!
		var ray = PhysicsRayQueryParameters2D.create(global_position + Vector2(0, -8), ring.global_position)
		ray.exclude = [self]
		ray.collision_mask = 1
		var hit = space_state.intersect_ray(ray)
		if not hit.is_empty():
			continue

		# Prioritize rings ahead in facing direction and above
		var dx = (ring.global_position.x - global_position.x) * facing_direction
		var dy = ring.global_position.y - global_position.y
		var score = (GRAPPLE_RANGE - dist) + (dx * 1.5) - (max(0.0, dy) * 1.8)
		if score > best_score:
			best_score = score
			target_ring = ring

	if target_ring:
		is_grappling = true
		grapple_has_passed_bottom = false
		grapple_swing_timer = 0.0
		grapple_anchor = target_ring.global_position
		grapple_length = clamp(global_position.distance_to(grapple_anchor), 110.0, GRAPPLE_RANGE)
		grapple_angle = (global_position - grapple_anchor).angle()

		# Preserve incoming tangential momentum:
		var v_tangent = -velocity.x * sin(grapple_angle) + velocity.y * cos(grapple_angle)
		grapple_angular_vel = v_tangent / grapple_length

		# Boost initial momentum forward if moving or jumping forward
		if facing_direction > 0:
			if grapple_angular_vel > -1.2:
				grapple_angular_vel = -2.2
		else:
			if grapple_angular_vel < 1.2:
				grapple_angular_vel = 2.2

		queue_redraw()

func _process_grapple_physics(dt: float) -> void:
	grapple_swing_timer += dt

	# 1. Gravity angular acceleration (correct sign for Godot +Y downwards):
	var angular_accel = (gravity / grapple_length) * cos(grapple_angle)

	# 2. Player Swing Pumping with [A] / [D] / Left / Right
	var swing_input = Input.get_axis("move_left", "move_right")
	if swing_input != 0.0:
		var pump_force = (480.0 / grapple_length)
		if swing_input > 0.0:
			grapple_angular_vel -= pump_force * dt
			facing_direction = 1
			sprite.scale.x = 1
		elif swing_input < 0.0:
			grapple_angular_vel += pump_force * dt
			facing_direction = -1
			sprite.scale.x = -1

	# Apply gravity acceleration
	grapple_angular_vel += angular_accel * dt

	# 3. Damping / Friction: swing loses momentum over time if just hanging
	var damping = pow(0.92, dt)
	grapple_angular_vel *= damping

	# Update angle
	grapple_angle += grapple_angular_vel * dt

	# Clamp angle to lower hemisphere (no wrapping over the top)
	var min_angle = deg_to_rad(15.0)
	var max_angle = deg_to_rad(165.0)
	if grapple_angle < min_angle:
		grapple_angle = min_angle
		grapple_angular_vel = 0.0
	elif grapple_angle > max_angle:
		grapple_angle = max_angle
		grapple_angular_vel = 0.0

	# 4. Smooth collision-aware pendulum update:
	# Sets velocity to drive towards target position, allowing move_and_slide() to respect walls (NO CLIPPING!)
	var target_pos = grapple_anchor + Vector2(cos(grapple_angle), sin(grapple_angle)) * grapple_length
	velocity = (target_pos - global_position) / dt

	# If hitting a wall, dampen angular velocity so we slide smoothly without sticking
	if is_on_wall():
		grapple_angular_vel *= 0.55
		grapple_length = clamp(global_position.distance_to(grapple_anchor), 90.0, GRAPPLE_RANGE)
		grapple_angle = (global_position - grapple_anchor).angle()

	# 5. Redraw the visible grappling hook cable
	queue_redraw()

	# 6. Automatic Single-Swing Release Check (Releases at forward apex after crossing bottom)
	if facing_direction > 0: # Swinging to the right
		if grapple_angle <= 1.57:
			grapple_has_passed_bottom = true
		if grapple_has_passed_bottom and (grapple_angular_vel >= -0.4 or grapple_angle <= deg_to_rad(48.0) or grapple_swing_timer >= 0.85):
			_catapult_release_grapple()
			return
	else: # Swinging to the left
		if grapple_angle >= 1.57:
			grapple_has_passed_bottom = true
		if grapple_has_passed_bottom and (grapple_angular_vel <= 0.4 or grapple_angle >= deg_to_rad(132.0) or grapple_swing_timer >= 0.85):
			_catapult_release_grapple()
			return

	# Fallback safety timeout (auto-release after 1.1s so player never hangs stuck)
	if grapple_swing_timer >= 1.1:
		_catapult_release_grapple()
		return

	# 7. Manual Early Jump Off with [SPACE]
	if Input.is_action_just_pressed("jump"):
		_catapult_release_grapple()

func _catapult_release_grapple() -> void:
	var launch_vel = velocity
	_release_grapple()
	velocity = launch_vel
	velocity.y = min(velocity.y, jump_velocity * 0.95)
	velocity.x += facing_direction * 180.0
	can_double_jump = true
	has_double_jumped = false

func _release_grapple() -> void:
	is_grappling = false
	queue_redraw()

func _update_animations(dt: float, input_dir: float) -> void:
	if attack_timer > 0.0 or is_firing_flamethrower:
		return

	var is_dmg = (GameManager.player_chassis == "damaged")
	anim_timer += dt

	if is_crouching:
		sprite.texture = tex_damaged_crouch if is_dmg else tex_standard_crouch
		sprite.hframes = 2
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
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 1
		sprite.scale.x = wall_direction
		sprite.offset = Vector2(0, 0)
	elif not is_on_floor():
		sprite.texture = tex_jump
		sprite.hframes = 3
		sprite.frame = 0 if velocity.y < 0.0 else 2
		sprite.scale.x = facing_direction
		sprite.offset = Vector2(0, 0)
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

func die_in_hazard(hazard_name: String = "acid") -> void:
	if is_grappling:
		_release_grapple()

	velocity = Vector2.ZERO
	GameManager.player_hp = GameManager.player_max_hp
	GameManager.player_ep = GameManager.player_max_ep
	GameManager.player_shield = GameManager.player_max_shield
	GameManager.player_health_changed.emit(GameManager.player_hp, GameManager.player_max_hp)
	GameManager.player_energy_changed.emit(GameManager.player_ep, GameManager.player_max_ep)
	GameManager.player_shield_changed.emit(GameManager.player_shield, GameManager.player_max_shield)

	global_position = respawn_position
	i_frame_timer = 1.0

	if sprite:
		var tween = create_tween()
		tween.tween_property(sprite, "modulate", Color(0.2, 1.4, 0.4, 1.0), 0.08)
		tween.tween_property(sprite, "modulate", Color(1.0, 1.0, 1.0, 1.0), 0.18)

	print("Player fell into ", hazard_name, "! Respawned before swing at: ", respawn_position)

func _die() -> void:
	die_in_hazard("defeated")
