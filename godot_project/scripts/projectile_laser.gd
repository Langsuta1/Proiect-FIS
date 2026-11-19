extends Area2D
# projectile_laser.gd - Cyan plasma pulse beam with safe universal damage calls

@export var speed: float = 480.0
@export var damage: float = 24.0
var direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)
	rotation = direction.angle()
	var t = get_tree().create_timer(3.0)
	t.timeout.connect(func(): if is_inside_tree(): queue_free())

func _physics_process(dt: float) -> void:
	position += direction * speed * dt

func _on_body_entered(body: Node2D) -> void:
	if not body is Player and not body.is_in_group("player"):
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	var target = area.get_parent()
	if area.is_in_group("enemies") or area.is_in_group("boss") or (target and (target.is_in_group("enemies") or target.is_in_group("boss"))):
		if target and target.has_method("take_damage"):
			var kb = sign(direction.x) if abs(direction.x) > 0.05 else 1.0
			target.take_damage(damage, kb)
		queue_free()
