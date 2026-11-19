extends Node2D
class_name AirJumpEffect
# air_jump_effect.gd - Cyberpunk thruster burst & expanding energy shockwave for mid-air double jump

@onready var particles: CPUParticles2D = get_node_or_null("CPUParticles2D")

var ring_radius_x: float = 5.0
var ring_radius_y: float = 2.0
var streak_length: float = 3.0
var effect_alpha: float = 1.0

func _ready() -> void:
	if particles:
		particles.emitting = true

	var tween = create_tween()
	if tween:
		tween.set_parallel(true)
		# Expand shockwave ring horizontally and slightly vertically
		tween.tween_property(self, "ring_radius_x", 30.0, 0.28).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tween.tween_property(self, "ring_radius_y", 8.0, 0.28).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		# Extend thruster jet streaks downward
		tween.tween_property(self, "streak_length", 16.0, 0.18).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		# Fade out opacity
		tween.tween_property(self, "effect_alpha", 0.0, 0.32).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
		
		# Auto queue_free after particles and animations finish
		var cleanup_timer = get_tree().create_timer(0.36)
		cleanup_timer.timeout.connect(queue_free)
	else:
		queue_free()

func _process(_delta: float) -> void:
	queue_redraw()

func _draw() -> void:
	if effect_alpha <= 0.01:
		return

	# 1. Dual-tone expanding shockwave ring
	var pts: PackedVector2Array = []
	var segments: int = 24
	for i in range(segments + 1):
		var angle = (float(i) / segments) * TAU
		pts.append(Vector2(cos(angle) * ring_radius_x, sin(angle) * ring_radius_y))

	# Outer cyan energy glow
	draw_polyline(pts, Color(0.2, 0.8, 1.0, effect_alpha * 0.7), 3.0)
	# Inner intense white-hot core
	draw_polyline(pts, Color(0.92, 1.0, 1.0, effect_alpha * 0.95), 1.2)

	# 2. Downward thruster jet streaks from left and right boots
	var jet_cyan = Color(0.25, 0.85, 1.0, effect_alpha * 0.85)
	var jet_core = Color(1.0, 1.0, 1.0, effect_alpha * 0.95)

	# Left boot thruster
	draw_line(Vector2(-5, 0), Vector2(-8, streak_length), jet_cyan, 2.4)
	draw_line(Vector2(-5, 0), Vector2(-8, streak_length * 0.65), jet_core, 1.1)

	# Right boot thruster
	draw_line(Vector2(5, 0), Vector2(8, streak_length), jet_cyan, 2.4)
	draw_line(Vector2(5, 0), Vector2(8, streak_length * 0.65), jet_core, 1.1)

	# 3. Initial ignition flash at center
	if effect_alpha > 0.5:
		var flash_ratio = (effect_alpha - 0.5) * 2.0
		draw_circle(Vector2.ZERO, 4.0 * flash_ratio, Color(1.0, 1.0, 1.0, flash_ratio * 0.9))
