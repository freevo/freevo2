def parse(filename, object, mminfo):
    """
    Parse additional data for video files.
    """
    if mminfo and mminfo.type == 'DVD':
        object['url']  = 'dvd://' + filename
        object['type'] = 'dvd'


def cache(listing):
    """
    Function for the 'cache' helper.
    """
    pass
