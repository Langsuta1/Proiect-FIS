extends CharacterBody2D
class_name BossCrusher
# boss_crusher.gd - The Crusher Titan: Cinematic Intro, Active Walking AI, 4 Telegraphed Special Attacks,
# Travelling Seismic Waves, Mortar Barrage, Wall-Crash Stun Vulnerability & Multi-Phase Enrage!

@export var max_hp: float = 650.0
var base_max_hp: float = 650.0
var hp: float = 650.0
var phase: int = 1 # Phase 1 (>50% HP), Phase 2 (<=50% HP Enraged Overdrive)

enum State {
	DORMANT,
	INTRO,
	STALK,
	TELEGRAPH_SLAM,
	SLAM_ACTIVE,
	TELEGRAPH_SHOCKWAVE,
	SHOCKWAVE_ACTIVE,
	TELEGRAPH_MORTAR,
	MORTAR_ACTIVE,
	TELEGRAPH_CHARGE,
	ROCKET_CHARGE,
	STUNNED,
	DEFEATED
}
var current_state: State = State.DORMANT

const ARENA_LEFT: float = 4150.0
const ARENA_RIGHT: float = 5100.0
const FLOOR_Y: float = 780.0
const BOSS_STANDING_Y: float = 721.0 # 780 - 59 (sprite feet offset)
const BOSS_CHECKPOINT: Vector2 = Vector2(4060, 750)

var state_timer: float = 0.0
var state_duration: float = 1.0
var facing_direction: int = -1
var walk_anim_timer: float = 0.0
var footstep_timer: float = 0.0
var attack_cycle_idx: int = 0
var intro_stage: int = 0

# Status Effects from Player Grenades
var chill_timer: float = 0.0
var burn_timer: float = 0.0
var burn_tick: float = 0.0

# Special Attack Data
var slam_target_xs: Array[float] = []
var piston_current_y: float = 420.0
var shockwaves: Array = [] # Array of Dictionaries: {x, dir, speed, width, height, hit_player}
var mortars: Array = [] # Array of Dictionaries: {pos, vel, target_x}
var charge_hit_player: bool = false
var death_explosion_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var compactor_piston: Sprite2D = $CompactorPiston
@onready var telegraph_zone: ColorRect = $TelegraphZone
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var hurtbox: Area2D = get_node_or_null("Hurtbox")

const ExplosionFXClass = preload("res://scripts/grenade_explosion_fx.gd")
var tex_boss = preload("res://assets/boss_crusher_titan_strip4.png")
var tex_piston = preload("res://assets/boss_compactor_piston_80x160.png")

var player_ref: Node2D = null

func _ready() -> void:
	add_to_group("boss")
	add_to_group("enemies")
	base_max_hp = max_hp
	max_hp = base_max_hp * GameManager.difficulty_multiplier
	hp = max_hp
	if sprite:
		sprite.texture = tex_boss
		sprite.hframes = 4
		sprite.frame = 0
	if compactor_piston:
		compactor_piston.texture = tex_piston
		compactor_piston.visible = false
	if telegraph_zone:
		telegraph_zone.visible = false
	if hurtbox:
		hurtbox.add_to_group("enemies")
		hurtbox.add_to_group("boss")

	# Start perched high in the ceiling shadows waiting for the player to enter the arena!
	_enter_dormant_ambush()

func _enter_dormant_ambush() -> void:
	current_state = State.DORMANT
	max_hp = base_max_hp * GameManager.difficulty_multiplier
	hp = max_hp
	phase = 1
	shockwaves.clear()
	mortars.clear()
	slam_target_xs.clear()
	if compactor_piston:
		compactor_piston.visible = false
	global_position = Vector2(4650.0, 240.0)
	velocity = Vector2.ZERO
	if sprite:
		sprite.modulate = Color(1, 1, 1, 0.0)
	var hud = get_tree().get_first_node_in_group("hud")
	if hud and hud.get("boss_panel"):
		hud.boss_panel.visible = false
	queue_redraw()

func activate_boss(player: Node2D) -> void:
	if current_state != State.DORMANT:
		return
	player_ref = player
	current_state = State.INTRO
	intro_stage = 0
	state_duration = 2.6
	state_timer = state_duration
	global_position = Vector2(4650.0, 240.0)
	velocity = Vector2.ZERO
	if sprite:
		sprite.modulate = Color(1, 1, 1, 0.0)
		sprite.frame = 1
		facing_direction = -1 if player.global_position.x < global_position.x else 1
		sprite.scale.x = facing_direction
	GameManager.boss_health_changed.emit(hp, max_hp, phase)
	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(3.5, 0.8)
	queue_redraw()

func _physics_process(dt: float) -> void:
	if not is_instance_valid(player_ref):
		player_ref = get_tree().get_first_node_in_group("player")

	# 1. DORMANT AMBUSH TRIGGER: Activate when player enters the Boss Arena (x >= 4180)
	if current_state == State.DORMANT:
		if player_ref:
			if player_ref.global_position.x >= 4180.0:
				if "respawn_position" in player_ref:
					player_ref.respawn_position = BOSS_CHECKPOINT
				activate_boss(player_ref)
		queue_redraw()
		return

	if current_state == State.DEFEATED:
		_process_defeated_sequence(dt)
		return

	# Reset fight cleanly if player died and respawned outside the arena
	if player_ref and player_ref.global_position.x < 4110.0:
		_enter_dormant_ambush()
		return

	# Keep player inside the locked Boss Arena during the encounter
	if player_ref:
		if player_ref.global_position.x < ARENA_LEFT + 14.0:
			player_ref.global_position.x = ARENA_LEFT + 14.0
		elif player_ref.global_position.x > ARENA_RIGHT - 14.0:
			player_ref.global_position.x = ARENA_RIGHT - 14.0

	# Status effects on Boss
	var speed_mult: float = 1.0
	if chill_timer > 0.0:
		chill_timer -= dt
		speed_mult = 0.6
	if burn_timer > 0.0:
		burn_timer -= dt
		burn_tick += dt
		if burn_tick >= 0.5:
			burn_tick = 0.0
			take_damage(10.0, 0.0)

	# Process active projectiles (Seismic Shockwaves & Molten Mortars) in all combat states
	_update_shockwaves(dt)
	_update_mortars(dt)

	state_timer -= dt * speed_mult

	match current_state:
		State.INTRO:
			_process_intro(dt)

		State.STALK:
			_process_stalk(dt, speed_mult)

		State.TELEGRAPH_SLAM:
			_process_telegraph_slam(dt)

		State.SLAM_ACTIVE:
			_process_slam_active(dt)

		State.TELEGRAPH_SHOCKWAVE:
			_process_telegraph_shockwave(dt)

		State.SHOCKWAVE_ACTIVE:
			_process_shockwave_active(dt)

		State.TELEGRAPH_MORTAR:
			_process_telegraph_mortar(dt)

		State.MORTAR_ACTIVE:
			_process_mortar_active(dt)

		State.TELEGRAPH_CHARGE:
			_process_telegraph_charge(dt)

		State.ROCKET_CHARGE:
			_process_rocket_charge(dt, speed_mult)

		State.STUNNED:
			_process_stunned(dt)

	queue_redraw()

# -------------------------------------------------------------------------
# STATE PROCESSORS
# -------------------------------------------------------------------------
func _process_intro(dt: float) -> void:
	var elapsed = state_duration - state_timer
	if elapsed < 0.85:
		# Stage 0: Red target warning lock-on on arena floor
		intro_stage = 0
		sprite.modulate.a = 0.0
	elif elapsed < 1.45:
		# Stage 1: Sky-Drop Descent from ceiling!
		intro_stage = 1
		sprite.modulate = Color(1, 1, 1, 1)
		sprite.frame = 1
		var drop_t = clamp((elapsed - 0.85) / 0.5, 0.0, 1.0)
		global_position.y = lerpf(240.0, BOSS_STANDING_Y, drop_t * drop_t)
		if drop_t >= 1.0 and intro_stage == 1:
			_trigger_intro_landing_impact()
	else:
		# Stage 2: Titanic Landing Roar & Steam Vent
		if intro_stage < 2:
			_trigger_intro_landing_impact()
		global_position.y = BOSS_STANDING_Y
		sprite.frame = 1 if fmod(elapsed * 8.0, 2.0) > 1.0 else 2

	if state_timer <= 0.0:
		global_position.y = BOSS_STANDING_Y
		sprite.modulate = Color(1, 1, 1, 1)
		_enter_stalk_state(1.2)

func _trigger_intro_landing_impact() -> void:
	intro_stage = 2
	global_position.y = BOSS_STANDING_Y
	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(13.0, 0.55)
	_spawn_explosion_fx("frag", Vector2(global_position.x - 28.0, FLOOR_Y - 6.0))
	_spawn_explosion_fx("frag", Vector2(global_position.x + 28.0, FLOOR_Y - 6.0))

func _enter_stalk_state(duration: float = 1.6) -> void:
	current_state = State.STALK
	state_duration = duration * (0.78 if phase == 2 else 1.0)
	state_timer = state_duration
	if compactor_piston:
		compactor_piston.visible = false

func _process_stalk(dt: float, speed_mult: float) -> void:
	if not is_on_floor():
		velocity.y += 980.0 * dt
	else:
		global_position.y = BOSS_STANDING_Y

	if player_ref:
		var dx = player_ref.global_position.x - global_position.x
		facing_direction = -1 if dx < 0.0 else 1
		sprite.scale.x = facing_direction

		# Walk toward player if distance > 115px, or back up slightly if right on top
		var walk_spd = (135.0 if phase == 2 else 95.0) * speed_mult
		if abs(dx) > 110.0:
			velocity.x = facing_direction * walk_spd
		else:
			velocity.x = move_toward(velocity.x, 0.0, 400.0 * dt)

		# Contact stomp knockback if player touches the boss chassis
		if global_position.distance_to(player_ref.global_position) < 56.0:
			if player_ref.has_method("take_damage"):
				player_ref.take_damage(GameManager.get_scaled_enemy_damage(18.0), float(facing_direction))

	move_and_slide()
	global_position.x = clamp(global_position.x, ARENA_LEFT + 55.0, ARENA_RIGHT - 55.0)

	# Heavy mechanical walk animation & footstep tremors
	if abs(velocity.x) > 10.0:
		walk_anim_timer += dt * (9.0 if phase == 2 else 6.5)
		var step_frame = int(walk_anim_timer) % 2
		sprite.frame = 2 if (phase == 2 and step_frame == 1) else step_frame
		sprite.offset.y = -3.0 if step_frame == 1 else 0.0
		footstep_timer += dt
		if footstep_timer >= 0.42:
			footstep_timer = 0.0
			if player_ref and player_ref.has_method("add_camera_shake"):
				player_ref.add_camera_shake(2.2, 0.1)
	else:
		sprite.frame = 2 if phase == 2 else 0
		sprite.offset.y = 0.0

	if state_timer <= 0.0:
		sprite.offset = Vector2.ZERO
		_choose_next_attack()

func _choose_next_attack() -> void:
	velocity = Vector2.ZERO
	# Cycle through all 4 signature special attacks with slight variation so the fight is super varied!
	var pattern = [0, 1, 2, 3]
	var choice = pattern[attack_cycle_idx % pattern.size()]
	attack_cycle_idx += 1

	match choice:
		0:
			_start_telegraph_slam()
		1:
			_start_telegraph_shockwave()
		2:
			_start_telegraph_mortar()
		3:
			_start_telegraph_charge()

# --- ATTACK 1: HYDRAULIC CEILING CRUSHER SLAM (2.0s Telegraph -> 50% Max HP Slam!) ---
func _start_telegraph_slam() -> void:
	current_state = State.TELEGRAPH_SLAM
	state_duration = 1.75 if phase == 2 else 2.0 # 2.0-second warning telegraph!
	state_timer = state_duration
	sprite.frame = 1 # Arm raised commanding ceiling crusher
	slam_target_xs.clear()
	var px = player_ref.global_position.x if player_ref else global_position.x - 160.0
	px = clamp(px, ARENA_LEFT + 70.0, ARENA_RIGHT - 70.0)
	slam_target_xs.append(px)

	# Phase 2 drops a SECOND hydraulic crusher simultaneously offset toward player movement!
	if phase == 2:
		var offset_x = clamp(px + (165.0 * facing_direction), ARENA_LEFT + 70.0, ARENA_RIGHT - 70.0)
		if abs(offset_x - px) < 90.0:
			offset_x = clamp(px - (165.0 * facing_direction), ARENA_LEFT + 70.0, ARENA_RIGHT - 70.0)
		slam_target_xs.append(offset_x)

func _process_telegraph_slam(_dt: float) -> void:
	sprite.frame = 1
	# Subtle tracking during the first 0.55s of telegraph, then locks in place so player can dodge!
	var elapsed = state_duration - state_timer
	if elapsed < 0.55 and player_ref and not slam_target_xs.is_empty():
		slam_target_xs[0] = lerpf(slam_target_xs[0], clamp(player_ref.global_position.x, ARENA_LEFT + 70.0, ARENA_RIGHT - 70.0), 0.15)
	if state_timer <= 0.0:
		_execute_slam()

func _execute_slam() -> void:
	current_state = State.SLAM_ACTIVE
	state_duration = 0.65
	state_timer = state_duration
	piston_current_y = FLOOR_Y - 80.0

	if compactor_piston and not slam_target_xs.is_empty():
		compactor_piston.visible = true
		compactor_piston.global_position = Vector2(slam_target_xs[0], piston_current_y)

	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(11.0, 0.38)

	# Spawn impact FX and check if player is inside any crusher zone (50% Max HP damage!)
	for tx in slam_target_xs:
		_spawn_explosion_fx("frag", Vector2(tx, FLOOR_Y - 12.0))
		if player_ref:
			var dist_x = abs(player_ref.global_position.x - tx)
			var dist_y = abs(player_ref.global_position.y - (FLOOR_Y - 24.0))
			if dist_x <= 56.0 and dist_y <= 85.0:
				var kb = 1.0 if player_ref.global_position.x >= tx else -1.0
				if player_ref.has_method("take_damage"):
					player_ref.take_damage(GameManager.get_scaled_enemy_damage(50.0), kb) # 50% MAX HP CRUSHER SLAM!

func _process_slam_active(_dt: float) -> void:
	if compactor_piston and not slam_target_xs.is_empty():
		var t = 1.0 - clamp(state_timer / state_duration, 0.0, 1.0)
		var retract = 0.0 if t < 0.45 else ((t - 0.45) / 0.55) * 180.0
		compactor_piston.global_position = Vector2(slam_target_xs[0], (FLOOR_Y - 80.0) - retract)
	if state_timer <= 0.0:
		if compactor_piston:
			compactor_piston.visible = false
		slam_target_xs.clear()
		_enter_stalk_state(1.5)

# --- ATTACK 2: SEISMIC GROUND SHOCKWAVE (Travelling floor waves player must JUMP over!) ---
func _start_telegraph_shockwave() -> void:
	current_state = State.TELEGRAPH_SHOCKWAVE
	state_duration = 1.05
	state_timer = state_duration
	sprite.frame = 1

func _process_telegraph_shockwave(_dt: float) -> void:
	sprite.frame = 1
	sprite.offset.y = sin(Time.get_ticks_msec() / 35.0) * 2.0
	if state_timer <= 0.0:
		sprite.offset = Vector2.ZERO
		_execute_shockwave()

func _execute_shockwave() -> void:
	current_state = State.SHOCKWAVE_ACTIVE
	state_duration = 1.15
	state_timer = state_duration
	sprite.frame = 2

	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(9.0, 0.32)

	var wave_spd = 360.0 if phase == 2 else 300.0
	shockwaves.append({"x": global_position.x - 36.0, "dir": -1.0, "speed": wave_spd, "w": 32.0, "h": 38.0, "hit": false})
	shockwaves.append({"x": global_position.x + 36.0, "dir": 1.0, "speed": wave_spd, "w": 32.0, "h": 38.0, "hit": false})
	_spawn_explosion_fx("emp", Vector2(global_position.x, FLOOR_Y - 8.0))

func _process_shockwave_active(_dt: float) -> void:
	if state_timer <= 0.0:
		_enter_stalk_state(1.4)

func _update_shockwaves(dt: float) -> void:
	for i in range(shockwaves.size() - 1, -1, -1):
		var sw = shockwaves[i]
		sw["x"] += sw["dir"] * sw["speed"] * dt

		# Check collision with Player if player hasn't jumped high enough over the wave
		if player_ref and not sw["hit"]:
			var px = player_ref.global_position.x
			var py = player_ref.global_position.y
			if abs(px - sw["x"]) <= 24.0 and py >= (FLOOR_Y - sw["h"] - 8.0):
				sw["hit"] = true
				if player_ref.has_method("take_damage"):
					player_ref.take_damage(GameManager.get_scaled_enemy_damage(24.0), sw["dir"])
				player_ref.velocity.y = -250.0

		if sw["x"] < ARENA_LEFT - 20.0 or sw["x"] > ARENA_RIGHT + 20.0:
			shockwaves.remove_at(i)

# --- ATTACK 3: MOLTEN SCRAP MORTAR BARRAGE (Arced bombs with floor bullseye landing circles!) ---
func _start_telegraph_mortar() -> void:
	current_state = State.TELEGRAPH_MORTAR
	state_duration = 0.95
	state_timer = state_duration
	sprite.frame = 1

func _process_telegraph_mortar(_dt: float) -> void:
	sprite.frame = 1
	if state_timer <= 0.0:
		_execute_mortar_barrage()

func _execute_mortar_barrage() -> void:
	current_state = State.MORTAR_ACTIVE
	state_duration = 1.4
	state_timer = state_duration
	sprite.frame = 2

	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(6.5, 0.25)

	var num_bombs = 5 if phase == 2 else 3
	var center_target = player_ref.global_position.x if player_ref else (ARENA_LEFT + ARENA_RIGHT) * 0.5
	var spacing = 125.0

	for i in range(num_bombs):
		var offset = (float(i) - float(num_bombs - 1) * 0.5) * spacing + randf_range(-22.0, 22.0)
		var tx = clamp(center_target + offset, ARENA_LEFT + 60.0, ARENA_RIGHT - 60.0)
		var start_pos = global_position + Vector2(0, -45.0)
		var flight_time = 1.15 + float(i) * 0.14
		var g = 680.0
		var vx = (tx - start_pos.x) / flight_time
		var vy = ((FLOOR_Y - 10.0 - start_pos.y) - 0.5 * g * flight_time * flight_time) / flight_time
		mortars.append({
			"pos": start_pos,
			"vel": Vector2(vx, vy),
			"grav": g,
			"target_x": tx
		})

func _process_mortar_active(_dt: float) -> void:
	if state_timer <= 0.0:
		_enter_stalk_state(1.5)

func _update_mortars(dt: float) -> void:
	for i in range(mortars.size() - 1, -1, -1):
		var m = mortars[i]
		m["vel"].y += m["grav"] * dt
		m["pos"] += m["vel"] * dt

		if m["pos"].y >= FLOOR_Y - 8.0:
			var impact_pos = Vector2(m["pos"].x, FLOOR_Y - 8.0)
			_spawn_explosion_fx("fire" if phase == 2 else "frag", impact_pos)
			if player_ref and player_ref.global_position.distance_to(impact_pos) <= 58.0:
				var kb = 1.0 if player_ref.global_position.x >= impact_pos.x else -1.0
				if player_ref.has_method("take_damage"):
					player_ref.take_damage(GameManager.get_scaled_enemy_damage(25.0), kb)
			mortars.remove_at(i)

# --- ATTACK 4: ROCKET OVERDRIVE CHARGE & WALL CRASH STUN (2x Critical Damage Window!) ---
func _start_telegraph_charge() -> void:
	current_state = State.TELEGRAPH_CHARGE
	state_duration = 1.15
	state_timer = state_duration
	if player_ref:
		facing_direction = -1 if player_ref.global_position.x < global_position.x else 1
		sprite.scale.x = facing_direction
	sprite.frame = 2
	charge_hit_player = false

func _process_telegraph_charge(_dt: float) -> void:
	sprite.frame = 2
	sprite.offset.x = randf_range(-2.5, 2.5)
	if state_timer <= 0.0:
		sprite.offset = Vector2.ZERO
		current_state = State.ROCKET_CHARGE
		state_duration = 2.4
		state_timer = state_duration
		if player_ref and player_ref.has_method("add_camera_shake"):
			player_ref.add_camera_shake(6.0, 0.25)

func _process_rocket_charge(dt: float, speed_mult: float) -> void:
	sprite.frame = 2
	var charge_spd = (600.0 if phase == 2 else 490.0) * speed_mult
	velocity.x = facing_direction * charge_spd
	if not is_on_floor():
		velocity.y += 980.0 * dt
	move_and_slide()

	# Check hit on player during charge
	if player_ref and not charge_hit_player:
		if global_position.distance_to(player_ref.global_position) <= 62.0:
			charge_hit_player = true
			if player_ref.has_method("take_damage"):
				player_ref.take_damage(GameManager.get_scaled_enemy_damage(32.0), float(facing_direction))
			player_ref.velocity = Vector2(facing_direction * 280.0, -240.0)

	# Check Wall Crash at Arena Boundaries!
	var hit_left_wall = (facing_direction < 0 and global_position.x <= ARENA_LEFT + 62.0)
	var hit_right_wall = (facing_direction > 0 and global_position.x >= ARENA_RIGHT - 62.0)

	if hit_left_wall or hit_right_wall or is_on_wall() or state_timer <= 0.0:
		velocity.x = -facing_direction * 90.0
		_trigger_wall_crash_stun()

func _trigger_wall_crash_stun() -> void:
	current_state = State.STUNNED
	state_duration = 3.8 # 3.8s critical vulnerability window!
	state_timer = state_duration
	velocity = Vector2.ZERO
	sprite.frame = 3
	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(12.0, 0.45)
	_spawn_explosion_fx("emp", global_position + Vector2(facing_direction * 30.0, 0.0))

func _process_stunned(_dt: float) -> void:
	sprite.frame = 3
	velocity = Vector2.ZERO
	if state_timer <= 0.0:
		_enter_stalk_state(1.2)

# -------------------------------------------------------------------------
# DAMAGE, PHASE 2 ENRAGE & VICTORY SEQUENCE
# -------------------------------------------------------------------------
func apply_grenade_effect(g_type: String, _blast_pos: Vector2, _falloff: float) -> void:
	if current_state == State.DORMANT or current_state == State.INTRO or current_state == State.DEFEATED:
		return
	match g_type:
		"cryo":
			chill_timer = max(chill_timer, 3.0)
			if sprite:
				var tw = create_tween()
				tw.tween_property(sprite, "modulate", Color(0.4, 0.9, 1.5, 1.0), 0.1)
				tw.tween_property(sprite, "modulate", Color(1.0, 1.0, 1.0, 1.0), 1.4)
		"emp":
			# EMP grenade short-circuits the Boss into STUNNED state for 2.6s!
			if current_state != State.STUNNED:
				current_state = State.STUNNED
				state_duration = 2.6
				state_timer = 2.6
				velocity = Vector2.ZERO
				if compactor_piston:
					compactor_piston.visible = false
				slam_target_xs.clear()
				if sprite:
					sprite.frame = 3
		"fire", "fire_pool":
			burn_timer = max(burn_timer, 3.0)

func take_damage(amount: float, _knockback: float = 0.0) -> void:
	if current_state == State.DORMANT or current_state == State.INTRO or current_state == State.DEFEATED:
		return

	# Double damage (2X CRITICAL!) while STUNNED!
	if current_state == State.STUNNED:
		amount *= 2.0

	hp = max(0.0, hp - amount)

	# Hit flash feedback
	if sprite:
		var flash_col = Color(2.4, 2.0, 0.5, 1.0) if current_state == State.STUNNED else Color(2.2, 0.45, 0.45, 1.0)
		var base_col = Color(1.25, 0.72, 0.65, 1.0) if phase == 2 else Color(1.0, 1.0, 1.0, 1.0)
		var tw = create_tween()
		tw.tween_property(sprite, "modulate", flash_col, 0.04)
		tw.tween_property(sprite, "modulate", base_col, 0.12)

	# Trigger Phase 2 Enrage at <= 50% HP!
	if hp <= max_hp * 0.5 and phase == 1:
		phase = 2
		_spawn_explosion_fx("fire", global_position)
		if player_ref and player_ref.has_method("add_camera_shake"):
			player_ref.add_camera_shake(10.0, 0.4)
		print("BOSS ENRAGED! Phase 2 Overdrive Activated!")

	GameManager.boss_health_changed.emit(hp, max_hp, phase)
	if hp <= 0.0:
		_start_defeated_sequence()

func _start_defeated_sequence() -> void:
	current_state = State.DEFEATED
	state_duration = 2.2
	state_timer = state_duration
	death_explosion_timer = 0.0
	velocity = Vector2.ZERO
	shockwaves.clear()
	mortars.clear()
	slam_target_xs.clear()
	if compactor_piston:
		compactor_piston.visible = false
	if sprite:
		sprite.frame = 3
	if player_ref and player_ref.has_method("add_camera_shake"):
		player_ref.add_camera_shake(14.0, 1.8)

func _process_defeated_sequence(dt: float) -> void:
	state_timer -= dt
	death_explosion_timer -= dt
	if sprite:
		sprite.offset = Vector2(randf_range(-5.0, 5.0), randf_range(-4.0, 4.0))
		sprite.modulate = Color(2.0, 0.5, 0.2, clamp(state_timer / 2.2, 0.0, 1.0))

	if death_explosion_timer <= 0.0:
		death_explosion_timer = 0.26
		var rand_off = Vector2(randf_range(-42.0, 42.0), randf_range(-48.0, 40.0))
		_spawn_explosion_fx("frag" if randf() > 0.4 else "emp", global_position + rand_off)

	queue_redraw()

	if state_timer <= 0.0:
		_spawn_explosion_fx("fire", global_position)
		GameManager.spawn_mob_loot(global_position, 1.0, 3)
		visible = false
		set_physics_process(false)
		if collision_shape:
			collision_shape.set_deferred("disabled", true)
		if hurtbox:
			hurtbox.set_deferred("monitoring", false)
			hurtbox.set_deferred("monitorable", false)
		GameManager.boss_defeated.emit()
		print("THE CRUSHER TITAN DEFEATED!")

func _spawn_explosion_fx(type: String, world_pos: Vector2) -> void:
	var parent_node = get_parent()
	if parent_node:
		var fx = ExplosionFXClass.new()
		parent_node.add_child(fx)
		fx.init(type, world_pos)

# -------------------------------------------------------------------------
# CUSTOM WORLD-SPACE VECTORS & TELEGRAPH RENDERING
# -------------------------------------------------------------------------
func _draw() -> void:
	var font = ThemeDB.fallback_font
	var t_sec = Time.get_ticks_msec() / 1000.0

	# 0. Dormant Ambush Floor Marker
	if current_state == State.DORMANT:
		var floor_pt = to_local(Vector2(4650.0, FLOOR_Y))
		var pulse = 0.4 + 0.3 * sin(t_sec * 4.0)
		draw_arc(floor_pt, 48.0, PI, TAU, 24, Color(1.0, 0.3, 0.1, pulse), 2.0)
		return

	# 1. Arena Lockdown Energy Gates (Left x=4150, Right x=5100)
	if current_state != State.DEFEATED:
		for gate_x in [ARENA_LEFT, ARENA_RIGHT]:
			var g_top = to_local(Vector2(gate_x, FLOOR_Y - 260.0))
			var g_bot = to_local(Vector2(gate_x, FLOOR_Y))
			var gate_alpha = 0.55 + 0.25 * sin(t_sec * 10.0)
			draw_line(g_top, g_bot, Color(1.0, 0.25, 0.15, gate_alpha * 0.5), 8.0)
			draw_line(g_top, g_bot, Color(1.0, 0.65, 0.2, gate_alpha), 2.5)

	# 2. INTRO SKY-DROP WARNING ZONE
	if current_state == State.INTRO and intro_stage == 0:
		var drop_pt = to_local(Vector2(4650.0, FLOOR_Y))
		var pulse = 0.5 + 0.45 * sin(t_sec * 18.0)
		draw_rect(Rect2(drop_pt + Vector2(-70, -14), Vector2(140, 14)), Color(1.0, 0.15, 0.1, pulse), true)
		draw_line(drop_pt + Vector2(0, -520), drop_pt, Color(1.0, 0.2, 0.2, 0.85), 3.0)
		if font:
			draw_string(font, drop_pt + Vector2(-115, -28), "! WARNING: CRUSHER TITAN INCOMING !", HORIZONTAL_ALIGNMENT_CENTER, -1, 13, Color(1.0, 0.3, 0.2, 1.0))

	# 3. HYDRAULIC CRUSHER SLAM TELEGRAPH ZONES (2.0s Warning + Countdown Progress!)
	if current_state == State.TELEGRAPH_SLAM or current_state == State.SLAM_ACTIVE:
		var progress = 1.0 - clamp(state_timer / max(state_duration, 0.01), 0.0, 1.0)
		for tx in slam_target_xs:
			var zone_center = to_local(Vector2(tx, FLOOR_Y))
			var zw = 110.0
			var zh = 22.0
			var rect = Rect2(zone_center + Vector2(-zw * 0.5, -zh), Vector2(zw, zh))
			var flash_a = 0.35 + 0.4 * abs(sin(t_sec * 14.0))
			draw_rect(rect, Color(1.0, 0.12, 0.12, flash_a), true)
			draw_rect(rect, Color(1.0, 0.85, 0.2, 0.95), false, 2.0)

			# Shrinking inner fill bar showing exact impact timing
			var fill_w = zw * progress
			draw_rect(Rect2(zone_center + Vector2(-fill_w * 0.5, -6), Vector2(fill_w, 6)), Color(1.0, 0.9, 0.2, 0.95), true)

			# Vertical laser guide lines from ceiling
			draw_line(zone_center + Vector2(-zw * 0.45, -360), zone_center + Vector2(-zw * 0.45, 0), Color(1.0, 0.2, 0.2, 0.55), 1.5)
			draw_line(zone_center + Vector2(zw * 0.45, -360), zone_center + Vector2(zw * 0.45, 0), Color(1.0, 0.2, 0.2, 0.55), 1.5)

			if current_state == State.TELEGRAPH_SLAM and font:
				var rem_str = "CRUSHER SLAM: %.1fs [DODGE!]" % max(0.0, state_timer)
				draw_string(font, zone_center + Vector2(-82, -30), rem_str, HORIZONTAL_ALIGNMENT_LEFT, -1, 11, Color(1.0, 0.9, 0.3, 1.0))

	# 4. SEISMIC SHOCKWAVE TELEGRAPH & TRAVELLING WAVES
	if current_state == State.TELEGRAPH_SHOCKWAVE:
		var r = 24.0 + 18.0 * sin(t_sec * 15.0)
		draw_arc(Vector2(0, 42), r, 0.0, TAU, 24, Color(0.25, 0.9, 1.0, 0.9), 3.0)
		if font:
			draw_string(font, Vector2(-85, -72), "! SEISMIC WAVE - JUMP !", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.3, 0.95, 1.0, 1.0))

	for sw in shockwaves:
		var sw_pt = to_local(Vector2(sw["x"], FLOOR_Y))
		var h = sw["h"]
		var d = sw["dir"]
		var poly = PackedVector2Array([
			sw_pt + Vector2(-18.0 * d, 0),
			sw_pt + Vector2(16.0 * d, 0),
			sw_pt + Vector2(6.0 * d, -h),
			sw_pt + Vector2(-8.0 * d, -h * 0.65)
		])
		draw_colored_polygon(poly, Color(1.0, 0.5, 0.1, 0.9))
		draw_polyline(PackedVector2Array([poly[0], poly[2], poly[1]]), Color(1.0, 0.95, 0.5, 1.0), 2.2)

	# 5. MOLTEN MORTAR BARRAGE BOMBS & FLOOR LANDING RETICLES
	if current_state == State.TELEGRAPH_MORTAR and font:
		draw_string(font, Vector2(-85, -72), "! MOLTEN MORTAR BARRAGE !", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(1.0, 0.55, 0.15, 1.0))

	for m in mortars:
		var b_pt = to_local(m["pos"])
		var t_pt = to_local(Vector2(m["target_x"], FLOOR_Y - 2.0))
		# Floor landing bullseye
		draw_arc(t_pt, 36.0, 0.0, TAU, 20, Color(1.0, 0.35, 0.1, 0.85), 2.0)
		draw_circle(t_pt, 12.0 + 6.0 * sin(t_sec * 16.0), Color(1.0, 0.6, 0.1, 0.45))
		# Falling molten bomb
		draw_circle(b_pt, 9.0, Color(1.0, 0.35, 0.05, 0.95))
		draw_circle(b_pt, 5.0, Color(1.0, 0.95, 0.4, 1.0))

	# 6. ROCKET CHARGE DIRECTIONAL TRACK & THRUSTER FLAMES
	if current_state == State.TELEGRAPH_CHARGE:
		var track_len = 360.0 * float(facing_direction)
		draw_line(Vector2(0, 35), Vector2(track_len, 35), Color(1.0, 0.15, 0.15, 0.65), 14.0)
		draw_line(Vector2(0, 35), Vector2(track_len, 35), Color(1.0, 0.85, 0.2, 0.95), 2.5)
		if font:
			draw_string(font, Vector2(-95, -72), "! ROCKET CHARGE - DODGE !", HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(1.0, 0.3, 0.2, 1.0))
	elif current_state == State.ROCKET_CHARGE:
		# Rear jet thruster cone
		var back_x = -44.0 * float(facing_direction)
		var flame_tip = Vector2(back_x - 45.0 * float(facing_direction), 10.0 + randf_range(-6.0, 6.0))
		draw_colored_polygon(PackedVector2Array([
			Vector2(back_x, -6),
			Vector2(back_x, 24),
			flame_tip
		]), Color(1.0, 0.45, 0.05, 0.9))

	# 7. STUNNED VULNERABILITY HALO (2X DAMAGE WINDOW!)
	if current_state == State.STUNNED:
		for i in range(4):
			var ang = t_sec * 5.5 + float(i) * (TAU / 4.0)
			var star_pt = Vector2(cos(ang) * 32.0, -64.0 + sin(ang) * 8.0)
			draw_circle(star_pt, 4.5, Color(1.0, 0.9, 0.2, 0.95))
			draw_circle(star_pt, 2.2, Color(1.0, 1.0, 1.0, 1.0))
		if font:
			var stun_str = "STUNNED! 2X DAMAGE (%.1fs)" % max(0.0, state_timer)
			draw_string(font, Vector2(-88, -82), stun_str, HORIZONTAL_ALIGNMENT_LEFT, -1, 12, Color(0.25, 0.95, 1.0, 1.0))
