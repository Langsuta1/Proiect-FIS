@tool
extends StaticBody2D
class_name ClimbableWall
# climbable_wall.gd - Static wall/platform with explicit `climbable` tag and automatic
# yellow-black construction hazard stripe overlay for climbable walls.

@export var climbable: bool = false:
	set(value):
		climbable = value
		_sync_climbable_state()

var _overlay: Node2D = null

class HazardStripeOverlay extends Node2D:
	func _draw() -> void:
		var wall: StaticBody2D = get_parent() as StaticBody2D
		if not wall:
			return
		var is_climb: bool = bool(wall.get("climbable"))
		if not is_climb:
			return

		for child in wall.get_children():
			if child is CollisionShape2D:
				var col_shape: CollisionShape2D = child as CollisionShape2D
				if col_shape.shape is RectangleShape2D and not col_shape.disabled:
					var rect_shape: RectangleShape2D = col_shape.shape as RectangleShape2D
					var rect_size: Vector2 = rect_shape.size * col_shape.scale.abs()
					if rect_size.x <= 1.0 or rect_size.y <= 1.0:
						continue

					var top_left: Vector2 = col_shape.position - rect_size * 0.5
					var rect_poly := PackedVector2Array([
						top_left,
						top_left + Vector2(rect_size.x, 0.0),
						top_left + rect_size,
						top_left + Vector2(0.0, rect_size.y)
					])

					# Dark matte construction tape base
					draw_rect(Rect2(top_left, rect_size), Color(0.07, 0.08, 0.1, 0.96), true)

					# Diagonal 45-degree yellow hazard stripes clipped cleanly to the wall rectangle
					var stripe_w: float = 14.0
					var period: float = 28.0
					var d: float = -rect_size.y - period
					var max_d: float = rect_size.x + rect_size.y + period
					while d <= max_d:
						var stripe_poly := PackedVector2Array([
							Vector2(top_left.x + d, top_left.y),
							Vector2(top_left.x + d + stripe_w, top_left.y),
							Vector2(top_left.x + d + stripe_w - rect_size.y, top_left.y + rect_size.y),
							Vector2(top_left.x + d - rect_size.y, top_left.y + rect_size.y)
						])
						var clipped: Array[PackedVector2Array] = Geometry2D.intersect_polygons(stripe_poly, rect_poly)
						for poly in clipped:
							if poly.size() >= 3:
								draw_colored_polygon(poly, Color(0.98, 0.78, 0.05, 0.98))
						d += period

					# Industrial dark border & subtle climbing edge rails
					draw_rect(Rect2(top_left, rect_size), Color(0.03, 0.04, 0.06, 1.0), false, 2.0)
					draw_line(
						top_left + Vector2(1.5, 2.0),
						top_left + Vector2(1.5, rect_size.y - 2.0),
						Color(1.0, 0.94, 0.45, 0.55),
						1.0
					)
					draw_line(
						top_left + Vector2(rect_size.x - 1.5, 2.0),
						top_left + Vector2(rect_size.x - 1.5, rect_size.y - 2.0),
						Color(1.0, 0.94, 0.45, 0.55),
						1.0
					)

func _ready() -> void:
	_sync_climbable_state()

func _ensure_overlay() -> void:
	if not is_inside_tree():
		return
	if _overlay == null or not is_instance_valid(_overlay):
		var existing: Node = get_node_or_null("_HazardStripeOverlay")
		if existing and existing is Node2D:
			_overlay = existing
		else:
			_overlay = HazardStripeOverlay.new()
			_overlay.name = "_HazardStripeOverlay"
			_overlay.z_index = 2
			add_child(_overlay)

func _sync_climbable_state() -> void:
	set_meta("climbable", climbable)
	if climbable:
		if not is_in_group("climbable_walls"):
			add_to_group("climbable_walls")
		if is_inside_tree():
			_ensure_overlay()
			if _overlay:
				_overlay.visible = true
				_overlay.queue_redraw()
	else:
		if is_in_group("climbable_walls"):
			remove_from_group("climbable_walls")
		if _overlay and is_instance_valid(_overlay):
			_overlay.visible = false
			_overlay.queue_redraw()
