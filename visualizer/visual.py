'''
Created on Aug 5, 2016

@author: linesprower
'''

'''
Created on Jul 10, 2016

@author: linesprower
'''

from PyQt4 import QtGui, QtCore
import json, sys, copy, os, re
import io#, time
#import re
import common as cmn

#import fractions

class Stats:
    def __init__(self):
        self.maxlen = 0
        self.maxlen2 = 0
    
    def check(self, s):
        #if len(s) > self.maxlen:
        if False:
            self.maxlen = len(s)
            print('maxlen = %d' % self.maxlen)
        return int(s)
    
    def check2(self, ss):
        s = str(ss)
        if len(s) > self.maxlen2:
            self.maxlen2 = len(s)
            print('maxlen2 = %d' % self.maxlen2)
        
    def parseNum(self, s):
        t = s.split('/')
        if len(t) == 1:
            t.append('1')
        
        t = list(map(self.check, t))
        #g = fractions.gcd(t[0], t[1])
            
        #self.check2(t[0] // g)
        #self.check2(t[1] // g)
        
        return t[0] / t[1]     
        
st = Stats()        

class Poly:
    def __init__(self, pts):
        self.pts = pts
        sum = 0
        for a, b in zip(pts, pts[1:] + [pts[0]]):
            sum += a[0] * b[1] - a[1] * b[0]
        #print(sum)
        self.hole = sum < 0 
        
class Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b

class InfoPanel(QtGui.QDockWidget):

    def __init__(self, owner):

        QtGui.QDockWidget.__init__(self, ' Text')

        self.owner = owner
        self.setObjectName('info_panel') # for state saving

        e = QtGui.QTextEdit()
        e.setFont(QtGui.QFont('Consolas', 10))
        e.setReadOnly(True)
        self.e = e
        self.setWidget(e)

        self.setFeatures(QtGui.QDockWidget.DockWidgetMovable)

    def setData(self, text):
        self.e.setPlainText(text)

class TileWidget(QtGui.QWidget):

    
    def __init__(self, owner):
        self.owner = owner
        self.has_data = False
        QtGui.QWidget.__init__(self)
        
        
    def load(self, fname):
        with io.open(fname) as f:
            
            def getint():
                return int(f.readline())
            
            def getpt(s):
                s = s.split(',')
                return (st.parseNum(s[0]), st.parseNum(s[1]))
            
            def readpoly():
                n = getint()
                return Poly([getpt(f.readline()) for _ in range(n)])
            
            allpts = []
            
            def readedge():
                t = list(map(getpt, f.readline().split()))
                allpts.extend(t)
                return Edge(t[0], t[1])
                
            
            n_polys = getint()
            self.polys = [readpoly() for _ in range(n_polys)]
            self.polys.sort(key=lambda x: x.hole)
            n_edges = getint()
            
            self.edges = [readedge() for _ in range(n_edges)]
            
            self.minx = min([a[0] for a in allpts])
            self.maxx = max([a[0] for a in allpts])
            self.miny = min([a[1] for a in allpts])
            self.maxy = max([a[1] for a in allpts])
            #print(self.minx)
            #print(self.maxx)
            #if self.minx == self.maxx:
            #    self.maxx += 1    
            self.has_data = True
            #print(self.polys[0].pts)                

    
    def mousePressEvent(self, ev):
        '''
        x = ev.x()
        y = ev.y()
        '''
        pass
    
    def transform(self, p):
        x, y = p
        rx = self.x0 + (self.x1 - self.x0) * (x - self.minx) / (self.maxx - self.minx)
        ry = self.y0 + (self.y1 - self.y0) * (y - self.miny) / (self.maxy - self.miny)
        return QtCore.QPointF(rx, ry)

    def paintEvent(self, ev):
        if not self.has_data:
            return
        
        border = 10
        self.x0 = border
        self.x1 = self.width() - border
        self.y0 = border
        self.y1 = self.height() - border
        
        p = QtGui.QPainter(self)        
        # polys
        p.setPen(QtCore.Qt.NoPen)        
        
        for q in self.polys:
            poly = QtGui.QPolygonF([self.transform(t) for t in q.pts])
            p.setBrush(QtGui.QColor('white' if q.hole else "pink"))            
            p.drawPolygon(poly)
            
        # edgges
        p.setPen(QtGui.QColor('black'))
        p.setBrush(QtCore.Qt.NoBrush)
        for e in self.edges:
            p.drawLine(self.transform(e.a), self.transform(e.b))

class MoveViewer(QtGui.QMainWindow):

    def __init__(self, arg):
        QtGui.QMainWindow.__init__(self)
        
        self.resize(800, 600)
        self.setWindowTitle('Origami')

        s = QtCore.QSettings('PlatBox', 'Hal0')
        t = s.value("origami/geometry")
        if t:
            self.restoreGeometry(t)
        t = s.value("origami/dockstate")
        if t:
            self.restoreState(t, 0)

        self.data_edit = QtGui.QComboBox()
        self.data_edit.addItems(['Task %d' % (i+1) for i in range(101)])
        self.data_edit.currentIndexChanged.connect(self.loadFile)
        
        self.info_box = InfoPanel(self)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.info_box)
        
                
        self.mview = TileWidget(self)
        self.loadFile(0)
                
        layout = cmn.VBox([
                           self.data_edit,
                           self.mview
                           ])
                
        self.setCentralWidget(cmn.ensureWidget(layout))
        self.statusBar().showMessage('Ready')
        self.show()
        self.data_edit.setFocus()
        
    def loadFile(self, idx):
        if idx >= 0:
            fname = '../data/problems/%d.in' % (idx+1)
            self.mview.load(fname)
            self.mview.update()
            with io.open(fname) as f:
                self.info_box.setData(f.read())              
            
        
    def closeEvent(self, event):
        s = QtCore.QSettings('PlatBox', 'Hal0')
        s.setValue("origami/geometry", self.saveGeometry())
        s.setValue('origami/dockstate', self.saveState(0))           
            

def main():    
    app = QtGui.QApplication(sys.argv)
    fname = ''
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    _ = MoveViewer(fname)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()