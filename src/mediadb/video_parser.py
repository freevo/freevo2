def parse(filename, object, mminfo):
    """
    Parse additional data for video files.
    """
    if object.has_key('type') and object['type'] in ('DVD',):
        del object['url']
        del object['type']
    if mminfo and mminfo.type == 'DVD':
        object['url'] = 'dvd://' + filename
        object['type'] = 'dvd'


def cache(listing):
    """
    Function for the 'cache' helper.
    """
    pass
