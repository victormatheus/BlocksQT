#!/usr/bin/python

from PyQt4 import QtGui, QtCore
from dock import Dock

class BlockModel(object):
    def __init__(self,imagefile="",x=0,y=0):
        self.x = x
        self.y = y
        self.imagefile = imagefile
        
    def code(self):
        raise NotImplementedError
        
def pixmap_select(imgfile):
    img = QtGui.QImage(imgfile)
    img.invertPixels()
    return QtGui.QPixmap.fromImage(img)

class BlockView(QtGui.QGraphicsItemGroup):
    
    __model__ = BlockModel
    __image__ = "motor.png"

    def __init__(self):
        QtGui.QGraphicsItemGroup.__init__(self)
        
        self.docks = []
        
        self.setFlags(QtGui.QGraphicsItem.ItemIsFocusable)
                
        self.startpos = self.scenePos()
        self._selected = False

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, v):
        if v:
            self.pixitem.setPixmap(self.pixmap_y)
        else:
            self.pixitem.setPixmap(self.pixmap_n)

        self._selected = v

    #overload this method
    def setModel(self, model):
        self.model  = model
        self.pixmap_y = pixmap_select(model.imagefile)
        self.pixmap_n = QtGui.QPixmap(model.imagefile)
        self.pixitem = QtGui.QGraphicsPixmapItem(self.pixmap_n)
        self.addToGroup( self.pixitem )
        self.setPos( QtCore.QPointF(model.x, model.y) )
        
    #overload this method
    def updateModel(self):
        model = self.model
        self.pixitem.setPixmap( QtGui.QPixmap(model.imagefile) )
        self.setPos( QtCore.QPointF(model.x, model.y) )
        
    #overload this method
    def dialog(self):
        return None
    
    #overload this method
    def erase(self):
        for d in self.docks:
            d.disconnect()
    
    def addDock(self, dock):
        self.addToGroup( dock )
        self.docks.append(dock)
    
    def getChildren(self):
        l = []
        l.append(self)
        for i in self.docks:
            if i.flow == Dock.flow.TO_CHILD and i.destiny:
                l.extend( i.destiny.block.getChildren() )
        return l
        
    def itemChange(self, change, value):
        if change == QtGui.QGraphicsItem.ItemPositionChange:
            self.model.x = value.toPointF().x()
            self.model.y = value.toPointF().y()
        elif change == QtGui.QGraphicsItem.ItemSelectedChange:
            self.model.selected = value.toBool()
        return QtGui.QGraphicsItem.itemChange(self, change, value)
        

## custom widgets ##

class BlockTextItem(QtGui.QGraphicsSimpleTextItem):
    def __init__(self, block=None, centralized=False):
        QtGui.QGraphicsSimpleTextItem.__init__(self)
        self.block = block
        self.centralized = centralized

    def setText(self, t):
        QtGui.QGraphicsSimpleTextItem.setText(self, t)

        if self.centralized:
            lw,lh = self.boundingRect().width(), \
                self.boundingRect().height()

            w,h = self.block.boundingRect().width(), \
                self.block.boundingRect().height()

            self.setPos(w/2-lw/2, h/2-lh/2)
        
## custom blocks ##
                        
class MotorBlockModel(BlockModel):
    
    __number_motors__ = 4
    
    def __init__(self):
        BlockModel.__init__(self)
        self.imagefile = "motor.png"
        self.motors = [True,]*self.__number_motors__
        
    def code(self):
        return [self.dock_parent, self.dock_child]

class MotorBlockView(BlockView):
    
    __model__ = MotorBlockModel
    __image__ = "brake.png"
    
    def __init__(self):
        BlockView.__init__(self)
        
        self.dock_parent = Dock(self, QtCore.QRectF(20, -10, 30, 20),
        Dock.type.NORMAL, Dock.format.FEM, Dock.flow.TO_PARENT )
        self.addDock(self.dock_parent)
        
        self.dock_child  = Dock(self, QtCore.QRectF(20, 29, 30, 20),
        Dock.type.NORMAL, Dock.format.MASC, Dock.flow.TO_CHILD )
        self.addDock(self.dock_child)
        
        self.label = BlockTextItem(self, True)
        self.addToGroup( self.label )
        self.label.setZValue(1)
        
    def setModel(self, model):
        BlockView.setModel(self, model)
        self.updateLabel()

    def updateModel(self):
        BlockView.updateModel(self)
        self.updateLabel()
        
    def updateLabel(self):
        s = ""
        for i,k in enumerate(self.model.motors):
            if k: s += chr(ord('a')+i)
        self.label.setText(s)

    def dialog(self):
        d = QtGui.QDialog()
        buttonBox = \
            QtGui.QDialogButtonBox(\
            QtGui.QDialogButtonBox.Ok | \
                QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(d.accept)
        buttonBox.rejected.connect(d.reject)
        
        chkbox = [QtGui.QCheckBox(chr(ord('A')+i))\
                      for i in\
                      range(self.model.__number_motors__)]
        [c.setChecked(self.model.motors[i]) for i,c in enumerate(chkbox)]
        mainLayout = QtGui.QVBoxLayout()
        
        def update(i):
            self.model.motors = \
                map(lambda k: k.isChecked(), chkbox)
            
        for i in chkbox:
            i.stateChanged.connect(update)
            mainLayout.addWidget(i)
        
        mainLayout.addWidget(buttonBox)
        d.setLayout(mainLayout)
        return d
