from layer import Layer


class Screen:
    """
    The screen implementation for pygame
    """
    def __init__(self, renderer):
        self.renderer = renderer
        self.layer    = {}
        self.layer['content'] = Layer('content', self.renderer)
        self.layer['alpha']   = Layer('alpha', self.renderer, True)
        self.layer['bg']      = Layer('bg', self.renderer)
        self.layer['widget']  = Layer('widget', self.renderer, True)
        self.complete_bg      = self.renderer.screen.convert()

        self.width  = self.renderer.width
        self.height = self.renderer.height
        

    def clear(self):
        """
        Clear the complete screen
        """
        _debug_('someone called clear')
        self.layer['bg'].add_to_update_rect(0, 0, 800, 600)


    def add(self, layer, object):
        """
        Add object to a specific layer. Right now, this screen has
        only three layers: bg, alpha and content
        """
        return self.layer[layer].add(object)
    
            
    def remove(self, layer, object):
        """
        Remove an object from the screen
        """
        if layer == None:
            return self.special_layer.remove(object)
        return self.layer[layer].remove(object)



    def update(self):
        """
        Show the screen using pygame
        """
        if self.renderer.must_lock:
            # only lock s_alpha layer, because only there
            # are pixel operations (round rectangle)
            self.layer['alpha'].lock()

        bg    = self.layer['bg']
        alpha = self.layer['alpha']

        update_area = bg.draw()[0]

        update_area = alpha.expand_update_rect(update_area)

        if update_area:
            alpha.screen.fill((0,0,0,0))
            alpha.draw()

        # and than blit only the changed parts of the screen
        for x0, y0, x1, y1 in update_area:
            self.complete_bg.blit(bg.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))
            self.complete_bg.blit(alpha.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))

        content = self.layer['content']

        update_area = content.expand_update_rect(update_area)

        for x0, y0, x1, y1 in update_area:
            content.blit(self.complete_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))

        rect = content.draw()[1]


        widget = self.layer['widget']
        update_area = widget.expand_update_rect(update_area)

        for x0, y0, x1, y1 in update_area:
            widget.blit(self.complete_bg, (x0, y0), (x0, y0, x1-x0, y1-y0))

        rect = widget.draw()[1]

        for x0, y0, x1, y1 in update_area:
            self.renderer.screenblit(content.screen, (x0, y0), (x0, y0, x1-x0, y1-y0))

        if self.renderer.must_lock:
            self.s_alpha.unlock()

        if update_area:
            self.renderer.update([rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]])
