# -*- coding: utf-8 -*-
"""
Created on Thu May 10 10:39:00 2012

@author: tiago
"""

from PyQt4 import QtCore, QtGui, uic, QtSql
import os, sys, re, subprocess
import getpass
import Queue, threading, logging
import datetime,time

uipath = os.path.dirname(__file__)

partsoi = str(getpass.getuser()[5:]).upper()

if getpass.getuser() == 'soar_brazil':
    partspartan = str(getpass.getuser()[5:]).title()
elif getpass.getuser() == 'soar_chile':
    partspartan = str(getpass.getuser()[5:]).title()
else:
    partspartan = str(getpass.getuser()[5:]).upper()


class DataTransfer():

    instrList = [
        'GOODMAN_OLD',
        'GOODMAN_BLUE',
        'GOODMAN_RED',
        # 'OSIRIS',
        'SOI',
        'SPARTAN',
        'SIFS',
        'SAM'
    ]

    instr2path = {
        'GOODMAN_OLD': '/home3/observer/today/',
        'GOODMAN_BLUE': '/home3/observer/today/',
        # 'OSIRIS': '/usr/remote/ic2home/observer/',
        'SOI': '/usr/remote/ic1home/images/' + str(partsoi) + '/%(yyyy)s-%(mm)s-%(dd)s/',
        'SPARTAN': '/home3/observer/SPARTAN_DATA/' + str(partspartan) + '/%(yyyy)s-%(mm)s-%(dd)s/',
        'SIFS': '/home2/images/SIFS/%(yyyy)s-%(mm)s-%(dd)s/',
        'SAM': '/home2/images/%(yyyy)s-%(mm)s-%(dd)s/'
    }

    instr2cpu = {
        'GOODMAN_OLD': 'soaric7',
        'GOODMAN_BLUE': 'soaric7',
        'GOODMAN_RED': 'soaric7',
        # 'OSIRIS': 'soaric7',
        'SOI': 'soaric7',
        'SPARTAN': 'soaric7',
        'SIFS': 'soaric5',
        'SAM': 'soarhrc'
    }

    ncopy = 0

    total_files = 0

    cmdline = 'rsync -auvz %(dryrun)s --chmod=g+rw %(instrPath)s*.fits %(localPath)s'
    currentInstrument = 0
    verboseLine = ''
    STATUS = False

    def __init__(self):
        pass

    def start_data_transfer(self):

        self.dataTransfer_ui = DataTransferUI()
        self.dataTransfer_ui.local_data_path.setText(self.dir)

        if self.total_files == 0:
            self.dataTransfer_ui.label_transfer.setText('NFiles: (waiting)')
        else:
            self.dataTransfer_ui.label_transfer.setText('NFiles: (%i/%i)'%(self.ncopy,self.total_files))
            self.dataTransfer_ui.verbose_text.setText(self.verboseLine)

        if self.STATUS:
            self.dataTransfer_ui.select_instrument.setEnabled(False)
            self.dataTransfer_ui.execute_button.setEnabled(False)

        for instr in self.instrList:
            self.dataTransfer_ui.select_instrument.addItem(instr)

        self.connect(self.dataTransfer_ui.select_instrument, QtCore.SIGNAL('currentIndexChanged(int)'), self.read_instrument)
        self.connect(self.dataTransfer_ui.execute_button, QtCore.SIGNAL('clicked()'), self.py_rsync_threaded)
        self.connect(self.dataTransfer_ui.stop_button, QtCore.SIGNAL('clicked()'), self.stop_transfer)
        self.connect(self, QtCore.SIGNAL('stopFileTransfer()'), self.stop_transfer)
        self.connect(self, QtCore.SIGNAL('copiedFiles(int,int)'), self.update_copied_files)
        self.connect(self, QtCore.SIGNAL('copy_done()'), self.copy_done)

        self.dataTransfer_ui.select_instrument.setCurrentIndex(self.currentInstrument)
        self.read_instrument()
        self.dataTransfer_ui.show()
        self.dataTransfer_ui.exec_()

        return 0

    def read_instrument(self):

        try:
            yyyy, mm, dd = self.dir.split('/')[-1].split('-')
            if self.dataTransfer_ui.select_instrument.currentText() == 'SPARTAN':
                obsdate = datetime.date(int(yyyy),int(mm),int(dd)) + datetime.timedelta(days=1)
                yyyy = obsdate.year
                mm = obsdate.month
                dd = obsdate.day
            yyyy = '%04d'%(int(yyyy)) 
            mm =   '%02d'%(int(mm))
            dd =   '%02d'%(int(dd))

        except:
            logging.exception(sys.exc_info()[1])
            yyyy = 'yyyy'
            mm = 'mm'
            dd = 'dd'
            pass
        self.currentInstrument = self.dataTransfer_ui.select_instrument.currentIndex()

        self.dataTransfer_ui.path_instrument.setText(
            self.instr2path[str(
                self.dataTransfer_ui.select_instrument.currentText())]%{'yyyy':yyyy, 'mm':mm, 'dd':dd})

    def execute(self):
        dtime = self.dataTransfer_ui.loop_delta_time.value()
        ttime = self.dataTransfer_ui.loop_delta_period.value()
        time_start   = datetime.datetime.now()
        time_stop   = time_start + datetime.timedelta(hours=ttime)

        self.STATUS = True

        while self.STATUS:

            self.py_rsync()

            ctime = datetime.datetime.now()
            if ctime > time_stop:
                self.emit(QtCore.SIGNAL('stopFileTransfer()'))

            time.sleep(dtime)

    def py_rsync(self):

        cmd = self.cmdline%{
            'instrCpu':self.instr2cpu[str(self.dataTransfer_ui.select_instrument.currentText())],
            'instrPath':self.dataTransfer_ui.path_instrument.text(),
            'localPath':self.dataTransfer_ui.local_data_path.text()+'/',
            'dryrun': '--stats --dry-run' }

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
        self.total_files = 0
        if len(mn) > 0:
            self.total_files = int(mn[0])
        
        self._dtproc = None

        if self.total_files > 0:

            self.emit(QtCore.SIGNAL('copiedFiles(int,int)'),0,self.total_files)

            cmd = self.cmdline%{'instrCpu':self.instr2cpu[str(self.dataTransfer_ui.select_instrument.currentText())],
                                'instrPath':self.dataTransfer_ui.path_instrument.text(),
                                'localPath':self.dataTransfer_ui.local_data_path.text()+'/',
                                'dryrun': '--progress' }

            logging.debug('Starting copy')
            self._dtproc = subprocess.Popen(cmd,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
                                            stderr=subprocess.PIPE)

            self._dtproc.wait()
            logging.debug('Copy done')
            self.emit(QtCore.SIGNAL('copy_done()'))

    def py_rsync_threaded(self):
        #self.wdd = wm.add_watch(str(self.dataTransfer_ui.path_instrument.text()),mask,rec=True)
        self.dataTransfer_ui.select_instrument.setEnabled(False)
        self.dataTransfer_ui.execute_button.setEnabled(False)
        rthread = threading.Thread(target=self.execute)
        rthread.start()

    def update_copied_files(self, nfiles, totfiles):
        self.dataTransfer_ui.label_transfer.setText('NFiles: (%i/%i)'%(nfiles,totfiles))
        return 0

    def copy_done(self):
        self.ncopy = 0
        self.total_files = 0
        self.dataTransfer_ui.label_transfer.setText('NFiles: (waiting)')
        return 0

    def stop_transfer(self):

        logging.debug('Stoping...')

        if self._dtproc:
            self._dtproc.terminate()

        self.dataTransfer_ui.select_instrument.setEnabled(True)
        self.dataTransfer_ui.execute_button.setEnabled(True)
        self.STATUS = False


class DataTransferUI(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.dq_ui = uic.loadUi(os.path.join(uipath,'datatransfer.ui'),self)
