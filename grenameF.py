import sys,os

try:
    from pyraf import iraf as i
    import pyfits
    PYRAF = True
except:
    print "ERROR: Did not find Pyraf"
    sys.exit(1)


def Rename(im,FLAG_END=False):    
     #FLAG_END = False
     BIN1X1 = '1 1'
     BIN2X2 = '2 2'
     BIN3X3 = '3 3'
     BIN4X4 = '4 4'
     while True:
        
        oldname = im.name.split('.')
        newname = os.path.join(im.path,oldname[1] + '.' + oldname[0] + '.' + oldname[2])
        acqnewname = os.path.join(im.path,oldname[1] + 'acq.' + oldname[0] + '.' + oldname[2])
#        acqnewname = oldname[1] + '.' + oldname[0] + '.' + oldname[2]
        if os.path.isfile(newname):
            print "Goodname already exist!"
            pass
        else:
            if os.path.isfile(im.fname):
	            if PYRAF:
	                fimg    = pyfits.open(im.fname,ignore_missing_end=True)
	                imhdr = fimg[0].header
	                CCDSUM = imhdr['CCDSUM']
	                IMTITLE = imhdr['OBJECT']
	                if 'acq' in IMTITLE:
	                    newname = acqnewname
	                    i.imcopy(im.fname+'[*,*,1]',newname)
	                elif 'HgAr' in IMTITLE:
	                    i.imcopy(im.fname+'[*,*,1]',newname)
	                    i.hedit(newname,fields='OBSTYPE',value='COMP', update='yes',addonly='no',delete='no',verify='no')
	
	                elif 'Quartz' in IMTITLE:
	                    i.imcopy(im.fname+'[*,*,1]',newname)
	                    i.hedit(newname,fields='OBSTYPE',value='FLAT', update='yes',addonly='no',delete='no',verify='no')
	                else:
	                    i.imcopy(im.fname+'[*,*,1]',newname)
	                i.astutil(_doprint=0)
	                i.hedit(newname,fields='OBSERVAT',value='SOAR',add='yes',verify='no')
	                i.hedit(newname,fields='EPOCH',value='2000',add='yes',verify='no')
			i.setjd.setParam('time','UT')
			i.setjd(newname)
	
	
	                if CCDSUM == BIN1X1:
				i.hedit(newname,fields='DETSIZE',value='[1:4069,1:1896]', update='yes',addonly='no',delete='no',verify='no')
				i.hedit(newname,fields='DATASEC',value='[28:4096,1:1896]',update='yes',addonly='no',delete='no',verify='no')
				i.hedit(newname,fields='TRIMSEC',value='[28:4096,1:1896]',update='yes',addonly='no',delete='no',verify='no')
				i.hedit(newname,fields='DETSEC', value='[1:4069,1:1896]', update='yes',addonly='no',delete='no',verify='no')
				i.hedit(newname,fields='CCDSEC', value='[1:4069,1:1896]', update='yes',addonly='no',delete='no',verify='no')
				i.hedit(newname,fields='CCDSIZE',value='[1:4069,1:1896]', update='yes',addonly='no',delete='no',verify='no')
	 			i.hedit(newname,fields='BIASSEC',value='[5:15,40:1860]',  update='yes',addonly='no',delete='no',verify='no')
	
	                elif CCDSUM == BIN2X2:
                             print "2x2"
                             i.hedit(newname,fields='DETSIZE',value='[1:2071,1:948]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='TRIMSEC',value='[12:2054,1:948]',update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSIZE',value='[1:2071,1:948]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='DETSEC', value='[1:2071,1:948]', update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='BIASSEC',value='[2:8,20:930]',   update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSEC', value='[1:2071,1:948]', update='yes',addonly='yes',delete='no',verify='no')

	                elif CCDSUM == BIN3X3:
                             print "3x3"
                             i.hedit(newname,fields='DETSIZE',value='[1:1356,1:632]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='TRIMSEC',value='[10:1365,1:632]',update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSIZE',value='[1:1356,1:632]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='DETSEC', value='[1:1356,1:632]', update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='BIASSEC',value='[3:5,13:629]',   update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSEC', value='[1:1356,1:632]', update='yes',addonly='yes',delete='no',verify='no')

	                elif CCDSUM == BIN4X4:
                             print "4x4"
                             i.hedit(newname,fields='DETSIZE',value='[1:1036,1:474]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='TRIMSEC',value='[6:1028,1:474]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSIZE',value='[1:1036,1:474]', update='yes',addonly='no',delete='no',verify='no')
                             i.hedit(newname,fields='DETSEC', value='[1:1036,1:474]', update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='BIASSEC',value='[1:4,10:465]',   update='yes',addonly='yes',delete='no',verify='no')
                             i.hedit(newname,fields='CCDSEC', value='[1:1036,1:474]', update='yes',addonly='yes',delete='no',verify='no')
	                else:
	                    print "ERROR: It's neither 1x1, 2x2, 3x3 or 4x4."
                            return -1
	                    #sys.exit(1)
	
        if not im.next:
            return newname
            #sys.exit(1)
        if FLAG_END:
            return newname
            break
        else:
            im.add()
