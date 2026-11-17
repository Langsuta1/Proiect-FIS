extends CanvasLayer
# hud.gd - Metroidvania HUD with Armor, Core Energy, Shield Bar, Primary/Secondary [Q], and 3x3 Inventory [I]

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

@onready var inv_modal: Panel = $InventoryModal
@onready var inv_grid: GridContainer = $InventoryModal/VBox/GridContainer

func _ready() -> void:
	layer = 100
	if boss_panel: boss_panel.visible = false
	if inv_modal: inv_modal.visible = false

	GameManager.player_health_changed.connect(_on_hp_changed)
	GameManager.player_energy_changed.connect(_on_ep_changed)
	GameManager.player_shield_changed.connect(_on_shield_changed)
	GameManager.weapon_swapped.connect(_on_weapon_swapped)
	GameManager.inventory_updated.connect(_update_inventory_ui)
	GameManager.boss_health_changed.connect(_on_boss_health)
	GameManager.boss_defeated.connect(_on_boss_defeated)

	_update_hud_display()

func _input(event: InputEvent) -> void:
	if event.is_action_pressed("inventory"):
		_toggle_inventory()

func _toggle_inventory() -> void:
	if inv_modal:
		inv_modal.visible = not inv_modal.visible
		if inv_modal.visible:
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

	if weapon_primary_lbl: weapon_primary_lbl.text = "PRIMARY: " + GameManager.primary_weapon.to_upper()
	if weapon_secondary_lbl: weapon_secondary_lbl.text = "SECONDARY: " + GameManager.secondary_weapon.to_upper()
	if grenade_lbl: grenade_lbl.text = "GRENADE: " + GameManager.active_grenade.to_upper()

func _on_hp_changed(_hp: float, _mx: float) -> void:
	_update_hud_display()

func _on_ep_changed(_ep: float, _mx: float) -> void:
	_update_hud_display()

func _on_shield_changed(_sh: float, _mx: float) -> void:
	_update_hud_display()

func _on_weapon_swapped(_p: String, _s: String) -> void:
	_update_hud_display()

func _update_inventory_ui() -> void:
	if not inv_grid: return
	for child in inv_grid.get_children():
		child.queue_free()

	for slot in GameManager.backpack:
		var btn = Button.new()
		btn.custom_minimum_size = Vector2(80, 60)
		btn.text = slot["name"] + (" x" + str(slot["count"]) if slot.has("count") else "")
		inv_grid.add_child(btn)

func _on_boss_health(curr: float, mx: float, phase: int) -> void:
	if boss_panel:
		boss_panel.visible = true
		boss_bar.max_value = mx
		boss_bar.value = curr
		if boss_phase_lbl:
			boss_phase_lbl.text = "PHASE 2 - ENRAGED CRUSHER" if phase == 2 else "PHASE 1 - COMPACTOR OVERLOAD"

func _on_boss_defeated() -> void:
	if boss_panel:
		boss_panel.visible = false
