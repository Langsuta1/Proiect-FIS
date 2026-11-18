extends Area2D
class_name DroppedItem
# dropped_item.gd - Physical world item with sprite, floating name, and [E] / click pickup

@export var item_data: Dictionary = {}

@onready var sprite: Sprite2D = $Sprite2D
@onready var label: Label = $Label
@onready var prompt: Label = $Prompt

var start_y: float = 0.0
var is_player_nearby: bool = false

func _ready() -> void:
	add_to_group("dropped_items")
	start_y = position.y
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	input_event.connect(_on_input_event)
	_update_visuals()

func _update_visuals() -> void:
	if item_data.is_empty():
		return

	var icon_name = item_data.get("icon", "cyber_pan_32x32")
	var tex_path = "res://assets/" + icon_name + ".png"
	if ResourceLoader.exists(tex_path):
		sprite.texture = load(tex_path)

	var count_txt = (" x" + str(item_data["count"])) if item_data.has("count") else ""
	label.text = item_data.get("name", "Unknown Item") + count_txt
	prompt.visible = false

func _process(dt: float) -> void:
	# Gentle hovering bob
	sprite.position.y = sin(Time.get_ticks_msec() / 250.0) * 3.5

	if is_player_nearby:
		if Input.is_action_just_pressed("interact"):
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
	if GameManager.pickup_item(item_data):
		# Floating pickup effect
		queue_free()
