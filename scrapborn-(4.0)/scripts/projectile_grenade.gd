extends CharacterBody2D
# projectile_grenade.gd - Bouncing Grenade with 2-second fuse and Angry-Birds ballistic physics

@export var grenade_type: String = "frag"
var fuse_time: float = 2.0
var fuse_timer: float = 2.0
var custom_gravity: float = 780.0
var is_exploded: bool = false

@onready var sprite: Sprite2D = $Sprite2D
@onready var blast_area: Area2D = $BlastArea
@onready var blast_shape: CollisionShape2D = $BlastArea/CollisionShape2D

var tex_frag = preload("res://assets/grenade_frag_32x32.png")
var tex_emp = preload("res://assets/grenade_emp_32x32.png")
var tex_cryo = preload("res://assets/grenade_cryo_32x32.png")
var tex_fire = preload("res://assets/grenade_fire_32x32.png")

func _ready() -> void:
	fuse_timer = fuse_time
	_apply_texture()

func _apply_texture() -> void:
	if not sprite: return
	match grenade_type:
		"emp": sprite.texture = tex_emp
		"cryo": sprite.texture = tex_cryo
		"fire": sprite.texture = tex_fire
		_: sprite.texture = tex_frag

func _physics_process(dt: float) -> void:
	if is_exploded: return

	# 1. Gravity & Air Resistance
	velocity.y += custom_gravity * dt
	velocity.x *= pow(0.988, dt * 60.0)

	# 2. Rotation during flight
	rotation += velocity.x * 0.02

	# 3. Bounce Physics with Solid World
	var collision = move_and_collide(velocity * dt)
	if collision:
		velocity = velocity.bounce(collision.get_normal()) * 0.54
		velocity.x *= 0.78
		if abs(velocity.y) < 25.0 and abs(velocity.x) < 20.0:
			velocity = Vector2.ZERO

	# 4. Fuse Countdown & Faster Blinking
	fuse_timer -= dt
	var blink_rate = clamp(1.0 / max(0.12, fuse_timer), 2.0, 18.0)
	if fmod(Time.get_ticks_msec() / (1000.0 / blink_rate), 2.0) > 1.0:
		sprite.modulate = Color(2.5, 0.4, 0.4, 1.0)
	else:
		sprite.modulate = Color(1.0, 1.0, 1.0, 1.0)

	if fuse_timer <= 0.0:
		detonate()

func detonate() -> void:
	if is_exploded: return
	is_exploded = true
	velocity = Vector2.ZERO

	var blast_color = Color(1.0, 0.55, 0.1, 0.9)
	var blast_dmg = 85.0
	match grenade_type:
		"emp":
			blast_color = Color(0.2, 0.8, 1.0, 0.9)
			blast_dmg = 65.0
		"cryo":
			blast_color = Color(0.5, 0.9, 1.0, 0.9)
			blast_dmg = 55.0
		"fire":
			blast_color = Color(1.0, 0.3, 0.1, 0.9)
			blast_dmg = 70.0

	# Damage all enemies, bosses, and destructible barricades in radius (75px)
	var space = get_world_2d().direct_space_state
	var query = PhysicsShapeQueryParameters2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 75.0
	query.shape = circle
	query.transform = Transform2D(0.0, global_position)
	query.collide_with_areas = true
	query.collide_with_bodies = true
	query.collision_mask = 8 | 1 # Enemies & Destructibles

	var hits = space.intersect_shape(query, 32)
	var damaged_entities = []
	for h in hits:
		var col = h.get("collider")
		if col:
			var target = col
			if col is Area2D and col.get_parent():
				target = col.get_parent()
			if target not in damaged_entities and target != self and not target.is_in_group("player"):
				damaged_entities.append(target)
				if target.has_method("take_damage"):
					var dist = global_position.distance_to(target.global_position)
					var falloff = clamp(1.0 - (dist / 90.0), 0.5, 1.0)
					target.take_damage(blast_dmg * falloff, 0.0)

	# Visual shockwave ring & fireball
	if sprite:
		sprite.visible = false
	queue_redraw()

	var blast_fx = Node2D.new()
	get_parent().add_child(blast_fx)
	blast_fx.global_position = global_position
	var circ = ColorRect.new()
	circ.custom_minimum_size = Vector2(80, 80)
	circ.position = Vector2(-40, -40)
	circ.color = blast_color
	blast_fx.add_child(circ)

	var tw = blast_fx.create_tween()
	tw.tween_property(circ, "scale", Vector2(1.8, 1.8), 0.22)
	tw.parallel().tween_property(circ, "modulate:a", 0.0, 0.22)
	tw.tween_callback(blast_fx.queue_free)

	get_tree().create_timer(0.25).timeout.connect(queue_free)
