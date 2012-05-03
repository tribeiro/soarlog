
from PyQt4 import QtCore,QtGui,uic,QtSql
import operator

class myQSqlTableModel(QtSql.QSqlTableModel):

	def __init__(self,parent,db):
		QtSql.QSqlTableModel.__init__(self,parent,db)
		self.EditableColumns = [17]
		#self.oldflags = self.flags
		
	def flags(self,index):
		
		if not index.isValid():
			return QtCore.Qt.ItemIsEnabled

		ret_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 

		if index.column() in self.EditableColumns:
			return ret_flags | QtCore.Qt.ItemIsEditable

		return ret_flags
	
	def changeEditableColumns(self,edlist):
		if type(edlist) == type(self.EditableColumns):
			self.EditableColumns = edlist

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
	self.EditableColumns = [16]
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
    def getData(self, i,j):
        return self.arraydata[i][j]

    def data(self, index, role): 
        if not index.isValid(): 
            return QtCore.QVariant() 
        elif role != QtCore.Qt.DisplayRole and role != QtCore.Qt.EditRole:
            return QtCore.QVariant() 
        return QtCore.QVariant(self.arraydata[index.row()][index.column()])
		
    def isEditable(self, index):
        """ Return true if the index is editable. """
	if index.column() in self.EditableColumns:
		return True
	else:
		return False
	
#        if self.headerdata[index.column()] == 'OBSNOTES':
#	        return True
#        else:
#	        return False

		
    def flagsOLD(self,index):
		
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        ret_flags = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable 

        if index.column() in self.EditableColumns:
            return ret_flags | QtCore.Qt.ItemIsEditable

        return ret_flags

    def changeEditableColumns(self,edlist):
        if type(edlist) == type(self.EditableColumns):
            self.EditableColumns = edlist

    def flags(self, index):  #function is called to chaeck if itmes are changable etc, index is a PyQt4.QtCore.QModelIndex object
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled
		
        ret_flags = QtCore.Qt.ItemIsDropEnabled |QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsSelectable | QtCore.QAbstractItemModel.flags(self, index)
        if self.isEditable(index):
#print index.row() #returns the selected elements row
#print index.column()
            ret_flags = ret_flags | QtCore.Qt.ItemIsEditable
        return ret_flags

	def supportedDropActions(self):
		return QtCore.Qt.MoveAction
		
				
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

    def mimeTypes(self):
        return ['text/xml']
		
    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        print indexes[0].row(),indexes[0].column()
        mimedata.setData('text/xml', self.arraydata[indexes[0].row()][indexes[0].column()])
        self.dragIndex = indexes[0]
        return mimedata
		
    def dropMimeData(self, data, action, row, column, parent):
        self.beginMoveRows(parent, self.dragIndex.row(),self.dragIndex.row() , parent, parent.row())		
        self.arraydata.insert(parent.row(), self.arraydata.pop(self.dragIndex.row()))
        self.dropParent = parent
        print 'dropMimeData %s %s %s %s' % (data.data('text/xml'), self.dragIndex.row(), row, parent.row()) 
        self.endMoveRows()
        return True


    def dropEvent(self, event): 
        print 'dropping'
        #self.beginMoveRows(self.dropParent, self.dragIndex.row(),self.dragIndex.row() , self.dropParent, self.dropParent.row())		
#self.endMoveRows()
