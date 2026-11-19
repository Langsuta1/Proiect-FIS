extends Node2D
class_name GrenadeExplosionFX
# grenade_explosion_fx.gd - Multi-layered procedural & particle explosion animation for Frag, EMP, Cryo & Fire grenades

var grenade_type: String = "frag"
var elapsed: float = 0.0
var duration: float = 0.65

# Lingering fire hazard state (for "fire" thermite grenade)
var is_lingering_fire: bool = false
var fire_pool_duration: float = 3.2
var fire_damage_tick: float = 0.0

var clouds: Array = []
var particles: Array = []
var lightning_bolts: Array = []
var ice_spikes: Array = []

func init(type: String, pos: Vector2) -> void:
	grenade_type = type
	global_position = pos
	z_index = 25
	_generate_fx_elements()

func _ready() -> void:
	if clouds.is_empty():
		_generate_fx_elements()
	_trigger_camera_shake()

func _trigger_camera_shake() -> void:
	var player = get_tree().get_first_node_in_group("player")
	if player and player.has_method("add_camera_shake"):
		player.add_camera_shake(7.5, 0.28)

func _generate_fx_elements() -> void:
	clouds.clear()
	particles.clear()
	lightning_bolts.clear()
	ice_spikes.clear()

	# 1. Generate billowing explosion cloud puffs
	var num_clouds = 14
	for i in range(num_clouds):
		var ang = (TAU * float(i) / float(num_clouds)) + randf_range(-0.2, 0.2)
		var spd = randf_range(45.0, 145.0)
		if i < 4:
			spd = randf_range(10.0, 45.0) # Dense center clouds
		clouds.append({
			"pos": Vector2.ZERO,
			"vel": Vector2(cos(ang), sin(ang)) * spd + Vector2(0, -18.0),
			"base_radius": randf_range(12.0, 24.0),
			"delay": randf_range(0.0, 0.06),
			"phase": randf_range(0.0, TAU)
		})

	# 2. Generate 28 high-speed flying sparks / shrapnel / ice shards / embers
	for i in range(28):
		var ang = randf_range(0.0, TAU)
		var spd = randf_range(90.0, 290.0)
		var grav = 520.0
		if grenade_type == "emp":
			grav = 40.0
		elif grenade_type == "cryo":
			grav = 220.0
		particles.append({
			"pos": Vector2(cos(ang), sin(ang)) * randf_range(2.0, 10.0),
			"prev_pos": Vector2.ZERO,
			"vel": Vector2(cos(ang), sin(ang)) * spd + Vector2(0, randf_range(-90.0, -20.0)),
			"grav": grav,
			"size": randf_range(2.0, 4.2),
			"life": randf_range(0.32, 0.62)
		})

	# 3. Type-specific geometry (Lightning bolts for EMP, Ice spikes for Cryo)
	if grenade_type == "emp":
		_regenerate_lightning()
	elif grenade_type == "cryo":
		var num_spikes = 10
		for i in range(num_spikes):
			var ang = (TAU * float(i) / float(num_spikes)) + randf_range(-0.1, 0.1)
			ice_spikes.append({
				"angle": ang,
				"max_len": randf_range(38.0, 76.0),
				"width": randf_range(5.0, 9.0)
			})
	elif grenade_type == "fire":
		is_lingering_fire = true

func _regenerate_lightning() -> void:
	lightning_bolts.clear()
	for i in range(9):
		var base_ang = (TAU * float(i) / 9.0) + randf_range(-0.25, 0.25)
		var max_r = randf_range(45.0, 88.0)
		var pts: PackedVector2Array = PackedVector2Array([Vector2.ZERO])
		var steps = 5
		for s in range(1, steps + 1):
			var frac = float(s) / float(steps)
			var r = max_r * frac
			var jitter_ang = base_ang + randf_range(-0.28, 0.28)
			pts.append(Vector2(cos(jitter_ang), sin(jitter_ang)) * r)
		lightning_bolts.append(pts)

func _process(dt: float) -> void:
	elapsed += dt

	# Update clouds
	for c in clouds:
		if elapsed >= c["delay"]:
			c["pos"] += c["vel"] * dt
			c["vel"] *= pow(0.08, dt) # Rapid air drag so clouds billow outward and stop

	# Update particles
	for p in particles:
		p["prev_pos"] = p["pos"]
		p["vel"].y += p["grav"] * dt
		p["vel"] *= pow(0.45, dt)
		p["pos"] += p["vel"] * dt

	# EMP crackle refresh
	if grenade_type == "emp" and elapsed < duration and int(elapsed * 30.0) != int((elapsed - dt) * 30.0):
		_regenerate_lightning()

	# Lingering fire pool damage ticks
	if is_lingering_fire and elapsed < fire_pool_duration:
		fire_damage_tick += dt
		if fire_damage_tick >= 0.45:
			fire_damage_tick = 0.0
			_apply_lingering_fire_pool()

	queue_redraw()

	var total_life = fire_pool_duration if is_lingering_fire else duration
	if elapsed >= total_life:
		queue_free()

func _apply_lingering_fire_pool() -> void:
	var pool_radius = 58.0
	for group_name in ["player", "enemies", "boss"]:
		for node in get_tree().get_nodes_in_group(group_name):
			if not is_instance_valid(node):
				continue
			var target = node.get_parent() if (node is Area2D and node.get_parent()) else node
			if is_instance_valid(target) and global_position.distance_to(target.global_position) <= pool_radius:
				if target.has_method("apply_grenade_effect"):
					target.apply_grenade_effect("fire_pool", global_position, 0.5)

func _draw() -> void:
	var t = clamp(elapsed / duration, 0.0, 1.0)

	# 1. LINGERING THERMITE FIRE POOL (Draws under primary explosion and lasts 3.2s)
	if is_lingering_fire and elapsed < fire_pool_duration:
		var pool_fade = clamp(1.0 - (elapsed / fire_pool_duration), 0.0, 1.0)
		var pool_w = 54.0 * clamp(elapsed * 5.0, 0.4, 1.0)
		# Glowing ember ground bed
		draw_circle(Vector2(0, 6), pool_w * 0.45, Color(1.0, 0.25, 0.05, 0.32 * pool_fade))
		# Animated dancing flame tongues across the ground
		for i in range(-5, 6):
			var fx = float(i) * 9.5
			var wave = sin(elapsed * 14.0 + float(i) * 1.7)
			var fh = (14.0 + 8.0 * wave) * pool_fade
			var base_pt = Vector2(fx, 8.0)
			var tip_pt = Vector2(fx + cos(elapsed * 9.0 + float(i)) * 4.0, 8.0 - fh)
			var tri_pts = PackedVector2Array([
				base_pt + Vector2(-5.5, 0),
				base_pt + Vector2(5.5, 0),
				tip_pt
			])
			draw_colored_polygon(tri_pts, Color(1.0, 0.38, 0.05, 0.75 * pool_fade))
			var inner_pts = PackedVector2Array([
				base_pt + Vector2(-2.5, 0),
				base_pt + Vector2(2.5, 0),
				base_pt + (tip_pt - base_pt) * 0.65
			])
			draw_colored_polygon(inner_pts, Color(1.0, 0.9, 0.3, 0.85 * pool_fade))

	if elapsed > duration:
		return

	# Palette by grenade type
	var core_col = Color(1.0, 0.98, 0.85, 1.0)
	var mid_col = Color(1.0, 0.55, 0.1, 1.0)
	var outer_col = Color(0.25, 0.22, 0.2, 0.85)
	var ring_col = Color(1.0, 0.75, 0.25, 1.0)

	match grenade_type:
		"emp":
			core_col = Color(0.9, 1.0, 1.0, 1.0)
			mid_col = Color(0.15, 0.78, 1.0, 0.95)
			outer_col = Color(0.08, 0.25, 0.65, 0.75)
			ring_col = Color(0.3, 0.92, 1.0, 1.0)
		"cryo":
			core_col = Color(0.92, 0.98, 1.0, 1.0)
			mid_col = Color(0.38, 0.85, 1.0, 0.95)
			outer_col = Color(0.18, 0.48, 0.82, 0.75)
			ring_col = Color(0.65, 0.95, 1.0, 1.0)
		"fire":
			core_col = Color(1.0, 0.95, 0.5, 1.0)
			mid_col = Color(1.0, 0.32, 0.05, 0.95)
			outer_col = Color(0.45, 0.1, 0.05, 0.8)
			ring_col = Color(1.0, 0.5, 0.1, 1.0)

	# 2. OUTER AMBIENT GLOW HALO
	var halo_alpha = (1.0 - t) * 0.42
	var halo_rad = lerpf(24.0, 96.0, ease(t, 0.3))
	draw_circle(Vector2.ZERO, halo_rad, Color(mid_col.r, mid_col.g, mid_col.b, halo_alpha))

	# 3. CRYO ICE SPIKES (Jutting crystalline shards)
	if grenade_type == "cryo":
		var spike_grow = clamp(elapsed / 0.12, 0.0, 1.0)
		var spike_fade = clamp(1.0 - ((elapsed - 0.25) / 0.4), 0.0, 1.0)
		for sp in ice_spikes:
			var ang = sp["angle"]
			var dir = Vector2(cos(ang), sin(ang))
			var perp = Vector2(-dir.y, dir.x)
			var slen = sp["max_len"] * spike_grow
			var sw = sp["width"] * spike_fade
			var poly = PackedVector2Array([
				perp * sw,
				dir * slen,
				-perp * sw,
				-dir * (slen * 0.15)
			])
			draw_colored_polygon(poly, Color(0.45, 0.88, 1.0, 0.8 * spike_fade))
			draw_polyline(PackedVector2Array([perp * sw, dir * slen, -perp * sw]), Color(0.95, 1.0, 1.0, 0.95 * spike_fade), 1.5)

	# 4. BILLOWING EXPLOSION CLOUDS (Outer layer -> Mid layer -> Hot Inner Core)
	for c in clouds:
		if elapsed < c["delay"]:
			continue
		var ct = clamp((elapsed - c["delay"]) / (duration - c["delay"]), 0.0, 1.0)
		var rad = c["base_radius"] * (0.4 + 1.15 * sin(ct * PI * 0.75))
		var alpha = clamp(1.0 - pow(ct, 1.6), 0.0, 1.0)

		# Color transition from core -> mid -> outer smoke/frost
		var col: Color
		if ct < 0.25:
			col = core_col.lerp(mid_col, ct / 0.25)
		else:
			col = mid_col.lerp(outer_col, (ct - 0.25) / 0.75)
		col.a *= alpha
		draw_circle(c["pos"], rad, col)

		# Bright rim highlight on early clouds
		if ct < 0.45:
			var inner_c = core_col
			inner_c.a = (1.0 - ct / 0.45) * 0.75
			draw_circle(c["pos"] * 0.7, rad * 0.55, inner_c)

	# 5. INITIAL BLINDING CORE FLASH (First 0.12s)
	if elapsed < 0.14:
		var ft = elapsed / 0.14
		var flash_r = lerpf(14.0, 56.0, ft)
		draw_circle(Vector2.ZERO, flash_r, Color(1.0, 1.0, 1.0, (1.0 - ft) * 0.95))

	# 6. SUPERSONIC EXPANDING SHOCKWAVE RINGS
	var ring_t = clamp(elapsed / 0.42, 0.0, 1.0)
	if ring_t < 1.0:
		var r1 = lerpf(10.0, 88.0, 1.0 - pow(1.0 - ring_t, 2.5))
		var a1 = (1.0 - ring_t) * 0.95
		var w1 = lerpf(6.0, 1.2, ring_t)
		draw_arc(Vector2.ZERO, r1, 0.0, TAU, 36, Color(ring_col.r, ring_col.g, ring_col.b, a1), w1)

		# Secondary inner pulse ring
		var r2 = r1 * 0.65
		draw_arc(Vector2.ZERO, r2, 0.0, TAU, 28, Color(1.0, 1.0, 1.0, a1 * 0.7), max(1.0, w1 * 0.5))

	# 7. EMP CRACKLING LIGHTNING ARCS
	if grenade_type == "emp" and elapsed < 0.48:
		var emp_alpha = clamp(1.0 - (elapsed / 0.48), 0.0, 1.0)
		for bolt in lightning_bolts:
			draw_polyline(bolt, Color(0.15, 0.75, 1.0, emp_alpha * 0.65), 4.0)
			draw_polyline(bolt, Color(0.92, 1.0, 1.0, emp_alpha), 1.6)

	# 8. FLYING SPARKS / SHRAPNEL / ICE SHARDS WITH TRAILS
	for p in particles:
		if elapsed > p["life"]:
			continue
		var pt_ratio = elapsed / p["life"]
		var p_alpha = 1.0 - pow(pt_ratio, 1.5)
		var trail_start = p["pos"] - p["vel"] * 0.032
		var p_col = core_col.lerp(ring_col, pt_ratio)
		p_col.a = p_alpha
		draw_line(trail_start, p["pos"], p_col, p["size"] * 0.75)
		draw_circle(p["pos"], p["size"] * 0.55, Color(1.0, 1.0, 1.0, p_alpha))
