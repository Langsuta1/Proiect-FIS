extends StaticBody2D
# scrap_barricade.gd - Destructible scrap barricade blocking tutorial progression

@export var max_hp: float = 45.0
var hp: float = 45.0
var is_destroyed: bool = false

@onready var sprite: Sprite2D = $Sprite2D
@onready var collision_shape: CollisionShape2D = $CollisionShape2D
@onready var hurtbox: Area2D = $Hurtbox

func _ready() -> void:
	hp = max_hp
	if hurtbox:
		hurtbox.add_to_group("enemies")

func take_damage(amount: float, _knockback: float = 0.0) -> void:
	if is_destroyed:
		return
	hp -= amount

	# White damage flash
	if sprite:
		var tw = create_tween()
		tw.tween_property(sprite, "modulate", Color(2.5, 2.5, 2.5, 1.0), 0.05)
		tw.tween_property(sprite, "modulate", Color(1.0, 1.0, 1.0, 1.0), 0.12)

	if hp <= 0.0:
		_shatter()

func _shatter() -> void:
	is_destroyed = true
	if collision_shape:
		collision_shape.set_deferred("disabled", true)
	if hurtbox:
		hurtbox.set_deferred("monitoring", false)
		hurtbox.set_deferred("monitorable", false)

	if sprite:
		var tw = create_tween()
		tw.tween_property(sprite, "scale", Vector2(1.25, 0.3), 0.16)
		tw.parallel().tween_property(sprite, "modulate", Color(1.0, 0.6, 0.2, 0.0), 0.16)
		tw.tween_callback(queue_free)
	else:
		queue_free()
