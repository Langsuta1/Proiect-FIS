extends Control
class_name PauseMenuUI
# pause_menu.gd - Cyberpunk Pause & Settings Menu (ESC) with "Will You Snail?" Difficulty Humor,
# Confirmation Warning before Level Reset, Audio Mixer (Master, SFX, Music, Ambience), Gameplay Options & Controls

var current_tab: int = 0
var pending_difficulty_idx: int = -1

# UI References
var tab_buttons: Array[Button] = []
var tab_pages: Array[Control] = []
var tab_scrolls: Array[ScrollContainer] = []
var header_diff_lbl: Label = null
var ai_quote_lbl: Label = null
var diff_card_buttons: Array[Button] = []
var diff_card_panels: Array[PanelContainer] = []

# Warning Modal References
var warning_overlay: Control = null
var warning_title_lbl: Label = null
var warning_desc_lbl: Label = null

# Audio UI References
var slider_master: HSlider = null
var slider_sfx: HSlider = null
var slider_music: HSlider = null
var slider_amb: HSlider = null
var lbl_master_val: Label = null
var lbl_sfx_val: Label = null
var lbl_music_val: Label = null
var lbl_amb_val: Label = null
var btn_mute_master: Button = null
var btn_mute_sfx: Button = null
var btn_mute_music: Button = null
var btn_mute_amb: Button = null

# Gameplay UI References
var btn_auto_pickup: Button = null
var slider_shake: HSlider = null
var lbl_shake_val: Label = null
var btn_chassis: Button = null
var btn_fullscreen: Button = null

# Keybinds Rebinding UI References
var listening_for_action: String = ""
var keybind_buttons: Dictionary = {} # action_name -> Button
var keybind_status_lbl: Label = null

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	visible = false
	_build_ui()
	_refresh_all_states()

func _input(event: InputEvent) -> void:
	if not visible or listening_for_action == "":
		return

	if event is InputEventKey and event.pressed and not event.echo:
		var k_code = event.keycode if event.keycode != 0 else event.physical_keycode
		if k_code == KEY_ESCAPE:
			# Cancel rebinding without closing the pause menu!
			listening_for_action = ""
			_refresh_keybinds_ui()
			get_viewport().set_input_as_handled()
			return

		GameManager.rebind_action(listening_for_action, event)
		listening_for_action = ""
		_refresh_keybinds_ui()
		get_viewport().set_input_as_handled()
		return

	elif event is InputEventMouseButton and event.pressed:
		# Ignore scroll wheel so user can scroll the list without binding scroll
		if event.button_index in [MOUSE_BUTTON_WHEEL_UP, MOUSE_BUTTON_WHEEL_DOWN, MOUSE_BUTTON_WHEEL_LEFT, MOUSE_BUTTON_WHEEL_RIGHT]:
			return
		GameManager.rebind_action(listening_for_action, event)
		listening_for_action = ""
		_refresh_keybinds_ui()
		get_viewport().set_input_as_handled()
		return

func open_pause_menu() -> void:
	visible = true
	warning_overlay.visible = false
	pending_difficulty_idx = -1
	listening_for_action = ""
	_refresh_all_states()
	get_tree().paused = true

func close_pause_menu() -> void:
	if listening_for_action != "":
		listening_for_action = ""
		_refresh_keybinds_ui()
		return
	if warning_overlay and warning_overlay.visible:
		warning_overlay.visible = false
		pending_difficulty_idx = -1
		return
	visible = false
	get_tree().paused = false

func _make_stylebox(bg: Color, border: Color, border_w: int = 2, radius: int = 6, pad: int = 10) -> StyleBoxFlat:
	var sb = StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	sb.content_margin_left = pad
	sb.content_margin_right = pad
	sb.content_margin_top = pad
	sb.content_margin_bottom = pad
	return sb

func _style_button(btn: Button, bg: Color, border: Color, hover_bg: Color, font_col: Color = Color.WHITE, f_size: int = 11) -> void:
	btn.add_theme_stylebox_override("normal", _make_stylebox(bg, border, 1, 5, 7))
	btn.add_theme_stylebox_override("hover", _make_stylebox(hover_bg, border.lightened(0.25), 2, 5, 7))
	btn.add_theme_stylebox_override("pressed", _make_stylebox(hover_bg.darkened(0.15), Color.WHITE, 2, 5, 7))
	btn.add_theme_stylebox_override("focus", _make_stylebox(hover_bg, border, 2, 5, 7))
	btn.add_theme_color_override("font_color", font_col)
	btn.add_theme_color_override("font_hover_color", Color.WHITE)
	btn.add_theme_color_override("font_pressed_color", Color.WHITE)
	btn.add_theme_font_size_override("font_size", f_size)

func _set_margins(mc: MarginContainer, left: int, top: int, right: int, bottom: int) -> void:
	mc.add_theme_constant_override("margin_left", left)
	mc.add_theme_constant_override("margin_top", top)
	mc.add_theme_constant_override("margin_right", right)
	mc.add_theme_constant_override("margin_bottom", bottom)

func _create_scrollable_tab_page(title_text: String, subtitle_text: String) -> Dictionary:
	var page := VBoxContainer.new()
	page.add_theme_constant_override("separation", 8)
	page.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	page.size_flags_vertical = Control.SIZE_EXPAND_FILL

	var hdr := Label.new()
	hdr.text = title_text
	hdr.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	hdr.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hdr.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	hdr.add_theme_font_size_override("font_size", 12)
	page.add_child(hdr)

	var sub: Label = null
	if subtitle_text != "":
		sub = Label.new()
		sub.text = subtitle_text
		sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		sub.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		sub.add_theme_color_override("font_color", Color(0.68, 0.76, 0.86))
		sub.add_theme_font_size_override("font_size", 10)
		page.add_child(sub)

	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.vertical_scroll_mode = ScrollContainer.SCROLL_MODE_AUTO
	page.add_child(scroll)

	var scroll_margin := MarginContainer.new()
	scroll_margin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_set_margins(scroll_margin, 0, 0, 6, 0)
	scroll.add_child(scroll_margin)

	var content := VBoxContainer.new()
	content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 8)
	scroll_margin.add_child(content)

	return {"page": page, "scroll": scroll, "content": content, "subtitle": sub}

func _build_ui() -> void:
	# 1. Fullscreen Dark Blur/Dimmer Backdrop
	var dimmer = ColorRect.new()
	dimmer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dimmer.color = Color(0.02, 0.04, 0.07, 0.86)
	add_child(dimmer)

	# 2. Main Centered Cyberpunk Window (Fixed 760 x 460 inside 960 x 540 viewport)
	var main_panel = Panel.new()
	main_panel.anchor_left = 0.5
	main_panel.anchor_top = 0.5
	main_panel.anchor_right = 0.5
	main_panel.anchor_bottom = 0.5
	main_panel.offset_left = -380.0
	main_panel.offset_top = -230.0
	main_panel.offset_right = 380.0
	main_panel.offset_bottom = 230.0
	main_panel.custom_minimum_size = Vector2(760, 460)
	main_panel.clip_contents = true
	main_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 0.98), Color(0.22, 0.74, 0.97, 0.9), 2, 8, 0))
	add_child(main_panel)

	var main_margin = MarginContainer.new()
	main_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_set_margins(main_margin, 14, 14, 14, 14)
	main_panel.add_child(main_margin)

	var root_vbox = VBoxContainer.new()
	root_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	root_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root_vbox.add_theme_constant_override("separation", 10)
	main_margin.add_child(root_vbox)

	# 3. Top Header Banner
	var header_panel = PanelContainer.new()
	header_panel.custom_minimum_size = Vector2(0, 38)
	header_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.08, 0.13, 0.21, 1.0), Color(0.22, 0.74, 0.97, 0.45), 1, 6, 8))
	root_vbox.add_child(header_panel)

	var header_hbox = HBoxContainer.new()
	header_panel.add_child(header_hbox)

	var title_lbl = Label.new()
	title_lbl.text = "⚙ SCRAPBORN // SYSTEM PAUSED [ESC]"
	title_lbl.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	title_lbl.add_theme_font_size_override("font_size", 14)
	title_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header_hbox.add_child(title_lbl)

	header_diff_lbl = Label.new()
	header_diff_lbl.text = "DIFICULTATE: THE EASIEST"
	header_diff_lbl.add_theme_color_override("font_color", Color(0.22, 0.88, 0.55))
	header_diff_lbl.add_theme_font_size_override("font_size", 12)
	header_hbox.add_child(header_diff_lbl)

	# 4. Split Content: Left Sidebar + Right Tab Pages
	var body_hbox = HBoxContainer.new()
	body_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body_hbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body_hbox.add_theme_constant_override("separation", 12)
	root_vbox.add_child(body_hbox)

	# --- LEFT SIDEBAR (Fixed width, never shifts between tabs) ---
	var sidebar_panel = Panel.new()
	sidebar_panel.custom_minimum_size = Vector2(205, 0)
	sidebar_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	sidebar_panel.clip_contents = true
	sidebar_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.07, 0.1, 0.16, 1.0), Color(0.18, 0.26, 0.38, 1.0), 1, 6, 0))
	body_hbox.add_child(sidebar_panel)

	var side_margin = MarginContainer.new()
	side_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_set_margins(side_margin, 10, 10, 10, 10)
	sidebar_panel.add_child(side_margin)

	var side_vbox = VBoxContainer.new()
	side_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	side_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	side_vbox.add_theme_constant_override("separation", 7)
	side_margin.add_child(side_vbox)

	var nav_lbl = Label.new()
	nav_lbl.text = "MENIU CONFIGURARE"
	nav_lbl.add_theme_color_override("font_color", Color(0.55, 0.65, 0.78))
	nav_lbl.add_theme_font_size_override("font_size", 10)
	side_vbox.add_child(nav_lbl)

	var tab_names = [
		"☠  DIFICULTATE (AI)",
		"🔊  OPȚIUNI AUDIO",
		"⚡  GAMEPLAY & VIDEO",
		"⌨  KEYBINDS (CONTROALE)"
	]
	tab_buttons.clear()
	for i in range(tab_names.size()):
		var t_btn = Button.new()
		t_btn.text = tab_names[i]
		t_btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
		t_btn.custom_minimum_size = Vector2(0, 32)
		var idx = i
		t_btn.pressed.connect(func(): _switch_tab(idx))
		side_vbox.add_child(t_btn)
		tab_buttons.append(t_btn)

	var spacer = Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	side_vbox.add_child(spacer)

	var act_lbl = Label.new()
	act_lbl.text = "ACȚIUNI SESIUNE"
	act_lbl.add_theme_color_override("font_color", Color(0.55, 0.65, 0.78))
	act_lbl.add_theme_font_size_override("font_size", 10)
	side_vbox.add_child(act_lbl)

	var btn_resume = Button.new()
	btn_resume.text = "▶ CONTINUĂ JOCUL"
	btn_resume.custom_minimum_size = Vector2(0, 32)
	_style_button(btn_resume, Color(0.08, 0.36, 0.26), Color(0.16, 0.85, 0.55), Color(0.12, 0.48, 0.34), Color(0.85, 1.0, 0.92), 11)
	btn_resume.pressed.connect(close_pause_menu)
	side_vbox.add_child(btn_resume)

	var btn_checkpoint = Button.new()
	btn_checkpoint.text = "↺ LA CHECKPOINT"
	btn_checkpoint.custom_minimum_size = Vector2(0, 28)
	_style_button(btn_checkpoint, Color(0.12, 0.18, 0.28), Color(0.25, 0.55, 0.85), Color(0.18, 0.28, 0.42), Color(0.85, 0.92, 1.0), 10)
	btn_checkpoint.pressed.connect(_on_respawn_checkpoint_pressed)
	side_vbox.add_child(btn_checkpoint)

	var btn_restart = Button.new()
	btn_restart.text = "⟳ RESETEAZĂ NIVELUL"
	btn_restart.custom_minimum_size = Vector2(0, 28)
	_style_button(btn_restart, Color(0.28, 0.18, 0.08), Color(0.95, 0.6, 0.15), Color(0.4, 0.26, 0.1), Color(1.0, 0.9, 0.7), 10)
	btn_restart.pressed.connect(func(): _prompt_difficulty_reset(GameManager.difficulty_index, true))
	side_vbox.add_child(btn_restart)

	var btn_quit = Button.new()
	btn_quit.text = "✖ IEȘIRE DIN JOC"
	btn_quit.custom_minimum_size = Vector2(0, 28)
	_style_button(btn_quit, Color(0.28, 0.1, 0.12), Color(0.88, 0.25, 0.28), Color(0.42, 0.14, 0.16), Color(1.0, 0.82, 0.82), 10)
	btn_quit.pressed.connect(func(): get_tree().quit())
	side_vbox.add_child(btn_quit)

	# --- RIGHT CONTENT PANEL (Fixed size, scrollable inside each tab) ---
	var content_panel = Panel.new()
	content_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	content_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	content_panel.clip_contents = true
	content_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.07, 0.1, 0.16, 1.0), Color(0.18, 0.26, 0.38, 1.0), 1, 6, 0))
	body_hbox.add_child(content_panel)

	var content_margin = MarginContainer.new()
	content_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_set_margins(content_margin, 12, 12, 12, 12)
	content_panel.add_child(content_margin)

	tab_pages.clear()
	tab_scrolls.clear()
	var page_diff = _build_difficulty_page()
	var page_audio = _build_audio_page()
	var page_gameplay = _build_gameplay_page()
	var page_controls = _build_controls_page()

	for p in [page_diff, page_audio, page_gameplay, page_controls]:
		content_margin.add_child(p)
		tab_pages.append(p)

	# 5. Confirmation Warning Overlay (Hidden until user changes difficulty or requests level reset)
	_build_warning_modal()
	_switch_tab(0)

# -------------------------------------------------------------------------
# TAB 0: DIFFICULTY PAGE ("Will You Snail?" Humor + Clean Tier Descriptions)
# -------------------------------------------------------------------------
func _build_difficulty_page() -> Control:
	var built := _create_scrollable_tab_page(
		"CALIBRARE DIFICULTATE AI",
		"Alege nivelul de dificultate dorit. (Atenție: Schimbarea dificultății resetează nivelul curent!)"
	)
	var page: VBoxContainer = built["page"]
	var scroll: ScrollContainer = built["scroll"]
	var list_vbox: VBoxContainer = built["content"]
	tab_scrolls.append(scroll)

	diff_card_buttons.clear()
	diff_card_panels.clear()

	for i in range(GameManager.DIFFICULTY_TIERS.size()):
		var tier = GameManager.DIFFICULTY_TIERS[i]
		var card = PanelContainer.new()
		card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		card.custom_minimum_size = Vector2(0, 60)
		list_vbox.add_child(card)
		diff_card_panels.append(card)

		var chbox = HBoxContainer.new()
		chbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		chbox.add_theme_constant_override("separation", 10)
		card.add_child(chbox)

		var info_vbox = VBoxContainer.new()
		info_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		info_vbox.add_theme_constant_override("separation", 3)
		chbox.add_child(info_vbox)

		var name_row = HBoxContainer.new()
		name_row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		name_row.add_theme_constant_override("separation", 8)
		info_vbox.add_child(name_row)

		var t_name = Label.new()
		t_name.text = tier["name"]
		t_name.add_theme_color_override("font_color", tier["color"])
		t_name.add_theme_font_size_override("font_size", 13)
		name_row.add_child(t_name)

		var t_tag = Label.new()
		t_tag.text = "[" + tier["tag"] + "]"
		t_tag.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		t_tag.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		t_tag.add_theme_color_override("font_color", Color(0.65, 0.72, 0.82))
		t_tag.add_theme_font_size_override("font_size", 10)
		name_row.add_child(t_tag)

		var desc_lbl = Label.new()
		desc_lbl.text = tier["desc"]
		desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		desc_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		desc_lbl.add_theme_color_override("font_color", Color(0.85, 0.9, 0.96))
		desc_lbl.add_theme_font_size_override("font_size", 10)
		info_vbox.add_child(desc_lbl)

		var sel_btn = Button.new()
		sel_btn.custom_minimum_size = Vector2(115, 34)
		sel_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var tier_idx = i
		sel_btn.mouse_entered.connect(func(): _show_ai_quote(tier_idx))
		sel_btn.pressed.connect(func(): _on_difficulty_card_clicked(tier_idx))
		chbox.add_child(sel_btn)
		diff_card_buttons.append(sel_btn)

	# AI Sarcastic Quote Box pinned at bottom (Fixed height so window never grows)
	var quote_panel = Panel.new()
	quote_panel.custom_minimum_size = Vector2(0, 56)
	quote_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	quote_panel.clip_contents = true
	quote_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.04, 0.06, 0.1, 1.0), Color(0.96, 0.62, 0.08, 0.6), 1, 6, 0))
	page.add_child(quote_panel)

	var q_margin = MarginContainer.new()
	q_margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_set_margins(q_margin, 8, 6, 8, 6)
	quote_panel.add_child(q_margin)

	ai_quote_lbl = Label.new()
	ai_quote_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	ai_quote_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ai_quote_lbl.size_flags_vertical = Control.SIZE_EXPAND_FILL
	ai_quote_lbl.text = "🤖 AI-UL SCRAPBORN: " + GameManager.DIFFICULTY_TIERS[0]["quote"]
	ai_quote_lbl.add_theme_color_override("font_color", Color(0.98, 0.82, 0.45))
	ai_quote_lbl.add_theme_font_size_override("font_size", 10)
	q_margin.add_child(ai_quote_lbl)

	return page

func _show_ai_quote(tier_idx: int) -> void:
	if ai_quote_lbl and tier_idx >= 0 and tier_idx < GameManager.DIFFICULTY_TIERS.size():
		var tier = GameManager.DIFFICULTY_TIERS[tier_idx]
		ai_quote_lbl.text = "🤖 COMENTARIU AI [" + tier["name"] + "]: " + tier["quote"]

func _on_difficulty_card_clicked(tier_idx: int) -> void:
	_show_ai_quote(tier_idx)
	if tier_idx == GameManager.difficulty_index:
		return
	_prompt_difficulty_reset(tier_idx, false)

# -------------------------------------------------------------------------
# TAB 1: AUDIO SETTINGS PAGE (Master, SFX, Music, Ambience + Mute)
# -------------------------------------------------------------------------
func _build_audio_page() -> Control:
	var built := _create_scrollable_tab_page(
		"MIXER AUDIO & CANALE DE SUNET (MASTER / SFX / MUSIC / AMBIENCE)",
		"Controlează volumul general și canalele individuale pentru efecte sonore (SFX), muzică și ambianță."
	)
	var page: VBoxContainer = built["page"]
	var scroll: ScrollContainer = built["scroll"]
	var vbox: VBoxContainer = built["content"]
	tab_scrolls.append(scroll)

	# Build 4 Audio Channel Controls
	var r_master = _create_audio_row(vbox, "MASTER VOLUME (Volum General)", "Controlează întregul output audio al jocului (AudioServer Master Bus)", GameManager.audio_master_volume, func(v):
		GameManager.audio_master_volume = v
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	, func():
		GameManager.audio_master_muted = not GameManager.audio_master_muted
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	)
	slider_master = r_master["slider"]
	lbl_master_val = r_master["val_lbl"]
	btn_mute_master = r_master["mute_btn"]

	var r_sfx = _create_audio_row(vbox, "SFX & COMBAT (Efecte Sonore)", "Arme melee, lasere, flamethrower, explozii grenade, grappling hook & inamici", GameManager.audio_sfx_volume, func(v):
		GameManager.audio_sfx_volume = v
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	, func():
		GameManager.audio_sfx_muted = not GameManager.audio_sfx_muted
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	)
	slider_sfx = r_sfx["slider"]
	lbl_sfx_val = r_sfx["val_lbl"]
	btn_mute_sfx = r_sfx["mute_btn"]

	var r_music = _create_audio_row(vbox, "MUSIC & BOSS THEME (Muzică)", "Coloana sonoră ambientală și muzica dinamică din timpul luptei cu The Crusher Titan", GameManager.audio_music_volume, func(v):
		GameManager.audio_music_volume = v
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	, func():
		GameManager.audio_music_muted = not GameManager.audio_music_muted
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	)
	slider_music = r_music["slider"]
	lbl_music_val = r_music["val_lbl"]
	btn_mute_music = r_music["mute_btn"]

	var r_amb = _create_audio_row(vbox, "AMBIENCE & UI (Ambianță & Interfață)", "Sunete industriale din groapa de fier vechi, acid toxic și sunete de inventar", GameManager.audio_ambience_volume, func(v):
		GameManager.audio_ambience_volume = v
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	, func():
		GameManager.audio_ambience_muted = not GameManager.audio_ambience_muted
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	)
	slider_amb = r_amb["slider"]
	lbl_amb_val = r_amb["val_lbl"]
	btn_mute_amb = r_amb["mute_btn"]

	var bottom_hbox = HBoxContainer.new()
	page.add_child(bottom_hbox)

	var btn_reset_audio = Button.new()
	btn_reset_audio.text = "↺ RESETEAZĂ VOLUMUL LA DEFAULT"
	btn_reset_audio.custom_minimum_size = Vector2(220, 30)
	_style_button(btn_reset_audio, Color(0.12, 0.18, 0.28), Color(0.22, 0.74, 0.97), Color(0.18, 0.28, 0.42), Color.WHITE, 10)
	btn_reset_audio.pressed.connect(func():
		GameManager.audio_master_volume = 85.0
		GameManager.audio_sfx_volume = 90.0
		GameManager.audio_music_volume = 75.0
		GameManager.audio_ambience_volume = 80.0
		GameManager.audio_master_muted = false
		GameManager.audio_sfx_muted = false
		GameManager.audio_music_muted = false
		GameManager.audio_ambience_muted = false
		GameManager.apply_audio_settings()
		_refresh_audio_ui()
	)
	bottom_hbox.add_child(btn_reset_audio)

	return page

func _create_audio_row(parent: Control, title: String, desc: String, init_val: float, on_slide: Callable, on_mute: Callable) -> Dictionary:
	var card = PanelContainer.new()
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 8))
	parent.add_child(card)

	var row_vbox = VBoxContainer.new()
	row_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row_vbox.add_theme_constant_override("separation", 4)
	card.add_child(row_vbox)

	var top_hbox = HBoxContainer.new()
	top_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row_vbox.add_child(top_hbox)

	var t_lbl = Label.new()
	t_lbl.text = title
	t_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	t_lbl.add_theme_color_override("font_color", Color(0.92, 0.96, 1.0))
	t_lbl.add_theme_font_size_override("font_size", 11)
	t_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_hbox.add_child(t_lbl)

	var d_lbl = Label.new()
	d_lbl.text = desc
	d_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	d_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	d_lbl.add_theme_color_override("font_color", Color(0.55, 0.65, 0.78))
	d_lbl.add_theme_font_size_override("font_size", 9)
	row_vbox.add_child(d_lbl)

	var ctrl_hbox = HBoxContainer.new()
	ctrl_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	ctrl_hbox.add_theme_constant_override("separation", 10)
	row_vbox.add_child(ctrl_hbox)

	var slider = HSlider.new()
	slider.min_value = 0.0
	slider.max_value = 100.0
	slider.step = 1.0
	slider.value = init_val
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.custom_minimum_size = Vector2(0, 22)
	slider.value_changed.connect(on_slide)
	ctrl_hbox.add_child(slider)

	var val_lbl = Label.new()
	val_lbl.custom_minimum_size = Vector2(46, 0)
	val_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	val_lbl.text = str(int(init_val)) + "%"
	val_lbl.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	val_lbl.add_theme_font_size_override("font_size", 11)
	ctrl_hbox.add_child(val_lbl)

	var mute_btn = Button.new()
	mute_btn.custom_minimum_size = Vector2(74, 24)
	mute_btn.text = "🔊 ON"
	mute_btn.pressed.connect(on_mute)
	ctrl_hbox.add_child(mute_btn)

	return {"slider": slider, "val_lbl": val_lbl, "mute_btn": mute_btn}

# -------------------------------------------------------------------------
# TAB 2: GAMEPLAY & VIDEO PAGE (Auto-Pickup, Screen Shake, Chassis Skin, Fullscreen)
# -------------------------------------------------------------------------
func _build_gameplay_page() -> Control:
	var built := _create_scrollable_tab_page(
		"OPȚIUNI GAMEPLAY, CAMERĂ & PERSONALIZARE ȘASIU",
		"Configurează colectarea automată, efectele de cameră, aspectul șasiului și modul de afișare."
	)
	var page: VBoxContainer = built["page"]
	var scroll: ScrollContainer = built["scroll"]
	var vbox: VBoxContainer = built["content"]
	tab_scrolls.append(scroll)

	# 1. Auto-Pickup Dropped Items Toggle
	var card_pickup = PanelContainer.new()
	card_pickup.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_pickup.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 9))
	vbox.add_child(card_pickup)
	var hb_pickup = HBoxContainer.new()
	hb_pickup.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_pickup.add_theme_constant_override("separation", 10)
	card_pickup.add_child(hb_pickup)
	var vb_p = VBoxContainer.new()
	vb_p.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_pickup.add_child(vb_p)
	var lbl_p1 = Label.new()
	lbl_p1.text = "AUTO-PICKUP ITEME DE PE JOS"
	lbl_p1.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_p1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_p1.add_theme_color_override("font_color", Color.WHITE)
	lbl_p1.add_theme_font_size_override("font_size", 11)
	vb_p.add_child(lbl_p1)
	var lbl_p2 = Label.new()
	lbl_p2.text = "Colectează automat armele, bandajele și grenadele de pe jos când treci peste ele."
	lbl_p2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_p2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_p2.add_theme_color_override("font_color", Color(0.6, 0.7, 0.82))
	lbl_p2.add_theme_font_size_override("font_size", 9)
	vb_p.add_child(lbl_p2)
	btn_auto_pickup = Button.new()
	btn_auto_pickup.custom_minimum_size = Vector2(125, 30)
	btn_auto_pickup.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	btn_auto_pickup.pressed.connect(func():
		GameManager.setting_auto_pickup = not GameManager.setting_auto_pickup
		_refresh_gameplay_ui()
	)
	hb_pickup.add_child(btn_auto_pickup)

	# 2. Screen Shake Intensity Slider
	var card_shake = PanelContainer.new()
	card_shake.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_shake.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 9))
	vbox.add_child(card_shake)
	var vb_shake = VBoxContainer.new()
	vb_shake.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_shake.add_child(vb_shake)
	var lbl_s1 = Label.new()
	lbl_s1.text = "INTENSITATE CAMERA SHAKE (Explozii Grenade & Impact Boss)"
	lbl_s1.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_s1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_s1.add_theme_color_override("font_color", Color.WHITE)
	lbl_s1.add_theme_font_size_override("font_size", 11)
	vb_shake.add_child(lbl_s1)
	var hb_shake = HBoxContainer.new()
	hb_shake.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_shake.add_theme_constant_override("separation", 10)
	vb_shake.add_child(hb_shake)
	slider_shake = HSlider.new()
	slider_shake.min_value = 0.0
	slider_shake.max_value = 150.0
	slider_shake.step = 5.0
	slider_shake.value = GameManager.setting_screen_shake
	slider_shake.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider_shake.value_changed.connect(func(v):
		GameManager.setting_screen_shake = v
		_refresh_gameplay_ui()
	)
	hb_shake.add_child(slider_shake)
	lbl_shake_val = Label.new()
	lbl_shake_val.custom_minimum_size = Vector2(52, 0)
	lbl_shake_val.text = "100%"
	lbl_shake_val.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	lbl_shake_val.add_theme_font_size_override("font_size", 11)
	hb_shake.add_child(lbl_shake_val)

	# 3. Robot Chassis Visual Model (Standard vs Battle-Damaged)
	var card_skin = PanelContainer.new()
	card_skin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_skin.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 9))
	vbox.add_child(card_skin)
	var hb_skin = HBoxContainer.new()
	hb_skin.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_skin.add_theme_constant_override("separation", 10)
	card_skin.add_child(hb_skin)
	var vb_sk = VBoxContainer.new()
	vb_sk.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_skin.add_child(vb_sk)
	var lbl_sk1 = Label.new()
	lbl_sk1.text = "STIL VIZUAL ȘASIU ROBOT (SKIN)"
	lbl_sk1.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_sk1.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_sk1.add_theme_color_override("font_color", Color.WHITE)
	lbl_sk1.add_theme_font_size_override("font_size", 11)
	vb_sk.add_child(lbl_sk1)
	var lbl_sk2 = Label.new()
	lbl_sk2.text = "Schimbă aspectul robotului între Standard Cyber-Blue și Battle-Damaged Scrap."
	lbl_sk2.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_sk2.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lbl_sk2.add_theme_color_override("font_color", Color(0.6, 0.7, 0.82))
	lbl_sk2.add_theme_font_size_override("font_size", 9)
	vb_sk.add_child(lbl_sk2)
	btn_chassis = Button.new()
	btn_chassis.custom_minimum_size = Vector2(150, 30)
	btn_chassis.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	btn_chassis.pressed.connect(func():
		GameManager.player_chassis = "damaged" if GameManager.player_chassis == "standard" else "standard"
		_refresh_gameplay_ui()
	)
	hb_skin.add_child(btn_chassis)

	# 4. Fullscreen / Windowed Mode
	var card_fs = PanelContainer.new()
	card_fs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card_fs.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 9))
	vbox.add_child(card_fs)
	var hb_fs = HBoxContainer.new()
	hb_fs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_fs.add_theme_constant_override("separation", 10)
	card_fs.add_child(hb_fs)
	var lbl_fs = Label.new()
	lbl_fs.text = "MOD AFIȘARE ECRAN (DISPLAY MODE)"
	lbl_fs.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_fs.add_theme_color_override("font_color", Color.WHITE)
	lbl_fs.add_theme_font_size_override("font_size", 11)
	lbl_fs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hb_fs.add_child(lbl_fs)
	btn_fullscreen = Button.new()
	btn_fullscreen.custom_minimum_size = Vector2(150, 30)
	btn_fullscreen.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	btn_fullscreen.pressed.connect(func():
		GameManager.setting_fullscreen = not GameManager.setting_fullscreen
		if GameManager.setting_fullscreen:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN)
		else:
			DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_WINDOWED)
		_refresh_gameplay_ui()
	)
	hb_fs.add_child(btn_fullscreen)

	return page

# -------------------------------------------------------------------------
# TAB 3: INTERACTIVE KEYBINDS CUSTOMIZATION PAGE
# -------------------------------------------------------------------------
func _build_controls_page() -> Control:
	var built := _create_scrollable_tab_page(
		"CONFIGURARE KEYBINDS (ARME, GRENADE, SCUT & MIȘCARE)",
		"Apasă pe butonul din dreapta oricărei acțiuni pentru a-i asigna o tastă nouă sau un click de mouse."
	)
	var page: VBoxContainer = built["page"]
	var scroll: ScrollContainer = built["scroll"]
	var list_vbox: VBoxContainer = built["content"]
	keybind_status_lbl = built["subtitle"]
	tab_scrolls.append(scroll)

	list_vbox.add_theme_constant_override("separation", 5)

	keybind_buttons.clear()
	var last_cat: String = ""

	for entry in GameManager.REBINDABLE_ACTIONS:
		var cat: String = entry["cat"]
		var act_id: String = entry["action"]
		var act_label: String = entry["label"]

		if cat != last_cat:
			last_cat = cat
			var cat_lbl = Label.new()
			cat_lbl.text = "▸ " + cat
			cat_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
			cat_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			cat_lbl.add_theme_color_override("font_color", Color(0.96, 0.68, 0.15))
			cat_lbl.add_theme_font_size_override("font_size", 11)
			list_vbox.add_child(cat_lbl)

		var row_card = PanelContainer.new()
		row_card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row_card.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 5, 6))
		list_vbox.add_child(row_card)

		var row_hbox = HBoxContainer.new()
		row_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row_hbox.add_theme_constant_override("separation", 10)
		row_card.add_child(row_hbox)

		var d_lbl = Label.new()
		d_lbl.text = act_label
		d_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		d_lbl.add_theme_color_override("font_color", Color(0.9, 0.94, 0.99))
		d_lbl.add_theme_font_size_override("font_size", 11)
		d_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row_hbox.add_child(d_lbl)

		var k_btn = Button.new()
		k_btn.custom_minimum_size = Vector2(165, 26)
		k_btn.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		var captured_act = act_id
		k_btn.pressed.connect(func(): _start_listening_for_keybind(captured_act))
		row_hbox.add_child(k_btn)
		keybind_buttons[act_id] = k_btn

	var bottom_hbox = HBoxContainer.new()
	bottom_hbox.add_theme_constant_override("separation", 12)
	page.add_child(bottom_hbox)

	var btn_reset_kb = Button.new()
	btn_reset_kb.text = "↺ RESETEAZĂ TOATE KEYBINDS LA DEFAULT"
	btn_reset_kb.custom_minimum_size = Vector2(245, 28)
	_style_button(btn_reset_kb, Color(0.12, 0.18, 0.28), Color(0.22, 0.74, 0.97), Color(0.18, 0.28, 0.42), Color.WHITE, 10)
	btn_reset_kb.pressed.connect(func():
		listening_for_action = ""
		GameManager.reset_all_keybinds_to_default()
		_refresh_keybinds_ui()
	)
	bottom_hbox.add_child(btn_reset_kb)

	return page

func _start_listening_for_keybind(action_name: String) -> void:
	listening_for_action = action_name
	_refresh_keybinds_ui()

# -------------------------------------------------------------------------
# WARNING CONFIRMATION DIALOG FOR DIFFICULTY CHANGE & LEVEL RESET
# -------------------------------------------------------------------------
func _build_warning_modal() -> void:
	warning_overlay = Control.new()
	warning_overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	warning_overlay.visible = false
	add_child(warning_overlay)

	var w_dim = ColorRect.new()
	w_dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	w_dim.color = Color(0.01, 0.02, 0.04, 0.85)
	warning_overlay.add_child(w_dim)

	var w_panel = PanelContainer.new()
	w_panel.anchor_left = 0.5
	w_panel.anchor_top = 0.5
	w_panel.anchor_right = 0.5
	w_panel.anchor_bottom = 0.5
	w_panel.offset_left = -245.0
	w_panel.offset_top = -125.0
	w_panel.offset_right = 245.0
	w_panel.offset_bottom = 125.0
	w_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.08, 0.09, 0.14, 0.99), Color(0.96, 0.62, 0.08, 1.0), 3, 8, 16))
	warning_overlay.add_child(w_panel)

	var w_vbox = VBoxContainer.new()
	w_vbox.add_theme_constant_override("separation", 12)
	w_panel.add_child(w_vbox)

	warning_title_lbl = Label.new()
	warning_title_lbl.text = "⚠ ATENȚIE: RESETARE NIVEL NECESARĂ ⚠"
	warning_title_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	warning_title_lbl.add_theme_color_override("font_color", Color(1.0, 0.72, 0.18))
	warning_title_lbl.add_theme_font_size_override("font_size", 14)
	w_vbox.add_child(warning_title_lbl)

	warning_desc_lbl = Label.new()
	warning_desc_lbl.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	warning_desc_lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	warning_desc_lbl.size_flags_vertical = Control.SIZE_EXPAND_FILL
	warning_desc_lbl.add_theme_color_override("font_color", Color(0.92, 0.95, 1.0))
	warning_desc_lbl.add_theme_font_size_override("font_size", 11)
	w_vbox.add_child(warning_desc_lbl)

	var btn_row = HBoxContainer.new()
	btn_row.alignment = BoxContainer.ALIGNMENT_CENTER
	btn_row.add_theme_constant_override("separation", 16)
	w_vbox.add_child(btn_row)

	var btn_confirm = Button.new()
	btn_confirm.text = "✔ ACCEPTĂ & RESETEAZĂ NIVELUL"
	btn_confirm.custom_minimum_size = Vector2(215, 36)
	_style_button(btn_confirm, Color(0.08, 0.4, 0.25), Color(0.2, 0.92, 0.55), Color(0.12, 0.52, 0.34), Color.WHITE, 11)
	btn_confirm.pressed.connect(_on_warning_confirmed)
	btn_row.add_child(btn_confirm)

	var btn_cancel = Button.new()
	btn_cancel.text = "✖ ANULEAZĂ"
	btn_cancel.custom_minimum_size = Vector2(135, 36)
	_style_button(btn_cancel, Color(0.32, 0.12, 0.15), Color(0.95, 0.3, 0.32), Color(0.45, 0.16, 0.2), Color.WHITE, 11)
	btn_cancel.pressed.connect(_on_warning_cancelled)
	btn_row.add_child(btn_cancel)

func _prompt_difficulty_reset(tier_idx: int, is_manual_restart: bool = false) -> void:
	pending_difficulty_idx = tier_idx
	var tier = GameManager.DIFFICULTY_TIERS[tier_idx]
	if is_manual_restart:
		warning_title_lbl.text = "⚠ CONFIRMARE RESETARE NIVEL ⚠"
		warning_desc_lbl.text = "Ești sigur că vrei să resetezi nivelul curent de la început pe dificultatea [%s]?\n\n%s\n\nTot progresul din această sesiune va fi reinițializat." % [tier["name"], tier["desc"]]
	else:
		warning_title_lbl.text = "⚠ ATENȚIE: SCHIMBAREA DIFICULTĂȚII RESETEAZĂ NIVELUL ⚠"
		warning_desc_lbl.text = "Ai selectat dificultatea: » %s «\n%s\n\nAplicarea noii dificultăți va RESETA complet nivelul curent de la început. Ești sigur că accepți?" % [tier["name"], tier["desc"]]
	warning_overlay.visible = true

func _on_warning_confirmed() -> void:
	var target_idx = pending_difficulty_idx if pending_difficulty_idx >= 0 else GameManager.difficulty_index
	warning_overlay.visible = false
	visible = false
	GameManager.apply_difficulty_and_reset_level(target_idx)

func _on_warning_cancelled() -> void:
	pending_difficulty_idx = -1
	warning_overlay.visible = false
	_refresh_difficulty_ui()

func _on_respawn_checkpoint_pressed() -> void:
	var player = get_tree().get_first_node_in_group("player")
	close_pause_menu()
	if player and player.has_method("die_in_hazard"):
		player.die_in_hazard("manual_checkpoint_reset")

# -------------------------------------------------------------------------
# UI STATE REFRESHERS
# -------------------------------------------------------------------------
func _switch_tab(idx: int) -> void:
	listening_for_action = ""
	current_tab = idx
	for i in range(tab_pages.size()):
		tab_pages[i].visible = (i == current_tab)
	if current_tab >= 0 and current_tab < tab_scrolls.size() and is_instance_valid(tab_scrolls[current_tab]):
		tab_scrolls[current_tab].scroll_vertical = 0
	for i in range(tab_buttons.size()):
		if i == current_tab:
			_style_button(tab_buttons[i], Color(0.12, 0.28, 0.44), Color(0.22, 0.85, 1.0), Color(0.16, 0.34, 0.52), Color(0.95, 1.0, 1.0), 11)
		else:
			_style_button(tab_buttons[i], Color(0.08, 0.12, 0.19), Color(0.18, 0.26, 0.38), Color(0.12, 0.18, 0.28), Color(0.72, 0.8, 0.9), 11)
	_refresh_keybinds_ui()

func _refresh_all_states() -> void:
	_refresh_difficulty_ui()
	_refresh_audio_ui()
	_refresh_gameplay_ui()
	_refresh_keybinds_ui()

func _refresh_keybinds_ui() -> void:
	if keybind_status_lbl:
		if listening_for_action != "":
			keybind_status_lbl.text = "⚡ APASĂ ORICE TASTĂ SAU CLICK DE MOUSE PENTRU A SETA COMANDA (sau ESC pentru anulare)..."
			keybind_status_lbl.add_theme_color_override("font_color", Color(1.0, 0.78, 0.2))
		else:
			keybind_status_lbl.text = "Apasă pe butonul din dreapta oricărei acțiuni pentru a-i asigna o tastă nouă sau un click de mouse."
			keybind_status_lbl.add_theme_color_override("font_color", Color(0.68, 0.76, 0.86))

	for act_id in keybind_buttons.keys():
		var btn: Button = keybind_buttons[act_id]
		if not is_instance_valid(btn):
			continue
		if listening_for_action == act_id:
			btn.text = "[ APASĂ O TASTĂ... ]"
			_style_button(btn, Color(0.38, 0.24, 0.06), Color(1.0, 0.78, 0.2), Color(0.46, 0.3, 0.08), Color(1.0, 0.95, 0.6), 10)
		else:
			var bind_txt = GameManager.get_action_binding_text(act_id)
			btn.text = "[ " + bind_txt + " ]"
			_style_button(btn, Color(0.09, 0.15, 0.24), Color(0.22, 0.74, 0.97, 0.7), Color(0.14, 0.24, 0.38), Color(0.95, 0.88, 0.45), 10)

func _refresh_difficulty_ui() -> void:
	var cur_idx = GameManager.difficulty_index
	var cur_tier = GameManager.DIFFICULTY_TIERS[cur_idx]
	if header_diff_lbl:
		header_diff_lbl.text = "DIFICULTATE: %s" % cur_tier["name"]
		header_diff_lbl.add_theme_color_override("font_color", cur_tier["color"])

	_show_ai_quote(cur_idx)

	for i in range(diff_card_buttons.size()):
		var tier = GameManager.DIFFICULTY_TIERS[i]
		var btn = diff_card_buttons[i]
		var card = diff_card_panels[i]
		if i == cur_idx:
			btn.text = "✔ ACTIV ACUM"
			_style_button(btn, Color(0.1, 0.38, 0.26), tier["color"], Color(0.14, 0.46, 0.32), Color.WHITE, 10)
			card.add_theme_stylebox_override("panel", _make_stylebox(Color(0.08, 0.14, 0.22, 1.0), tier["color"], 2, 6, 8))
		else:
			btn.text = "SELECTEAZĂ"
			_style_button(btn, Color(0.1, 0.15, 0.24), Color(0.25, 0.38, 0.54), Color(0.16, 0.24, 0.36), Color(0.88, 0.94, 1.0), 10)
			card.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.13, 1.0), Color(0.16, 0.24, 0.36, 1.0), 1, 6, 8))

func _refresh_audio_ui() -> void:
	if lbl_master_val:
		lbl_master_val.text = "MUTE" if GameManager.audio_master_muted else (str(int(GameManager.audio_master_volume)) + "%")
	if lbl_sfx_val:
		lbl_sfx_val.text = "MUTE" if GameManager.audio_sfx_muted else (str(int(GameManager.audio_sfx_volume)) + "%")
	if lbl_music_val:
		lbl_music_val.text = "MUTE" if GameManager.audio_music_muted else (str(int(GameManager.audio_music_volume)) + "%")
	if lbl_amb_val:
		lbl_amb_val.text = "MUTE" if GameManager.audio_ambience_muted else (str(int(GameManager.audio_ambience_volume)) + "%")

	_style_mute_btn(btn_mute_master, GameManager.audio_master_muted)
	_style_mute_btn(btn_mute_sfx, GameManager.audio_sfx_muted)
	_style_mute_btn(btn_mute_music, GameManager.audio_music_muted)
	_style_mute_btn(btn_mute_amb, GameManager.audio_ambience_muted)

func _style_mute_btn(btn: Button, is_muted: bool) -> void:
	if not btn: return
	if is_muted:
		btn.text = "🔇 MUTED"
		_style_button(btn, Color(0.35, 0.12, 0.15), Color(0.95, 0.3, 0.32), Color(0.46, 0.16, 0.2), Color(1.0, 0.85, 0.85), 10)
	else:
		btn.text = "🔊 ACTIV"
		_style_button(btn, Color(0.08, 0.32, 0.24), Color(0.2, 0.85, 0.55), Color(0.12, 0.42, 0.3), Color(0.85, 1.0, 0.92), 10)

func _refresh_gameplay_ui() -> void:
	if btn_auto_pickup:
		if GameManager.setting_auto_pickup:
			btn_auto_pickup.text = "✔ ACTIVAT (ON)"
			_style_button(btn_auto_pickup, Color(0.08, 0.36, 0.26), Color(0.2, 0.88, 0.55), Color(0.12, 0.48, 0.34), Color.WHITE, 10)
		else:
			btn_auto_pickup.text = "DEZACTIVAT (OFF)"
			_style_button(btn_auto_pickup, Color(0.14, 0.18, 0.26), Color(0.32, 0.42, 0.55), Color(0.2, 0.26, 0.36), Color(0.82, 0.88, 0.95), 10)

	if lbl_shake_val:
		lbl_shake_val.text = str(int(GameManager.setting_screen_shake)) + "%"

	if btn_chassis:
		var is_dmg = (GameManager.player_chassis == "damaged")
		btn_chassis.text = "DAMAGED RUST" if is_dmg else "STANDARD CYBER"
		_style_button(btn_chassis, Color(0.28, 0.18, 0.1) if is_dmg else Color(0.1, 0.24, 0.38), Color(0.95, 0.6, 0.2) if is_dmg else Color(0.22, 0.85, 1.0), Color(0.36, 0.24, 0.14) if is_dmg else Color(0.14, 0.32, 0.48), Color.WHITE, 10)

	if btn_fullscreen:
		btn_fullscreen.text = "FULLSCREEN" if GameManager.setting_fullscreen else "WINDOWED"
		_style_button(btn_fullscreen, Color(0.12, 0.22, 0.34), Color(0.22, 0.78, 0.98), Color(0.16, 0.3, 0.44), Color.WHITE, 10)
