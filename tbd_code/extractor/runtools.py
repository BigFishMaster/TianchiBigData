import sys
import os

import logging
def setuplogger(logfile=None,LOG_LEVEL = logging.DEBUG):
    if not logfile: #isfrozen():
        logging.basicConfig(level=LOG_LEVEL,
                format="%(levelname)s:%(name)s:%(funcName)s->%(message)s",  #logging.BASIC_FORMAT,
                datefmt='%a, %d %b %Y %H:%M:%S')
    if logfile:
        LOG_FILE = logfile+'.'+str(os.getpid())+'.log'
        _logdformat = '%(asctime)s %(name)-12s: %(levelname)-8s %(message)s'
        formatter = logging.Formatter(_logdformat)
        fileLog = logging.handlers.RotatingFileHandler(
                  LOG_FILE, maxBytes=50000000, backupCount=20)
        fileLog.setLevel(LOG_LEVEL)
        fileLog.setFormatter(formatter)
        # add the handler to the root logger
        mylogger = logging.getLogger('')
        mylogger.addHandler(fileLog)
        mylogger.setLevel(LOG_LEVEL)

def runtools(modulename):
    if isinstance(modulename,str):
        modulename =sys.modules[modulename]
    if not hasattr(modulename ,sys.argv[1]):
        return
    function = getattr(modulename,sys.argv[1])
    if hasattr(function,'__call__'):
        argcount =function.func_code.co_argcount
        argnames = function.func_code.co_varnames[:argcount]
        sysargs = sys.argv[2:]
        namedargs = [a for a in sysargs if a.startswith('--')]
        defaults = function.func_defaults if function.func_defaults is not None else []
        defaultargnames = argnames[-len(defaults):]
        defaultvaluemap = dict(zip(defaultargnames,defaults))
        try:
            if len(namedargs) > 0:
                import optparse
                parser = optparse.OptionParser(usage='runtools.py %s args'%sys.argv[1])
                for i,argname in enumerate(argnames):
                     parser.add_option("--"+argname, dest=argname, default=defaultvaluemap.get(argname))
                options, args = parser.parse_args()
                notfoundoptions = [argname for i,argname in enumerate(argnames) if options.__dict__.get(argname) is None and argname not in defaultvaluemap]
                if notfoundoptions:
                    print >> sys.stderr,'named args value not found',notfoundoptions
                    sys.exit(0)
                function(**options.__dict__)
            else:
                function(*sys.argv[2:])
        except TypeError,e:
            if sys.argv[1] in str(e):
                argnames = function.func_code.co_varnames[:function.func_code.co_argcount]
                print >> sys.stdout,function.__name__, '(', ','.join([ '%s=%r'%(a,defaultvaluemap[a]) if a in defaultvaluemap else a for a in function.func_code.co_varnames[:function.func_code.co_argcount]]),')'
            else:
                raise
    sys.exit(0)


allloadmodules = []
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

def printhelp(command):
    global allloadmodules
    allcmds = []
    for m in allloadmodules:
        callablefuncnames = [(m,a) for a,b in m.__dict__.items() if hasattr(b,'__call__') and not a.startswith('_') ]
        allcmds.extend(callablefuncnames)
    findcmd = [c for c in allcmds if c[1] ==command ]
    if not findcmd: #find again
        findcmd = [c for c in allcmds if command in c[1]]
    if findcmd:
        if len(findcmd)==1:
            try:
                import IPython
                from IPython.terminal.embed import InteractiveShellEmbed
                shell = InteractiveShellEmbed(user_module=findcmd[0][0])
                #shell.mainloop()
                magic=IPython.core.magics.namespace.NamespaceMagics(shell)
                magic.pinfo2(findcmd[0][1])
            except:
                help(getattr(findcmd[0][0],findcmd[0][1]))
        else:
            print >>sys.stderr, '\n'.join([c[1] for c in findcmd])
    else:
        print >>sys.stderr,'not found'
    sys.exit(0)
def testpack():

    import mcpack
    mcpack.set_default_buffer_size(10000000)
    key,data = readkv(open('a.txt','rb'))

    a = mcpack.loads(data)
    print a

usage= """"""
def main():
    setuplogger(None)
    if len(sys.argv)==1:
        print >>sys.stderr, 'usage: runtools.py command arg1 arg2 ...'
        return
    addtools('evaltools')
    addtools('featureextract')
    if len(sys.argv) == 3 and sys.argv[1]=='help':
        printhelp(sys.argv[2])
    elif len(sys.argv)>1:
        print 'wrong arguments:',sys.argv
        sys.exit(-1)

if __name__=='__main__':
    main()

