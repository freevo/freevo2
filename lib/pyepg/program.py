class Program:
    """
    A tv program item for the tv guide and other parts of the tv submenu.
    """
    def __init__(self, id, title, start, stop, episode, subtitle,
                 description, channel):
        self.title = title
        self.name  = self.title
        self.start = start
        self.stop  = stop

        self.channel     = channel
        self.id          = id
        self.subtitle    = subtitle
        self.description = description
        self.episode     = episode
        
        # FIXME: remove that information
        self.scheduled = False

        # TODO: add category support (from epgdb)
        self.categories = ''
        # TODO: add ratings support (from epgdb)
        self.ratings = ''


