def addtools(modulename,reporterror=False):
    try:
        if '.' in modulename:
            a = modulename.split('.')
            t = __import__('.'.join(a[:-1]),fromlist=[a[-1]])
            tempmodulename = getattr(t,a[-1])
        else:
            tempmodulename = __import__(modulename)
        allloadmodules.append(tempmodulename)
        if hasattr(tempmodulename,'doc'):
            doc = tempmodulename.doc
        else:
            doc = ''
    except ImportError,e:
        if 'No module named' in str(e):
            if reporterror:
                logging.warning('fail to import %s',str(e))
            return
        else:
            raise
    runtools(tempmodulename)
