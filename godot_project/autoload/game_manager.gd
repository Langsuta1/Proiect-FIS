extends Node
# game_manager.gd - V9 Global Game Manager & Inventory Controller

signal player_health_changed(hp, max_hp)
signal player_energy_changed(ep, max_ep)
signal player_shield_changed(shield_hp, max_shield_hp)
signal inventory_updated()
signal weapon_swapped(primary_w, secondary_w)
signal boss_health_changed(hp, max_hp, phase)
signal boss_defeated()
signal difficulty_changed(diff_name, diff_mult)
signal keybinds_updated()

var player_chassis: String = "standard"

# -------------------------------------------------------------
# DIFFICULTY SYSTEM ("Will You Snail?" Sarcastic AI Humor Style)
# Scales both enemy HP and enemy damage cleanly per tier
# -------------------------------------------------------------
var difficulty_index: int = 0
var difficulty_name: String = "THE EASIEST"
var difficulty_multiplier: float = 1.0
var difficulty_damage_multiplier: float = 1.0

const DIFFICULTY_TIERS: Array = [
	{
		"id": 0,
		"name": "THE EASIEST",
		"mult": 1.0,
		"dmg_mult": 1.0,
		"tag": "MODUL MELC ADORMIT",
		"color": Color(0.22, 0.88, 0.55),
		"desc": "Experiență relaxată. Inamici fragili și lovituri blânde, ideal pentru explorare.",
		"quote": "\"Pentru oameni care joacă cu monitorul stins. Inamicii sunt făcuți din carton umed.\""
	},
	{
		"id": 1,
		"name": "VERY EASY",
		"mult": 1.5,
		"dmg_mult": 1.3,
		"tag": "ÎNCĂ CU ROȚI AJUTĂTOARE",
		"color": Color(0.22, 0.78, 0.98),
		"desc": "Inamici ceva mai rezistenți și mai agresivi, dar încă foarte abordabili.",
		"quote": "\"Tot ușor e, dar măcar am băgat baterii noi în drone și crawlere.\""
	},
	{
		"id": 2,
		"name": "EASY",
		"mult": 2.3,
		"dmg_mult": 1.7,
		"tag": "AI-UL ÎNCEPE SĂ RÂDĂ",
		"color": Color(0.96, 0.62, 0.08),
		"desc": "Provocare serioasă. Inamicii rezistă mult și lovesc destul de tare.",
		"quote": "\"Așa numesc eu 'Easy'. Tu probabil o să plângi când ajungi la The Crusher Titan.\""
	},
	{
		"id": 3,
		"name": "ULTRA EASY (TRUST ME)",
		"mult": 3.2,
		"dmg_mult": 2.2,
		"tag": "100% CORECT, PROMIT :)",
		"color": Color(0.95, 0.28, 0.32),
		"desc": "Brutal și nemilos. Blindaj greu și daune masive la fiecare greșeală.",
		"quote": "\"Cel mai 'ușor' mod posibil! Inamicii sunt tancuri blindate. Sper că îți place baia în acid verde.\""
	}
]

# -------------------------------------------------------------
# AUDIO & GAMEPLAY SETTINGS (Future-Proofed + AudioServer Bus Sync)
# -------------------------------------------------------------
var audio_master_volume: float = 85.0
var audio_sfx_volume: float = 90.0
var audio_music_volume: float = 75.0
var audio_ambience_volume: float = 80.0
var audio_master_muted: bool = false
var audio_sfx_muted: bool = false
var audio_music_muted: bool = false
var audio_ambience_muted: bool = false

var setting_auto_pickup: bool = false
var setting_screen_shake: float = 100.0 # 0% to 150%
var setting_fullscreen: bool = false

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

const ITEM_BANDAGE: Dictionary = {
	"id": "bandage",
	"name": "Bandage",
	"type": "consumable",
	"icon": "bandage_32x32",
	"heal": 35.0,
	"count": 1
}

const GRENADE_DROP_TEMPLATES: Array = [
	{"id": "frag", "name": "Frag Grenades", "type": "grenade", "icon": "grenade_frag_32x32", "count": 1},
	{"id": "emp", "name": "EMP Grenades", "type": "grenade", "icon": "grenade_emp_32x32", "count": 1},
	{"id": "cryo", "name": "Cryo Grenades", "type": "grenade", "icon": "grenade_cryo_32x32", "count": 1},
	{"id": "fire", "name": "Thermite Grenades", "type": "grenade", "icon": "grenade_fire_32x32", "count": 1}
]

const REBINDABLE_ACTIONS: Array = [
	{"action": "attack_melee", "label": "Atac Main Hand (Armă Principală)", "cat": "ARME & SCUT"},
	{"action": "attack_ranged", "label": "Atac Secondary Hand (Armă Secundară)", "cat": "ARME & SCUT"},
	{"action": "switch_weapon", "label": "Swap Arme (Main ↔ Secondary)", "cat": "ARME & SCUT"},
	{"action": "shield", "label": "Activare Scut Energetic Aegis", "cat": "ARME & SCUT"},
	{"action": "heal", "label": "Folosește Bandaj (Heal HP)", "cat": "ARME & SCUT"},
	{"action": "grenade", "label": "Aruncă Grenadă (Ține Apăsat Slingshot)", "cat": "GRENADE"},
	{"action": "cycle_grenade", "label": "Schimbă Tipul Grenadei (Următoarea)", "cat": "GRENADE"},
	{"action": "grenade_1", "label": "Selectează Frag Grenade", "cat": "GRENADE"},
	{"action": "grenade_2", "label": "Selectează EMP Grenade", "cat": "GRENADE"},
	{"action": "grenade_3", "label": "Selectează Cryo (Freeze) Grenade", "cat": "GRENADE"},
	{"action": "grenade_4", "label": "Selectează Thermite (Fire) Grenade", "cat": "GRENADE"},
	{"action": "interact", "label": "Grappling Hook & Pickup Item", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "dash", "label": "Cyber Dash", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "jump", "label": "Jump / Double Jump / Wall Jump", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "crouch", "label": "Crouch (Ghemuire)", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "sprint", "label": "Sprint Rapid", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "move_left", "label": "Mișcare Stânga", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "move_right", "label": "Mișcare Dreapta", "cat": "MIȘCARE & ABILITĂȚI"},
	{"action": "inventory", "label": "Deschide / Închide Inventarul", "cat": "MIȘCARE & ABILITĂȚI"}
]

func _ready() -> void:
	_setup_inputs()

func _setup_inputs() -> void:
	var all_actions = [
		"move_left", "move_right", "jump", "sprint", "crouch",
		"attack_melee", "attack_ranged", "switch_weapon", "inventory",
		"ui_cancel", "shield", "grenade", "cycle_grenade",
		"grenade_1", "grenade_2", "grenade_3", "grenade_4",
		"grapple", "interact", "dash", "heal"
	]
	for act in all_actions:
		if InputMap.has_action(act):
			InputMap.action_erase_events(act)

	_add_action("move_left", [KEY_A, KEY_LEFT])
	_add_action("move_right", [KEY_D, KEY_RIGHT])
	_add_action("jump", [KEY_SPACE, KEY_W, KEY_UP])
	_add_action("sprint", [KEY_SHIFT])
	_add_action("crouch", [KEY_S, KEY_DOWN])
	_add_mouse_action("attack_melee", MOUSE_BUTTON_LEFT)
	_add_action("attack_melee", [KEY_X])
	_add_action("attack_ranged", [KEY_Z])
	_add_action("switch_weapon", [KEY_Q])
	_add_action("inventory", [KEY_I])
	_add_action("ui_cancel", [KEY_ESCAPE])
	_add_mouse_action("shield", MOUSE_BUTTON_RIGHT)
	_add_action("shield", [KEY_F])
	_add_action("grenade", [KEY_G])
	_add_action("cycle_grenade", [KEY_T])
	_add_action("grenade_1", [KEY_1])
	_add_action("grenade_2", [KEY_2])
	_add_action("grenade_3", [KEY_3])
	_add_action("grenade_4", [KEY_4])
	_add_action("grapple", [KEY_E])
	_add_action("interact", [KEY_E])
	_add_action("dash", [KEY_C])
	_add_action("heal", [KEY_H])

func reset_all_keybinds_to_default() -> void:
	_setup_inputs()
	keybinds_updated.emit()

func rebind_action(action_name: String, new_event: InputEvent) -> void:
	if not InputMap.has_action(action_name):
		InputMap.add_action(action_name)
	InputMap.action_erase_events(action_name)

	if new_event is InputEventKey:
		var ev = InputEventKey.new()
		ev.keycode = new_event.keycode if new_event.keycode != 0 else new_event.physical_keycode
		InputMap.action_add_event(action_name, ev)
	elif new_event is InputEventMouseButton:
		var ev = InputEventMouseButton.new()
		ev.button_index = new_event.button_index
		InputMap.action_add_event(action_name, ev)

	# Keep "grapple" synced with "interact"
	if action_name == "interact":
		if InputMap.has_action("grapple"):
			InputMap.action_erase_events("grapple")
			for e in InputMap.action_get_events("interact"):
				InputMap.action_add_event("grapple", e)

	keybinds_updated.emit()

func get_action_binding_text(action_name: String) -> String:
	if not InputMap.has_action(action_name):
		return "NONE"
	var events = InputMap.action_get_events(action_name)
	if events.is_empty():
		return "UNBOUND"
	var names: Array[String] = []
	for ev in events:
		if ev is InputEventKey:
			var k_code = ev.keycode if ev.keycode != 0 else ev.physical_keycode
			var k_str = OS.get_keycode_string(k_code).to_upper()
			if k_str != "" and k_str not in names:
				names.append(k_str)
		elif ev is InputEventMouseButton:
			var m_str = "MOUSE " + str(ev.button_index)
			match ev.button_index:
				MOUSE_BUTTON_LEFT: m_str = "CLICK STÂNGA"
				MOUSE_BUTTON_RIGHT: m_str = "CLICK DREAPTA"
				MOUSE_BUTTON_MIDDLE: m_str = "CLICK MIJLOC"
				MOUSE_BUTTON_XBUTTON1: m_str = "MOUSE SIDE 1"
				MOUSE_BUTTON_XBUTTON2: m_str = "MOUSE SIDE 2"
			if m_str not in names:
				names.append(m_str)
		if names.size() >= 2:
			break
	return " / ".join(names) if not names.is_empty() else "CUSTOM"

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

	if main_hand.get("type", "") == "grenade":
		active_grenade = main_hand.get("id", active_grenade)
	elif secondary_hand.get("type", "") == "grenade":
		active_grenade = secondary_hand.get("id", active_grenade)

	inventory_updated.emit()
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func swap_weapons() -> void:
	var temp = main_hand.duplicate()
	main_hand = secondary_hand.duplicate()
	secondary_hand = temp
	if main_hand.get("type", "") == "grenade":
		active_grenade = main_hand.get("id", active_grenade)
	elif secondary_hand.get("type", "") == "grenade":
		active_grenade = secondary_hand.get("id", active_grenade)
	weapon_swapped.emit(primary_weapon, secondary_weapon)
	inventory_updated.emit()

# -------------------------------------------------------------
# WORLD DROP & PICKUP SYSTEM
# -------------------------------------------------------------
func spawn_world_drop(item: Dictionary, world_pos: Vector2, launch_vel: Vector2 = Vector2.ZERO, pickup_delay: float = 0.25) -> void:
	if item.is_empty():
		return
	var scene = load("res://scenes/dropped_item.tscn")
	if scene:
		var inst = scene.instantiate()
		inst.item_data = item.duplicate()
		inst.position = world_pos
		inst.drop_velocity = launch_vel
		inst.pickup_cooldown = pickup_delay
		var current_scene = get_tree().current_scene
		if current_scene:
			current_scene.call_deferred("add_child", inst)
			print("Dropped item into world:", item.get("name", "Unknown"))

func drop_item_in_world(item: Dictionary, pos: Vector2, facing: int) -> void:
	spawn_world_drop(item, Vector2(pos.x + facing * 32.0, pos.y - 12.0), Vector2(facing * 45.0, -90.0), 0.45)

func spawn_mob_loot(world_pos: Vector2, drop_chance: float = 0.85, guaranteed_drops: int = 0) -> void:
	var drops_to_spawn: Array[Dictionary] = []

	if guaranteed_drops > 0:
		drops_to_spawn.append(ITEM_BANDAGE.duplicate())
		for i in range(1, guaranteed_drops):
			if i % 2 == 1:
				var g_tmpl: Dictionary = GRENADE_DROP_TEMPLATES[randi() % GRENADE_DROP_TEMPLATES.size()]
				drops_to_spawn.append(g_tmpl.duplicate())
			else:
				drops_to_spawn.append(ITEM_BANDAGE.duplicate())
	else:
		if randf() > drop_chance:
			return
		var bandage_bias: float = 0.65 if player_hp < player_max_hp * 0.65 else 0.5
		var first_is_bandage: bool = randf() < bandage_bias
		if first_is_bandage:
			drops_to_spawn.append(ITEM_BANDAGE.duplicate())
		else:
			var g_tmpl: Dictionary = GRENADE_DROP_TEMPLATES[randi() % GRENADE_DROP_TEMPLATES.size()]
			drops_to_spawn.append(g_tmpl.duplicate())

		if randf() < 0.25:
			if first_is_bandage:
				var bonus_g: Dictionary = GRENADE_DROP_TEMPLATES[randi() % GRENADE_DROP_TEMPLATES.size()]
				drops_to_spawn.append(bonus_g.duplicate())
			else:
				drops_to_spawn.append(ITEM_BANDAGE.duplicate())

	for drop_item in drops_to_spawn:
		var offset := Vector2(randf_range(-10.0, 10.0), -10.0)
		var vel := Vector2(randf_range(-70.0, 70.0), randf_range(-190.0, -130.0))
		spawn_world_drop(drop_item, world_pos + offset, vel, 0.3)

func pickup_item(item: Dictionary) -> bool:
	if item.is_empty():
		return false

	var item_type: String = item.get("type", "")
	var item_id: String = item.get("id", "")
	var add_count: int = int(item.get("count", 1))

	if item_type == "grenade" or item_type == "consumable":
		# 1. Stack onto existing slot in backpack, main_hand, or secondary_hand
		for slot in backpack:
			if slot.get("id", "") == item_id:
				slot["count"] = int(slot.get("count", 1)) + add_count
				inventory_updated.emit()
				return true
		if main_hand.get("id", "") == item_id:
			main_hand["count"] = int(main_hand.get("count", 1)) + add_count
			inventory_updated.emit()
			return true
		if secondary_hand.get("id", "") == item_id:
			secondary_hand["count"] = int(secondary_hand.get("count", 1)) + add_count
			inventory_updated.emit()
			return true

		# 2. Place into first empty slot in 3x3 Backpack
		for i in range(backpack.size()):
			if backpack[i].is_empty():
				backpack[i] = item.duplicate()
				inventory_updated.emit()
				return true

		# 3. If backpack is full and it's a bandage while hurt, apply heal directly
		if item_id == "bandage" and player_hp < player_max_hp:
			var heal_amt := float(item.get("heal", 35.0)) * float(add_count)
			player_hp = min(player_max_hp, player_hp + heal_amt)
			player_health_changed.emit(player_hp, player_max_hp)
			return true

		# 4. Fallback to empty Secondary Hand, then Main Hand
		if secondary_hand.is_empty():
			secondary_hand = item.duplicate()
			inventory_updated.emit()
			weapon_swapped.emit(primary_weapon, secondary_weapon)
			return true
		if main_hand.is_empty():
			main_hand = item.duplicate()
			inventory_updated.emit()
			weapon_swapped.emit(primary_weapon, secondary_weapon)
			return true

		return false

	# Non-stackable weapons / modules: Main Hand -> Secondary Hand -> Backpack
	if main_hand.is_empty():
		main_hand = item.duplicate()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	if secondary_hand.is_empty():
		secondary_hand = item.duplicate()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	for i in range(backpack.size()):
		if backpack[i].is_empty():
			backpack[i] = item.duplicate()
			inventory_updated.emit()
			return true

	# Inventory is completely full!
	return false

func get_bandage_count() -> int:
	var total: int = 0
	if main_hand.get("id", "") == "bandage":
		total += int(main_hand.get("count", 1))
	if secondary_hand.get("id", "") == "bandage":
		total += int(secondary_hand.get("count", 1))
	for slot in backpack:
		if slot.get("id", "") == "bandage":
			total += int(slot.get("count", 1))
	return total

func use_bandage() -> bool:
	if player_hp >= player_max_hp:
		return false

	for slot in backpack:
		if slot.get("id", "") == "bandage" and int(slot.get("count", 0)) > 0:
			var heal_amt := float(slot.get("heal", 35.0))
			player_hp = min(player_max_hp, player_hp + heal_amt)
			slot["count"] = int(slot.get("count", 1)) - 1
			if slot["count"] <= 0:
				slot.clear()
			player_health_changed.emit(player_hp, player_max_hp)
			inventory_updated.emit()
			weapon_swapped.emit(primary_weapon, secondary_weapon)
			return true

	if secondary_hand.get("id", "") == "bandage" and int(secondary_hand.get("count", 0)) > 0:
		var heal_amt := float(secondary_hand.get("heal", 35.0))
		player_hp = min(player_max_hp, player_hp + heal_amt)
		secondary_hand["count"] = int(secondary_hand.get("count", 1)) - 1
		if secondary_hand["count"] <= 0:
			secondary_hand.clear()
		player_health_changed.emit(player_hp, player_max_hp)
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	if main_hand.get("id", "") == "bandage" and int(main_hand.get("count", 0)) > 0:
		var heal_amt := float(main_hand.get("heal", 35.0))
		player_hp = min(player_max_hp, player_hp + heal_amt)
		main_hand["count"] = int(main_hand.get("count", 1)) - 1
		if main_hand["count"] <= 0:
			main_hand.clear()
		player_health_changed.emit(player_hp, player_max_hp)
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	return false

func set_active_grenade(g_id: String) -> void:
	active_grenade = g_id
	inventory_updated.emit()
	weapon_swapped.emit(primary_weapon, secondary_weapon)

func cycle_active_grenade() -> void:
	var order = ["frag", "emp", "cryo", "fire"]
	var cur_idx = order.find(active_grenade)
	for offset in range(1, 5):
		var next_id = order[(cur_idx + offset) % 4]
		if get_grenade_count(next_id) > 0:
			set_active_grenade(next_id)
			return
	set_active_grenade(order[(cur_idx + 1) % 4])

func get_grenade_count(g_id: String) -> int:
	var total: int = 0
	if main_hand.get("id", "") == g_id:
		total += int(main_hand.get("count", 1))
	if secondary_hand.get("id", "") == g_id:
		total += int(secondary_hand.get("count", 1))
	for slot in backpack:
		if slot.get("id", "") == g_id:
			total += int(slot.get("count", 1))
	return total

func use_grenade() -> bool:
	# 1. If Main Hand or Secondary Hand holds a grenade, prioritize its type
	if main_hand.get("type", "") == "grenade" and main_hand.get("count", 1) > 0:
		active_grenade = main_hand.get("id", active_grenade)
		main_hand["count"] = int(main_hand.get("count", 1)) - 1
		if main_hand["count"] <= 0:
			main_hand.clear()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	if secondary_hand.get("type", "") == "grenade" and secondary_hand.get("count", 1) > 0:
		active_grenade = secondary_hand.get("id", active_grenade)
		secondary_hand["count"] = int(secondary_hand.get("count", 1)) - 1
		if secondary_hand["count"] <= 0:
			secondary_hand.clear()
		inventory_updated.emit()
		weapon_swapped.emit(primary_weapon, secondary_weapon)
		return true

	# 2. Check backpack for active_grenade
	for slot in backpack:
		if slot.get("id", "") == active_grenade and slot.get("count", 0) > 0:
			slot["count"] -= 1
			if slot["count"] <= 0:
				slot.clear()
			inventory_updated.emit()
			weapon_swapped.emit(primary_weapon, secondary_weapon)
			return true

	# 3. Fallback: if active_grenade ran out, auto-select next available grenade in backpack
	for slot in backpack:
		if slot.get("type", "") == "grenade" and slot.get("count", 0) > 0:
			active_grenade = slot.get("id", "frag")
			slot["count"] -= 1
			if slot["count"] <= 0:
				slot.clear()
			inventory_updated.emit()
			weapon_swapped.emit(primary_weapon, secondary_weapon)
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

func apply_audio_settings() -> void:
	var master_lin = clamp(audio_master_volume / 100.0, 0.0001, 1.0)
	AudioServer.set_bus_volume_db(0, linear_to_db(master_lin))
	AudioServer.set_bus_mute(0, audio_master_muted or audio_master_volume <= 0.5)

	# Sync optional SFX / Music / Ambience buses if present in project
	for bus_info in [
		{"name": "SFX", "vol": audio_sfx_volume, "mute": audio_sfx_muted},
		{"name": "Music", "vol": audio_music_volume, "mute": audio_music_muted},
		{"name": "Ambience", "vol": audio_ambience_volume, "mute": audio_ambience_muted}
	]:
		var idx = AudioServer.get_bus_index(bus_info["name"])
		if idx >= 0:
			var lin = clamp(float(bus_info["vol"]) / 100.0, 0.0001, 1.0)
			AudioServer.set_bus_volume_db(idx, linear_to_db(lin))
			AudioServer.set_bus_mute(idx, bool(bus_info["mute"]) or float(bus_info["vol"]) <= 0.5)

func get_effective_sfx_volume_db() -> float:
	if audio_master_muted or audio_sfx_muted or audio_master_volume <= 0.5 or audio_sfx_volume <= 0.5:
		return -80.0
	var combined = (audio_master_volume / 100.0) * (audio_sfx_volume / 100.0)
	return linear_to_db(clamp(combined, 0.0001, 1.0))

func reset_run_state() -> void:
	player_hp = player_max_hp
	player_ep = player_max_ep
	player_shield = player_max_shield
	ep_regen_delay = 0.0
	shield_regen_timer = 0.0
	active_grenade = "frag"
	main_hand = {"id": "pan", "name": "Cyber Frying Pan", "type": "melee", "icon": "cyber_pan_32x32"}
	secondary_hand = {"id": "blaster", "name": "Laser Blaster", "type": "ranged", "icon": "laser_blaster_arm_32x32"}
	backpack = [
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
	player_health_changed.emit(player_hp, player_max_hp)
	player_energy_changed.emit(player_ep, player_max_ep)
	player_shield_changed.emit(player_shield, player_max_shield)
	inventory_updated.emit()

func get_scaled_enemy_damage(base_damage: float) -> float:
	return base_damage * difficulty_damage_multiplier

func apply_difficulty_and_reset_level(tier_idx: int) -> void:
	if tier_idx < 0 or tier_idx >= DIFFICULTY_TIERS.size():
		return
	var tier = DIFFICULTY_TIERS[tier_idx]
	difficulty_index = tier_idx
	difficulty_name = tier["name"]
	difficulty_multiplier = float(tier["mult"])
	difficulty_damage_multiplier = float(tier.get("dmg_mult", tier["mult"]))
	reset_run_state()
	difficulty_changed.emit(difficulty_name, difficulty_multiplier)
	get_tree().paused = false
	get_tree().reload_current_scene()

func restart_current_level() -> void:
	reset_run_state()
	get_tree().paused = false
	get_tree().reload_current_scene()

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
