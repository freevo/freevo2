import plugin
import config
import rc
import os
import re


from event import *

#
# Name 			blue
# 
# Description		Remote control Freevo (http://freevo.sf.net) with your cellphone over bluetooth
# 
# Author		Erik "ikea" Pettersson (ikea at hotbrev dot com)
#



#Todo: All try-except blocks MUST give more details! (printing the error message too)
#Todo: Lock Mode should not listen for keys, it should look for an AT lock event instead. Might cause more traffic.
#Todo: Logical names and better structure

#Should this one be here?
rc = rc.get_singleton()

class PluginInterface(plugin.DaemonPlugin):
    """
    Control Freevo with your cellphone
    
    Use any phone with bluetooth and event reporting as a remote! So what is event reporting?
    It is a function that most cellphones with bluetooth have, what it does is that it sends information about
    what buttons you press. I used this to make a little plugin that receives and interprets the keypresses
    and converts them to regular Freevo events, making it possible to control Freevo with your cellphone.
    All buttons can be configured, diffrent ways to press "1", "2" and "3" exists and not to forget Lock Mode,
    which makes this deamon only send events to Freevo when you got your keypad locked.


    
    I think that the installation instrctions was too big to be placed here.
    You may find them in "Docs/plugins/bluetooth.txt" or at "http://asm.meeep.net/ikea/blue/"
    
    """




    def __init__(self):

	plugin.DaemonPlugin.__init__(self)
	
	self.default_config()
	
	self.read_conf()
	
        self.poll_interval = self.BLUE_SLEEP

        self.init_sock()
        
	self.rex = re.compile(r"\+CKEV:\s+(\w+,\w+)")
	
	self.key_lock = 1
	self.data = "i"
	self.last_data = "i"
	self.s = "i"

	self.onestep = 0
	self.twostep = 0
	self.threestep = 0
	self.stepping_plus = 0
	self.stepping_minus = 0

    def process_KP(self, event_s):
        # Uncomment this is you want to see what it's doing.
	#print "event_s:", event_s

	# Don't grab key-release thingys.
	if event_s.endswith(",0"): return

	self.command = self.kp2direction.get(event_s.split(",")[0], False)

	if self.command: self.send_command(self.command);




    def send_command(self, data):
        
	# Keypad locking mode, this is a bit tricky and that's why it looks like crap :)
	# It checks if a combination of two keys have been pressed, and returns if no command gonna be sent.
	if self.BLUE_KP_LOCK == 1:
	    
	    if self.key_lock == 1:
	        if data == "UNLOCK2" or data == "UNILOCK":
		    if self.last_data == "UNLOCK1" or self.last_data == "UNILOCK":
		        self.key_lock = 0
			self.last_data = data
			return
		
		
	    if self.key_lock == 0:
	        if data == "LOCK2" or data == "UNILOCK":
		    if self.last_data == "LOCK1" or self.last_data == "UNILOCK":
	                self.key_lock = 1
		    else: self.last_data = data; return
	   	else: self.last_data = data; return 
	    
	    # Must set self.last_data before translation

	    self.last_data = data
	    
            # Translate keypad locking keys
	    if data == "UNILOCK": data = self.BLUE_UNILOCK
	    if data == "LOCK1":   data = self.BLUE_LOCK1
	    if data == "LOCK2":   data = self.BLUE_LOCK2
	    if data == "UNLOCK1": data = self.BLUE_UNLOCK1
	    if data == "UNLOCK2": data = self.BLUE_UNLOCK2
	    
	# Two diffrent ways to zoom images. One simple and one more complex.	
	if self.BLUE_SIMPLE_ZOOM == 1:
            
	    # The simple way
	    if data == "STEPPING_PLUS":
	        self.stepping += 1
                data = self.stepping
            
	    if data == "STEPPING_MINUS":
                self.stepping -= 1
	        data = self.stepping

	else:
            
	    # The complex way	
            if data == "STEP1":
	    
                if   self.onestep == 0: data = "1"; self.onestep = 1
                elif self.onestep == 1: data = "2"; self.onestep = 2
                elif self.onestep == 2: data = "3"; self.onestep = 0
	    
	    if data == "STEP2":
	    
                if   self.twostep == 0: data = "4"; self.twostep = 1
                elif self.twostep == 1: data = "5"; self.twostep = 2
	        elif self.twostep == 2: data = "6"; self.twostep = 0
            
	    if data == "STEP3":
	    
	        if   self.threestep == 0: data = "7"; self.threestep = 1
	        elif self.threestep == 1: data = "8"; self.threestep = 2
	        elif self.threestep == 2: data = "9"; self.threestep = 3
		elif self.threestep == 3: data = "0"; self.threestep = 0				  
	
	#Making sure commands isn't sent if the phone is unlocked.
	if self.key_lock == 1 and data != '':
	    print 'data to send: ', data
	    data = rc.key_event_mapper(data)
	    #rc.post_event(Event(BUTTON, data))
	    rc.post_event(data)
	    #rc.post_event('SELECT')
   
   
    def default_config(self):
        
	#Default config that should work, but not be satisfactory, for most people.
	self.BLUE_RFCOMM = "/dev/bluetooth/rfcomm/1"
	self.KEEP_ALIVE = 0
	self.BLUE_SLEEP = 1
	self.KP_LOCK = 0
	self.BLUE_SIMPLE_ZOOM = 1
	
	#Ericsson T68 defaults	
	self.kp2direction = {"u":"VOL+", "d":"VOL-", "e":"PLAY", "s":"UNILOCK", "1":"STEP1",
	"2":"STEP2", "3":"STEP3", "4":"LEFT", "5":"UP", "6":"RIGHT", "7":"SELECT",
        "8":"DOWN", "9":"EXIT", "0":"0", "L":"LOCK1", "v":"EXIT", "c":"UNLOCK1", }


	

    def read_conf(self):

	#rfcomm device path
	if config.BLUE_RFCOMM != '':
	    self.BLUE_RFCOMM = config.BLUE_RFCOMM

   	#Keepalive
	if config.BLUE_KEEP_ALIVE != '':
	    self.KEEP_ALIVE = config.BLUE_KEEP_ALIVE

	#Poll value. (How much should I sleep in the main loop?)
	if config.BLUE_SLEEP != '':
	    self.BLUE_SLEEP = config.BLUE_SLEEP

	#Buttonconfig (experimental)
	if config.BLUE_CMDS != '':
	    self.kp2direction = config.BLUE_CMDS
	else:
	    print 'blue: Warning (Could not read BLUE_CMDS from config! Using SE T68 default settings)'
	
	# Keypad locking mode
	#TODO: Think about this for a while...
	if config.BLUE_KP_LOCK !='':
	    self.BLUE_KP_LOCK = 1
	    
	    #Translation
	    self.BLUE_UNILOCK = config.BLUE_UNILOCK
	    self.BLUE_LOCK1 = config.BLUE_LOCK1
	    self.BLUE_LOCK2 = config.BLUE_LOCK1
	    self.BLUE_UNLOCK1 = config.BLUE_UNLOCK1
	    self.BLUE_UNLOCK2 = config.BLUE_UNLOCK2

	else:
	    print 'blue: Warning (Not using keypad locking mode! Your phone might do stuff when you remote controll)'

	if config.BLUE_SIMPLE_ZOOM != '':
	    self.BLUE_SIMPLE_ZOOM = config.BLUE_SIMPLE_ZOOM
	



    def init_sock(self):

	print 'blue: opening ', self.BLUE_RFCOMM
	
	try:
	    self.bluefd = os.open(self.BLUE_RFCOMM, os.O_RDWR)
	except OSError:
	    print 'blue: CRITICAL ERROR (Could not open device "', self.BLUE_RFCOMM, '", check permissions and path)'
	    self.shutdown()
	
	try:
	    if self.bluefd:
	        os.write(self.bluefd, "AT+CMER=3,2,0,0,0\r")
	except OSError: 
	    print 'blue: CRITICAL ERROR (Could not write to device! Check permissions and connection)'
	    self.shutdown()




    def poll(self):
	#Mainloop stuff.        
	self.s += os.read(self.bluefd, 1024)
	if self.rex.search(self.s):
	    self.process_KP(self.rex.search(self.s).group(1))
	    self.s = ""

	if self.KEEP_ALIVE >= 1:
	    self.KEEP_ALIVE += 1

	    if self.KEEP_ALIVE >= self.KEEP_ALIVE:
	        try:
		    os.write(self.bluefd, "ATI")
		except OSError: 
		    print 'blue: CRITICAL ERROR (Could not write to device! Check permissions and connection)'
		    shutdown(self)
		    
		self.keep_alive = 0




    def shutdown(self):
        	
	try:
	    os.write(self.bluefd, "AT+CMER=0,0,0,0\r")
	    
	except OSError:
	    print 'blue: An error has occured during shutdown.'
	    print 'Cannot write to rfcomm device, please check the config and that the connection is working.'
	
	try:
	    os.close(self.bluefd)
	except OSError:
	    print 'blue: An error has occured during shutdown.'
	    print 'Cannot close (as in "not read from it") rfcomm device.'
	
	print 'blue: Exiting'
	
	
	
