import os 
import plugin

# VUX - Vacillating Utilitarian eXtemporizer
# vux.py - a trivial vux plugin for freevo
#
# coded by P.W.deBruin@its.tudelft.nl
#
# Debian packages a simple tool called vux that can
# randomly play a set of files. Based on how a file is
# skipped the 'score' of that file is adapted. My freevo box is
# Debian based, so adding vux is as simple as:
# apt-get install vux
#
# have all the playlist and scorelist stuff done (see man vux)
#
# plonk this file in src/audio/plugins and
# add a line to local_conf.py containing
# plugin.activate('audio.vux')
#
# TODO
# 1) use mplayer to play ogg/mp3
# 2) display which song is playing
# 3) playlist control and what have you
# 4) ...
#
# Usage: 
# after adding the plugin any of of the items (dir/mp3/ogg) in the music
# menu should have a number of [VUX] entries. 

class PluginInterface(plugin.ItemPlugin):

	def __init__(self):

		plugin.ItemPlugin.__init__(self)

		# create actions and corresponding functions
		self.commands = [('default', _('[VUX] Start playing'),           'vuxctl start'),
		                 ('default', _('[VUX] Stop playing'),            'vuxctl stop'),
				 ('default', _('[VUX] Next (rating down)'),      'vuxctl down next'),
				 ('default', _('[VUX] Next (rating intact)'),    'vuxctl next'),
				 ('default', _('[VUX] Next (rating up)'),        'vuxctl up next'),
				 ('default', _('[VUX] Playing item rating up'),  'vuxctl up'),
				 ('default', _('[VUX] Playing item rating down'),'vuxctl down'),
				 ('dir',     _('[VUX] a dir item do not select'), None),
				 ('audio',   _('[VUX] an audio item, do not select'), None) ]


	def actions(self, item): 
		items = []
		for action_type in ['default', item.type]:
			items.extend(([(eval('lambda arg=None, menuw=None: os.system("%s")' % x[2]) , x[1]) for x in self.commands if x[0] == action_type]))

		return items
