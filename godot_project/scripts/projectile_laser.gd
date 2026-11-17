extends Area2D
# projectile_laser.gd - Cyan plasma pulse beam

@export var speed: float = 480.0
@export var damage: float = 24.0
var direction: Vector2 = Vector2.RIGHT

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(dt: float) -> void:
	position += direction * speed * dt

func _on_body_entered(body: Node2D) -> void:
	if not body is Player:
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	if area.is_in_group("enemies"):
		if area.get_parent().has_method("take_damage"):
			area.get_parent().take_damage(damage, direction.x)
		queue_free()
