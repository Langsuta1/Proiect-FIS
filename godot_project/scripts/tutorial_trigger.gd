extends Area2D
class_name TutorialTrigger
# tutorial_trigger.gd - Floating holographic tutorial billboard with smooth fade

@export var prompt_key: String = "[SHIFT]"
@export var prompt_action: String = "HOLD TO SPRINT"
@export var prompt_subtitle: String = "Accelerate mechanical chassis"

# Aliases for compatibility
@export var tutorial_title: String = "":
	set(val):
		tutorial_title = val
		prompt_key = val
@export var tutorial_desc: String = "":
	set(val):
		tutorial_desc = val
		prompt_action = val
@export var detection_radius: float = 140.0

@onready var panel: Panel = $Panel
@onready var key_label: Label = $Panel/KeyLabel
@onready var action_label: Label = $Panel/ActionLabel
@onready var sub_label: Label = $Panel.get_node_or_null("SubLabel")

func _ready() -> void:
	body_entered.connect(_on_body_entered)
	body_exited.connect(_on_body_exited)
	if panel:
		panel.modulate.a = 0.0
	if key_label:
		key_label.text = prompt_key
	if action_label:
		action_label.text = prompt_action
	if sub_label:
		sub_label.text = prompt_subtitle

func _on_body_entered(body: Node2D) -> void:
	if body is Player or body.is_in_group("player"):
		if panel:
			var t = create_tween()
			t.tween_property(panel, "modulate:a", 1.0, 0.25)

func _on_body_exited(body: Node2D) -> void:
	if body is Player or body.is_in_group("player"):
		if panel:
			var t = create_tween()
			t.tween_property(panel, "modulate:a", 0.0, 0.25)
