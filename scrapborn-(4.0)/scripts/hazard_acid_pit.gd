extends Area2D
# hazard_acid_pit.gd - Detects player falling into toxic green chasm

func _ready() -> void:
	body_entered.connect(_on_body_entered)

func _on_body_entered(body: Node2D) -> void:
	if body.is_in_group("player"):
		if body.has_method("die_in_hazard"):
			body.die_in_hazard("toxic_acid")
		elif body.has_method("_die"):
			body._die()
