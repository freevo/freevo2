# python imports
import os

# kaa imports
import kaa.utils

for widget in kaa.utils.get_plugins(os.path.dirname(__file__)):
    exec('from %s import *' % widget)
