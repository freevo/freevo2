import time, os, fcntl, struct, math
import mevas

from bitmapcanvas import *

IVTVFB_IOCTL_SET_STATE = 1074282498
IVTVFB_IOCTL_PREP_FRAME = 1074544643
FBIOGET_FSCREENINFO = 17922

class IvtvCanvas(BitmapCanvas):

	def __init__(self, size, fb_device = "/dev/fb0"):
		super(IvtvCanvas, self).__init__(size, preserve_alpha = True)
		self._fb_device = fb_device

		self._fd = os.open(fb_device, os.O_RDWR)
		r = fcntl.ioctl(self._fd, FBIOGET_FSCREENINFO, " " * 68)
		r = struct.unpack("16sLLLLLHHHLLLLHHHH", r)
		self._fb_size, self._fb_stride = r[2], r[9]

		self._fb_height = self._fb_size / self._fb_stride
		self._fb_width = self._fb_stride / 4
		self._set_ivtv_alpha(255)

	def __del__(self):
		self.clear()
		# We can't call update() because self.canvas weakref is dead.
		self.child_paint(self)

	def _set_ivtv_alpha(self, alpha):
		r = struct.pack("LL", 13L, alpha)
		r = fcntl.ioctl(self._fd, IVTVFB_IOCTL_SET_STATE, r)


	def _blit_regions(self, img, regions):
		regions = rect.clip_list(regions, ((0, 0), self.get_size()) )
		if len(regions) == 0:
			return

		scale_x = self._fb_width / float(img.width)
		scale_y = self._fb_height / float(img.height)
		t0=time.time()
		if self.alpha < 255:
			self._backing_store_with_alpha.clear( (0, 0), img.size )
			self._backing_store_with_alpha.blend(img, alpha = self.alpha)
			img = self._backing_store_with_alpha

		# Make a union of all the regions.
		src_region = regions.pop()
		while regions:
			src_region = rect.union(src_region, regions.pop())

		# Grow it a bit to account for lost precision when scaling
		# FIXME: This is weird, but when we blit an image whose height is
		# less than 60 or so, things go all screwy.
		offset_h = 5
		if src_region[1][1] < 70/scale_y:
			offset_h = int(70/scale_y)
		src_region = rect.offset(src_region, (-2, -2), (5, offset_h) )
			
		# Clip it to the backing store.
		src_region = rect.clip(src_region, ((0, 0), self.get_size()) )
		# Translate the canvas region to the framebuffer region.
		dst_region = rect.translate(src_region, scale = (scale_x, scale_y), scale_pos = True)
		print "Src", src_region, "Dst", dst_region, img.width
		# Scale the slice to the necessary aspect.
		#img = img.scale( (self._fb_width, dst_region[1][1]), 
		#                 (0, src_region[0][1]), 
		#                 (img.width, src_region[1][1]) )
		# DEBUG stuff...
		img = img.crop( (0, img.height-self._fb_height), (self._fb_width, self._fb_height) )
		#img.save("/home/tack/foo.png")
		#img = img.scale ( (self._fb_width, self._fb_height) )


		# Now blit.
		data = img.get_raw_data("BGRA")
		address = data.get_buffer_address()
		if not address:
			print "FATAL: can't access raw image data for blitting"
			return

		start = dst_region[0][1] * self._fb_stride
		#size = 44 * self._fb_stride
		#size = dst_region[1][1] * self._fb_stride
		args = struct.pack("PLi", address, 0, len(data))
		#args = struct.pack("PLi", address, start, size)
		r = fcntl.ioctl(self._fd, IVTVFB_IOCTL_PREP_FRAME, args)
		print "Blit took", time.time()-t0, regions
		

# vim: ts=4
