from PyQt4 import QtCore,QtGui
import logging


class MyLineEdit(QtGui.QLineEdit):

    def __init__(self, *args):
        QtGui.QLineEdit.__init__(self, *args)
        
    def event(self, event):

        if (event.type()==QtCore.QEvent.KeyPress) and (event.key()==QtCore.Qt.Key_Escape):
            self.emit(QtCore.SIGNAL("escapePressed()"))
            return True

        if (event.type()==QtCore.QEvent.KeyPress) and (event.modifiers() == QtCore.Qt.ControlModifier) and (event.key() == QtCore.Qt.Key_F):
            self.emit(QtCore.SIGNAL("searchPressed()"))
            return True

        #logging.debug('--> aqui {0}'.format(event.key()))
        return QtGui.QLineEdit.event(self, event)
