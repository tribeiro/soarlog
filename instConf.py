
from PyQt4 import QtCore,QtGui,uic,QtSql
from sqlalchemy import Column,Integer,String,TEXT
from sqlalchemy import FLOAT as REAL
import numpy as np


def SPARTAN_OBSTIME(query):
    return str(query['TIME-END']).split('T')[1]


def GOODMAN_RDMODE(query):
    RD = {330 : '100kHz', 130 : '200kHz' , 30 : '400kHz'}
    return RD[query['PARAM26']] + ' ATT' + '%s'%(query['PARAM27'])

def GOODMAN_SPCONF(query):
    """GOODMAN SP configuration."""

    _GconfMap_300  = {
        '': [ 5. , 11.]
    }

    _GconfMap_400  = {
        'b': [6.5 , 13.],
        'r': [ 8. , 16.]
    } # Check the 400r configuration!

    _GconfMap_600  = {
        'b': [ 7. , 17.],
        'm': [10. , 20.],
        'r': [12. , 27.]
    }

    _GconfMap_1200 = {
        'm0': [16.3,26.0],
        'm1': [16.3,29.5],
        'm2': [18.7,34.4],
        'm3': [20.2,39.4],
        'm4': [22.2,44.4],
        'm5': [24.8,49.6],
        'm6': [27.4,54.8],
        'm7': [30.1,60.2]
    }

    _Gratings = {
        '300': _GconfMap_300,
        '400': _GconfMap_400,
        '600': _GconfMap_600,
        '1200': _GconfMap_1200,
    }

    # Grating
    grt = ''
    if query['GRATING'] == '<NO GRATING>':
        return 'ACQ'
    else:
        grt = query['GRATING'].split('_')[1]

    # Filter (yes or no)
    filter = ''

    if query['FILTER'] != '<NO FILTER>' or query['FILTER2'] != '<NO FILTER>':
        filter = 'F'

    # Region 300() 600(custom,red,mid,blue) 1200(custom,m1,m2,m3,m4,m5,m6,m7)

    spcfg = ''

    grt_a,cam_a = float(query['GRT_ANG']),float(query['CAM_ANG'])
    grt_d,cam_d = grt_a,cam_a
    Gconf = _Gratings[grt]
    for key in Gconf.keys():
        dg = np.abs(grt_a-Gconf[key][0])
        dc = np.abs(cam_a-Gconf[key][1])
        if dg+dc < grt_d+cam_d:
            spcfg = key
            grt_d = dg
            cam_d = dc

    if grt_d > 1.0 or cam_d > 1.0:
        spcfg = spcfg + 'C'

    return grt+spcfg+filter


def instConfGoodman(query):
    """Return instrument configuration for the GOODMAN Spectrograph."""
    rdmode = query.RON_MODE
    spconf = query.SP_CONF
    binn = query.BINNING
    slit = query.SLIT
    ffilter = ''

    if query.FILTER != '<NO FILTER>':
        ffilter = query.FILTER
    elif query.FILTER2 != '<NO FILTER>':
        ffilter = query.FILTER2
    
    return spconf+' '+ffilter+' '+binn+' '+rdmode+' '+slit


def instConfOSIRIS(query):

    slit = query.SLIT
    spconf = query.SP_CONF
    binn = query.BINNING
    ffilter = 'Open'
    if query.FILTER != 'Open':
        ffilter = query.FILTER
    elif query.FILTER2 != 'Open':
        ffilter = query.FILTER2
    grt = query.GRATING
    
    if spconf == 'ACQ':
        return spconf+' '+ffilter+' '+binn
    elif spconf == 'SP':
        return slit+' '+ffilter+' '+binn
    else:
        return ffilter+' '+binn
 
    return 'None'


def instConfSOI(query):

    binn = query.BINNING
    ffilter = query.FILTER
    if ffilter.find('Open') >= 0:
        ffilter = query.FILTER2

    return ffilter+' '+binn


def instConfSPARTAN(query):
    
    return query.FILTER+' '+query.FILTER2+' '+query.SLIT
