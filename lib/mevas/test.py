from src import *
t0=time.time()
c = CanvasContainer()
img = c.draw_image("/tmp/background.png", alpha = 256)
print img.width * img.height * 4
print len(img.image.get_bytes())
#img.draw_image("/data/movies/Leon/cover.jpg", dst_pos=(150, 150), src_pos = (50, 50), src_size = (300, 300), alpha=128)
#img.draw_image("/data/movies/Leon/cover.jpg", dst_pos=(50, 50), alpha=128)
#c.draw_ellipse( (80, 80), (150, 150), color = (255, 0, 255), fill = True, alpha = 80)
#print time.time()-t0
#c.to_image().save("/home/tack/zot.png")
