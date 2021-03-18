import pyqtgraph as pg
from PyQt5.QtWidgets import QPushButton, QApplication, QWidget, QVBoxLayout, QGroupBox, QLineEdit, QTableWidget, QTableWidgetItem
class customViewBox(pg.ViewBox):
    def __init__(self, parent = None):
        self.myParent = parent
        pg.ViewBox.__init__(self)
    def wheelEvent(self, ev, axis = None):
        if ev.delta() < 0:
            self.myParent.lowerScanCallback()
        else:
            self.myParent.raiseScanCallback()
        #return pg.ViewBox.wheelEvent(self, ev, axis) ### add to restore original behavior

class customImageView(pg.ImageView):
    def __init__(self, parent = None):
        my_view = customViewBox(parent)
        pg.ImageView.__init__(self, view=my_view)
        #self.view = pg.ViewBox()
    #def wheelEvent(self, ev, axis = None):
    #    print(ev.angleDelta())
    #    return None
    #    #return pg.ImageView.autoLevels
    #    #QApplication.sendEvent(mainWindow,ev.angleDelta())
