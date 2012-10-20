# -*- coding: utf-8 -*-
"""
Created on Thu May 10 10:39:00 2012

@author: tiago
"""

from PyQt4 import QtCore,QtGui,uic,QtSql
import os,sys,re,subprocess
import Queue,threading,logging
import datetime,time

uipath = os.path.dirname(__file__)

################################################################################################
################################################################################################
#
#

class DataTransfer():

    instrList = ['GOODMAN',
                 'OSIRIS',
                 'SOI',
                 'SPARTAN',
                 'SIFS',
                 'SAM']


    instr2path = {'GOODMAN':'/home3/observer/today/',
                  'OSIRIS':'/usr/remote/ic2home/observer/',
                  'SOI':'/usr/remote/ic1home/images/BRAZIL/{yyyy}-{mm}-{dd}/',
                  'SPARTAN':'/home3/observer/SPARTAN_DATA/Brazil/{yyyy}-{mm}-{dd}/',
                  'SIFS':'/home2/images/SIFS/{yyyy}-{mm}-{dd}/',
                  'SAM':'/home2/images/{yyyy}{mm}{dd}/'}

    instr2cpu = {'GOODMAN':'soaric7',
                 'OSIRIS':'soaric7',
                 'SOI':'soaric7',
                 'SPARTAN':'soaric7',
                 'SIFS':'soaric5',
                 'SAM':'soarhrc'}

    ncopy = 0

    total_files = 0

    cmdline = 'rsync -auvz {dryrun} --chmod=g+rw simager@{instrCpu}:{instrPath}*.fits {localPath}'
    currentInstrument = 0
    verboseLine = ''
    STATUS = False
#
#
################################################################################################

################################################################################################
#
#
    def startDataTransfer(self):

        self.dataTransfer_ui = DataTransferUI()

        self.dataTransfer_ui.local_data_path.setText(self.dir)
        if self.total_files == 0:
            self.dataTransfer_ui.label_transfer.setText('NFiles: (waiting)')
        else:
            self.dataTransfer_ui.label_transfer.setText('NFiles: ({0}/{1})'.format(self.ncopy,self.total_files))
            self.dataTransfer_ui.verbose_text.setText(self.verboseLine)

        if self.STATUS:
            self.dataTransfer_ui.select_instrument.setEnabled(False)
            self.dataTransfer_ui.execute_button.setEnabled(False)

        for instr in self.instrList:
            self.dataTransfer_ui.select_instrument.addItem(instr)

        self.connect(self.dataTransfer_ui.select_instrument, QtCore.SIGNAL('currentIndexChanged(int)'), self.readInstrument)
        self.connect(self.dataTransfer_ui.execute_button, QtCore.SIGNAL('clicked()'), self.py_rsync_threaded)
        self.connect(self.dataTransfer_ui.stop_button, QtCore.SIGNAL('clicked()'), self.stopTransfer)
        self.connect(self,QtCore.SIGNAL('stopFileTransfer()'), self.stopTransfer)
        self.connect(self,QtCore.SIGNAL('copiedFiles(int,int)'), self.updateCopiedFiles)
        self.connect(self,QtCore.SIGNAL('copyDone()'), self.copyDone)

        self.dataTransfer_ui.select_instrument.setCurrentIndex(self.currentInstrument)
        self.readInstrument()


        self.dataTransfer_ui.show()
		
        self.dataTransfer_ui.exec_()

        return 0

#
#
################################################################################################

################################################################################################
#
#      self.
    def readInstrument(self):
        try:
            yyyy,mm,dd = self.dir.split('/')[-1].split('-')
            if self.dataTransfer_ui.select_instrument.currentText() == 'SPARTAN':
                obsdate = datetime.date(int(yyyy),int(mm),int(dd)) + datetime.timedelta(days=1)
                yyyy = obsdate.year
                mm = obsdate.month
                dd = obsdate.day
            yyyy = '{0:04d}'.format(int(yyyy)) 
            mm = '{0:02d}'.format(int(mm))
            dd = '{0:02d}'.format(int(dd))
        except:
            logging.debug(sys.exc_info()[1])
            yyyy = 'yyyy'
            mm = 'mm'
            dd = 'dd'
            pass
        self.currentInstrument = self.dataTransfer_ui.select_instrument.currentIndex()
        self.dataTransfer_ui.path_instrument.setText(self.instr2path[str(self.dataTransfer_ui.select_instrument.currentText())].format(yyyy=yyyy,
                                                                                                                                      mm=mm,
                                                                                                                                      dd=dd))
#
#
################################################################################################

################################################################################################
#
#

    def execute(self):
        dtime = self.dataTransfer_ui.loop_delta_time.value()
        ttime = self.dataTransfer_ui.loop_delta_period.value()
        time_start   = datetime.datetime.now()
        time_stop   = time_start + datetime.timedelta(hours=ttime)

        self.STATUS = True

        while self.STATUS:

            #logging.debug('Running rsync...')

            self.py_rsync()

            ctime = datetime.datetime.now()
            
            if ctime > time_stop:
                #logging.debug('Stoping...')
                self.emit(QtCore.SIGNAL('stopFileTransfer()'))
                

            time.sleep(dtime)

#
#
################################################################################################

################################################################################################
#
#


    def py_rsync(self):

        
        cmd = self.cmdline.format(instrCpu=self.instr2cpu[str(self.dataTransfer_ui.select_instrument.currentText())],
                                  instrPath=self.dataTransfer_ui.path_instrument.text(),
                                  localPath=self.dataTransfer_ui.local_data_path.text()+'/',
                                  dryrun = '--stats --dry-run' )

        self.verboseLine = cmd
        self.dataTransfer_ui.verbose_text.setText(cmd)

        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

        remainder = proc.communicate()[0]
        #logging.debug(remainder)
        mn = re.findall(r'Number of files transferred: (\d+)',remainder)
        self.total_files = int(mn[0])

        if self.total_files > 0:

            self.emit(QtCore.SIGNAL('copiedFiles(int,int)'),0,self.total_files)

            cmd = self.cmdline.format(instrCpu=self.instr2cpu[str(self.dataTransfer_ui.select_instrument.currentText())],
                                      instrPath=self.dataTransfer_ui.path_instrument.text(),
                                      localPath=self.dataTransfer_ui.local_data_path.text()+'/',
                                      dryrun = '--progress' )

            proc = subprocess.Popen(cmd,
                                    shell=True,
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        #output = proc.communicate()[0]
        #logging.debug(output)
        #return 0

            while True:

                output = proc.stdout.readline()
                #logging.debug(output)

                if output == '':
                    self.emit(QtCore.SIGNAL('copyDone()'))
                    break
                elif 'to-check' in output:
                    mn = re.findall(r'to-check=(\d+)/(\d+)',output)
                    self.ncopy = self.total_files - int(mn[0][0]) + 1
                    self.emit(QtCore.SIGNAL('copiedFiles(int,int)'),self.ncopy,self.total_files)
                    if mn[0][0] == 0:
                        self.emit(QtCore.SIGNAL('copyDone()'))
                        break
                  
#
#
################################################################################################

################################################################################################
#
#
    def py_rsync_threaded(self):
        self.dataTransfer_ui.select_instrument.setEnabled(False)
        self.dataTransfer_ui.execute_button.setEnabled(False)
        rthread = threading.Thread(target=self.execute)
        rthread.start()
            

#
#
################################################################################################

################################################################################################
#
#

    def updateCopiedFiles(self,nfiles,totfiles):
        self.dataTransfer_ui.label_transfer.setText('NFiles: ({0}/{1})'.format(nfiles,totfiles))
        return 0
#
#
################################################################################################

################################################################################################
#
#

    def copyDone(self):
        self.ncopy = 0
        self.total_files = 0
        self.dataTransfer_ui.label_transfer.setText('NFiles: (waiting)')
        return 0
        
#
#
################################################################################################

################################################################################################
#
#
    def stopTransfer(self):
        #logging.debug('Stoping...')
        self.dataTransfer_ui.select_instrument.setEnabled(True)
        self.dataTransfer_ui.execute_button.setEnabled(True)
        self.STATUS = False
        
#
#
################################################################################################

################################################################################################
#
#

        
#
#
################################################################################################

#
#
################################################################################################
################################################################################################


class DataTransferUI(QtGui.QDialog):
	
################################################################################################
#
#	
	
    def __init__(self):
		
        QtGui.QDialog.__init__(self)
        
        ##########################################################
	#
	#
 
        self.dq_ui = uic.loadUi(os.path.join(uipath,'datatransfer.ui'),self)

        #
        #
        ##########################################################

#
#
################################################################################################
