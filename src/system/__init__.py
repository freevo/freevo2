def detect(*what):
    for module in what:
        exec('import %s' % module)
