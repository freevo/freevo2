import mailbox
import osd
import time

osd  = osd.get_singleton()

class IdleTool:
    
    def __init__(self):
        self.idlecount = -1
        self.clock_surface = osd.getsurface(525, 25, 225, 50)
        self.mail_surface  = osd.getsurface(25,25,225,50)
        self.MAILBOX='/var/mail/aubin'
        self.CLOCKFONT='skins/fonts/Trebuchet_MS.ttf'
        self.NO_MAILIMAGE='skins/images/status/newmail_dimmed.png'
        self.MAILIMAGE='skins/images/status/newmail_active.png'
        self.interval = 300

    def checkmail(self):
        mb = mailbox.UnixMailbox (file(self.MAILBOX,'r'))
        msg = mb.next()
        count = 0
        while msg is not None:
            count = count + 1
            msg = mb.next()
        return count

    def drawclock(self):
        clock = time.strftime('%a %I:%M %P')
        osd.putsurface(self.clock_surface,525,25)
        osd.drawstring(clock,580,40,fgcolor=0xffffff,font=self.CLOCKFONT,ptsize=12)

    def drawmail(self):
        osd.putsurface(self.mail_surface,25,25)
        if self.checkmail() > 0:
            osd.drawbitmap(self.MAILIMAGE,25,25)
        else:
            osd.drawbitmap(self.NO_MAILIMAGE,25,25) 

    def poll(self):
        if (self.idlecount%self.interval) == 0:
            self.drawclock()
            self.drawmail()
            osd.update()
        self.idlecount = self.idlecount + 1
