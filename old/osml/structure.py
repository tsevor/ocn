from typing import Any


class Attribute:
	def __init__(self, type, default, other):
		self.type = type
		self.default = default
		self.other = other

class Object:
	def __init__(self):
		self.attributes = {}
	def __add_attribute(self, name, attr: Attribute):
		self.attributes.update(name, attr)

class ObjectInstance:
	def __init__(self):
		self.type


class Scene:
	def __init__(self):
		pass


class Structure:
	def __init__(self):
		self.__scenes = {}
	def __getattribute__(self, __name: str) -> Any:
		if __name in getattr(self, "__scenes").keys():
			return getattr(self, "__scenes").get(__name)
		return getattr(self, __name)
	def __iter__(self):
		return self.__scenes
	def __add_scene(self, name, scene: Scene):
		self.__scenes.update()