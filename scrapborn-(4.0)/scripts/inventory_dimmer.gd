extends Control
# inventory_dimmer.gd - Handles dropping an item outside inventory slots to drop it into the world!

func _can_drop_data(_at_position: Vector2, data: Variant) -> bool:
	return data is Dictionary and data.has("source_type")

func _drop_data(_at_position: Vector2, data: Variant) -> void:
	var item = GameManager.get_slot_item(data["source_type"], data["source_idx"])
	if not item.is_empty():
		GameManager.clear_slot_item(data["source_type"], data["source_idx"])
		var player = get_tree().get_first_node_in_group("player")
		var drop_pos = player.global_position if player else Vector2(200, 750)
		var facing = player.facing_direction if player else 1
		GameManager.drop_item_in_world(item, drop_pos, facing)
