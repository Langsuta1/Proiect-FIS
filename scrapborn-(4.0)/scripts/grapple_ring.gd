extends Node2D
# grapple_ring.gd - Overhead Grappling Anchor Ring with glow feedback

@onready var sprite: Sprite2D = $Sprite2D
var time_accum: float = 0.0

func _ready() -> void:
	add_to_group("grapple_rings")

func _process(dt: float) -> void:
	time_accum += dt
	if sprite:
		# Subtle bobbing
		sprite.scale = Vector2(1.0 + sin(time_accum * 3.5) * 0.07, 1.0 + sin(time_accum * 3.5) * 0.07)

		var player = get_tree().get_first_node_in_group("player")
		if player and global_position.distance_to(player.global_position) < 380.0:
			# High-visibility neon amber glow when in latch range
			sprite.modulate = Color(1.4, 1.15, 0.45, 1.0)
		else:
			sprite.modulate = Color(1.0, 1.0, 1.0, 0.9)
