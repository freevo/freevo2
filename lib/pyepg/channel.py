from program import Program



class Channel:
    """
    Information about one specific channel, also containing
    epg informations.
    """
    def __init__(self, id, display_name, access_id, epg):
        self.id   = id
        self.access_id = access_id
        self.programs  = []
        self.logo      = ''
        self.epg       = epg
        # XXX Change this to config.TV_CHANNEL_DISPLAY_FORMAT or something as
        # XXX many people won't want to see the access_id.
        # XXX What should we use, name or title, or both?
        self.name = self.title = display_name


    def sort_programs(self):
        f = lambda a, b: cmp(a.start, b.start)
        self.programs.sort(f)


    def __get_dummy_programs(self, start, stop):
        """
        Return some default Program with intervals no longer than a
        set default.
        """
        default_prog_interval = 30 * 60
        dummies = []
        d_start = start
        d_stop  = 0

        sec_after_last = start % default_prog_interval
        sec_until_next = default_prog_interval - sec_after_last

        while(d_stop < stop):
            d_stop = d_start + sec_until_next
            if d_stop > stop:
                d_stop = stop

            dummies.append(Program(-1, u'NO DATA', d_start, d_stop,
                                   '', '', '', self))

            sec_until_next = default_prog_interval
            d_start = d_stop

        return dummies


    def __import_programs(self, start, stop=-1, progs=[]):
        """
        Get programs from the database to create Program from then
        add them to our local list.  If there are gaps between the programs
        we will add dummy programs to fill it (TODO).
        """
        new_progs = []
        dummy_progs = []

        if not progs:
            progs = self.epg.get_programs(self.id, start, stop)
        for p in progs:
            i = Program(p.id, p.title, p.start, p.stop, p.episode, p.subtitle,
                        p['description'], channel=self)
            new_progs.append(i)

            # TODO: add information about program being recorded which
            #       comes from another DB table - same with categories,
            #       ratings and advisories.

        l = len(new_progs)
        if not l:
            dummy_progs = self.__get_dummy_programs(start, stop)
        else:
            for p in new_progs:
                i = new_progs.index(p)
                if i == 0:
                    # fill gaps before
                    if p.start > start:
                        n = self.__get_dummy_programs(start, p.start)
                        dummy_progs += n

                if i < l-1:
                    # fill gaps between programs
                    next_p = new_progs[i+1]
                    if p.stop < next_p.start:
                        n = self.__get_dummy_programs(p.stop, next_p.start)
                        dummy_progs += n

                elif i == l-1:
                    # fill gaps at the end
                    if p.stop < stop:
                        n = self.__get_dummy_programs(p.stop, stop)
                        dummy_progs += n

        for i in new_progs + dummy_progs:
            if not i in self.programs:
                self.programs.append(i)

        self.sort_programs()


    def get(self, start, stop=0):
        """
        get programs between start and stop time or if stop=0, get
        the program running at 'start'
        """
        # get programs
        if self.programs:
            # see if we're missing programs before start
            p = self.programs[0]
            if p.start > start - 60:
                self.__import_programs(start - 60, p.start)
            # see if we're missing programs after end
            p = self.programs[-1]
            if stop == -1:
                self.__import_programs(p.stop, stop)
            elif stop == 0 and p.stop < start + 60:
                self.__import_programs(p.stop, start + 60)
            elif p.stop < stop:
                self.__import_programs(p.stop, stop + 60)
        else:
            if stop == 0:
                self.__import_programs(start - 60, start + 60)
            else:
                self.__import_programs(start, stop)

        # return the needed programs
        if stop == 0:
            # only get what's running at time start
            return filter(lambda x: x.start <= start, self.programs)[-1]
        elif stop == -1:
            # get everything from time start onwards
            return filter(lambda x: x.stop > start, self.programs)

        elif stop > 0:
            # get everything from time start to time stop
            return filter(lambda x: (x.start <= start and x.stop > start) or \
                          (x.start > start and x.stop < stop) or \
                          (x.start < stop and x.stop >= stop),
                          self.programs)
        raise Exception('bad request: %s-%s' % (start, stop))



    def get_relative(self, pos, prog):
        new_pos = self.programs.index(prog) + pos
        if new_pos < 0:
            # requested program before start
            self.__import_programs(prog.start-3*3600, prog.start)
            return self.get_relative(pos, prog)
        if new_pos >= len(self.programs):
            # requested program after end
            last = self.programs[-1]
            self.__import_programs(last.stop, last.stop+3*3600)
            return self.get_relative(pos, prog)
        return self.programs[new_pos]
    


