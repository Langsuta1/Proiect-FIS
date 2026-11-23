extends Control
class_name MainMenuUI
# main_menu.gd - Cyberpunk Main Menu with Live Animated Scrapyard Preview & 3-Slot Save File Manager

# Preview Textures
var tex_sky: Texture2D = preload("res://assets/bg_layer1_sky.png")
var tex_distant: Texture2D = preload("res://assets/bg_layer2_distant_scrap.png")
var tex_pipes: Texture2D = preload("res://assets/bg_layer3_midground_pipes.png")
var tex_girders: Texture2D = preload("res://assets/bg_layer4_foreground_girders.png")
var tex_robot_idle: Texture2D = preload("res://assets/robot_standard_idle_strip4.png")
var tex_robot_walk: Texture2D = preload("res://assets/robot_standard_walk_strip8.png")
var tex_drone: Texture2D = preload("res://assets/enemy_junk_drone_strip4.png")
var tex_boss: Texture2D = preload("res://assets/boss_crusher_titan_strip4.png")
var tex_car: Texture2D = preload("res://assets/crushed_car_obstacle.png")
var font_bold: Font = preload("res://assets/ui_font_bold.tres")

# Live Preview Animation State
var preview_time: float = 0.0
var scroll_distant: float = 0.0
var scroll_pipes: float = 0.0
var scroll_girders: float = 0.0
var embers: Array = []

# UI References
var btn_continue: Button = null
var lbl_continue_sub: Label = null
var btn_new_game: Button = null
var btn_save_files: Button = null
var btn_difficulty: Button = null
var lbl_diff_quote: Label = null
var status_card_panel: PanelContainer = null
var lbl_status_title: Label = null
var lbl_status_body: Label = null
var save_panel: PanelContainer = null
var save_slots_vbox: VBoxContainer = null
var right_spacer: Control = null
var is_save_panel_open: bool = false

func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	get_tree().paused = false
	_init_embers()
	_build_ui()
	_refresh_menu_state()

func _init_embers() -> void:
	embers.clear()
	for i in range(42):
		embers.append({
			"pos": Vector2(randf_range(0.0, 960.0), randf_range(0.0, 540.0)),
			"vel": Vector2(randf_range(-28.0, -8.0), randf_range(-32.0, -10.0)),
			"size": randf_range(1.2, 3.0),
			"phase": randf_range(0.0, TAU),
			"is_cyan": randf() < 0.35
		})

func _process(dt: float) -> void:
	preview_time += dt
	scroll_distant = fmod(scroll_distant + 10.0 * dt, 960.0)
	scroll_pipes = fmod(scroll_pipes + 24.0 * dt, 960.0)
	scroll_girders = fmod(scroll_girders + 44.0 * dt, 960.0)

	for e in embers:
		e["pos"] += e["vel"] * dt
		e["pos"].x += sin(preview_time * 2.2 + e["phase"]) * 8.0 * dt
		if e["pos"].y < -10.0 or e["pos"].x < -10.0:
			e["pos"] = Vector2(randf_range(180.0, 980.0), randf_range(440.0, 560.0))

	queue_redraw()

func _draw() -> void:
	var vp_size := get_viewport_rect().size
	if vp_size.x <= 0.0 or vp_size.y <= 0.0:
		vp_size = Vector2(960.0, 540.0)

	# 1. Atmospheric Sky & Parallax Scrapyard Layers
	if tex_sky:
		draw_texture_rect(tex_sky, Rect2(Vector2.ZERO, vp_size), false, Color(0.82, 0.88, 0.96, 1.0))
	else:
		draw_rect(Rect2(Vector2.ZERO, vp_size), Color(0.04, 0.06, 0.1, 1.0), true)

	_draw_scrolling_layer(tex_distant, scroll_distant, vp_size, Color(0.75, 0.82, 0.92, 0.85))
	_draw_scrolling_layer(tex_pipes, scroll_pipes, vp_size, Color(0.85, 0.9, 0.96, 0.92))
	_draw_scrolling_layer(tex_girders, scroll_girders, vp_size, Color(0.7, 0.78, 0.88, 0.7))

	# 2. Live Preview Stage on the Right Half (Scrapyard Platform + Hero Robot + Drone + Looming Boss)
	var floor_y: float = vp_size.y * 0.78
	var stage_left: float = vp_size.x * 0.40

	# Looming Boss Silhouette in the Smokey Background
	if tex_boss:
		var boss_frame: int = int(preview_time * 3.0) % 4
		var b_fw: float = float(tex_boss.get_width()) / 4.0
		var b_fh: float = float(tex_boss.get_height())
		var b_src := Rect2(boss_frame * b_fw, 0.0, b_fw, b_fh)
		var b_scale: float = 1.65
		var b_bob: float = sin(preview_time * 1.8) * 3.0
		var b_pos := Vector2(vp_size.x * 0.82, floor_y - b_fh * b_scale * 0.5 + 8.0 + b_bob)
		var b_dst := Rect2(b_pos - Vector2(b_fw * b_scale * 0.5, b_fh * b_scale * 0.5), Vector2(b_fw * b_scale, b_fh * b_scale))
		draw_texture_rect_region(tex_boss, b_dst, b_src, Color(0.32, 0.24, 0.28, 0.62))
		# Pulsing red boss visor glow
		var eye_a: float = 0.5 + 0.45 * sin(preview_time * 4.5)
		draw_circle(b_pos + Vector2(-18.0, -34.0), 6.0, Color(1.0, 0.2, 0.12, eye_a * 0.5))
		draw_circle(b_pos + Vector2(-18.0, -34.0), 2.5, Color(1.0, 0.55, 0.25, eye_a))

	# Scrapyard Ground Deck
	draw_rect(Rect2(Vector2(0.0, floor_y), Vector2(vp_size.x, vp_size.y - floor_y)), Color(0.05, 0.07, 0.11, 0.96), true)
	draw_line(Vector2(0.0, floor_y), Vector2(vp_size.x, floor_y), Color(0.22, 0.85, 1.0, 0.65), 2.0)
	draw_line(Vector2(stage_left, floor_y + 4.0), Vector2(vp_size.x, floor_y + 4.0), Color(0.96, 0.62, 0.08, 0.35), 1.5)

	# Crushed Car Scrap Prop on Right
	if tex_car:
		var cw: float = float(tex_car.get_width()) * 1.15
		var ch: float = float(tex_car.get_height()) * 1.15
		draw_texture_rect(tex_car, Rect2(Vector2(vp_size.x * 0.72, floor_y - ch + 6.0), Vector2(cw, ch)), false, Color(0.75, 0.8, 0.88, 0.92))

	# Patrolling Junk Drone in Mid-Air
	if tex_drone:
		var d_frame: int = int(preview_time * 8.0) % 4
		var d_fw: float = float(tex_drone.get_width()) / 4.0
		var d_fh: float = float(tex_drone.get_height())
		var d_src := Rect2(d_frame * d_fw, 0.0, d_fw, d_fh)
		var d_x: float = vp_size.x * 0.68 + sin(preview_time * 0.9) * 58.0
		var d_y: float = vp_size.y * 0.36 + cos(preview_time * 2.1) * 14.0
		var d_scale: float = 2.0
		var d_dst := Rect2(Vector2(d_x - d_fw * d_scale * 0.5, d_y - d_fh * d_scale * 0.5), Vector2(d_fw * d_scale, d_fh * d_scale))
		draw_texture_rect_region(tex_drone, d_dst, d_src, Color(0.95, 0.95, 1.0, 0.95))
		# Drone scanner beam
		var beam_pts := PackedVector2Array([
			Vector2(d_x, d_y + 10.0),
			Vector2(d_x - 32.0, floor_y),
			Vector2(d_x + 32.0, floor_y)
		])
		draw_colored_polygon(beam_pts, Color(1.0, 0.3, 0.15, 0.08 + 0.04 * sin(preview_time * 6.0)))

	# Hero Robot Animated Preview (Alternates between confident walk & heroic idle)
	var cycle_t: float = fmod(preview_time, 6.0)
	var is_walking: bool = cycle_t < 2.2
	var hero_x: float = vp_size.x * 0.58
	if is_walking:
		hero_x += sin((cycle_t / 2.2) * PI) * 26.0
	var hero_tex: Texture2D = tex_robot_walk if is_walking else tex_robot_idle
	var hero_frames: int = 8 if is_walking else 4
	if hero_tex:
		var h_frame: int = int(preview_time * (9.0 if is_walking else 4.5)) % hero_frames
		var h_fw: float = float(hero_tex.get_width()) / float(hero_frames)
		var h_fh: float = float(hero_tex.get_height())
		var h_src := Rect2(h_frame * h_fw, 0.0, h_fw, h_fh)
		var h_scale: float = 3.2
		var h_w: float = h_fw * h_scale
		var h_h: float = h_fh * h_scale
		# Ground shadow & cyan underglow
		draw_circle(Vector2(hero_x, floor_y + 2.0), 28.0, Color(0.0, 0.0, 0.0, 0.45))
		draw_arc(Vector2(hero_x, floor_y + 1.0), 34.0 + 4.0 * sin(preview_time * 3.5), PI, TAU, 24, Color(0.22, 0.85, 1.0, 0.35), 2.0)
		var h_dst := Rect2(Vector2(hero_x - h_w * 0.5, floor_y - h_h + 4.0), Vector2(h_w, h_h))
		draw_texture_rect_region(hero_tex, h_dst, h_src, Color(1.0, 1.0, 1.0, 1.0))

	# 3. Drifting Cyber Embers & Sparks
	for e in embers:
		var glow: float = 0.45 + 0.45 * sin(preview_time * 5.0 + e["phase"])
		var col: Color = Color(0.22, 0.88, 1.0, glow * 0.85) if e["is_cyan"] else Color(1.0, 0.55, 0.12, glow * 0.9)
		draw_circle(e["pos"], e["size"], col)

	# 4. Left-Side Gradient Readability Scrim (so Menu Buttons Pop Cleanly)
	var scrim_steps: int = 16
	var scrim_w: float = vp_size.x * 0.52
	for i in range(scrim_steps):
		var frac: float = float(i) / float(scrim_steps)
		var x0: float = frac * scrim_w
		var w0: float = (scrim_w / float(scrim_steps)) + 1.0
		var a: float = lerpf(0.88, 0.0, frac * frac)
		draw_rect(Rect2(Vector2(x0, 0.0), Vector2(w0, vp_size.y)), Color(0.03, 0.05, 0.09, a), true)

	# Subtle top/bottom cinematic letterbox accent lines
	draw_line(Vector2(0.0, 2.0), Vector2(vp_size.x, 2.0), Color(0.22, 0.85, 1.0, 0.35), 2.0)
	draw_line(Vector2(0.0, vp_size.y - 2.0), Vector2(vp_size.x, vp_size.y - 2.0), Color(0.22, 0.85, 1.0, 0.35), 2.0)

func _draw_scrolling_layer(tex: Texture2D, offset_x: float, vp_size: Vector2, tint: Color) -> void:
	if not tex:
		return
	var w: float = vp_size.x
	var h: float = vp_size.y
	var x1: float = -fmod(offset_x, w)
	draw_texture_rect(tex, Rect2(Vector2(x1, 0.0), Vector2(w, h)), false, tint)
	draw_texture_rect(tex, Rect2(Vector2(x1 + w, 0.0), Vector2(w, h)), false, tint)

# -------------------------------------------------------------------------
# UI CONSTRUCTION
# -------------------------------------------------------------------------
func _make_stylebox(bg: Color, border: Color, border_w: int = 2, radius: int = 6, pad: int = 10) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	sb.content_margin_left = pad
	sb.content_margin_right = pad
	sb.content_margin_top = pad
	sb.content_margin_bottom = pad
	return sb

func _style_button(btn: Button, bg: Color, border: Color, hover_bg: Color, font_col: Color = Color.WHITE, f_size: int = 13) -> void:
	btn.add_theme_stylebox_override("normal", _make_stylebox(bg, border, 1, 6, 9))
	btn.add_theme_stylebox_override("hover", _make_stylebox(hover_bg, border.lightened(0.25), 2, 6, 9))
	btn.add_theme_stylebox_override("pressed", _make_stylebox(hover_bg.darkened(0.15), Color.WHITE, 2, 6, 9))
	btn.add_theme_stylebox_override("disabled", _make_stylebox(Color(0.06, 0.08, 0.12, 0.75), Color(0.16, 0.2, 0.28, 0.7), 1, 6, 9))
	btn.add_theme_color_override("font_color", font_col)
	btn.add_theme_color_override("font_hover_color", Color.WHITE)
	btn.add_theme_color_override("font_disabled_color", Color(0.42, 0.48, 0.56))
	btn.add_theme_font_size_override("font_size", f_size)

func _build_ui() -> void:
	# Root Margin
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 36)
	margin.add_theme_constant_override("margin_right", 36)
	margin.add_theme_constant_override("margin_top", 28)
	margin.add_theme_constant_override("margin_bottom", 24)
	add_child(margin)

	var main_hbox := HBoxContainer.new()
	main_hbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	main_hbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main_hbox.add_theme_constant_override("separation", 28)
	margin.add_child(main_hbox)

	# --- LEFT COLUMN: TITLE + MENU BUTTONS ---
	var left_vbox := VBoxContainer.new()
	left_vbox.custom_minimum_size = Vector2(340, 0)
	left_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left_vbox.add_theme_constant_override("separation", 10)
	main_hbox.add_child(left_vbox)

	# Badge
	var badge := Label.new()
	badge.text = "● PLAYABLE DEMO // BUILD V9"
	badge.add_theme_color_override("font_color", Color(0.22, 0.88, 0.55))
	badge.add_theme_font_size_override("font_size", 10)
	left_vbox.add_child(badge)

	# Game Title
	var title := Label.new()
	title.text = "SCRAPBORN"
	title.add_theme_font_override("font", font_bold)
	title.add_theme_color_override("font_color", Color(0.95, 0.98, 1.0))
	title.add_theme_color_override("font_outline_color", Color(0.08, 0.45, 0.65, 0.9))
	title.add_theme_constant_override("outline_size", 5)
	title.add_theme_font_size_override("font_size", 42)
	left_vbox.add_child(title)

	var subtitle := Label.new()
	subtitle.text = "CYBER METROIDVANIA // SCRAPYARD SECTOR 01"
	subtitle.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	subtitle.add_theme_font_size_override("font_size", 11)
	left_vbox.add_child(subtitle)

	var sep := ColorRect.new()
	sep.custom_minimum_size = Vector2(0, 2)
	sep.color = Color(0.22, 0.85, 1.0, 0.45)
	left_vbox.add_child(sep)

	var top_gap := Control.new()
	top_gap.custom_minimum_size = Vector2(0, 8)
	left_vbox.add_child(top_gap)

	# 1. CONTINUE Button
	btn_continue = Button.new()
	btn_continue.text = "▶  CONTINUĂ SALVAREA"
	btn_continue.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn_continue.custom_minimum_size = Vector2(0, 42)
	btn_continue.pressed.connect(_on_continue_pressed)
	left_vbox.add_child(btn_continue)

	lbl_continue_sub = Label.new()
	lbl_continue_sub.text = ""
	lbl_continue_sub.add_theme_color_override("font_color", Color(0.68, 0.78, 0.88))
	lbl_continue_sub.add_theme_font_size_override("font_size", 10)
	left_vbox.add_child(lbl_continue_sub)

	# 2. START / NEW GAME Button
	btn_new_game = Button.new()
	btn_new_game.text = "⚡  JOC NOU (START GAME)"
	btn_new_game.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn_new_game.custom_minimum_size = Vector2(0, 40)
	_style_button(btn_new_game, Color(0.08, 0.24, 0.38, 0.92), Color(0.22, 0.85, 1.0), Color(0.12, 0.34, 0.52), Color(0.92, 0.98, 1.0), 13)
	btn_new_game.pressed.connect(_on_new_game_pressed)
	left_vbox.add_child(btn_new_game)

	# 3. SAVE FILES Manager Toggle
	btn_save_files = Button.new()
	btn_save_files.text = "💾  FIȘIERE SALVARE (3 SLOTURI)"
	btn_save_files.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn_save_files.custom_minimum_size = Vector2(0, 36)
	_style_button(btn_save_files, Color(0.09, 0.13, 0.21, 0.92), Color(0.32, 0.52, 0.75), Color(0.14, 0.2, 0.32), Color(0.86, 0.92, 1.0), 12)
	btn_save_files.pressed.connect(_toggle_save_panel)
	left_vbox.add_child(btn_save_files)

	# 4. DIFFICULTY Quick Selector
	btn_difficulty = Button.new()
	btn_difficulty.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn_difficulty.custom_minimum_size = Vector2(0, 36)
	btn_difficulty.pressed.connect(_on_cycle_difficulty_pressed)
	left_vbox.add_child(btn_difficulty)

	lbl_diff_quote = Label.new()
	lbl_diff_quote.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_diff_quote.add_theme_color_override("font_color", Color(0.65, 0.72, 0.82))
	lbl_diff_quote.add_theme_font_size_override("font_size", 10)
	left_vbox.add_child(lbl_diff_quote)

	var bot_spacer := Control.new()
	bot_spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	left_vbox.add_child(bot_spacer)

	# 5. QUIT Button
	var btn_quit := Button.new()
	btn_quit.text = "✕  IEȘIRE DIN JOC"
	btn_quit.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn_quit.custom_minimum_size = Vector2(0, 34)
	_style_button(btn_quit, Color(0.22, 0.08, 0.1, 0.88), Color(0.85, 0.26, 0.3), Color(0.34, 0.12, 0.15), Color(1.0, 0.84, 0.84), 12)
	btn_quit.pressed.connect(_on_quit_pressed)
	left_vbox.add_child(btn_quit)

	var controls_hint := Label.new()
	controls_hint.text = "WASD / SPACE Mișcare  •  C Dash  •  E Grapple  •  I Inventar  •  ESC Pauză"
	controls_hint.add_theme_color_override("font_color", Color(0.55, 0.65, 0.76))
	controls_hint.add_theme_font_size_override("font_size", 9)
	left_vbox.add_child(controls_hint)

	# --- RIGHT COLUMN: LIVE PREVIEW OVERLAY & SAVE FILES PANEL ---
	var right_vbox := VBoxContainer.new()
	right_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	right_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	main_hbox.add_child(right_vbox)

	# Top-right Preview Label
	var preview_tag := Label.new()
	preview_tag.text = "LIVE PREVIEW // SECTOR 01: THE HEAP"
	preview_tag.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	preview_tag.add_theme_color_override("font_color", Color(0.96, 0.62, 0.08, 0.9))
	preview_tag.add_theme_font_size_override("font_size", 10)
	right_vbox.add_child(preview_tag)

	# Expandable Save Files Panel (hidden by default so the Live Preview shines!)
	save_panel = PanelContainer.new()
	save_panel.visible = false
	save_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	save_panel.size_flags_vertical = Control.SIZE_EXPAND_FILL
	save_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.04, 0.07, 0.12, 0.92), Color(0.22, 0.85, 1.0, 0.85), 2, 8, 14))
	right_vbox.add_child(save_panel)

	var save_root := VBoxContainer.new()
	save_root.add_theme_constant_override("separation", 10)
	save_panel.add_child(save_root)

	var save_hdr_hbox := HBoxContainer.new()
	save_root.add_child(save_hdr_hbox)

	var save_title := Label.new()
	save_title.text = "💾 FIȘIERE SALVARE (SAVE FILES)"
	save_title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	save_title.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	save_title.add_theme_font_size_override("font_size", 14)
	save_hdr_hbox.add_child(save_title)

	var btn_close_saves := Button.new()
	btn_close_saves.text = "✕ ÎNCHIDE"
	_style_button(btn_close_saves, Color(0.14, 0.18, 0.26), Color(0.38, 0.5, 0.65), Color(0.22, 0.28, 0.4), Color.WHITE, 10)
	btn_close_saves.pressed.connect(_toggle_save_panel)
	save_hdr_hbox.add_child(btn_close_saves)

	save_slots_vbox = VBoxContainer.new()
	save_slots_vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	save_slots_vbox.add_theme_constant_override("separation", 10)
	save_root.add_child(save_slots_vbox)

	# Bottom-right Compact Save Status Card (shown when Save Panel is closed)
	right_spacer = Control.new()
	right_spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	right_vbox.add_child(right_spacer)

	status_card_panel = PanelContainer.new()
	status_card_panel.size_flags_horizontal = Control.SIZE_SHRINK_END
	status_card_panel.custom_minimum_size = Vector2(310, 0)
	status_card_panel.add_theme_stylebox_override("panel", _make_stylebox(Color(0.05, 0.08, 0.14, 0.86), Color(0.22, 0.85, 1.0, 0.6), 1, 6, 10))
	right_vbox.add_child(status_card_panel)

	var st_vbox := VBoxContainer.new()
	st_vbox.add_theme_constant_override("separation", 3)
	status_card_panel.add_child(st_vbox)

	lbl_status_title = Label.new()
	lbl_status_title.add_theme_color_override("font_color", Color(0.22, 0.85, 1.0))
	lbl_status_title.add_theme_font_size_override("font_size", 11)
	st_vbox.add_child(lbl_status_title)

	lbl_status_body = Label.new()
	lbl_status_body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lbl_status_body.add_theme_color_override("font_color", Color(0.78, 0.86, 0.94))
	lbl_status_body.add_theme_font_size_override("font_size", 10)
	st_vbox.add_child(lbl_status_body)

# -------------------------------------------------------------------------
# STATE REFRESH & ACTIONS
# -------------------------------------------------------------------------
func _refresh_menu_state() -> void:
	# 1. Latest Save / Continue Button
	var latest_slot: int = GameManager.get_latest_save_slot()
	if latest_slot > 0:
		var info: Dictionary = GameManager.get_save_slot_info(latest_slot)
		btn_continue.disabled = false
		btn_continue.text = "▶  CONTINUĂ (SLOT 0%d)" % latest_slot
		_style_button(btn_continue, Color(0.08, 0.36, 0.26, 0.95), Color(0.2, 0.88, 0.55), Color(0.12, 0.48, 0.34), Color(0.92, 1.0, 0.95), 14)
		var zone: String = str(info.get("zone_name", "Sector 01"))
		var diff: String = str(info.get("difficulty_name", "MEDIUM"))
		var hp_val: int = int(round(float(info.get("player_hp", 100.0))))
		var saved_at: String = str(info.get("saved_at", ""))
		lbl_continue_sub.text = "   %s  •  HP %d%%  •  %s" % [zone, hp_val, diff]
		lbl_continue_sub.visible = true

		lbl_status_title.text = "💾 ULTIMA SALVARE // SLOT 0%d" % latest_slot
		lbl_status_body.text = "%s\nDificultate: %s  |  HP: %d%%\nSalvat: %s" % [zone, diff, hp_val, saved_at]
	else:
		btn_continue.disabled = true
		btn_continue.text = "▶  CONTINUĂ (FĂRĂ SALVARE)"
		_style_button(btn_continue, Color(0.08, 0.1, 0.14, 0.75), Color(0.2, 0.26, 0.34), Color(0.08, 0.1, 0.14, 0.75), Color(0.5, 0.56, 0.64), 13)
		lbl_continue_sub.visible = false

		lbl_status_title.text = "📡 SISTEM PREGĂTIT"
		lbl_status_body.text = "Niciun fișier de salvare găsit.\nApasă JOC NOU pentru a începe aventura în Scrapyard!"

	# 2. Difficulty Button
	var tier: Dictionary = GameManager.DIFFICULTY_TIERS[GameManager.difficulty_index]
	btn_difficulty.text = "⚔  DIFICULTATE: %s" % tier["name"]
	var t_col: Color = tier["color"]
	_style_button(btn_difficulty, Color(0.09, 0.12, 0.19, 0.92), t_col, Color(0.14, 0.18, 0.28), t_col.lightened(0.2), 12)
	lbl_diff_quote.text = tier["desc"] + "\n" + tier["quote"]

	# 3. Rebuild Save Slots Panel
	_rebuild_save_slots_ui()

func _rebuild_save_slots_ui() -> void:
	for child in save_slots_vbox.get_children():
		child.queue_free()

	for slot_idx in range(1, GameManager.SAVE_SLOT_COUNT + 1):
		var info: Dictionary = GameManager.get_save_slot_info(slot_idx)
		var has_data: bool = not info.is_empty()

		var card := PanelContainer.new()
		var border_col: Color = Color(0.22, 0.85, 1.0, 0.8) if has_data else Color(0.2, 0.28, 0.38, 0.8)
		card.add_theme_stylebox_override("panel", _make_stylebox(Color(0.07, 0.11, 0.18, 0.94), border_col, 1, 6, 10))
		save_slots_vbox.add_child(card)

		var vbox := VBoxContainer.new()
		vbox.add_theme_constant_override("separation", 6)
		card.add_child(vbox)

		var top_row := HBoxContainer.new()
		vbox.add_child(top_row)

		var slot_lbl := Label.new()
		slot_lbl.text = "SLOT 0%d  —  %s" % [slot_idx, str(info.get("zone_name", "GOL")) if has_data else "SLOT GOL"]
		slot_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		slot_lbl.add_theme_color_override("font_color", Color(0.95, 0.98, 1.0) if has_data else Color(0.55, 0.62, 0.72))
		slot_lbl.add_theme_font_size_override("font_size", 12)
		top_row.add_child(slot_lbl)

		if has_data:
			var time_lbl := Label.new()
			time_lbl.text = str(info.get("saved_at", ""))
			time_lbl.add_theme_color_override("font_color", Color(0.6, 0.7, 0.8))
			time_lbl.add_theme_font_size_override("font_size", 9)
			top_row.add_child(time_lbl)

			var details := Label.new()
			var hp_v: int = int(round(float(info.get("player_hp", 100.0))))
			var diff_s: String = str(info.get("difficulty_name", "MEDIUM"))
			var boss_txt: String = "  •  ✔ BOSS ÎNVINS" if bool(info.get("boss_defeated", false)) else ""
			details.text = "HP: %d%%  •  Dificultate: %s%s" % [hp_v, diff_s, boss_txt]
			details.add_theme_color_override("font_color", Color(0.22, 0.88, 0.55) if bool(info.get("boss_defeated", false)) else Color(0.75, 0.84, 0.92))
			details.add_theme_font_size_override("font_size", 10)
			vbox.add_child(details)

		var btn_row := HBoxContainer.new()
		btn_row.add_theme_constant_override("separation", 8)
		vbox.add_child(btn_row)

		var s_num: int = slot_idx
		if has_data:
			var btn_load := Button.new()
			btn_load.text = "▶ ÎNCARCĂ"
			btn_load.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			_style_button(btn_load, Color(0.08, 0.36, 0.26), Color(0.2, 0.88, 0.55), Color(0.12, 0.48, 0.34), Color.WHITE, 11)
			btn_load.pressed.connect(func(): GameManager.load_game(s_num))
			btn_row.add_child(btn_load)

			var btn_overwrite := Button.new()
			btn_overwrite.text = "⟳ JOC NOU"
			_style_button(btn_overwrite, Color(0.12, 0.2, 0.32), Color(0.22, 0.78, 0.98), Color(0.16, 0.28, 0.44), Color.WHITE, 10)
			btn_overwrite.pressed.connect(func(): GameManager.start_new_game(s_num, GameManager.difficulty_index))
			btn_row.add_child(btn_overwrite)

			var btn_del := Button.new()
			btn_del.text = "🗑 ȘTERGE"
			_style_button(btn_del, Color(0.28, 0.1, 0.12), Color(0.92, 0.28, 0.32), Color(0.4, 0.14, 0.16), Color(1.0, 0.85, 0.85), 10)
			btn_del.pressed.connect(func():
				GameManager.delete_save_slot(s_num)
				_refresh_menu_state()
			)
			btn_row.add_child(btn_del)
		else:
			var btn_start_slot := Button.new()
			btn_start_slot.text = "⚡ ÎNCEPE JOC NOU ÎN SLOT 0%d" % s_num
			btn_start_slot.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			_style_button(btn_start_slot, Color(0.08, 0.22, 0.36), Color(0.22, 0.85, 1.0), Color(0.12, 0.32, 0.5), Color.WHITE, 11)
			btn_start_slot.pressed.connect(func(): GameManager.start_new_game(s_num, GameManager.difficulty_index))
			btn_row.add_child(btn_start_slot)

func _toggle_save_panel() -> void:
	is_save_panel_open = not is_save_panel_open
	save_panel.visible = is_save_panel_open
	status_card_panel.visible = not is_save_panel_open
	if right_spacer:
		right_spacer.visible = not is_save_panel_open
	if is_save_panel_open:
		_rebuild_save_slots_ui()

func _on_continue_pressed() -> void:
	var latest: int = GameManager.get_latest_save_slot()
	if latest > 0:
		GameManager.load_game(latest)

func _on_new_game_pressed() -> void:
	var empty_slot: int = GameManager.get_first_empty_save_slot()
	GameManager.start_new_game(empty_slot, GameManager.difficulty_index)

func _on_cycle_difficulty_pressed() -> void:
	var next_idx: int = (GameManager.difficulty_index + 1) % GameManager.DIFFICULTY_TIERS.size()
	GameManager.set_difficulty_tier(next_idx)
	_refresh_menu_state()

func _on_quit_pressed() -> void:
	get_tree().quit()
