from base import BaseAnimation

class Move(BaseAnimation):
    def __init__(self, objects, orientation, pixel_per_move, max_pixel):
        BaseAnimation.__init__(self, 25)

        self.objects        = objects
        self.pixel_per_move = pixel_per_move
        self.max_pixel      = max_pixel
        self.orientation    = orientation
        

    def draw(self):
        if self.pixel_per_move < self.max_pixel:
            self.max_pixel -= self.pixel_per_move
        else:
            self.pixel_per_move = self.max_pixel
            self.max_pixel = 0
            self.remove()

        if self.orientation == 'vertical':
            for o in self.objects:
                o.set_position(o.x1, o.y1 - self.pixel_per_move,
                               o.x2, o.y2 - self.pixel_per_move)
        else:
            for o in self.objects:
                o.set_position(o.x1 - self.pixel_per_move, o.y1,
                               o.x2 - self.pixel_per_move, o.y2)
            
