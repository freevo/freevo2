import copy
import pygame

class Layer:
    """
    This is a layer implementation for pygame. You can add objects from
    basic.py to it and they will be drawn.
    """
    def __init__(self, name, parent, alpha=False):
        self.name     = name
        self.parent   = parent
        self.renderer = parent.renderer
        self.update   = parent.update
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

        self.width  = parent.width
        self.height = parent.height
        

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
            

    def __savepixel__(self, x, y, s):
        """
        help functions to save and restore a pixel
        for drawcircle
        """
        try:
            return (x, y, s.get_at((x,y)))
        except:
            return None

            
    def __restorepixel__(self, save, s):
        """
        restore the saved pixel
        """
        if save:
            s.set_at((save[0],save[1]), save[2])


    def __drawcircle__(self, s, color, x, y, radius):
        """
        draws a circle to the surface s and fixes the borders
        pygame.draw.circle has a bug: there are some pixels where
        they don't belong. This function stores the values and
        restores them
        """
        p1 = self.__savepixel__(x-1, y-radius-1, s)
        p2 = self.__savepixel__(x,   y-radius-1, s)
        p3 = self.__savepixel__(x+1, y-radius-1, s)
        p4 = self.__savepixel__(x-1, y+radius, s)
        p5 = self.__savepixel__(x,   y+radius, s)
        p6 = self.__savepixel__(x+1, y+radius, s)

        pygame.draw.circle(s, color, (x, y), radius)
        
        self.__restorepixel__(p1, s)
        self.__restorepixel__(p2, s)
        self.__restorepixel__(p3, s)
        self.__restorepixel__(p4, s)
        self.__restorepixel__(p5, s)
        self.__restorepixel__(p6, s)
        
        
    def drawbox(self, x0, y0, x1, y1, color=None, border_size=0,
                border_color=None, radius=0):
        """
        Draw a round box
        """
        # Make sure the order is top left, bottom right
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)

        w = x1 - x0
        h = y1 - y0

        if self.alpha:
            x = x0
            y = y0
            box = self.screen
        else:
            x = 0
            y = 0
            box = pygame.Surface((w, h)).convert_alpha()
            box.fill((0,0,0,0))
            
        bc = self.renderer._sdlcol(border_color)
        c  = self.renderer._sdlcol(color)

        # make sure the radius fits the box
        radius = min(radius, h / 2, w / 2)
        
        if border_size:
            if radius >= 1:
                self.__drawcircle__(box, bc, x+radius, y+radius, radius)
                self.__drawcircle__(box, bc, x+w-radius, y+radius, radius)
                self.__drawcircle__(box, bc, x+radius, y+h-radius, radius)
                self.__drawcircle__(box, bc, x+w-radius, y+h-radius, radius)
                pygame.draw.rect(box, bc, (x+radius, y, w-2*radius, h))
            pygame.draw.rect(box, bc, (x, y+radius, w, h-2*radius))
        
            x += border_size
            y += border_size
            h -= 2* border_size
            w -= 2* border_size
            radius -= min(0, border_size)
        
        if radius >= 1:
            self.__drawcircle__(box, c, x+radius, y+radius, radius)
            self.__drawcircle__(box, c, x+w-radius, y+radius, radius)
            self.__drawcircle__(box, c, x+radius, y+h-radius, radius)
            self.__drawcircle__(box, c, x+w-radius, y+h-radius, radius)
            pygame.draw.rect(box, c, (x+radius, y, w-2*radius, h))
        pygame.draw.rect(box, c, (x, y+radius, w, h-2*radius))

        if not self.alpha:
            self.screen.blit(box, (x0, y0))


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
        x1 = max(x1, 0)
        y1 = max(y1, 0)
        x2 = min(x2, self.width)
        y2 = min(y2, self.height)
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
        object.screen = self
        self.objects.append(object)
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)


    def remove(self, object):
        """
        Add an object from this layer
        """
        self.objects.remove(object)
        object.screen = None
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)

        # FIXME: bad hack for background layer
        if self.name == 'bg' and not self.objects:
            # cleanup please
            self.screen.fill((0,0,0))
            self.update_rect = [ (0, 0, self.width, self.height) ]
        return True


    def set_position(self, object, x1, y1, x2, y2):
        """
        Move or resize the object. The old and new position will be redrawn
        """
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)
        self.add_to_update_rect(x1, y1, x2, y2)
        
        
    def modified(self, object):
        """
        An object has been modified and needs a redraw
        """
        self.add_to_update_rect(object.x1, object.y1, object.x2, object.y2)

        
    def clear(self):
        """
        Clear this layer
        """
        _debug_('someone called clear')
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

        self.objects.sort(lambda  l, o: cmp(l.layer, o.layer))
        for o in self.objects:
            if self.in_update(o.x1, o.y1, o.x2, o.y2, self.update_rect):
                o.draw(rect)

        ret = self.update_rect
        self.update_rect = []
        return ret, rect
    
        

