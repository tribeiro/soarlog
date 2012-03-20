#!/usr/bin/env python
##!/usr/bin/env python2.6
# Author				version		Up-date			Description
#------------------------------------------------------------------------
# T. Ribeiro (SOAR)		0.0			09 Jun 2011     Creation

'''

soarlog - Provide GUI-based automatic log production/database for in-site
observations. This program is intended to aid the exection of the brazilian
queue on SOAR, as well as to aid data quality and data sharing procedures.

Ribeiro, T., June 2011.

'''

from soarlogF_qt4_mt import *

MasterQueue = Queue.Queue()

if __name__ == "__main__":

	
	root = QtGui.QApplication(sys.argv)
	
	usergui = SoarLog(MasterQueue)
	
	usergui.initGUI()
		
	usergui.initWatch()

	usergui.show()
	
	sys.exit(root.exec_())