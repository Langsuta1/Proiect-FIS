extends Control
class_name InventorySlotUI
# inventory_slot_ui.gd - High-fidelity Drag & Drop Inventory Slot Control

@export var slot_type: String = "backpack" # "main", "sec", "backpack"
@export var slot_index: int = 0

@onready var bg_rect: TextureRect = $Bg
@onready var icon_rect: TextureRect = $Icon
@onready var name_label: Label = $NameLabel
@onready var count_label: Label = $CountLabel

var tex_bg = preload("res://assets/inv_slot_bg.png")
var tex_hover = preload("res://assets/inv_slot_hover.png")
var tex_sel = preload("res://assets/inv_slot_selected.png")

var is_selected: bool = false
var item_data: Dictionary = {}

func _ready() -> void:
	custom_minimum_size = Vector2(76, 76)
	mouse_entered.connect(_on_mouse_entered)
	mouse_exited.connect(_on_mouse_exited)
	gui_input.connect(_on_gui_input)
	bg_rect.texture = tex_bg

func update_slot(item: Dictionary, selected: bool) -> void:
	item_data = item.duplicate()
	is_selected = selected

	if is_selected:
		bg_rect.texture = tex_sel
	else:
		bg_rect.texture = tex_bg

	if item_data.is_empty():
		icon_rect.visible = false
		name_label.text = "EMPTY" if slot_type != "backpack" else ""
		count_label.text = ""
	else:
		icon_rect.visible = true
		var icon_name = item_data.get("icon", "cyber_pan_32x32")
		var tex_path = "res://assets/" + icon_name + ".png"
		if ResourceLoader.exists(tex_path):
			icon_rect.texture = load(tex_path)

		name_label.text = item_data.get("name", "")
		count_label.text = ("x" + str(item_data["count"])) if item_data.has("count") and item_data["count"] > 1 else ""

func _on_mouse_entered() -> void:
	if not is_selected:
		bg_rect.texture = tex_hover

func _on_mouse_exited() -> void:
	if not is_selected:
		bg_rect.texture = tex_bg

func _on_gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_LEFT:
			# Tell HUD this slot was clicked (for click-to-swap fallback)
			var hud = get_tree().get_first_node_in_group("hud")
			if hud and hud.has_method("_on_slot_ui_clicked"):
				hud._on_slot_ui_clicked(slot_type, slot_index)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			if item_data.get("type", "") == "consumable":
				var player = get_tree().get_first_node_in_group("player")
				if player and player.has_method("_try_use_bandage"):
					player._try_use_bandage()
				else:
					GameManager.use_bandage()
			# Quick equip into Main Hand!
			elif slot_type == "backpack" and not item_data.is_empty():
				GameManager.swap_slots("backpack", slot_index, "main", 0)

# DRAG & DROP IMPLEMENTATION
func _get_drag_data(_at_position: Vector2) -> Variant:
	if item_data.is_empty():
		return null

	var data = {
		"source_type": slot_type,
		"source_idx": slot_index,
		"item": item_data.duplicate()
	}

	# Create drag preview showing the actual item icon
	var preview = TextureRect.new()
	preview.texture = icon_rect.texture
	preview.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	preview.custom_minimum_size = Vector2(48, 48)
	preview.size = Vector2(48, 48)
	var c = Control.new()
	c.add_child(preview)
	preview.position = -Vector2(24, 24)
	set_drag_preview(c)

	return data

func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
	return data is Dictionary and data.has("source_type")

func _drop_data(_at_position: Vector2, data: Variant) -> void:
	GameManager.swap_slots(data["source_type"], data["source_idx"], slot_type, slot_index)
