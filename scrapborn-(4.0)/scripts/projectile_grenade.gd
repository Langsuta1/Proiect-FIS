extends CharacterBody2D
# projectile_grenade.gd - Bouncing Grenade with 2-second fuse, Angry-Birds ballistic physics,
# rich multi-layered explosion animation, and full status effects on BOTH Enemies and Player!

@export var grenade_type: String = "frag"
var fuse_time: float = 2.0
var fuse_timer: float = 2.0
var custom_gravity: float = 780.0
var is_exploded: bool = false

@onready var sprite: Sprite2D = $Sprite2D
@onready var blast_area: Area2D = $BlastArea
@onready var blast_shape: CollisionShape2D = $BlastArea/CollisionShape2D

const ExplosionFXClass = preload("res://scripts/grenade_explosion_fx.gd")

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
	rotation += velocity.x * 0.02 * dt * 60.0

	# 3. Bounce Physics with Solid World
	var collision = move_and_collide(velocity * dt)
	if collision:
		velocity = velocity.bounce(collision.get_normal()) * 0.54
		velocity.x *= 0.78
		if abs(velocity.y) < 25.0 and abs(velocity.x) < 20.0:
			velocity = Vector2.ZERO

	# 4. Fuse Countdown & Faster Blinking
	fuse_timer -= dt
	var blink_rate = clamp(1.0 / max(0.12, fuse_timer), 2.5, 20.0)
	if fmod(Time.get_ticks_msec() / (1000.0 / blink_rate), 2.0) > 1.0:
		sprite.modulate = Color(2.5, 0.45, 0.45, 1.0)
	else:
		sprite.modulate = Color(1.0, 1.0, 1.0, 1.0)

	queue_redraw()

	if fuse_timer <= 0.0:
		detonate()

func _draw() -> void:
	if is_exploded:
		return
	# Subtle danger radius warning pulse when fuse is below 0.8s
	if fuse_timer < 0.85:
		var pulse = 1.0 - (fuse_timer / 0.85)
		var warn_col = Color(1.0, 0.35, 0.15, 0.28 * pulse)
		if grenade_type == "cryo":
			warn_col = Color(0.35, 0.85, 1.0, 0.28 * pulse)
		elif grenade_type == "emp":
			warn_col = Color(0.2, 0.8, 1.0, 0.28 * pulse)
		draw_arc(Vector2.ZERO, 88.0 * pulse, 0.0, TAU, 28, warn_col, 1.5)

func detonate() -> void:
	if is_exploded: return
	is_exploded = true
	velocity = Vector2.ZERO

	var blast_dmg = 85.0
	match grenade_type:
		"emp":
			blast_dmg = 65.0
		"cryo":
			blast_dmg = 55.0
		"fire":
			blast_dmg = 70.0

	var blast_radius: float = 88.0

	# 1. Gather all entities in blast radius (Physics Query + Group Distance Check for 100% reliability)
	var space = get_world_2d().direct_space_state
	var query = PhysicsShapeQueryParameters2D.new()
	var circle = CircleShape2D.new()
	circle.radius = blast_radius
	query.shape = circle
	query.transform = Transform2D(0.0, global_position)
	query.collide_with_areas = true
	query.collide_with_bodies = true
	query.collision_mask = 1 | 2 | 8 # World/Barricades (1), Player (2), Enemies/Boss (8)

	var hits = space.intersect_shape(query, 32)
	var hit_targets: Array = []

	for h in hits:
		var col = h.get("collider")
		if col:
			var target = col.get_parent() if (col is Area2D and col.get_parent()) else col
			if is_instance_valid(target) and target != self and target not in hit_targets:
				hit_targets.append(target)

	# Ensure Player, Enemies, and Boss within blast_radius are never missed
	for grp in ["player", "enemies", "boss"]:
		for node in get_tree().get_nodes_in_group(grp):
			if not is_instance_valid(node):
				continue
			var target = node.get_parent() if (node is Area2D and node.get_parent()) else node
			if is_instance_valid(target) and target != self and target not in hit_targets:
				if global_position.distance_to(target.global_position) <= blast_radius:
					hit_targets.append(target)

	# 2. Apply Damage & Specific Grenade Status Effects to Player and Enemies!
	for target in hit_targets:
		if not is_instance_valid(target):
			continue
		var dist = global_position.distance_to(target.global_position)
		if dist > blast_radius + 16.0:
			continue
		var falloff = clamp(1.0 - (dist / (blast_radius + 18.0)), 0.45, 1.0)
		var kb_dir = 1.0 if target.global_position.x >= global_position.x else -1.0

		if target.is_in_group("player"):
			# Player takes self-damage and receives full grenade status effects (Freeze, EMP, Burn, Blast Knockback)!
			if target.has_method("apply_grenade_effect"):
				target.apply_grenade_effect(grenade_type, global_position, falloff)
			elif target.has_method("take_damage"):
				target.take_damage(30.0 * falloff, kb_dir)
		else:
			# Enemies, Boss, and Barricades
			if target.has_method("take_damage"):
				target.take_damage(blast_dmg * falloff, kb_dir)
			if target.has_method("apply_grenade_effect"):
				target.apply_grenade_effect(grenade_type, global_position, falloff)

	# 3. Spawn Rich Multi-Layered Explosion Animation
	if sprite:
		sprite.visible = false
	queue_redraw()

	var parent_node = get_parent()
	if parent_node:
		var fx = ExplosionFXClass.new()
		parent_node.add_child(fx)
		fx.init(grenade_type, global_position)

	queue_free()
