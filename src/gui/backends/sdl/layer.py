import copy


class Layer:
    """
    This is a layer implementation for pygame. You can add objects from
    basic.py to it and they will be drawn.
    """
    def __init__(self, name, renderer, alpha=False):
        self.name     = name
        self.renderer = renderer
        self.alpha    = alpha
        if alpha:
            self.screen = self.renderer.screen.convert_alpha()
            self.screen.fill((0,0,0,0))
        else:
            self.screen = self.renderer.screen.convert()

        # some Surface functions from pygame
        self.fill = self.screen.fill
        self.lock = self.screen.lock
        self.lock = self.screen.unlock

        self.update_rect = []
        self.objects     = []
        self.width       = self.renderer.width
        self.height      = self.renderer.height
        

    def __str__(self):
        """
        Debug output for this layer
        """
        return '%s layer [%s]' % (self.name, len(self.objects))

    
    def blit(self, layer, *arg1, **arg2):
        """
        Interface for the objects to blit something on the layer
        """
        try:
            return self.screen.blit(layer.screen, *arg1, **arg2)
        except AttributeError:
            return self.screen.blit(layer, *arg1, **arg2)
            

    def drawroundbox(self, *arg1, **arg2):
        """
        Interface for the objects draw a round box
        """
        arg2['layer'] = self.screen
        return self.renderer.drawroundbox(*arg1, **arg2)


    def in_update(self, x1, y1, x2, y2, update_area, full=False):
        """
        Helper function to check if we need to update or not
        """
        if full:
            for ux1, uy1, ux2, uy2 in update_area:
                # check if x1, y1, x2, y2 are completly inside the rect
                if ux1 <= x1 <= x2 <= ux2 and uy1 <= y1 <= y2 <= uy2:
                    return True
            return False

        for ux1, uy1, ux2, uy2 in update_area:
            # check if x1, y1, x2, y2 is somewere inside the rect
            if not (x2 < ux1 or y2 < uy1 or x1 > ux2 or y1 > uy2):
                return True
        return False


    def add_to_update_rect(self, x1, y1, x2, y2):
        """
        Add (x1,y1,x2,y2) to the list of rectangles we need to update
        """
        if not self.in_update(x1, y1, x2, y2, self.update_rect, True):
            self.update_rect.append((x1, y1, x2, y2))


    def expand_update_rect(self, update_area):
        """
        Add all rectangles in update_area to the list of rectangles we need
        to update
        """
        old_rect = self.update_rect
        self.update_rect = copy.copy(update_area)
        for x1, y1, x2, y2 in old_rect:
            self.add_to_update_rect(x1, y1, x2, y2)
        return self.update_rect

    
    def add(self, object):
        """
        Add an object to this layer
        """
        object.layer = self
        self.objects.append(object)
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)


    def remove(self, object):
        """
        Add an object from this layer
        """
        self.objects.remove(object)
        object.layer = None
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)
        return True


    def clear(self):
        """
        Clear this layer
        """
        self.update_rect = []
        self.objects     = []
        if self.alpha:
            self.screen.fill((0,0,0,0))
        else:
            self.screen.fill((0,0,0))


    def draw(self):
        """
        Draw all objects on this layer
        """
        rect = (self.width, self.height, 0, 0)

        if not self.update_rect:
            return self.update_rect, rect

        for x0, y0, x1, y1 in self.update_rect:
            rect = ( min(x0, rect[0]), min(y0, rect[1]),
                     max(x1, rect[2]), max(y1, rect[3]))
            
        self.objects.sort(lambda  l, o: cmp(l.position, o.position))
        for o in self.objects:
            if self.in_update(o.x1, o.y1, o.x2, o.y2, self.update_rect):
                o.draw(rect)

        ret = self.update_rect
        self.update_rect = []
        return ret, rect
    
        

