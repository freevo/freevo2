import traceback
import __builtin__
import config

try:
    # this should crash when not running with Freevo
    # XXX check if util is freevo.util
    import util # load util for String() and Unicode()

    if config.DEBUG:
        print 'compat.py: freevo detected, auto configure'
    for i in config.__all__ + [ 'encoding', 'LOCALE' ]:
        setattr(config, i, getattr(util.config, i))
    if util.config.DEBUG > config.DEBUG:
        config.DEBUG = util.config.DEBUG
        
except:
    if config.DEBUG:
        print "compat.py: starting compat lib"

    def _debug_(s, level=1):
        if config.DEBUG < level:
            return
        # add the current trace to the string
        where =  traceback.extract_stack(limit = 2)[0]
        if isinstance(s, unicode):
            s = s.encode(config.encoding, 'replace')
        s = '%s (%s): %s' % (where[0][where[0].rfind('/')+1:], where[1], s)
        # print debug message
        print s

            
    def Unicode(string, encoding=config.encoding):
        if string.__class__ == str:
            try:
                return unicode(string, encoding)
            except Exception, e:
                try:
                    return unicode(string, config.LOCALE)
                except Exception, e:
                    print 'Error: Could not convert %s to unicode' % repr(string)
                    print 'tried encoding %s and %s' % (encoding, config.LOCALE)
                    print e
        elif string.__class__ != unicode:
            return unicode(str(string), config.LOCALE)
        
        return string


    def String(string, encoding=config.encoding):
        if string.__class__ == unicode:
            return string.encode(encoding, 'replace')
        if string.__class__ != str:
            try:
                return str(string)
            except:
                return unicode(string).encode(encoding, 'replace')
        return string


    __builtin__.__dict__['Unicode'] = Unicode
    __builtin__.__dict__['String']  = String
    __builtin__.__dict__['_debug_'] = _debug_


try:
    foo = _('test string')
except:
    __builtin__.__dict__['_']= lambda m: m
