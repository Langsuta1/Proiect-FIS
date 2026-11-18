extends CharacterBody2D
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

func take_damage(amount: float, knockback: float = 0.0) -> void:
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
