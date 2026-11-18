extends Area2D
# projectile_flame.gd - Fiery flame stream puff from flamethrower

@export var speed: float = 360.0
@export var damage: float = 8.0
var direction: Vector2 = Vector2.RIGHT
var lifetime: float = 0.32
var timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	area_entered.connect(_on_area_entered)

func _physics_process(dt: float) -> void:
	timer += dt
	if timer >= lifetime:
		queue_free()
		return

	position += direction * speed * dt
	var progress = timer / lifetime
	scale = Vector2(0.8 + progress * 0.7, 0.8 + progress * 0.5)
	modulate.a = 1.0 - (progress * 0.75)
	if sprite:
		sprite.frame = min(3, int(progress * 4.0))

func _on_body_entered(body: Node2D) -> void:
	if not body is Player and not body.is_in_group("player"):
		queue_free()

func _on_area_entered(area: Area2D) -> void:
	var target = area.get_parent()
	if area.is_in_group("enemies") or area.is_in_group("boss") or (target and (target.is_in_group("enemies") or target.is_in_group("boss"))):
		if target and target.has_method("take_damage"):
			target.take_damage(damage, direction.x * 0.2)
		queue_free()
