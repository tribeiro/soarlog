#----------------------Imports----------------------------#
import sys,os,linecache


#----------------------Classes----------------------------#
class Single:
    def __init__(self,Image=None):
        self.name  = os.path.basename(Image)
        self.path = os.path.dirname(Image)
        self.fname = Image
        self.index,self.rootname,self.fits = self.name.split('.')
        self.format =  '%0'+str(len(self.index))+'d.'+ self.rootname +'.fits'
        self.int_index = int(self.index)
        Single.update(self)

    def add(self):
        self.int_index += 1
        Single.update(self)
    def sub(self):
        self.int_index -= 1
        Single.update(self)

    def update(self):
        self.name = self.format%(self.int_index)
        self.fname = os.path.join(self.path,self.name)
        #IF file previous exist OK, if not self.previous = None
        self.previous = self.format%(self.int_index - 1)
        if not os.path.isfile(os.path.join(self.path,self.previous)):
            self.previous = None

        #IF file previous exist OK, if not self.previous = None
        self.next = self.format%(self.int_index + 1)
        if not os.path.isfile(os.path.join(self.path,self.next)):
            self.next = None

class RSingle:
    def __init__(self,Image=None):
        self.name  = Image
        self.rootname,self.index,self.fits = self.name.split('.')
        self.format =  self.rootname + '.%0'+str(len(self.index)) +'d.fits'
        self.int_index = int(self.index)
        RSingle.update(self)

    def add(self):
        self.int_index += 1
        RSingle.update(self)
    def sub(self):
        self.int_index -= 1
        RSingle.update(self)

    def update(self):
        self.name = self.format%(self.int_index)
        #IF file previous exist OK, if not self.previous = None
        self.previous = self.format%(self.int_index - 1)
        if not os.path.isfile(self.previous):
            self.previous = None

        #IF file previous exist OK, if not self.previous = None
        self.next = self.format%(self.int_index + 1)
        if not os.path.isfile(self.next):
            self.next = None

class List:
    def __init__(self,ListName=None):
        self.filename = ListName
        self.LINE = 1
        List.update2(self)

    def add(self):
        self.LINE += 1
        List.update2(self)

    def sub(self):
        self.LINE -= 1
        List.update2(self)

    def update2(self):
        self.name = linecache.getline\
            (self.filename,self.LINE).replace('\n','')
        self.next = linecache.getline\
            (self.filename,self.LINE + 1).replace('\n','')

        #IF the line is lower than the first line, do previous = None
        if self.LINE -1 > 0:
            self.previous = linecache.getline\
                (self.filename,self.LINE -1).replace('\n','')
        else:
            self.previous = None
             

