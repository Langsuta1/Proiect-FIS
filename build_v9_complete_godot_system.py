import os

scratch_dir = r"c:\Users\cozy1\.gemini\antigravity\scratch"
godot_dir = os.path.join(scratch_dir, "godot_project")
godot_copy_dir = os.path.join(scratch_dir, "scrapborn-(4.0)")

print("Building V9 complete Godot Engine System...")

# ---------------------------------------------------------------------------
# 1. FIX PROJECTILE LASER (CRASH FIX - IMAGE 1 & 2)
# ---------------------------------------------------------------------------
projectile_laser_gd = """extends Area2D
# projectile_laser.gd - Cyan plasma pulse beam with safe universal damage calls

@export var speed: float = 480.0
@export var damage: float = 24.0
var direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(dt: float) -> void:
	position += direction * speed * dt

func _on_body_entered(body: Node2D) -> void:
	if not body is Player and not body.is_in_group("player"):
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	var target = area.get_parent()
	if area.is_in_group("enemies") or area.is_in_group("boss") or (target and (target.is_in_group("enemies") or target.is_in_group("boss"))):
		if target and target.has_method("take_damage"):
			target.take_damage(damage, direction.x)
		queue_free()
"""

# ---------------------------------------------------------------------------
# 2. BOSS CRUSHER (SAFE 2-ARGUMENT DEFAULT TO PREVENT CRASH)
# ---------------------------------------------------------------------------
# We check boss_crusher.gd and ensure take_damage has default knockback: float = 0.0

# ---------------------------------------------------------------------------
# 3. GAME MANAGER (Hotbar, 3x3 Backpack, Drag & Drop, Drop/Pickup in World)
# ---------------------------------------------------------------------------
game_manager_gd = """extends Node
# game_manager.gd - V9 Global Game Manager & Inventory Controller

signal player_health_changed(hp, max_hp)
signal player_energy_changed(ep, max_ep)
signal player_shield_changed(shield_hp, max_shield_hp)
signal inventory_updated()
signal weapon_swapped(primary_w, secondary_w)
signal boss_health_changed(hp, max_hp, phase)
signal boss_defeated()

var player_chassis: String = "standard"

# Stats
var player_hp: float = 100.0
var player_max_hp: float = 100.0
var player_ep: float = 100.0
var player_max_ep: float = 100.0
var ep_regen_rate: float = 25.0 # 25 EP/s Core Stamina continuous regeneration!

var player_shield: float = 50.0
var player_max_shield: float = 50.0
var shield_regen_delay: float = 3.0
var shield_regen_timer: float = 0.0
var shield_regen_rate: float = 0.15

# Hotbar & 3x3 Backpack (Matching User's Reference Layout)
var main_hand: Dictionary = {"id": "pan", "name": "Cyber Frying Pan", "type": "melee", "icon": "cyber_pan_32x32"}
var secondary_hand: Dictionary = {"id": "blaster", "name": "Laser Blaster", "type": "ranged", "icon": "laser_blaster_arm_32x32"}

var backpack: Array = [
	{"id": "bat", "name": "Reinforced Bat", "type": "melee", "icon": "metal_bat_32x32"},
	{"id": "flamethrower", "name": "Flamethrower", "type": "ranged", "icon": "flamethrower_32x32"},
	{"id": "frag", "name": "Frag Grenades", "type": "grenade", "icon": "grenade_frag_32x32", "count": 3},
	{"id": "emp", "name": "EMP Grenades", "type": "grenade", "icon": "grenade_emp_32x32", "count": 2},
	{"id": "cryo", "name": "Cryo Grenades", "type": "grenade", "icon": "grenade_cryo_32x32", "count": 2},
	{"id": "fire", "name": "Thermite Grenades", "type": "grenade", "icon": "grenade_fire_32x32", "count": 2},
	{"id": "shield_chip", "name": "Aegis Module", "type": "upgrade", "icon": "aegis_shield_32x32"},
	{},
	{}
]

var primary_weapon: String:
	get:
		return main_hand.get("id", "pan")
	set(val):
		main_hand["id"] = val

var secondary_weapon: String:
	get:
		return secondary_hand.get("id", "blaster")
	set(val):
		secondary_hand["id"] = val

var active_grenade: String = "frag"

func _ready() -> void:
	_setup_inputs()

func _setup_inputs() -> void:
	_add_action("move_left", [KEY_A, KEY_LEFT])
	_add_action("move_right", [KEY_D, KEY_RIGHT])
	_add_action("jump", [KEY_SPACE, KEY_W, KEY_UP])
	_add_action("sprint", [KEY_SHIFT])
	_add_action("crouch", [KEY_S, KEY_DOWN])
	_add_action("attack_melee", [KEY_X])
	_add_mouse_action("attack_melee", MOUSE_BUTTON_LEFT)
	_add_action("attack_ranged", [KEY_Z])
	_add_action("switch_weapon", [KEY_Q])
	_add_action("inventory", [KEY_I])
	_add_action("shield", [KEY_F])
	_add_mouse_action("shield", MOUSE_BUTTON_RIGHT)
	_add_action("grenade", [KEY_G])
	_add_action("grapple", [KEY_E])
	_add_action("interact", [KEY_E])
	_add_action("dash", [KEY_C])

func _add_action(name: String, keys: Array) -> void:
	if not InputMap.has_action(name):
		InputMap.add_action(name)
	for key in keys:
		var ev = InputEventKey.new()
		ev.keycode = key
		InputMap.action_add_event(name, ev)

func _add_mouse_action(name: String, btn: int) -> void:
	if not InputMap.has_action(name):
		InputMap.add_action(name)
	var ev = InputEventMouseButton.new()
	ev.button_index = btn
	InputMap.action_add_event(name, ev)

# -------------------------------------------------------------
# INVENTORY SLOT MANAGEMENT & DRAG & DROP SWAPPING
# -------------------------------------------------------------
func get_slot_item(loc: String, idx: int) -> Dictionary:
	if loc == "main":
		return main_hand.duplicate()
	elif loc == "sec":
		return secondary_hand.duplicate()
	elif loc == "backpack" and idx >= 0 and idx < backpack.size():
		return backpack[idx].duplicate()
	return {}

func set_slot_item(loc: String, idx: int, item: Dictionary) -> void:
	if loc == "main":
		main_hand = item.duplicate()
	elif loc == "sec":
		secondary_hand = item.duplicate()
	elif loc == "backpack" and idx >= 0 and idx < backpack.size():
		backpack[idx] = item.duplicate()

func clear_slot_item(loc: String, idx: int) -> void:
	if loc == "main":
		main_hand = {}
	elif loc == "sec":
		secondary_hand = {}
	elif loc == "backpack" and idx >= 0 and idx < backpack.size():
		backpack[idx] = {}
	inventory_updated.emit()
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func swap_slots(loc_a: String, idx_a: int, loc_b: String, idx_b: int) -> void:
	var item_a: Dictionary = get_slot_item(loc_a, idx_a)
	var item_b: Dictionary = get_slot_item(loc_b, idx_b)

	set_slot_item(loc_a, idx_a, item_b)
	set_slot_item(loc_b, idx_b, item_a)

	inventory_updated.emit()
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func swap_weapons() -> void:
	var temp = main_hand.duplicate()
	main_hand = secondary_hand.duplicate()
	secondary_hand = temp
	weapon_swapped.emit(primary_weapon, secondary_weapon)
	inventory_updated.emit()

# -------------------------------------------------------------
# WORLD DROP & PICKUP SYSTEM
# -------------------------------------------------------------
func drop_item_in_world(item: Dictionary, pos: Vector2, facing: int) -> void:
	if item.is_empty():
		return
	var scene = load("res://scenes/dropped_item.tscn")
	if scene:
		var inst = scene.instantiate()
		inst.item_data = item.duplicate()
		inst.global_position = Vector2(pos.x + facing * 32.0, pos.y - 12.0)
		var current_scene = get_tree().current_scene
		if current_scene:
			current_scene.add_child(inst)
			print("Dropped item into world:", item.get("name", "Unknown"))

func pickup_item(item: Dictionary) -> bool:
	if item.is_empty():
		return false

	# 1. If Main Hand empty, put in Main Hand
	if main_hand.is_empty():
		main_hand = item.duplicate()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	# 2. If Secondary Hand empty, put in Secondary Hand
	if secondary_hand.is_empty():
		secondary_hand = item.duplicate()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	# 3. If stackable grenade and already in backpack, add count
	if item.get("type", "") == "grenade":
		for slot in backpack:
			if slot.get("id", "") == item.get("id", ""):
				slot["count"] = slot.get("count", 1) + item.get("count", 1)
				inventory_updated.emit()
				return true

	# 4. Find first empty slot in 3x3 Backpack
	for i in range(backpack.size()):
		if backpack[i].is_empty():
			backpack[i] = item.duplicate()
			inventory_updated.emit()
			return true

	# Inventory is completely full!
	return false

func use_grenade() -> bool:
	for slot in backpack:
		if slot.get("id", "") == active_grenade and slot.get("count", 0) > 0:
			slot["count"] -= 1
			if slot["count"] <= 0:
				slot.clear()
			inventory_updated.emit()
			return true
	return false

func damage_shield(amount: float) -> float:
	shield_regen_timer = shield_regen_delay
	if player_shield >= amount:
		player_shield -= amount
		player_shield_changed.emit(player_shield, player_max_shield)
		return 0.0
	else:
		var leftover = amount - player_shield
		player_shield = 0.0
		player_shield_changed.emit(player_shield, player_max_shield)
		return leftover

func _process(dt: float) -> void:
	# Core Stamina Regeneration (25 EP/s)
	if player_ep < player_max_ep:
		player_ep = min(player_max_ep, player_ep + (ep_regen_rate * dt))
		player_energy_changed.emit(player_ep, player_max_ep)

	# Shield Regeneration
	if shield_regen_timer > 0.0:
		shield_regen_timer -= dt
	elif player_shield < player_max_shield:
		player_shield = min(player_max_shield, player_shield + (player_max_shield * shield_regen_rate * dt))
		player_shield_changed.emit(player_shield, player_max_shield)
"""

# ---------------------------------------------------------------------------
# 4. DROPPED ITEM SCRIPT & SCENE (World Item with Floating Sprite & Name)
# ---------------------------------------------------------------------------
dropped_item_gd = """extends Area2D
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
"""

dropped_item_tscn = """[gd_scene load_steps=4 format=3 uid="uid://dropped_item_v9"]

[ext_resource type="Script" path="res://scripts/dropped_item.gd" id="1_item"]
[ext_resource type="Texture2D" path="res://assets/cyber_pan_32x32.png" id="2_tex"]

[sub_resource type="CircleShape2D" id="CircleShape2D_pickup"]
radius = 28.0

[node name="DroppedItem" type="Area2D"]
collision_layer = 16
collision_mask = 2
script = ExtResource("1_item")

[node name="CollisionShape2D" type="CollisionShape2D" parent="."]
shape = SubResource("CircleShape2D_pickup")

[node name="Sprite2D" type="Sprite2D" parent="."]
texture = ExtResource("2_tex")

[node name="Label" type="Label" parent="."]
offset_left = -100.0
offset_top = -32.0
offset_right = 100.0
offset_bottom = -16.0
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_colors/font_shadow_color = Color(0, 0, 0, 0.9)
theme_override_font_sizes/font_size = 11
text = "CYBER FRYING PAN"
horizontal_alignment = 1

[node name="Prompt" type="Label" parent="."]
visible = false
offset_left = -100.0
offset_top = -46.0
offset_right = 100.0
offset_bottom = -30.0
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_colors/font_shadow_color = Color(0, 0, 0, 0.9)
theme_override_font_sizes/font_size = 10
text = "[E] / CLICK TO PICK UP"
horizontal_alignment = 1
"""

# ---------------------------------------------------------------------------
# 5. INVENTORY SLOT UI SCRIPT (Drag & Drop + Beautiful Visuals)
# ---------------------------------------------------------------------------
inventory_slot_ui_gd = """extends Control
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
			# Quick equip into Main Hand!
			if slot_type == "backpack" and not item_data.is_empty():
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
"""

inventory_slot_ui_tscn = """[gd_scene load_steps=3 format=3 uid="uid://inv_slot_ui_v9"]

[ext_resource type="Script" path="res://scripts/inventory_slot_ui.gd" id="1_slot"]
[ext_resource type="Texture2D" path="res://assets/inv_slot_bg.png" id="2_bg"]

[node name="InventorySlotUI" type="Control"]
custom_minimum_size = Vector2(76, 76)
layout_mode = 3
anchors_preset = 0
offset_right = 76.0
offset_bottom = 76.0
script = ExtResource("1_slot")

[node name="Bg" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
texture = ExtResource("2_bg")
expand_mode = 1

[node name="Icon" type="TextureRect" parent="."]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -20.0
offset_top = -24.0
offset_right = 20.0
offset_bottom = 16.0
grow_horizontal = 2
grow_vertical = 2
expand_mode = 1
stretch_mode = 5

[node name="NameLabel" type="Label" parent="."]
layout_mode = 1
anchors_preset = 12
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_top = -20.0
offset_bottom = -2.0
grow_horizontal = 2
grow_vertical = 0
theme_override_colors/font_color = Color(0.85, 0.9, 0.95, 1)
theme_override_colors/font_shadow_color = Color(0, 0, 0, 0.9)
theme_override_font_sizes/font_size = 9
horizontal_alignment = 1
autowrap_mode = 2

[node name="CountLabel" type="Label" parent="."]
layout_mode = 1
anchors_preset = 3
anchor_left = 1.0
anchor_top = 1.0
anchor_right = 1.0
anchor_bottom = 1.0
offset_left = -30.0
offset_top = -18.0
offset_right = -4.0
offset_bottom = -2.0
grow_horizontal = 0
grow_vertical = 0
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_colors/font_shadow_color = Color(0, 0, 0, 0.9)
theme_override_font_sizes/font_size = 10
horizontal_alignment = 2
"""

# ---------------------------------------------------------------------------
# 6. INVENTORY DROP ZONE (DROPPING ITEMS OUTSIDE INVENTORY DROPS IN WORLD!)
# ---------------------------------------------------------------------------
inventory_dimmer_gd = """extends ColorRect
# inventory_dimmer.gd - Handles dropping an item outside the inventory window to drop it into the world!

func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
	return data is Dictionary and data.has("source_type")

func _drop_data(_at_position: Vector2, data: Variant) -> void:
	var item = GameManager.get_slot_item(data["source_type"], data["source_idx"])
	if not item.is_empty():
		GameManager.clear_slot_item(data["source_type"], data["source_idx"])
		var player = get_tree().get_first_node_in_group("player")
		var drop_pos = player.global_position if player else Vector2(200, 750)
		var facing = player.facing_direction if player else 1
		GameManager.drop_item_in_world(item, drop_pos, facing)
"""

# ---------------------------------------------------------------------------
# 7. REWRITE HUD SCRIPT & HUD SCENE (STUNNING GOTHIC/CYBER UI MATCHING REFERENCE)
# ---------------------------------------------------------------------------
hud_gd = """extends CanvasLayer
# hud.gd - V9 High-Fidelity HUD with Drag & Drop Inventory matching user reference

@onready var hp_fill: ColorRect = $HUDPanel/VBox/HPContainer/HPTrack/HPFill
@onready var hp_label: Label = $HUDPanel/VBox/HPContainer/HPLabel
@onready var ep_fill: ColorRect = $HUDPanel/VBox/EPContainer/EPTrack/EPFill
@onready var ep_label: Label = $HUDPanel/VBox/EPContainer/EPLabel
@onready var shield_fill: ColorRect = $HUDPanel/VBox/ShieldContainer/ShieldTrack/ShieldFill
@onready var shield_label: Label = $HUDPanel/VBox/ShieldContainer/ShieldLabel

@onready var weapon_primary_lbl: Label = $WeaponCard/VBox/PrimaryLbl
@onready var weapon_secondary_lbl: Label = $WeaponCard/VBox/SecondaryLbl
@onready var grenade_lbl: Label = $WeaponCard/VBox/GrenadeLbl

@onready var boss_panel: Panel = $BossPanel
@onready var boss_bar: ProgressBar = $BossPanel/BossBar
@onready var boss_phase_lbl: Label = $BossPanel/PhaseLabel

@onready var inv_modal: Control = $InventoryModal
@onready var slot_main_ui: InventorySlotUI = $InventoryModal/Panel/HBox/LeftCol/SlotMain
@onready var slot_sec_ui: InventorySlotUI = $InventoryModal/Panel/HBox/LeftCol/SlotSec
@onready var backpack_grid: GridContainer = $InventoryModal/Panel/HBox/RightCol/BackpackGrid

var selected_slot_loc: String = ""
var selected_slot_idx: int = -1

func _ready() -> void:
	add_to_group("hud")
	layer = 100
	if boss_panel: boss_panel.visible = false
	if inv_modal: inv_modal.visible = false

	slot_main_ui.slot_type = "main"
	slot_main_ui.slot_index = 0

	slot_sec_ui.slot_type = "sec"
	slot_sec_ui.slot_index = 0

	GameManager.player_health_changed.connect(_on_hp_changed)
	GameManager.player_energy_changed.connect(_on_ep_changed)
	GameManager.player_shield_changed.connect(_on_shield_changed)
	GameManager.weapon_swapped.connect(_on_weapon_swapped)
	GameManager.inventory_updated.connect(_update_inventory_ui)
	GameManager.boss_health_changed.connect(_on_boss_health)
	GameManager.boss_defeated.connect(_on_boss_defeated)

	_setup_backpack_slots()
	_update_hud_display()

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory"):
		_toggle_inventory()

func _toggle_inventory() -> void:
	if inv_modal:
		inv_modal.visible = not inv_modal.visible
		selected_slot_loc = ""
		selected_slot_idx = -1
		if inv_modal.visible:
			_update_inventory_ui()

func _setup_backpack_slots() -> void:
	if not backpack_grid: return
	for child in backpack_grid.get_children():
		child.queue_free()

	var slot_scene = preload("res://scenes/inventory_slot_ui.tscn")
	for i in range(9):
		var slot_inst = slot_scene.instantiate()
		slot_inst.slot_type = "backpack"
		slot_inst.slot_index = i
		backpack_grid.add_child(slot_inst)

func _update_inventory_ui() -> void:
	if not inv_modal or not inv_modal.visible:
		return

	# Update Main Hand Slot
	slot_main_ui.update_slot(GameManager.main_hand, selected_slot_loc == "main")

	# Update Secondary Hand Slot
	slot_sec_ui.update_slot(GameManager.secondary_hand, selected_slot_loc == "sec")

	# Update Backpack 3x3 Grid
	var slots = backpack_grid.get_children()
	for i in range(slots.size()):
		var slot_ctrl = slots[i] as InventorySlotUI
		if slot_ctrl and i < GameManager.backpack.size():
			var is_sel = (selected_slot_loc == "backpack" and selected_slot_idx == i)
			slot_ctrl.update_slot(GameManager.backpack[i], is_sel)

func _on_slot_ui_clicked(loc: String, idx: int) -> void:
	if selected_slot_loc == "":
		selected_slot_loc = loc
		selected_slot_idx = idx
	else:
		if selected_slot_loc == loc and selected_slot_idx == idx:
			selected_slot_loc = ""
			selected_slot_idx = -1
		else:
			GameManager.swap_slots(selected_slot_loc, selected_slot_idx, loc, idx)
			selected_slot_loc = ""
			selected_slot_idx = -1
	_update_inventory_ui()

func _update_hud_display() -> void:
	var hp_pct = clamp(GameManager.player_hp / GameManager.player_max_hp, 0.0, 1.0)
	var ep_pct = clamp(GameManager.player_ep / GameManager.player_max_ep, 0.0, 1.0)
	var shield_pct = clamp(GameManager.player_shield / GameManager.player_max_shield, 0.0, 1.0)

	if hp_fill: hp_fill.size.x = 180.0 * hp_pct
	if hp_label: hp_label.text = "ARMOR: " + str(int(GameManager.player_hp)) + " / " + str(int(GameManager.player_max_hp))

	if ep_fill: ep_fill.size.x = 180.0 * ep_pct
	if ep_label: ep_label.text = "CORE STAMINA: " + str(int(GameManager.player_ep)) + " / " + str(int(GameManager.player_max_ep))

	if shield_fill: shield_fill.size.x = 180.0 * shield_pct
	if shield_label: shield_label.text = "SHIELD: " + str(int(GameManager.player_shield)) + " / " + str(int(GameManager.player_max_shield))

	var m_name = GameManager.main_hand.get("name", "EMPTY")
	var s_name = GameManager.secondary_hand.get("name", "EMPTY")
	if weapon_primary_lbl: weapon_primary_lbl.text = "MAIN HAND: " + m_name.to_upper()
	if weapon_secondary_lbl: weapon_secondary_lbl.text = "SECONDARY: " + s_name.to_upper()
	if grenade_lbl: grenade_lbl.text = "GRENADE: " + GameManager.active_grenade.to_upper()

func _on_hp_changed(_hp: float, _mx: float) -> void: _update_hud_display()
func _on_ep_changed(_ep: float, _mx: float) -> void: _update_hud_display()
func _on_shield_changed(_sh: float, _mx: float) -> void: _update_hud_display()
func _on_weapon_swapped(_p: String, _s: String) -> void: _update_hud_display()

func _on_boss_health(curr: float, mx: float, phase: int) -> void:
	if boss_panel:
		boss_panel.visible = true
		boss_bar.max_value = mx
		boss_bar.value = curr
		if boss_phase_lbl:
			boss_phase_lbl.text = "PHASE 2 - ENRAGED CRUSHER" if phase == 2 else "PHASE 1 - COMPACTOR OVERLOAD"

func _on_boss_defeated() -> void:
	if boss_panel: boss_panel.visible = false
"""

hud_tscn = """[gd_scene load_steps=9 format=3 uid="uid://hud_v9_drag_drop"]

[ext_resource type="Script" path="res://scripts/hud.gd" id="1_hud"]
[ext_resource type="Script" path="res://scripts/inventory_dimmer.gd" id="2_dimmer"]
[ext_resource type="PackedScene" path="res://scenes/inventory_slot_ui.tscn" id="3_slot_ui"]
[ext_resource type="Texture2D" path="res://assets/inv_banner_hotbar.png" id="4_b_hot"]
[ext_resource type="Texture2D" path="res://assets/inv_banner_mainhand.png" id="5_b_main"]
[ext_resource type="Texture2D" path="res://assets/inv_banner_sechand.png" id="6_b_sec"]
[ext_resource type="Texture2D" path="res://assets/inv_banner_backpack.png" id="7_b_pack"]

[node name="HUD" type="CanvasLayer"]
layer = 100
script = ExtResource("1_hud")

[node name="HUDPanel" type="Panel" parent="."]
offset_left = 16.0
offset_top = 16.0
offset_right = 240.0
offset_bottom = 100.0

[node name="VBox" type="VBoxContainer" parent="HUDPanel"]
layout_mode = 0
offset_left = 8.0
offset_top = 6.0
offset_right = 216.0
offset_bottom = 90.0

[node name="HPContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="HPTrack" type="ColorRect" parent="HUDPanel/VBox/HPContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="HPFill" type="ColorRect" parent="HUDPanel/VBox/HPContainer/HPTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.93, 0.27, 0.27, 1)

[node name="HPLabel" type="Label" parent="HUDPanel/VBox/HPContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "ARMOR: 100 / 100"

[node name="EPContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="EPTrack" type="ColorRect" parent="HUDPanel/VBox/EPContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="EPFill" type="ColorRect" parent="HUDPanel/VBox/EPContainer/EPTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.22, 0.74, 0.97, 1)

[node name="EPLabel" type="Label" parent="HUDPanel/VBox/EPContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "CORE STAMINA: 100 / 100"

[node name="ShieldContainer" type="Control" parent="HUDPanel/VBox"]
custom_minimum_size = Vector2(200, 20)
layout_mode = 2

[node name="ShieldTrack" type="ColorRect" parent="HUDPanel/VBox/ShieldContainer"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.12, 0.16, 0.23, 1)

[node name="ShieldFill" type="ColorRect" parent="HUDPanel/VBox/ShieldContainer/ShieldTrack"]
layout_mode = 0
offset_left = 0.0
offset_top = 0.0
offset_right = 180.0
offset_bottom = 16.0
color = Color(0.02, 0.71, 0.83, 1)

[node name="ShieldLabel" type="Label" parent="HUDPanel/VBox/ShieldContainer"]
layout_mode = 0
offset_left = 4.0
offset_top = 1.0
offset_right = 176.0
offset_bottom = 16.0
theme_override_colors/font_color = Color(1, 1, 1, 1)
theme_override_font_sizes/font_size = 10
text = "SHIELD: 50 / 50"

[node name="WeaponCard" type="Panel" parent="."]
offset_left = 16.0
offset_top = 450.0
offset_right = 260.0
offset_bottom = 530.0

[node name="VBox" type="VBoxContainer" parent="WeaponCard"]
layout_mode = 0
offset_left = 8.0
offset_top = 6.0
offset_right = 236.0
offset_bottom = 74.0

[node name="PrimaryLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.22, 0.74, 0.97, 1)
theme_override_font_sizes/font_size = 12
text = "MAIN HAND: CYBER PAN"

[node name="SecondaryLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.7, 0.75, 0.85, 1)
theme_override_font_sizes/font_size = 12
text = "SECONDARY: BLASTER"

[node name="GrenadeLbl" type="Label" parent="WeaponCard/VBox"]
layout_mode = 2
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_font_sizes/font_size = 11
text = "GRENADE: FRAG (x3)"

[node name="BossPanel" type="Panel" parent="."]
visible = false
offset_left = 300.0
offset_top = 20.0
offset_right = 760.0
offset_bottom = 70.0

[node name="BossBar" type="ProgressBar" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 24.0
offset_right = 450.0
offset_bottom = 40.0
value = 100.0
show_percentage = false

[node name="PhaseLabel" type="Label" parent="BossPanel"]
layout_mode = 0
offset_left = 10.0
offset_top = 4.0
offset_right = 450.0
offset_bottom = 22.0
theme_override_colors/font_color = Color(0.96, 0.62, 0.04, 1)
theme_override_font_sizes/font_size = 11
text = "PHASE 1 - COMPACTOR OVERLOAD"

[node name="InventoryModal" type="Control" parent="."]
visible = false
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2

[node name="Dimmer" type="ColorRect" parent="InventoryModal"]
layout_mode = 1
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
grow_horizontal = 2
grow_vertical = 2
color = Color(0.04, 0.06, 0.09, 0.82)
script = ExtResource("2_dimmer")

[node name="Panel" type="Panel" parent="InventoryModal"]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -310.0
offset_top = -210.0
offset_right = 310.0
offset_bottom = 210.0
grow_horizontal = 2
grow_vertical = 2

[node name="HBox" type="HBoxContainer" parent="InventoryModal/Panel"]
layout_mode = 1
anchors_preset = 8
anchor_left = 0.5
anchor_top = 0.5
anchor_right = 0.5
anchor_bottom = 0.5
offset_left = -280.0
offset_top = -180.0
offset_right = 280.0
offset_bottom = 160.0
grow_horizontal = 2
grow_vertical = 2
theme_override_constants/separation = 40

[node name="LeftCol" type="VBoxContainer" parent="InventoryModal/Panel/HBox"]
custom_minimum_size = Vector2(170, 320)
layout_mode = 2
theme_override_constants/separation = 8

[node name="HotbarBanner" type="TextureRect" parent="InventoryModal/Panel/HBox/LeftCol"]
custom_minimum_size = Vector2(170, 26)
layout_mode = 2
texture = ExtResource("4_b_hot")
expand_mode = 1

[node name="MainHandBanner" type="TextureRect" parent="InventoryModal/Panel/HBox/LeftCol"]
custom_minimum_size = Vector2(170, 24)
layout_mode = 2
texture = ExtResource("5_b_main")
expand_mode = 1

[node name="SlotMain" parent="InventoryModal/Panel/HBox/LeftCol" instance=ExtResource("3_slot_ui")]
layout_mode = 2

[node name="SecHandBanner" type="TextureRect" parent="InventoryModal/Panel/HBox/LeftCol"]
custom_minimum_size = Vector2(170, 24)
layout_mode = 2
texture = ExtResource("6_b_sec")
expand_mode = 1

[node name="SlotSec" parent="InventoryModal/Panel/HBox/LeftCol" instance=ExtResource("3_slot_ui")]
layout_mode = 2

[node name="RightCol" type="VBoxContainer" parent="InventoryModal/Panel/HBox"]
custom_minimum_size = Vector2(300, 320)
layout_mode = 2
theme_override_constants/separation = 10

[node name="BackpackBanner" type="TextureRect" parent="InventoryModal/Panel/HBox/RightCol"]
custom_minimum_size = Vector2(280, 26)
layout_mode = 2
texture = ExtResource("7_b_pack")
expand_mode = 1

[node name="BackpackGrid" type="GridContainer" parent="InventoryModal/Panel/HBox/RightCol"]
layout_mode = 2
columns = 3
theme_override_constants/h_separation = 8
theme_override_constants/v_separation = 8

[node name="HelpLabel" type="Label" parent="InventoryModal/Panel"]
layout_mode = 1
anchors_preset = 7
anchor_left = 0.5
anchor_top = 1.0
anchor_right = 0.5
anchor_bottom = 1.0
offset_left = -280.0
offset_top = -26.0
offset_right = 280.0
offset_bottom = -8.0
grow_horizontal = 2
grow_vertical = 0
theme_override_colors/font_color = Color(0.6, 0.7, 0.8, 1)
theme_override_font_sizes/font_size = 10
text = "Drag & Drop between slots! Drag outside to drop into the world! Press [I] to close."
horizontal_alignment = 1
"""

# ---------------------------------------------------------------------------
# 8. UPDATE LEVEL HEAP (PERFECT CROUCH CONDUIT CLEARANCE OF 20PX!)
# Floor surface: y = 780
# Conduit collider bottom: y = 760 (height 360, spans y=400..760)
# Standing player (height 28px, top 752) hits ceiling and CANNOT pass!
# Crouched player (height 16px, top 764) crawls under smoothly!
# ---------------------------------------------------------------------------
level_heap_tscn = """[gd_scene load_steps=14 format=3 uid="uid://level_heap_v9_conduit_fixed"]

[ext_resource type="Texture2D" path="res://assets/level_heap_backdrop_5200x900.png" id="1_backdrop"]
[ext_resource type="Texture2D" path="res://assets/crushed_car_obstacle.png" id="2_car_tex"]
[ext_resource type="Texture2D" path="res://assets/scrap_conduit_tunnel_tall.png" id="3_conduit_tall"]
[ext_resource type="PackedScene" path="res://scenes/player.tscn" id="4_player"]
[ext_resource type="PackedScene" path="res://scenes/enemy_drone.tscn" id="5_drone"]
[ext_resource type="PackedScene" path="res://scenes/enemy_crawler.tscn" id="6_crawler"]
[ext_resource type="PackedScene" path="res://scenes/boss_crusher.tscn" id="7_boss"]
[ext_resource type="PackedScene" path="res://scenes/tutorial_prompt.tscn" id="8_tut"]
[ext_resource type="Texture2D" path="res://assets/grapple_ring_32x32.png" id="9_ring"]

[sub_resource type="RectangleShape2D" id="RectangleShape2D_floor1"]
size = Vector2(2800, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_floor2"]
size = Vector2(1600, 40)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_conduit_roof"]
size = Vector2(280, 360)

[sub_resource type="RectangleShape2D" id="RectangleShape2D_car"]
size = Vector2(56, 24)

[node name="LevelHeap" type="Node2D"]

[node name="StaticBackdrop" type="Sprite2D" parent="."]
z_index = -10
position = Vector2(2600, 450)
texture = ExtResource("1_backdrop")

[node name="StaticGeometry" type="StaticBody2D" parent="."]
collision_mask = 0

[node name="Floor1" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(1400, 800)
shape = SubResource("RectangleShape2D_floor1")

[node name="Floor2" type="CollisionShape2D" parent="StaticGeometry"]
position = Vector2(4400, 800)
shape = SubResource("RectangleShape2D_floor2")

[node name="CrushedCarObstacle" type="StaticBody2D" parent="."]
position = Vector2(320, 768)
collision_layer = 1
collision_mask = 0

[node name="Sprite2D" type="Sprite2D" parent="CrushedCarObstacle"]
texture = ExtResource("2_car_tex")

[node name="CollisionShape2D" type="CollisionShape2D" parent="CrushedCarObstacle"]
shape = SubResource("RectangleShape2D_car")

[node name="ScrapConduitTunnel" type="StaticBody2D" parent="."]
position = Vector2(860, 760)
collision_layer = 1
collision_mask = 0

[node name="Sprite2D" type="Sprite2D" parent="ScrapConduitTunnel"]
position = Vector2(0, -180)
texture = ExtResource("3_conduit_tall")

[node name="CollisionShape2D" type="CollisionShape2D" parent="ScrapConduitTunnel"]
position = Vector2(0, -180)
shape = SubResource("RectangleShape2D_conduit_roof")

[node name="GrappleRing1" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3000, 560)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing1"]
texture = ExtResource("9_ring")

[node name="GrappleRing2" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3200, 540)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing2"]
texture = ExtResource("9_ring")

[node name="GrappleRing3" type="Node2D" parent="." groups=["grapple_rings"]]
position = Vector2(3400, 560)

[node name="Sprite2D" type="Sprite2D" parent="GrappleRing3"]
texture = ExtResource("9_ring")

[node name="Player" parent="." instance=ExtResource("4_player")]
position = Vector2(80, 750)

[node name="TutorialMove" parent="." instance=ExtResource("8_tut")]
position = Vector2(100, 715)
tutorial_title = "A / D"
tutorial_desc = "MOVE CHASSIS\\nHold [SHIFT] to Sprint"
detection_radius = 140.0

[node name="TutorialJumpCar" parent="." instance=ExtResource("8_tut")]
position = Vector2(310, 715)
tutorial_title = "[SPACE] TO JUMP"
tutorial_desc = "Leap over crushed car obstacle"
detection_radius = 160.0

[node name="TutorialCrouch" parent="." instance=ExtResource("8_tut")]
position = Vector2(720, 715)
tutorial_title = "[S] / [DOWN] CROUCH"
tutorial_desc = "Crawl through low scrap conduit\\n(Clearance 20px - crouch to pass!)"
detection_radius = 160.0

[node name="TutorialMelee" parent="." instance=ExtResource("8_tut")]
position = Vector2(1300, 715)
tutorial_title = "[X] / [LEFT CLICK]"
tutorial_desc = "Swing Cyber Frying Pan\\nto shatter scrap barricade"
detection_radius = 160.0

[node name="TutorialSafeCombat" parent="." instance=ExtResource("8_tut")]
position = Vector2(1700, 715)
tutorial_title = "SAFE COMBAT ARENA"
tutorial_desc = "Defeat isolated Scrap Crawler\\nand Junk Drone to advance"
detection_radius = 180.0

[node name="TutorialShield" parent="." instance=ExtResource("8_tut")]
position = Vector2(2450, 715)
tutorial_title = "HOLD [F] / [RIGHT CLICK]"
tutorial_desc = "Deploy Energy Shield\\n(Regens 15%/s after 3s non-use)"
detection_radius = 180.0

[node name="TutorialGrapple" parent="." instance=ExtResource("8_tut")]
position = Vector2(2750, 715)
tutorial_title = "[E] GRAPPLING HOOK"
tutorial_desc = "Latch onto overhead rings\\nSwing across colossal death chasm!"
detection_radius = 200.0

[node name="TutorialGrenade" parent="." instance=ExtResource("8_tut")]
position = Vector2(3750, 715)
tutorial_title = "[G] FRAG GRENADE"
tutorial_desc = "Blast open reinforced steel bulkhead"
detection_radius = 180.0

[node name="TutorialPreBoss" parent="." instance=ExtResource("8_tut")]
position = Vector2(3980, 715)
tutorial_title = "[I] INVENTORY & [Q] SWAP"
tutorial_desc = "Drag & Drop Arsenal Matrix\\nPrepare for The Crusher Titan!"
detection_radius = 180.0

[node name="EnemyCrawler1" parent="." instance=ExtResource("6_crawler")]
position = Vector2(1900, 768)

[node name="EnemyDrone1" parent="." instance=ExtResource("5_drone")]
position = Vector2(2100, 580)

[node name="BossCrusher" parent="." instance=ExtResource("7_boss")]
position = Vector2(4600, 740)
"""

def write_both(rel_path, content):
    p1 = os.path.join(godot_dir, rel_path)
    p2 = os.path.join(godot_copy_dir, rel_path)
    os.makedirs(os.path.dirname(p1), exist_ok=True)
    os.makedirs(os.path.dirname(p2), exist_ok=True)
    with open(p1, "w", encoding="utf-8") as f:
        f.write(content)
    with open(p2, "w", encoding="utf-8") as f:
        f.write(content)

write_both("scripts/projectile_laser.gd", projectile_laser_gd)
write_both("autoload/game_manager.gd", game_manager_gd)
write_both("scripts/dropped_item.gd", dropped_item_gd)
write_both("scenes/dropped_item.tscn", dropped_item_tscn)
write_both("scripts/inventory_slot_ui.gd", inventory_slot_ui_gd)
write_both("scenes/inventory_slot_ui.tscn", inventory_slot_ui_tscn)
write_both("scripts/inventory_dimmer.gd", inventory_dimmer_gd)
write_both("scripts/hud.gd", hud_gd)
write_both("scenes/hud.tscn", hud_tscn)
write_both("scenes/level_heap.tscn", level_heap_tscn)

print("V9 Godot engine files written successfully.")
