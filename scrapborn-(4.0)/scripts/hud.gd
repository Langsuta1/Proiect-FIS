extends CanvasLayer
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
