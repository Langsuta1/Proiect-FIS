extends Sprite2D
class_name DashGhost

func init(
	p_texture: Texture2D,
	p_hframes: int,
	p_frame: int,
	p_scale: Vector2,
	p_offset: Vector2,
	p_global_pos: Vector2,
	p_color: Color = Color(0.25, 0.85, 1.0, 0.75),
	fade_time: float = 0.25,
	p_z_index: int = 0
) -> void:
	texture = p_texture
	hframes = p_hframes
	frame = p_frame
	scale = p_scale
	offset = p_offset
	global_position = p_global_pos
	modulate = p_color
	z_index = p_z_index

	var tween = create_tween()
	if tween:
		tween.set_trans(Tween.TRANS_QUAD)
		tween.set_ease(Tween.EASE_OUT)
		tween.tween_property(self, "modulate", Color(0.05, 0.35, 0.85, 0.0), fade_time)
		tween.finished.connect(queue_free)
	else:
		queue_free()
