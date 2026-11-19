extends Node2D
# grapple_ring.gd - Overhead Grappling Anchor Ring with closest-node targeting reticle & glow

@onready var sprite: Sprite2D = $Sprite2D
var time_accum: float = 0.0
var is_closest_target: bool = false
var is_attached_target: bool = false

func _ready() -> void:
	add_to_group("grapple_rings")

func _process(dt: float) -> void:
	time_accum += dt
	var player = get_tree().get_first_node_in_group("player")
	is_closest_target = false
	is_attached_target = false

	if player:
		if player.get("is_grappling") and player.get("current_grapple_ring") == self:
			is_attached_target = true
		elif player.get("closest_available_ring") == self:
			is_closest_target = true

	if sprite:
		if is_attached_target:
			sprite.scale = Vector2(1.18, 1.18)
			sprite.modulate = Color(0.4, 1.4, 1.8, 1.0)
		elif is_closest_target:
			var pulse = 1.0 + sin(time_accum * 8.0) * 0.1
			sprite.scale = Vector2(pulse, pulse)
			sprite.modulate = Color(1.5, 1.25, 0.4, 1.0)
		else:
			sprite.scale = Vector2(1.0 + sin(time_accum * 3.0) * 0.04, 1.0 + sin(time_accum * 3.0) * 0.04)
			sprite.modulate = Color(0.85, 0.88, 0.95, 0.85)

	queue_redraw()

func _draw() -> void:
	if is_closest_target and not is_attached_target:
		# Draw crisp animated lock-on reticle around the closest valid ring!
		var rad = 20.0 + sin(time_accum * 8.0) * 2.5
		var col = Color(0.25, 0.92, 1.0, 0.9)
		draw_arc(Vector2.ZERO, rad, -0.4, 0.4, 8, col, 2.0)
		draw_arc(Vector2.ZERO, rad, PI - 0.4, PI + 0.4, 8, col, 2.0)
		draw_arc(Vector2.ZERO, rad, PI * 0.5 - 0.4, PI * 0.5 + 0.4, 8, Color(1.0, 0.78, 0.2, 0.9), 2.0)
		draw_arc(Vector2.ZERO, rad, -PI * 0.5 - 0.4, -PI * 0.5 + 0.4, 8, Color(1.0, 0.78, 0.2, 0.9), 2.0)
	elif is_attached_target:
		draw_arc(Vector2.ZERO, 18.0, 0.0, TAU, 24, Color(0.22, 0.9, 1.0, 0.75), 2.0)
