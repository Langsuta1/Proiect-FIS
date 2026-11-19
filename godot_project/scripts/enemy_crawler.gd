extends CharacterBody2D
class_name EnemyCrawler
# enemy_crawler.gd - Scrap Crawler with Grenade Status Effects (Freeze, EMP Stun, Burn DoT, Knockback)

@export var patrol_distance: float = 140.0
@export var speed: float = 45.0
@export var max_hp: float = 32.0

var hp: float = 32.0
var start_x: float = 0.0
var direction: int = 1
var anim_timer: float = 0.0

# Grenade Status Timers
var freeze_timer: float = 0.0
var emp_timer: float = 0.0
var burn_timer: float = 0.0
var burn_tick: float = 0.0
var knockback_vel_x: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox
@onready var damage_area: Area2D = $DamageArea

func _ready() -> void:
	start_x = global_position.x
	max_hp = max_hp * GameManager.difficulty_multiplier
	hp = max_hp
	hurtbox.add_to_group("enemies")
	damage_area.body_entered.connect(_on_damage_body_entered)

func _physics_process(dt: float) -> void:
	if not is_on_floor():
		velocity.y += 850.0 * dt

	# Status Effect Timers
	if burn_timer > 0.0:
		burn_timer -= dt
		burn_tick += dt
		if burn_tick >= 0.5:
			burn_tick = 0.0
			take_damage(6.0, 0.0)

	if freeze_timer > 0.0:
		freeze_timer -= dt
		velocity.x = move_toward(velocity.x, 0.0, 600.0 * dt)
		sprite.modulate = Color(0.4, 0.9, 1.5, 1.0)
		move_and_slide()
		queue_redraw()
		return
	elif emp_timer > 0.0:
		emp_timer -= dt
		velocity.x = move_toward(velocity.x, 0.0, 600.0 * dt)
		sprite.modulate = Color(0.5, 0.9, 1.4, 1.0)
		move_and_slide()
		queue_redraw()
		return

	if burn_timer <= 0.0:
		sprite.modulate = Color(1, 1, 1, 1)

	if abs(knockback_vel_x) > 5.0:
		velocity.x = knockback_vel_x
		knockback_vel_x = move_toward(knockback_vel_x, 0.0, 500.0 * dt)
	else:
		velocity.x = direction * speed

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	anim_timer += dt
	sprite.frame = int(anim_timer / 0.12) % 4

	move_and_slide()
	queue_redraw()

func _draw() -> void:
	if freeze_timer > 0.0:
		# Ice Block Encasement
		var rect = Rect2(Vector2(-15, -14), Vector2(30, 26))
		draw_rect(rect, Color(0.35, 0.85, 1.0, 0.45), true)
		draw_rect(rect, Color(0.85, 0.98, 1.0, 0.9), false, 1.5)
	elif emp_timer > 0.0:
		# Electric arcs
		var t = Time.get_ticks_msec() / 45.0
		draw_line(Vector2(-12, -6 + sin(t) * 4), Vector2(12, 4 - cos(t) * 4), Color(0.3, 0.95, 1.0, 0.95), 1.8)
	elif burn_timer > 0.0:
		var t = Time.get_ticks_msec() / 70.0
		draw_circle(Vector2(sin(t) * 6.0, -8.0), 4.5, Color(1.0, 0.45, 0.05, 0.75))

func _on_damage_body_entered(body: Node2D) -> void:
	if freeze_timer > 0.0 or emp_timer > 0.0:
		return
	if body is Player:
		var kb_dir = 1.0 if body.global_position.x > global_position.x else -1.0
		body.take_damage(20.0, kb_dir)

func apply_grenade_effect(g_type: String, blast_pos: Vector2, falloff: float) -> void:
	var dir = sign(global_position.x - blast_pos.x)
	if dir == 0: dir = 1.0
	match g_type:
		"cryo":
			freeze_timer = max(freeze_timer, 2.5 * falloff)
		"emp":
			emp_timer = max(emp_timer, 2.8 * falloff)
		"fire", "fire_pool":
			burn_timer = max(burn_timer, 3.0)
		"frag":
			knockback_vel_x = dir * 220.0 * falloff
			velocity.y = -140.0 * falloff

func take_damage(amount: float, knockback: float = 0.0) -> void:
	hp -= amount
	if knockback != 0.0:
		knockback_vel_x = knockback * 140.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
