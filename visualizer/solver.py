'''
Created on Aug 6, 2016

@author: linesprower
'''
import os, re, io, json, subprocess, datetime, traceback
from facets import Poly, Edge, transp, parseNum, splitEdges, make_nagib, saveSol,\
    saveFacets
import facets
import icfp_api
from nagibator import denagibate

def soldirname(idx):
    if idx < 0:
        return '../data/nagibated'
    return '../data/solutions'
    
def probdirname(idx):
    if idx < 0:
        return '../data/nagibated'
    return '../data/problems'

def checkResponse(respfile):
    with io.open(soldirname(1) + '/' + respfile) as f:
        j = json.loads(f.read())
        if ('resemblance' in j) and j['resemblance'] == 1:
            return True
        return False
            

def checkOk(idx):
    try:        
        test = re.compile(r'solution_%d_.*response' % idx)
        fnames = [f for f in os.listdir(soldirname(1)) if re.match(test, f)]
        for fname in fnames:
            if checkResponse(fname):
                return True            
        return False
    except:
        return False
    
    
def getAllSolved():
    test = re.compile(r'solution_(\d+)_(.*)\.out\.response')
    fnames = [f for f in os.listdir(soldirname(1)) if re.match(test, f)]
    res = {}
    for fn in fnames:
        m = re.match(test, fn)
        num = int(m.group(1))
        solver = m.group(2)
        if checkResponse(fn):
            res[num] = solver    
    return res

#kVersion = '_defiler_1'
kBorderVersion = 1
kBorderSubversion = 1


def ensureInd(idx, force=False):
    fname = probdirname(idx) + '/%d.ind' % abs(idx)
    if os.path.exists(fname) and not force:
        return
    infname = probdirname(idx) + '/%d.in' % abs(idx)
    with io.open(infname) as f:
            
        def getint():
            return int(f.readline())
        
        def getpt(s):
            s = s.split(',')                
            return (parseNum(s[0]), parseNum(s[1]))
        
        allpts = set()
        
        def readpoly():
            n = getint()
            t = [getpt(f.readline()) for _ in range(n)]
            #allpts.update(t)
            return Poly(t)        
        
        def readedge():
            t = list(map(getpt, f.readline().split()))
            allpts.update(t)
            return Edge(t[0], t[1])
                
            
        n_polys = getint()
        _polys = [readpoly() for _ in range(n_polys)]
        n_edges = getint()
            
        edges = [readedge() for _ in range(n_edges)]
        allpts = sorted(list(allpts))            
        p0 = allpts[0]
        
                
    with io.open(fname, 'wt') as f:
        f.write('%d\n' % len(allpts))
        for p in allpts:
            t = transp(p, p0)
            f.write('%.15f %.15f\n' % (t[0], t[1]))
            
        xedges = splitEdges(allpts, edges)
        
        f.write('%d\n' % len(xedges))
        for e in xedges:
            u, v = allpts.index(e.a), allpts.index(e.b)            
            f.write('%d %d\n' % (u, v))


def runBorder(idx):
    metafname = probdirname(idx) + '/%d.pm%d' % (abs(idx), kBorderVersion)
    pfname = probdirname(idx) + '/%d.p%d' % (abs(idx), kBorderVersion)
    dfname = probdirname(idx) + '/%d.ind' % abs(idx)
    if os.path.exists(pfname):
        return True
    if os.path.exists(metafname):
        print('Found %s' % metafname)
        return False
    args = ['../bordersearcher/bordersearcher', '-in', dfname, '-out', pfname, '-t', '5']
    print(' '.join(args))
    try:
        code = subprocess.call(args, timeout=22)
    except subprocess.TimeoutExpired:
        code = -66
    #out = subprocess.check_output(args)
    #code = 0
    if code == 0:
        if not os.path.exists(pfname):
            code = -42
    else:
        if os.path.exists(pfname):
            os.remove(pfname)
    
    logEvent(idx, 'BorderSearcher returned %d' % code)
    with io.open(metafname, 'wt') as meta:
        data = {'code' : code, 'subver' : kBorderSubversion} 
        meta.write(json.dumps(data))
    return code == 0    
    

def logEvent(task, s):
    with io.open('solver.log', 'a') as f:
        ss = '%s: Task %d: %s' % (str(datetime.datetime.now().time()), task, s)
        print(ss)
        f.write(ss + '\n')        
        
def logSolved(task):
    with io.open('solved.log', 'a') as f:
        ss = '%s: Task %d solved!' % (str(datetime.datetime.now().time()), task)
        print(ss)
        f.write(ss + '\n')

def do_send(idx):
    resp = icfp_api.send_solution_logged(idx, facets.getSolName(idx))
    logEvent(idx, 'Response: %s' % resp)
    if checkOk(idx):
        logSolved(idx)


def hasBeenTried(idx):
    metafname = probdirname(-1) + '/%d.pm%d' % (idx, kBorderVersion)
    pfname = probdirname(-1) + '/%d.p%d' % (idx, kBorderVersion)
    #metafname = probdirname(1) + '/%d.pm%d' % (idx, kBorderVersion)
    #pfname = probdirname(1) + '/%d.p%d' % (idx, kBorderVersion)    
    if os.path.exists(metafname) or os.path.exists(pfname):
        return True
    return False

def trySolve(idx, send):
    if idx > 0 and checkOk(idx):
        print('%d is already solved' % idx)
        return True
    
    if idx > 0:
        respfile = facets.getSolName(idx) + '.response'
        if os.path.exists(respfile):
            print('found response file %s. Skip' % respfile)
            return True
    
    ensureInd(idx)
    if not runBorder(idx):
        return False
    try:
        if facets.test(idx, kBorderVersion):
            solname = facets.getSolName(idx)
            print(solname)
            if os.path.exists(solname):
                if send:
                    do_send(idx)
                else:
                    print('Not sending')                
            else:
                logEvent(idx, 'returned True, but no solution file')
                return False
            
    except facets.ESolverFailure as sf:
        logEvent(idx, sf.msg)
        return False
    except Exception:
        logEvent(idx, traceback.format_exc())
        return False
    return True

def problemExists(idx):
    infname = probdirname(1) + '/%d.in' % idx    
    return os.path.exists(infname)

def trySolveIfExists(idx, send=False):    
    if not problemExists(idx):
        print('%d does not exist' % idx)
        return False
    return trySolve(idx, send)

def cleanupBS(idx):
    metafname = probdirname(idx) + '/%d.pm%d' % (abs(idx), kBorderVersion)
    pfname = probdirname(idx) + '/%d.p%d' % (abs(idx), kBorderVersion)
    if os.path.exists(metafname):
        os.remove(metafname)
    if os.path.exists(pfname):
        os.remove(pfname)

'''
def isFailedInd(idx):
    if not problemExists(idx):
        return False
    ind_name = probdirname + '/%d.ind' % idx
    if not os.path.exists(ind_name):
        cleanupBS(idx)
        return True
    return False   
    '''     
'''        
def updateInd():
    #for idx in range(589, 590):
    for idx in range(3417, 6000):
        if isFailedInd(idx):
            print(" ========== %d ========= " % idx)
            trySolve(idx, True)
            '''
            
def isBSCode(idx, code):
    metafname = probdirname + '/%d.pm%d' % (idx, kBorderVersion)
    if not os.path.exists(metafname):
        return False
    with io.open(metafname) as f:
        data = json.loads(f.read())
    return data['code'] == code

def killBSMeta(idx):
    metafname = probdirname(idx) + '/%d.pm%d' % (abs(idx), kBorderVersion)
    if os.path.exists(metafname):
        os.remove(metafname)    


def update():
    for idx in range(1511, 7000):
    #for idx in range(1, 101):
        #print(idx)
        #print(hasBeenTried(idx))
        #print(checkOk(idx))
        if problemExists(idx) and not hasBeenTried(idx) and not checkOk(idx):
            print(" ========== %d ========= " % idx)
            #trySolve(idx, True)
            trySolveNagib(idx, True)
    print('Done!')
                

def isNotOkResponse(respfile):
    with io.open(soldirname(1) + '/' + respfile) as f:
        j = json.loads(f.read())
        return j['ok'] == False

def findOkFalse():
    test = re.compile(r'solution_(\d+)_oxyethylene_1\.out\.response')
    fnames = [f for f in os.listdir(soldirname(1)) if re.match(test, f)]    
    res = []
    for fn in fnames:
        m = re.match(test, fn)
        num = int(m.group(1))
        if isNotOkResponse(fn):
            res.append(num)
    print(len(res))
    return res

def trySolveNagib(n, send=False):
    
    def extractedges(facets):
        es = []
        for f in facets:
            for a, b in zip(f, f[1:] + f[:1]):
                es.append((a, b))
        return es
    
    ensureInd(n)
    if make_nagib(n):
        if trySolve(-n, False):
            
            t = denagibate(n)
            if t:
                saveSol(n, t[0], t[1], t[2])                
                saveFacets(t[0], extractedges(t[2]), 'facets.json')                
                print('Solution written')
                if send:                
                    solname = facets.getSolName(n)
                    print(solname)
                    if os.path.exists(solname):
                        do_send(n)

def main():
    #trySolveNagib(1510, True)        
    #return
    #cleanupBS(25)
    #ensureInd(25, True)
    #trySolveIfExists(25)
    #runBorder(3293)
    #return
    #trySolveIfExists(187, True)
    #return
    #ids = [i for i in range(5000) if isBSCode(i, 3)]
    #for idx in ids:
    #    killBSMeta(idx)
    #return
    
    #print(len(ids))
    #return
    #print(getAllSolved())
    #print(findOkFalse())
    
    update()
    #updateInd()
    return
    
    #for idx in range(788, 1500):
    #for idx in range(102, 500):
    for idx in range(1500, 3600):
        print(" ========== %d ========= " % idx)
        trySolveIfExists(idx, True)

if __name__ == '__main__':
    main()
    
    
