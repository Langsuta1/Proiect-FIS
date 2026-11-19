extends Area2D
class_name DroppedItem
# dropped_item.gd - Physical world item with drop physics, color-coded label, and [E] / click pickup

@export var item_data: Dictionary = {}
@export var drop_velocity: Vector2 = Vector2.ZERO
@export var pickup_cooldown: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var label: Label = $Label
@onready var prompt: Label = $Prompt

var start_y: float = 0.0
var is_player_nearby: bool = false
var is_grounded: bool = false
var is_picked_up: bool = false

func _ready() -> void:
	add_to_group("dropped_items")
	start_y = position.y
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	input_event.connect(_on_input_event)
	GameManager.keybinds_updated.connect(_update_visuals)
	_update_visuals()

func _update_visuals() -> void:
	if item_data.is_empty():
		return

	var icon_name: String = item_data.get("icon", "cyber_pan_32x32")
	var tex_path: String = "res://assets/" + icon_name + ".png"
	if ResourceLoader.exists(tex_path):
		sprite.texture = load(tex_path)

	var count_val: int = int(item_data.get("count", 1))
	var count_txt: String = (" x" + str(count_val)) if (item_data.has("count") and count_val > 1) else ""
	label.text = item_data.get("name", "Unknown Item") + count_txt

	var item_type: String = item_data.get("type", "")
	match item_type:
		"consumable":
			label.add_theme_color_override("font_color", Color(0.28, 0.96, 0.56, 1.0))
		"grenade":
			label.add_theme_color_override("font_color", Color(1.0, 0.72, 0.2, 1.0))
		_:
			label.add_theme_color_override("font_color", Color(0.22, 0.74, 0.97, 1.0))

	prompt.text = "[" + GameManager.get_action_binding_text("interact") + "] / CLICK TO PICK UP"
	prompt.visible = is_player_nearby

func _physics_process(dt: float) -> void:
	if pickup_cooldown > 0.0:
		pickup_cooldown = max(0.0, pickup_cooldown - dt)

	if not is_grounded:
		drop_velocity.y = min(drop_velocity.y + 680.0 * dt, 520.0)
		drop_velocity.x = move_toward(drop_velocity.x, 0.0, 95.0 * dt)

		var space_state: PhysicsDirectSpaceState2D = get_world_2d().direct_space_state

		# Horizontal wall collision check
		if abs(drop_velocity.x) > 0.5:
			var h_dir: float = signf(drop_velocity.x)
			var h_ray: PhysicsRayQueryParameters2D = PhysicsRayQueryParameters2D.create(
				global_position,
				global_position + Vector2(drop_velocity.x * dt + h_dir * 10.0, 0.0)
			)
			h_ray.collision_mask = 1
			var h_hit: Dictionary = space_state.intersect_ray(h_ray)
			if not h_hit.is_empty():
				drop_velocity.x = 0.0
			else:
				position.x += drop_velocity.x * dt

		# Vertical floor / ceiling check
		if drop_velocity.y >= 0.0:
			var v_dist: float = max(drop_velocity.y * dt + 14.0, 15.0)
			var v_ray: PhysicsRayQueryParameters2D = PhysicsRayQueryParameters2D.create(
				global_position,
				global_position + Vector2(0.0, v_dist)
			)
			v_ray.collision_mask = 1
			var v_hit: Dictionary = space_state.intersect_ray(v_ray)
			if not v_hit.is_empty():
				global_position.y = v_hit.position.y - 14.0
				drop_velocity = Vector2.ZERO
				is_grounded = true
				start_y = position.y
			else:
				position.y += drop_velocity.y * dt
		else:
			var c_ray: PhysicsRayQueryParameters2D = PhysicsRayQueryParameters2D.create(
				global_position,
				global_position + Vector2(0.0, drop_velocity.y * dt - 10.0)
			)
			c_ray.collision_mask = 1
			var c_hit: Dictionary = space_state.intersect_ray(c_ray)
			if not c_hit.is_empty():
				drop_velocity.y = 0.0
			else:
				position.y += drop_velocity.y * dt

		if global_position.y > 980.0:
			queue_free()

func _process(_dt: float) -> void:
	if is_grounded or drop_velocity == Vector2.ZERO:
		sprite.position.y = sin(Time.get_ticks_msec() / 250.0) * 3.5
	else:
		sprite.position.y = 0.0

	if is_player_nearby and pickup_cooldown <= 0.0:
		if GameManager.setting_auto_pickup or Input.is_action_just_pressed("interact"):
			_pickup()

func _on_body_entered(body: Node2D) -> void:
	if body is Player or body.is_in_group("player"):
		is_player_nearby = true
		prompt.visible = true

func _on_body_exited(body: Node2D) -> void:
	if body is Player or body.is_in_group("player"):
		is_player_nearby = false
		prompt.visible = false

func _on_input_event(_viewport: Node, event: InputEvent, _shape_idx: int) -> void:
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		_pickup()

func _pickup() -> void:
	if is_picked_up or pickup_cooldown > 0.0:
		return
	if GameManager.pickup_item(item_data):
		is_picked_up = true
		queue_free()
