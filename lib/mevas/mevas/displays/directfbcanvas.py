import mevas
import mevas.rect as rect

from directfb import *

#import directfb
#print dir(directfb)

from bitmapcanvas import *

# DSPF_A8 0x00118005
# DSPF_ALUT44 0x4011420c
# DSPF_ARGB 0x00418c04
# DSPF_ARGB1555 0x00211780
# DSPF_I420 0x08100609
# DSPF_LUT8 0x4011040b
# DSPF_RGB16 0x00200801
# DSPF_RGB24 0x00300c02
# DSPF_RGB32 0x00400c03
# DSPF_RGB332 0x00100407
# DSPF_UNKNOWN 0x00000000
# DSPF_UYVY 0x00200808
# DSPF_YUY2 0x00200806
# DSPF_YV12 0x0810060a


class DirectFBCanvas(BitmapCanvas):

	def __init__(self, size, layerno):
		super(DirectFBCanvas, self).__init__(size, preserve_alpha = False, blit_once = True)
		width, height = size
		self.layerno = layerno
		print 'DEBUG: size is %sx%s' % (width, height)

		self.dfb = DirectFB()
		caps = self.dfb.getCardCapabilities()
		self.layer = self.dfb.getDisplayLayer(self.layerno)
		self.layer.setCooperativeLevel(DLSCL_ADMINISTRATIVE)
		self.layer.setConfiguration(pixelformat = DSPF_ARGB, buffermode = DLBM_BACKSYSTEM)

		print 'DirectFB layer config:'
		layer_config = self.layer.getConfiguration()
		for k, v in layer_config.items():
			print '  %s:  %s' % (k, v)

		print '  goemetry: %dx%d' % (layer_config.get('width'), layer_config.get('height'))
		print '  pixelformat: %x' % layer_config.get('pixelformat')

		self.layer.enableCursor(0)

		self.osd = self.layer.createWindow(caps=DWCAPS_ALPHACHANNEL, 
                                           width=width, 
                                           height=height)
		self._surface = self.osd.getSurface()
		self.osd.setOpacity(0xFF)

		self._rect    = []


	def _blit(self, img, r):
		pos, size = r

		self._rect = rect.optimize_for_rendering(self._rect)
		#data = self._backing_store._image.get_bytes()
		data = img.get_raw_data("BGRA")
		#data = img.get_raw_data("RGBA")
		#data = img.get_raw_data("YV12A")
		#data = img.get_raw_data("ARGB")

		self._surface.overlay(DSPF_ARGB, str(data))
		self._surface.flip()
		return

# vim: ts=4
