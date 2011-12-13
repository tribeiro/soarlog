
from PyQt4 import QtCore,QtGui,uic
import operator

class SOLogTableModel(QtCore.QAbstractTableModel): 

    def __init__(self, datain, headerdata, parent=None, *args,**argv): 
        """ 
			datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata
        self.commitDB = argv['commitDB']
#		self._parent = parent
#		self._children = []

        
			
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent):
        return len(self.headerdata) #len(self.arraydata[0]) 

#    def data(self, index, role): 
#       if not index.isValid(): 
#            return QtCore.QVariant() 
#        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole: 
#            return QtCore.QVariant() 
#        return QtCore.QVariant(self.arraydata[index.row()][index.column()]) 
	
    def data(self, index, role): 
        if not index.isValid(): 
            return QtCore.QVariant() 
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return QtCore.QVariant() 
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])
		
    def isEditable(self, index):
        """ Return true if the index is editable. """
        if self.headerdata[index.column()] == 'OBSNOTES':
	        return True
        else:
	        return False
		
    def flags(self, index):  #function is called to chaeck if itmes are changable etc, index is a PyQt4.QtCore.QModelIndex object
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
		
        ret_flags = QtCore.Qt.ItemIsSelectable | QtCore.QAbstractItemModel.flags(self, index)
        if self.isEditable(index):
#print index.row() #returns the selected elements row
#print index.column()
            ret_flags = ret_flags | QtCore.Qt.ItemIsEditable
        return ret_flags


    def setData(self, index, value, role):
        """ if a item is edited, this command is called value.toString() constains the new value cahnge here to have it evaluate stuff!"""
		
        try:
            self.arraydata[index.row()][index.column()] = QtCore.QVariant(value.toString())
        except AttributeError:
            try:
                self.arraydata[index.row()][index.column()] = value
            except:
                self.arraydata[index.row()][index.column()] = ''
		
        self.dataChanged.emit(index, index)

        if role == QtCore.Qt.EditRole:
			self.commitDB(index)

        return True

    def insertRow(self,index, parent=QtCore.QModelIndex()):
	
        print index, self.rowCount(None)
		
#        self.beginInsertRows(self.createIndex(parent,0),index,index)
        self.beginInsertRows(parent,index,index)

#        print self.arraydata

        self.arraydata.append( ['']*self.columnCount(parent)) #len(self.arraydata[0]) )
        self.endInsertRows()
        return True
				
#        print self.arraydata[0]
#        print self.arraydata[index]
						

		
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()
