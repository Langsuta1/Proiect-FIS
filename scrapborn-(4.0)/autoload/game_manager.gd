extends Node
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
var ep_regen_rate: float = 25.0 # 25 EP/s Core Stamina regeneration
var ep_regen_delay: float = 0.0 # Delay countdown before stamina starts regenerating
var ep_regen_delay_duration: float = 1.0 # 1.0s cooldown after using stamina / flamethrower

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

func pause_ep_regen(duration: float = 1.0) -> void:
	ep_regen_delay = max(ep_regen_delay, duration)

func consume_ep(amount: float) -> bool:
	if player_ep < amount:
		return false
	player_ep -= amount
	pause_ep_regen(ep_regen_delay_duration)
	player_energy_changed.emit(player_ep, player_max_ep)
	return true

func _process(dt: float) -> void:
	# Core Stamina / Energy Regeneration (Paused while firing or just after using stamina!)
	if ep_regen_delay > 0.0:
		ep_regen_delay -= dt
	elif player_ep < player_max_ep:
		player_ep = min(player_max_ep, player_ep + (ep_regen_rate * dt))
		player_energy_changed.emit(player_ep, player_max_ep)

	# Shield Regeneration
	if shield_regen_timer > 0.0:
		shield_regen_timer -= dt
	elif player_shield < player_max_shield:
		player_shield = min(player_max_shield, player_shield + (player_max_shield * shield_regen_rate * dt))
		player_shield_changed.emit(player_shield, player_max_shield)
