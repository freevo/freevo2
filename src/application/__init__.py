from base import Application
from menuapp import MenuApplication
from childapp import Application as ChildApp
from eventhandler import add_window, remove_window, get_active, \
     app_change_signal

# signals defined by the application base code
signals = { 'application change': app_change_signal }
