#Python Bluetooth deamon. Requires a bluetooth phone, an USB bluetooth dongle or similiar. There is some good guides on how to get your dongle working. 
#A new kernel is good, since the bluetooth subsystem (bluez) is there by default (2.4.21).
#Get yourself a copy of bluez-utils as well. You'll need rfcomm and hciconfig. 
#If you got any questions or want to share an updated version with me, please mail me: lmq137t@tninet.se or ikea@hotbrev.com (Dunno what mail I'll keep) =/


import time, os, re, socket

#This is for my T68 and some buttons on it are more or less non operational and that's why the keys is pretty much fucked up.
#e and s is yes and no. Pressing Yes (s) will pause the movie/music if you answer an incomming call.1

kp2direction = {"u":"VOL+", "d":"VOL-", "e":"PLAY", "s":"PAUSE", "1":"STEP1",
"2":"STEP2", "3":"STEP3", "4":"LEFT", "5":"UP", "6":"RIGHT", "7":"SELECT",
"8":"DOWN", "9":"EXIT", "0":"0", "L":"SELECT", "v":"EXIT", "c":"SLEEP", }

data = ''
c_lock = 0
onestep = 0
twostep = 0
threestep = 0
last_data = ''

def process_KP(event_s):
    print "event_s:", event_s
    if event_s.endswith(",0"): return
    command = kp2direction.get(event_s.split(",")[0], False)

    if command: send_command(command)

def send_command(data):

    global c_lock; global onestep; global twostep; global threestep; global last_data

    #Unlocking the keypad lock on the phone will ignore commands and locking will once again accept commands. (Useful for reading SMS and other stuff)
    #There is ways to sneak around this, by mistake, if you are writing an SMS you better keep your fingers of C -> Yes combinations.   
 
    if data == "PAUSE" and last_data == "SLEEP":
        c_lock = 1
    if data == "PAUSE" and last_data == "SELECT":
        c_lock = 0

    last_data = data
    
    #Using keys 1,2,3 as 1-9. The only way to zoom pictures with my strange key settings. I'm pretty sure this part could be done in better ways.

    if data == "STEP1":
       if onestep == 0: data = "1"; onestep = 1
       elif onestep == 1: data = "2"; onestep = 2
       elif onestep == 2: data = "3"; onestep = 0

    if data == "STEP2":
        if twostep == 0: data = "4"; twostep = 1
        elif twostep == 1: data = "5"; twostep = 2
        elif twostep == 2: data = "6"; twostep = 0

    if data == "STEP3":
       if threestep == 0: data = "7"; threestep = 1
       elif threestep == 1: data = "8"; threestep = 2
       elif threestep == 2: data = "9"; threestep = 0

    #Making sure commands isn't sent if the phone is unlocked.
    if c_lock == 0:
        sockobj.send(data)

#Open socket. Port 35000 is not default. You gotta change either this or look through local_conf.py.
host = 'localhost'
port = 35000
sockobj = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sockobj.connect((host, port))
#Keypad events return in the form "+CKEV: s,1" (or something like that) and this sorts it a bit.
rex = re.compile(r"\+CKEV:\s+(\w+,\w+)")
#Open the bluetooth device. This requires rfcomm (bluez-utils) and the bluetooth subsystem (kernel)
bluefd = os.open("/dev/bluetooth/rfcomm/1", os.O_RDWR)
#Sending the initstring to the phone so it sends all keypad events. For Ericsson T68.
os.write(bluefd, "AT+CMER=3,2,0,0,0\r")
s=""

while 1:
    try:
        s += os.read(bluefd, 1024)
        if rex.search(s): process_KP(rex.search(s).group(1)); s = ""
    except KeyboardInterrupt: break

os.write(bluefd, "AT+CMER=0,0,0,0,0\r")
s=""
while not s.endswith('\n'): s += os.read(bluefd, 1024)
os.close(bluefd)
sockobj.close()

