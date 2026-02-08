#!/usr/bin/env python3
# PeakPeek

import os, sys, functools, itertools
import euclid3, UnityPy
from PIL import Image

class Icon:
	@staticmethod
	def _load(name): return Image.open(os.path.join(os.path.dirname(sys.argv[0]), 'icons/', name+'.png')).resize((64, 64))

	antlion = _load('AntLion')
	beehive = _load('beehive')
	capybara = _load('CapybaraOnsen')
	eggs = _load('EggNest')
	luggage_ancient = _load('LuggageAncient')
	luggage_big = _load('LuggageBig')
	luggage_epic = _load('LuggageEpic')
	luggage_small = _load('LuggageSmall')
	luggage_ancient_mirage = _load('MirageLuggageAncient')
	luggage_big_mirage = _load('MirageLuggageBig')
	luggage_epic_mirage = _load('MirageLuggageEpic')
	luggage_small_mirage = _load('MirageLuggageSmall')
	tomb_closed = _load('ClosedTomb')
	tomb_open = _load('OpenTomb')

def _parse(obj):
	if (isinstance(obj, UnityPy.classes.PPtr)): obj = obj.deref()
	if (isinstance(obj, UnityPy.environment.ObjectReader)): return obj.parse_as_object()
	return obj
def parse(f):
	@functools.wraps(f)
	def decorated(*args, **kwargs): return _parse(f(*map(_parse, args), **kwargs))
	return decorated

@parse
def transform(obj): return obj.m_Transform
def position(obj):
	tf = transform(obj)
	loc = tf.m_LocalPosition
	pos = euclid3.Vector3(loc.x, loc.y, loc.z)

	while (tf.m_Father):
		tf = tf.m_Father.deref_parse_as_object()

		scale = tf.m_LocalScale
		pos.x *= scale.x
		pos.y *= scale.y
		pos.z *= scale.z

		rot = tf.m_LocalRotation
		pos = (pos
			.rotate_around(euclid3.Vector3(x=1), rot.x)
			.rotate_around(euclid3.Vector3(y=1), rot.y)
			.rotate_around(euclid3.Vector3(z=1), rot.z)
		)

		loc = tf.m_LocalPosition
		pos.x += loc.x
		pos.y += loc.y
		pos.z += loc.z

	return pos

def parent(obj): return transform(obj).m_Father.deref_parse_as_object().m_GameObject
def children(obj): return (i.deref_parse_as_object().m_GameObject.deref_parse_as_object() for i in transform(obj).m_Children)
def descendants(obj, kind): return filter(lambda x: (x.m_Name.endswith(kind) and x.m_Name != kind), children(obj))
def behaviours(obj): return (mb.parse_monobehaviour_head().m_Script.deref() for i in _parse(obj).m_Components if (mb := i.deref()).type == UnityPy.enums.ClassIDType.MonoBehaviour)
def behavers(obj, name): return filter(lambda x: (x.m_IsActive is True and any(i.peek_name().startswith(name) for i in behaviours(x))), children(obj))

def segments(obj): return descendants(obj, 'Segment')
def campfires(obj): return descendants(obj, 'Campfire')
def variants(obj): return behavers(obj, 'BiomeVariant')
def spawners(obj): return behavers(obj, 'PropSpawner')

def main():
	data = UnityPy.load(*sys.argv[1:])
	for level in filter(lambda x: (x.peek_name() == 'Map'), data.objects):
		biomes = {i.m_Name: next(behavers(i, 'Biome')) for i in children(level) if i.m_Name != 'Global'}
		print("Biomes:")
		for ii, (k, biome) in enumerate(biomes.items(), 1):
			print(f"{ii}. {k.removesuffix('Model')}")
			for seg in segments(biome):
				try: mods = tuple(variants(seg))
				except StopIteration: mods = None
				print('    •', (name := seg.m_Name.removesuffix('Segment').rstrip('_')), *((', '.join(i.m_Name for i in mods).join('()'),) if (mods) else ()))
			#for cf in campfires(biome):
			#	try: mods = tuple(campfires(cf))
			#	except StopIteration: mods = None
			#	print('    •', cf.m_Name.removeprefix(name).lstrip('_'), *((', '.join(i.m_Name.removesuffix('Campfire').rstrip('_') for i in mods).join('()'),) if (mods) else ()))
		print()

		img = Image.new('RGBA', (720, 512*(len(biomes)+1)))

		for biome in biomes.values():
			for seg in itertools.chain(segments(biome), *map(variants, segments(biome))):
				for props in itertools.chain(children(seg), *map(children, children(seg))):
					for spawner in spawners(props):
						for obj in children(spawner):
							pos = position(obj)
							def draw(icon, opacity=None):
								#print(obj.m_Name, pos)
								x, y = round(pos.x)+320, img.size[1]-round(pos.z)-360
								if (opacity is not None): mask = icon.getchannel('A').point(lambda x: int(x*opacity))
								else: mask = icon
								img.paste(icon, (x, y), mask=mask)

							match obj.m_Name:
								case 'AntLion': draw(Icon.antlion)
								case 'Beehive_Spawner': draw(Icon.beehive)  # sic!
								case 'Oasis': draw(Icon.capybara)
								case 'MirageOasis': draw(Icon.capybara, .5)
								case 'EggNest': draw(Icon.eggs)
								case 'LuggageAncient': draw(Icon.luggage_ancient)
								case 'LuggageBig': draw(Icon.luggage_big)
								case 'LuggageEpic': draw(Icon.luggage_epic)
								case 'LuggageSmall': draw(Icon.luggage_small)
								case 'MirageLuggageAncient': draw(Icon.luggage_ancient_mirage, .5)
								case 'MirageLuggageBig': draw(Icon.luggage_big_mirage, .5)
								case 'MirageLuggageEpic': draw(Icon.luggage_epic_mirage, .5)
								case 'MirageLuggageSmall': draw(Icon.luggage_small_mirage, .5)
								#case _: print(obj.m_Name)

					for spawner in behavers(props, 'DesertRockSpawner'):
						for obj in (k for i in children(spawner) if i.m_Name == 'Enterences' for j in children(i) for k in children(j)):  # sic!
							pos = position(obj)
							def draw(icon): img.paste(icon, (round(pos.x)+320, img.size[1]-round(pos.z)-360))

							if (obj.m_Name.endswith('_E')): draw(Icon.tomb_open)
							else: draw(Icon.tomb_closed)

		img.save(sys.argv[1]+'.png')

if (__name__ == '__main__'): exit(main())

# by Sdore, 2026
#  www.sdore.me
