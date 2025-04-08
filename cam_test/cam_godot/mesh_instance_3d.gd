extends MeshInstance3D
@export var speed = 20

func _process(delta: float) -> void:
	rotation.x += delta * speed
	
