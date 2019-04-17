'''
MIT License

Copyright (c) 2019 Enrique Sandoval

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
from configparser import ConfigParser
from os.path import dirname, join

class Config:
	def __init__(self, config_file):
		self.set_config_file(config_file)
		self.update()

	def update(self):
		config = ConfigParser()
		config.read(self.config_file)
		self.token = config["Discord"]["Token"]
		self.stream_URL = config["Discord"]["StreamURL"]
		self.current_event = config["Discord"]["CurrentEvent"]
		self.command_start = config["Discord"]["CommandStart"]
		self.element_emoji = dict(config.items("ElementEmojis"))
		self.weapon_emoji = dict(config.items("WeaponEmojis"))
		self.unit_emoji = dict(config.items("UnitEmojis"))
		self.rarity_emoji = {int(k):v for k,v in config.items("RarityEmojis")}
		self.picture_server = config["Other"]["PictureServer"]
		self.help_text = config["Other"]["HelpText"].format(self.command_start)
		self.adventurer_reactions = ["\U0001F5BC","\U0001F508","\U0001F509","\U0001F50A"]
		self.wyrmprint_reactions = ["\U0001F5BC","\U0001F508","\U0001F509"]
		self.dragon_reactions = ["\U0001F5BC","\U0001F508","\U0001F509"]
		self.authorized_ids = config["Discord"]["AuthorizedIds"].split(',') or []

	def set_config_file(self, config_file):
		project_root = dirname(dirname(__file__))
		self.config_file = join(project_root, config_file)
