extends Node
# game_manager.gd - Global Game Manager & Inventory Controller

signal player_health_changed(hp, max_hp)
signal player_energy_changed(ep, max_ep)
signal player_shield_changed(shield_hp, max_shield_hp)
signal inventory_updated()
signal weapon_swapped(primary_w, secondary_w)
signal boss_health_changed(hp, max_hp, phase)
signal boss_defeated()

# Player Chassis
var player_chassis: String = "standard" # "standard" or "damaged"

# Health & Energy & Shield
var player_hp: float = 100.0
var player_max_hp: float = 100.0
var player_ep: float = 100.0
var player_max_ep: float = 100.0
var player_shield: float = 50.0
var player_max_shield: float = 50.0
var shield_regen_delay: float = 3.0
var shield_regen_timer: float = 0.0
var shield_regen_rate: float = 0.15 # 15% per second

# Inventory Matrix (3x3 = 9 slots)
# Each slot: {"id": String, "name": String, "type": String, "icon": String, "count": int}
var backpack: Array = [
	{"id": "pan", "name": "Cyber Frying Pan", "type": "weapon", "icon": "cyber_pan_32x32"},
	{"id": "bat", "name": "Reinforced Metal Bat", "type": "weapon", "icon": "metal_bat_32x32"},
	{"id": "blaster", "name": "Laser Blaster Arm", "type": "weapon", "icon": "laser_blaster_arm_32x32"},
	{"id": "flamethrower", "name": "Scrap Flamethrower", "type": "weapon", "icon": "flamethrower_32x32"},
	{"id": "frag", "name": "Frag Grenades", "type": "grenade", "icon": "grenade_frag_32x32", "count": 3},
	{"id": "emp", "name": "EMP Grenades", "type": "grenade", "icon": "grenade_emp_32x32", "count": 2},
	{"id": "cryo", "name": "Cryo Grenades", "type": "grenade", "icon": "grenade_cryo_32x32", "count": 2},
	{"id": "fire", "name": "Thermite Grenades", "type": "grenade", "icon": "grenade_fire_32x32", "count": 2},
	{"id": "nano_core", "name": "Overclock Chip", "type": "upgrade", "icon": "chip_nano_repair_32x32"}
]

# Equipped Weapons: Primary (Melee) & Secondary (Ranged)
var primary_weapon: String = "pan"
var secondary_weapon: String = "blaster"
var active_grenade: String = "frag"

var is_inventory_open: bool = false

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

func swap_weapons() -> void:
	var temp = primary_weapon
	primary_weapon = secondary_weapon
	secondary_weapon = temp
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func use_grenade() -> bool:
	for slot in backpack:
		if slot.id == active_grenade and slot.get("count", 0) > 0:
			slot["count"] -= 1
			inventory_updated.emit()
			return true
	return false

func damage_shield(amount: float) -> float:
	# Returns leftover damage penetrating to HP
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
	# Shield Regeneration after 3.0s without damage
	if shield_regen_timer > 0.0:
		shield_regen_timer -= dt
	elif player_shield < player_max_shield:
		player_shield = min(player_max_shield, player_shield + (player_max_shield * shield_regen_rate * dt))
		player_shield_changed.emit(player_shield, player_max_shield)
