
from PyQt4 import QtCore,QtGui,uic,QtSql
import operator
import sys,logging

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

class ComboBoxDelegate(QtGui.QItemDelegate):

	def __init__(self, owner, itemslist):
		QtGui.QItemDelegate.__init__(self, owner)
		self.itemslist = itemslist
		
	def createEditor(self, parent, option, index):
		editor = QtGui.QComboBox( parent )
		_inst = index.model().getData(index.row(),13) # QtCore.Qt.DisplayRole).toString()
		for i in range(len(self.itemslist[_inst])):
			editor.insertItem(i,self.itemslist[_inst][i])
		return editor

	def setEditorData( self, comboBox, index ):
		value = index.model().data(index, QtCore.Qt.DisplayRole).toString()
		_inst = index.model().getData(index.row(),13)
		ii = self.itemslist[_inst].index(value)
		comboBox.setCurrentIndex(ii)

	def setModelData(self, editor, model, index):
		value = editor.currentIndex()
		_inst = index.model().getData(index.row(),13)
		#print value,len(self.itemslist[_inst])
		model.setData( index, self.itemslist[_inst][value],QtCore.Qt.EditRole)

	def updateEditorGeometry( self, editor, option, index ):

		editor.setGeometry(option.rect)



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
        self.EditableColumns = [11,16]
#        self.imageTYPE = ['','OBJECT','FLAT','DFLAT','BIAS','ZERO','DARK','COMP','FAILED','Object']
#        self.setItemDelegateForColumn(11,ComboBoxDelegate(self, self.imageTYPE))
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

	xvalue = value
	if index.row() < 0 or index.column() < 0:
		return False

        try:

	    if type(value) == type(QtCore.QVariant()):
		    self.arraydata[index.row()][index.column()] = value
		    #logging.debug('{0} {1} {2}'.format(index.row(),index.column(),value.toString()))
	    else:
		    self.arraydata[index.row()][index.column()] = QtCore.QVariant(value)
		    xvalue = QtCore.QVariant(value)
        except AttributeError:
            logging.debug('Exception in setData {0}'.format(value))
	    logging.debug(sys.exc_info()[1])
		    
            try:
                self.arraydata[index.row()][index.column()] = value
            except:
                self.arraydata[index.row()][index.column()] = ''
		
        self.dataChanged.emit(index, index)

        if role == QtCore.Qt.EditRole:
		self.commitDB(index)

        return True

    def insertRow(self,index, parent=QtCore.QModelIndex()):
	
#        print index, self.rowCount(None)
		
#        self.beginInsertRows(self.createIndex(parent,0),index,index)
        self.beginInsertRows(parent,index,index)

#        print self.arraydata
        self.arraydata.append( ['']*self.columnCount(parent)) #len(self.arraydata[0]) )
        self.endInsertRows()
        return True
				
#        print self.arraydata[0]
#        print self.arraydata[index]
						
    def removeRows(self,index,count,parent=QtCore.QModelIndex()):

	    self.beginRemoveRows(parent,index,index+count-1)

	    for i in range(index,index+count):
		    self.arraydata.pop(index)

	    self.endRemoveRows()

	    return True
		
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def mimeTypes(self):
        return ['text/xml']
		
    def mimeData(self, indexes):
        mimedata = QtCore.QMimeData()
        #print indexes[0].row(),indexes[0].column()
        mimedata.setData('text/xml', self.arraydata[indexes[0].row()][indexes[0].column()])
        self.dragIndex = indexes[0]
        return mimedata
		
    def dropMimeData(self, data, action, row, column, parent):
        self.beginMoveRows(parent, self.dragIndex.row(),self.dragIndex.row() , parent, parent.row())		
        self.arraydata.insert(parent.row(), self.arraydata.pop(self.dragIndex.row()))
        self.dropParent = parent
        #print 'dropMimeData %s %s %s %s' % (data.data('text/xml'), self.dragIndex.row(), row, parent.row()) 
        self.endMoveRows()
        return True


    def dropEvent(self, event): 
        print 'dropping'
        #self.beginMoveRows(self.dropParent, self.dragIndex.row(),self.dragIndex.row() , self.dropParent, self.dropParent.row())		
#self.endMoveRows()
