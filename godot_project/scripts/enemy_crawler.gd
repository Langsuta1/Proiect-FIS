extends CharacterBody2D
class_name EnemyCrawler
# enemy_crawler.gd - Scrap Crawler with safe default parameters to prevent crash

@export var patrol_distance: float = 140.0
@export var speed: float = 45.0
@export var max_hp: float = 32.0

var hp: float = 32.0
var start_x: float = 0.0
var direction: int = 1
var anim_timer: float = 0.0

@onready var sprite: Sprite2D = $Sprite2D
@onready var hurtbox: Area2D = $Hurtbox
@onready var damage_area: Area2D = $DamageArea

func _ready() -> void:
	start_x = global_position.x
	hp = max_hp
	hurtbox.add_to_group("enemies")
	damage_area.body_entered.connect(_on_damage_body_entered)

func _physics_process(dt: float) -> void:
	if not is_on_floor():
		velocity.y += 850.0 * dt

	velocity.x = direction * speed

	if global_position.x > start_x + patrol_distance:
		direction = -1
	elif global_position.x < start_x - patrol_distance:
		direction = 1

	sprite.flip_h = (direction == -1)

	anim_timer += dt
	sprite.frame = int(anim_timer / 0.12) % 4

	move_and_slide()

func _on_damage_body_entered(body: Node2D) -> void:
	if body is Player:
		var kb_dir = 1.0 if body.global_position.x > global_position.x else -1.0
		body.take_damage(20.0, kb_dir)

func take_damage(amount: float, knockback: float = 0.0) -> void:
	hp -= amount
	velocity.x = knockback * 140.0
	modulate = Color(1, 0.3, 0.3)
	var t = create_tween()
	t.tween_property(self, "modulate", Color(1, 1, 1), 0.15)
	if hp <= 0.0:
		queue_free()
