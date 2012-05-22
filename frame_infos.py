
from sqlalchemy import Column,Integer,String,TEXT
from sqlalchemy import FLOAT as REAL
import pyfits
import time,os,sys
import numpy as np


'''
	Basic definition of header parameters contained in each database.
'''

def GOODMAN_RDMODE(query):
	
	RD = {330 : '100kHz', 130 : '200kHz' , 30 : '400kHz'}
	return RD[query['PARAM26']] + ' ATT' + '{0}'.format(query['PARAM27'])

def GOODMAN_SPCONF(query):
	'''
		GOODMAN SP configuration.
	'''
	
	# Grating
	grt = '' #query.GRATNGID.split('_')[1]
	if query['GRATING'] == '<NO GRATING>':
		return 'ACQ'
	else:
		grt = query['GRATING'].split('_')[1]
	
	# Filter (yes or no)
	filter = ''
	
	if query['FILTER'] != '<NO FILTER>' or query['FILTER'] != '<NO FILTER>':
		filter = 'F'
	
	# Region 300() 600(custom,red,mid,blue) 1200(custom,m1,m2,m3,m4,m5,m6,m7)
	
	spcfg = ''
	

	grtAng = [  5. ,   7. ,  10. ,  12. ,  16.3,  18.7,  20.2,  22.2,  24.8, 27.4,  30.1]
	camAng = [ 11. ,  17. ,  20. ,  27. ,  29.5,  34.4,  39.4,  44.4,  49.6, 54.8,  60.2]
	
	if grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[1]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[1]) < 1.0):
		
		spcfg = 'b'

	elif grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[2]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[2]) < 1.0):
		
		spcfg = 'm'

	elif grt == '600' and ( np.abs(float(query['CAM_ANG']) - camAng[3]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[3]) < 1.0):
		
		spcfg = 'r'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[4]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[4]) < 1.0):
			spcfg = 'm1'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[5]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[5]) < 1.0):
			spcfg = 'm2'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[6]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[6]) < 1.0):
			spcfg = 'm3'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[7]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[7]) < 1.0):
			spcfg = 'm4'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[8]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[8]) < 1.0):
			spcfg = 'm5'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[9]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[9]) < 1.0):
			spcfg = 'm6'

	elif grt == '1200' and ( np.abs(float(query['CAM_ANG']) - camAng[10]) < 1.0 or np.abs(float(query['GRT_ANG']) - grtAng[10]) < 1.0):
			spcfg = 'm7'
	
	else:
		spcfg = 'C'
	
	return grt+filter+spcfg
		


# defines the image header parameter for instrument!

_INSTRUME = {'OSIRIS':'INSTRUME','GOODMAN':'INSTRUME','SOI':'INSTRUME','SPARTAN':'INSTRUME','SBIG ST-L' : 'INSTRUME'}

instTemplates = {'Goodman Spectrograph' : os.path.join(os.path.dirname(__file__),'Resources/goodmanTemplate.fits'),
'OSIRIS' : os.path.join(os.path.dirname(__file__),'Resources/osirisTemplate.fits'),
'SOI' : os.path.join(os.path.dirname(__file__),'Resources/soiTemplate.fits'),
'Spartan IR Camera' : os.path.join(os.path.dirname(__file__),'Resources/spartanTemplate.fits')}

SPARTAN = 'Spartan IR Camera'

##################################################################################################################################
#
# Common Information Database

CID = { 'FILENAME' : Column('FILENAME',String)	,\
		'OBJECT' : Column('OBJECT',String)		,\
		'IMAGETYP' : Column('IMAGETYP',String)	,\
		'TIMEOBS' : Column('TIMEOBS',String)	,\
		'DATEOBS' : Column('DATEOBS',String)	,\
		'EXPTIME' : Column('EXPTIME',REAL)		,\
		'JD' : Column('JD',String)				,\
		'OBSERVER' : Column('OBSERVER',String)	,\
		'INSTRUME' : Column('INSTRUME',String)	,\
		'OBSERVAT' : Column('OBSERVAT',String)	,\
		'AIRMASS' : Column('AIRMASS',REAL)		,\
		'RA' : Column('RA',String)				,\
		'DEC' : Column('DEC',String)			,\
		'EQUINOX': Column('EQUINOX',String)		,\
		'OBSNOTES' :Column('OBSNOTES',TEXT)	,\
		'SEEING' : Column('SEEING',String)		}

#
#
##################################################################################################################################		

##################################################################################################################################
#
# Table View Database

tvDB = { 'FILENAME' : Column('FILENAME',String)	,\
		'PATH' : Column('PATH',String)			,\
		'OBJECT' : Column('OBJECT',String)		,\
		'IMAGETYP' : Column('IMAGETYP',String)	,\
		'TIMEOBS' : Column('TIMEOBS',String)	,\
		'DATEOBS' : Column('DATEOBS',String)	,\
		'EXPTIME' : Column('EXPTIME',REAL)		,\
		'JD' : Column('JD',String)				,\
		'OBSERVER' : Column('OBSERVER',String)	,\
		'INSTRUME' : Column('INSTRUME',String)	,\
		'OBSERVAT' : Column('OBSERVAT',String)	,\
		'AIRMASS' : Column('AIRMASS',REAL)		,\
		'RA' : Column('RA',String)				,\
		'DEC' : Column('DEC',String)			,\
		'EQUINOX': Column('EQUINOX',String)		,\
		'OBSNOTES' : Column('OBSNOTES',String)	,\
		'SEEING' : Column('SEEING',String)		,\
		'FILTER' : Column('FILTER',String)		,\
		'FILTER2': Column('FILTER2',String)		,\
		'SLIT': Column('SLIT',String)			,\
		'GRATING' : Column('GRATING',String)	,\
		'FOCUS'	: Column('FOCUS',String)		,\
		'CAM_ANGLE': Column('CAM_ANGLE',String)	,\
		'GRT_ANGLE'	: Column('GRT_ANGLE',String),\
		'RON_MODE'	: Column('RON_MODE',String)	,\
		'BINNING'	: Column('BINNING',String)	,\
		'PA'	: Column('PA',String)			,\
		'SP_CONF' : Column('SP_CONF',String)	}


#
#
##################################################################################################################################		

##################################################################################################################################
#
# data Quality Database. It is related to tvDB and instrument db.

dataQualityDB = {	'TYPE'		: Column('TYPE',String)			,\
					'SEMESTER'	: Column('SEMESTER',String)		,\
					'PID'		: Column('PID',String)			,\
					'DATASET'	: Column('DATASET',String)		,\
					'DQNOTE'	: Column('DQNOTE',TEXT)			,\
					'BIAS'		: Column('BIAS',String)			,\
					'DARK'		: Column('DARK',String)			,\
					'FLATFIELD'	: Column('FLATFIELD',String)	,\
					'BIASNOTE'	: Column('BIASNOTE',TEXT)			,\
					'DARKNOTE'	: Column('DARKNOTE',TEXT)			,\
					'FLATFIELDNOTE'	: Column('FLATFIELDNOTE',TEXT)	,\
					'FROMDB'	: Column('FROMDB',String),
					'OBSTIME'  : Column('OBSTIME',REAL),
					'VALIDTIME'  : Column('VALIDTIME',REAL)}


#
#
##################################################################################################################################		

##################################################################################################################################
#
# object specific data quality database. it is related to dataQualityDB

frameDataQualityDB = {	'SEMESTER'	: Column('SEMESTER',String)		,\
					'PID'		: Column('PID',String)			,\
					'DATASET'	: Column('DATASET',String)		,\
					'OBJECT'	: Column('OBJECT',String)		,\
					'FIELD'	: Column('FIELD',String)		,\
					'FIELDNOTE'	: Column('FIELDNOTE',String)		,\
					'CONFIG'	: Column('CONFIG',String)		,\
					'CONFIGNOTE': Column('CONFIGNOTE',String)	,\
					'FWHM'	: Column('FWHM',REAL)		,\
					'E'	      : Column('E',REAL)}

frameListDataQualityDB = {'id_tvDB' : Column('id_tvDB',Integer),
                          'id_INSTRUME' : Column('id_INSTRUME',Integer),
                          'DATASET'	: Column('DATASET',String)}
#
#
##################################################################################################################################		

##################################################################################################################################
#
# Project file database. This database stores the files related to each project. The db stores information on file location, file
# name and type (calibration[BIAS, DARK, FLAT-FIELD, WAVELENGHT]/day-ligth-calibration[BIAS, DARK, FLAT-FIELD, WAVELENGHT]/
# observatarions[TARGET,STANDARD].

projectFilesDB = {	'PID'		:	Column('PID',String)		,
					'TYPE'		:	Column('TYPE',Integer)		,
					'SUBTYPE'	:	Column('SUBTYPE',Integer)	,
					'FILENAME'	:	Column('FILENAME',String)	,
					'PATH'		:	Column('PATH',String)		}

#
#
##################################################################################################################################		

##################################################################################################################################
#
# Infos particular to OSIRIS

OSIRIS_ID = {   'FILENAME'	: Column('FILENAME',String)		,\
				'NCOADDS'	: Column('NCOADDS' ,Integer)	,\
				'DETECTOR'	: Column('DETECTOR',String)		,\
				'DISPAXIS'	: Column('DISPAXIS',Integer)	,\
				'MODE'		: Column('MODE'	  ,String)		,\
				'FILTERID'	: Column('FILTERID',String)		,\
				'PREFLTID'	: Column('PREFLTID',String)		,\
				'CAMERAID'	: Column('CAMERAID',String)		,\
				'CAMFOCUS'	: Column('CAMFOCUS',Integer)	,\
				'SLITID'	: Column('SLITID'  ,String)		,\
				'GRATNGID'	: Column('GRATNGID',String)		,\
				'GRATTILT'	: Column('GRATTILT',String)		,\
				'DECPANGL'	: Column('DECPANGL',String)}

#			
# Translation of OSIRIS Common Information Database (CID) Header parameters
#

OSIRIS_TRANSLATE_CID = { 'FILENAME' : 'FILENAME'	,\
		'OBJECT' : 'OBJECT'		,\
		'IMAGETYP' : 'IMAGETYP'	,\
		'TIMEOBS' : 'TIME-OBS'	,\
		'DATEOBS' : 'DATE-OBS'	,\
		'EXPTIME'  : 'EXPTIME'	,\
		'JD' : 'JD'				,\
		'OBSERVER' : 'OBSERVER'	,\
		'INSTRUME' : 'INSTRUME'	,\
		'OBSERVAT' : 'OBSERVAT'	,\
		'AIRMASS'  : 'SECZ'		,\
		'RA' : 'RA'				,\
		'DEC' : 'DEC'			,\
		'EQUINOX': 'EQUINOX'	,\
		'SEEING' : 'SEEING'}
		#,\
		#'SEEING' : 'SEEING'	
		#}

#
# Translation of OSIRIS header to TableViewDataBase (tvDB)
#

OSIRIS_TV = {	'FILTER'	:	'FILTERID'		,
				'FILTER2'	:	'PREFLTID'		,
				'SLIT'		:	'SLITID'		,
				'GRATING'	:	'GRATNGID'		,
				'FOCUS'		:	'CAMFOCUS'		,
				'CAM_ANGLE'	:	None			,
				'GRT_ANGLE'	:	'GRATTILT'		,
				'RON_MODE'	:	'NCOADDS'		,
				'BINNING'	:	'CAMERAID'		,
				'PA'		:	'DECPANGL'		,
				'SP_CONF'	:	'MODE'			 }

#
#
##################################################################################################################################		

##################################################################################################################################
#			
# Infos particular to GOODMAN
		
GOODMAN_ID = {  'FILENAME'	: Column('FILENAME',String) ,\
'FOCUS'		:	Column( 'FOCUS'	  ,String)	,\
'MOUNT_AZ'	:	Column( 'MOUNT_AZ',String)	,\
'MOUNT_EL'	:	Column( 'MOUNT_EL',String)	,\
'ROTATOR'	:	Column( 'ROTATOR' ,String)	,\
'POSANGLE'	:	Column( 'POSANGLE',String)	,\
'SEEING'	:	Column( 'SEEING'  ,String)	,\
'CAM_ANG'	:	Column( 'CAM_ANG' ,String)	,\
'GRT_ANG'	:	Column( 'GRT_ANG' ,String)	,\
'CAM_FOC'	:	Column( 'CAM_FOC' ,String)	,\
'COLL_FOC'	:	Column( 'COLL_FOC',String)	,\
'FILTER'	:	Column( 'FILTER'  ,String)	,\
'FILTER2'	:	Column( 'FILTER2' ,String)	,\
'GRATING'	:	Column( 'GRATING' ,String)	,\
'SLIT'		:	Column( 'SLIT'	  ,String)	,\
'COL_TEMP'	:	Column( 'COL_TEMP',String)	,\
'CAM_TEMP'	:	Column( 'CAM_TEMP',String)	,\
'EXPTIME'	:	Column( 'EXPTIME' ,String)	,\
'RDNOISE'	:	Column( 'RDNOISE' ,String)	,\
'GAIN'		:	Column( 'GAIN'	  ,String)	,\
'PROPOSAL'	:	Column( 'PROPOSAL',String)	,\
'DISPAXIS'	:	Column( 'DISPAXIS',String)	,\
'DETSIZE'	:	Column( 'DETSIZE' ,String)	,\
'TRIMSEC'	:	Column( 'TRIMSEC' ,String)	,\
'CCDSIZE'	:	Column( 'CCDSIZE' ,String)	,\
'CCDSUM'	:	Column( 'CCDSUM'  ,String)	,\
'WCSDIM'	:	Column( 'WCSDIM'  ,String)	,\
'PARAM26'	:	Column( 'PARAM26' ,String)	,\
'PARAM27'	:	Column( 'PARAM27' ,String)
}


#
# Translation of GOODMAN Common Information Database (CID) Header parameters
#

GOODMAN_TRANSLATE_CID = {'FILENAME' : 'FILENAME'	,\
		'OBJECT' : 'OBJECT'		,\
		'IMAGETYP' : 'OBSTYPE'	,\
		'TIMEOBS' : 'UT'	,\
		'DATEOBS' : 'DATE-OBS'	,\
		'EXPTIME'  : 'EXPTIME'	,\
		'JD' : 'UT'				,\
		'OBSERVER' : 'OBSERVER'	,\
		'INSTRUME' : 'INSTRUME'	,\
		'OBSERVAT' : 'TELESCOP'	,\
		'AIRMASS'  : 'AIRMASS'	,\
		'RA' : 'RA'				,\
		'DEC' : 'DEC'			,\
		'EQUINOX': 'EQUINOX'	,\
		'SEEING' : 'SEEING'

}

		
GOODMAN_TV = {	'FILTER'	:	'FILTER'		,
				'FILTER2'	:	'FILTER2'		,
				'SLIT'		:	'SLIT'			,
				'GRATING'		:	'GRATING'		,
				'FOCUS'		:	'CAM_FOC'		,
				'CAM_ANGLE'	:	'CAM_ANG'		,
				'GRT_ANGLE'	:	'GRT_ANG'		,
				'RON_MODE'	:	GOODMAN_RDMODE	,
				'BINNING'	:	'CCDSUM'		,
				'PA'		:	'POSANGLE'		,
				'SP_CONF'	:	GOODMAN_SPCONF	 }

#
#
##################################################################################################################################		

##################################################################################################################################
#
# Infos particular to SOI
		
SOI_ID = {  'FILENAME'	: Column('FILENAME',String) ,\
'TELFOCUS' : Column('TELFOCUS',String) ,\
'ROTATOR' : Column('ROTATOR',String) ,\
'FILTER1' : Column('FILTER1',String) ,\
'FILTER2' : Column('FILTER2',String) ,\
'DIMMSEE' : Column('DIMMSEE',String) ,\
'CCDSUM' : Column('CCDSUM',String) ,\
'DECPANG' : Column('DECPANG',String)}


SOI_TRANSLATE_CID = {'FILENAME' : 'FILENAME'  ,\
		'OBJECT' : 'OBJECT'		,\
		'IMAGETYP' : 'OBSTYPE'	,\
		'TIMEOBS' : 'TIME-OBS'	,\
		'DATEOBS' : 'DATE-OBS'	,\
		'EXPTIME'  : 'EXPTIME'	,\
		'JD' : 'MJD-OBS'				,\
		'OBSERVER' : 'OBSERVER'	,\
		'INSTRUME' : 'INSTRUME'	,\
		'OBSERVAT' : 'TELESCOP'	,\
		'AIRMASS'  : 'AIRMASS'	,\
		'RA' : 'RA'				,\
		'DEC' : 'DEC'			,\
		'EQUINOX': 'RADECEQ'	,\
		'SEEING' : 'DIMMSEE'		
}
				
SOI_TV = {		'FILTER'	:	'FILTER1'		,
				'FILTER2'	:	'FILTER2'		,
				'SLIT'		:	None			,
				'GRATING'		:	None			,
				'FOC'		:	'TELFOCUS'		,
				'CAM_ANGLE'	:	None			,
				'GRT_ANGLE'	:	None			,
				'RON_MODE'	:	None			,
				'BINNING'	:	'CCDSUM'		,
				'PA'		:	'DECPANGL'		,
				'SP_CONF'	:	None			 }

#
#
##################################################################################################################################		

##################################################################################################################################
#
# Infos particular to SPARTAN
		
SPARTAN_ID = {  'FILENAME'	: Column('FILENAME',String) ,\
'BZERO' : Column('BZERO',String)	,\
'OBSID' : Column('OBSID',String)	,\
'FILTER' : Column('FILTER',String)	,\
'MASK' : Column('MASK',String)		,\
'PUPIL' : Column('PUPIL',String)	,\
'ANG-RES' : Column('ANG-RES',String)	,\
'LST-OBS' : Column('LST-OBS',String)	,\
'EXP-BTWN' : Column('EXP-BTWN',String)	,\
'TARGETNR' : Column('TARGETNR',String)	,\
'TARGETNA' : Column('TARGETNA',String)	,\
'RAPANGL' : Column('RAPANGL',String)	,\
'DECPANGL' : Column('DECPANGL',String)	,\
'TRAPANGL' : Column('TRAPANGL',String)	,\
'TDECPANG' : Column('TDECPANG',String)	,\
'PIXSCAL1' : Column('PIXSCAL1',String)	,\
'PIXSCAL2' : Column('PIXSCAL2',String)	,\
'DETSIZE' : Column('DETSIZE',String)	,\
'DETSEC' : Column('DETSEC',String)	,\
'DETSERNO' : Column('DETSERNO',String)	,\
'DETBIASG' : Column('DETBIASG',String)	,\
'DETRESET' : Column('DETRESET',String)	,\
'DETOSET0' : Column('DETOSET0',String)	,\
'DETOSET1' : Column('DETOSET1',String)	,\
'DETOSET2' : Column('DETOSET2',String)	,\
'DETOSET3' : Column('DETOSET3',String)	,\
'INSTEM1' : Column('INSTEM1',String)	,\
'INSTEM2' : Column('INSTEM2',String)	,\
'INSTEM3' : Column('INSTEM3',String)	,\
'INSTEM4' : Column('INSTEM4',String)	,\
'INSTEM5' : Column('INSTEM5',String)	,\
'INSTEM6' : Column('INSTEM6',String)	,\
'INSTEM7' : Column('INSTEM7',String)	,\
'INSTEM8' : Column('INSTEM8',String)	,\
'INSTEM9' : Column('INSTEM9',String)	,\
'DETTEM1' : Column('DETTEM1',String)	,\
'DETTEM2' : Column('DETTEM2',String)	,\
'DETTEM3' : Column('DETTEM3',String)	,\
'DETTEM4' : Column('DETTEM4',String)	,\
'INSPRESS' : Column('INSPRESS',String)	,\
'TELFOCUS' : Column('TELFOCUS',String)	,\
'TELALT' : Column('TELALT',String)	,\
'TELAZ' : Column('TELAZ',String)	,\
'DOMEAZ' : Column('DOMEAZ',String)	,\
'DOMEALT' : Column('DOMEALT',String)	,\
'HA' : Column('HA',String)		,\
'ROTATOR' : Column('ROTATOR',String)	,\
'TELMJD' : Column('TELMJD',String)	,\
'TELUTC' : Column('TELUTC',String)	,\
'ZD' : Column('ZD',String)		,\
'TELRA' : Column('TELRA',String)	,\
'TELDEC' : Column('TELDEC',String)	,\
'OBSRA' : Column('OBSRA',String)	,\
'OBSDEC' : Column('OBSDEC',String)	,\
'REFRA' : Column('REFRA',String)	,\
'REFDEC' : Column('REFDEC',String)	,\
'OFFSERA' : Column('OFFSERA',String)	,\
'OFFSEDEC' : Column('OFFSEDEC',String)	,\
'SEEING' : Column('SEEING',String)	,\
'ENVHUM' : Column('ENVHUM',String)	,\
'ENVWIN' : Column('ENVWIN',String)	,\
'ENVDIR' : Column('ENVDIR',String)	,\
'ENVTEM' : Column('ENVTEM',String)	,\
'ENVTEI' : Column('ENVTEI',String)	,\
'ENVPRE' : Column('ENVPRE',String)	,\
'ORIGIN' : Column('ORIGIN',String)	,\
'INSTSWV' : Column('INSTSWV',String)	,\
'CONTROLR' : Column('CONTROLR',String)	,\
'CONHWV' : Column('CONHWV',String)	,\
'CONSWV' : Column('CONSWV',String)	,\
'DETECTOR' : Column('DETECTOR',String)	,\
'GUIDXERR' : Column('GUIDXERR',String)	,\
'GUIDYERR' : Column('GUIDYERR',String)	,\
'GUIDSTAR' : Column('GUIDSTAR',String)	,\
'GUIDVMAG' : Column('GUIDVMAG',String)	,\
'GUIDPRBX' : Column('GUIDPRBX',String)	,\
'GUIDPRBY' : Column('GUIDPRBY',String)	,\
'GUIDPRBU' : Column('GUIDPRBU',String)	,\
'GUIDPRBV' : Column('GUIDPRBV',String)	,\
'GUIDEXP' : Column('GUIDEXP',String)	,\
'GUIDLOOP' : Column('GUIDLOOP',String)	,\
'GUIDROI' : Column('GUIDROI',String)	,\
'GUIDBIN' : Column('GUIDBIN',String)	,\
'GUIDBOX' : Column('GUIDBOX',String)	,\
'GUIDIPK' : Column('GUIDIPK',String)	,\
'GUIDITOT' : Column('GUIDITOT',String)	,\
'GUIDBKGD' : Column('GUIDBKGD',String)	,\
'CRVAL1' : Column('CRVAL1',String)	,\
'CRVAL2' : Column('CRVAL2',String)	,\
'CTYPE1' : Column('CTYPE1',String)	,\
'CTYPE2' : Column('CTYPE2',String)	,\
'CRPIX1' : Column('CRPIX1',String)	,\
'CRPIX2' : Column('CRPIX2',String)	,\
'CD1_1' : Column('CD1_1',String)	,\
'CD1_2' : Column('CD1_2',String)	,\
'CD2_1' : Column('CD2_1',String)	,\
'CD2_2' : Column('CD2_2',String)	,\
'A_ORDER' : Column('A_ORDER',String)	,\
'A_0_2' : Column('A_0_2',String)	,\
'A_0_3' : Column('A_0_3',String)	,\
'A_1_1' : Column('A_1_1',String)	,\
'A_1_2' : Column('A_1_2',String)	,\
'A_2_0' : Column('A_2_0',String)	,\
'A_2_1' : Column('A_2_1',String)	,\
'A_3_0' : Column('A_3_0',String)	,\
'B_ORDER' : Column('B_ORDER',String)	,\
'B_0_2' : Column('B_0_2',String)	,\
'B_0_3' : Column('B_0_3',String)	,\
'B_1_1' : Column('B_1_1',String)	,\
'B_1_2' : Column('B_1_2',String)	,\
'B_2_0' : Column('B_2_0',String)	,\
'B_2_1' : Column('B_2_1',String)	,\
'B_3_0' : Column('B_3_0',String)	,\
'AP_ORDER' : Column('AP_ORDER',String)	,\
'AP_0_1' : Column('AP_0_1',String)	,\
'AP_0_2' : Column('AP_0_2',String)	,\
'AP_0_3' : Column('AP_0_3',String)	,\
'AP_1_0' : Column('AP_1_0',String)	,\
'AP_1_1' : Column('AP_1_1',String)	,\
'AP_1_2' : Column('AP_1_2',String)	,\
'AP_2_0' : Column('AP_2_0',String)	,\
'AP_2_1' : Column('AP_2_1',String)	,\
'AP_3_0' : Column('AP_3_0',String)	,\
'BP_ORDER' : Column('BP_ORDER',String)	,\
'BP_0_1' : Column('BP_0_1',String)	,\
'BP_0_2' : Column('BP_0_2',String)	,\
'BP_0_3' : Column('BP_0_3',String)	,\
'BP_1_0' : Column('BP_1_0',String)	,\
'BP_1_1' : Column('BP_1_1',String)	,\
'BP_1_2' : Column('BP_1_2',String)	,\
'BP_2_0' : Column('BP_2_0',String)	,\
'BP_2_1' : Column('BP_2_1',String)	,\
'BP_3_0' : Column('BP_3_0',String)	,\
'CUNIT1' : Column('CUNIT1',String)	,\
'CUNIT2' : Column('CUNIT2',String)	,\
'UNITTEMP' : Column('UNITTEMP',String)	,\
'UNITPRES' : Column('UNITPRES',String)	,\
'TIMESYS' : Column('TIMESYS',String)	,\
'RADECSYS' : Column('RADECSYS',String)	,\
'RADECEQ' : Column('RADECEQ',String)	,\
'TELRADEC' : Column('TELRADEC',String)	,\
'TELEQUIN' : Column('TELEQUIN',String)	,\
'HDR_REV' : Column('HDR_REV',String)	}


SPARTAN_TRANSLATE_CID = {'FILENAME' : 'FILENAME'  ,\
		'OBJECT' : 'OBJECT'		,\
		'IMAGETYP' : 'OBSTYPE'	,\
		'TIMEOBS' : 'TIME-END'	,\
		'DATEOBS' : 'DATE-OBS'	,\
		'EXPTIME'  : 'EXPTIME'	,\
		'JD' : 'MJD-OBS'				,\
		'OBSERVER' : 'OBSERVER'	,\
		'INSTRUME' : 'INSTRUME'	,\
		'OBSERVAT' : 'TELESCOP'	,\
		'AIRMASS'  : 'AIRMASS'	,\
		'RA' : 'RA'				,\
		'DEC' : 'DEC'			,\
		'EQUINOX': 'RADECEQ'	,\
		'SEEING' : 'SEEING'		
}


SPARTAN_TV = {	'FILTER'	:	'FILTER'		,
				'FILTER2'	:	'PUPIL'			,
				'SLIT'		:	'MASK'			,
				'GRATING'		:	None			,
				'FOC'		:	'TELFOCUS'		,
				'CAM_ANGLE'	:	None			,
				'GRT_ANGLE'	:	None			,
				'RON_MODE'	:	None			,
				'BINNING'	:	None			,
				'PA'		:	'DECPANGL'		,
				'SP_CONF'	:	None			 }


#
#
##################################################################################################################################		

SBIG_TRANSLATE_CID = {'FILENAME' : 'FILENAME'  ,\
		'OBJECT' : 'OBJECT'		,\
		'IMAGETYP' : 'OBJECT'	,\
		'TIMEOBS' : 'DATE-OBS'	,\
		'DATEOBS' : 'DATE-OBS'	,\
		'EXPTIME'  : 'EXPTIME'	,\
		'JD' : 'EXPTIME'				,\
		'OBSERVER' : 'OBSERVER'	,\
		'INSTRUME' : 'INSTRUME'	,\
		'OBSERVAT' : 'TELESCOP'	,\
		'AIRMASS'  : 'EXPTIME'	,\
		'RA' : 'XPIXSC'				,\
		'DEC' : 'XPIXSC'			,\
		'EQUINOX': 'CBLACK'	,\
		'SEEING' : 'BSCALE'		
}

SBIG_TV = {		'FILTER'	:	None			,
				'FILTER2'	:	None			,
				'SLIT'		:	None			,
				'GRATING'		:	None			,
				'FOC'		:	None			,
				'CAM_ANGLE'	:	None			,
				'GRT_ANGLE'	:	None			,
				'RON_MODE'	:	None			,
				'BINNING'	:	None			,
				'PA'		:	None			,
				'SP_CONF'	:	None			 }


SBIG_ID  = {  'FILENAME'	: Column('FILENAME',String) ,\
'BZERO' : Column('BZERO',String)       }

##################################################################################################################################
#
# Dictionaries of instrument translation

INSTRUMENT_TRANSLATE = { 'OSIRIS' : OSIRIS_TRANSLATE_CID ,\
'Goodman Spectrograph' : GOODMAN_TRANSLATE_CID ,\
'SOI' : SOI_TRANSLATE_CID ,\
'Spartan IR Camera' : SPARTAN_TRANSLATE_CID,\
'SBIG ST-L' : SBIG_TRANSLATE_CID}

INSTRUMENT_DB = { 'OSIRIS' : OSIRIS_ID	,\
'Goodman Spectrograph' : GOODMAN_ID	,\
'SOI' : SOI_ID ,\
'Spartan IR Camera' : SPARTAN_ID,\
'SBIG ST-L' : SBIG_ID}

INSTRUMENT_TV = { 'OSIRIS' : OSIRIS_TV	,\
'Goodman Spectrograph' : GOODMAN_TV	,\
'SOI' : SOI_TV ,\
'Spartan IR Camera' : SPARTAN_TV,\
'SBIG ST-L' : SBIG_TV}

#imageTYPE = ['','OBJECT','FLAT','DFLAT','BIAS','ZERO','DARK','COMP','FAILED','Object'] 

imageTYPE = {'OSIRIS' : ['OBJECT','FLAT','ZERO','COMP','DARK','FAILED'],
'Goodman Spectrograph' : ['OBJECT','COMP','FLAT','BIAS','FAILED'],
'Spartan IR Camera' : ['Object','Flat-Field','Dark','FAILED'],
'SOI' : ['ZERO','DFLAT','OBJECT','FAILED']}

#
#
##################################################################################################################################

##################################################################################################################################
#
# Definitions of Table for viewing

ExtraTableHeaders=['FILTER' ,\
		'FILTER2'			,\
		'SLIT'				,\
		'GRATING'			,\
		'FOC'				,\
		'CAM ANG'		,\
		'GRT ANG'		,\
		'RD MODE'			,\
		'BIN'			,\
		'PA'			,\
		'SP CONF']

	

TableTranslate_GOODMAN = ['FILTER' ,\
		'FILTER2'			,\
		'SLIT'				,\
		'GRATING'			,\
		'CAM_FOC'			,\
		'CAM_ANG'			,\
		'GRT_ANG'			,\
		GOODMAN_RDMODE		,\
		'CCDSUM'			,\
		'POSANGLE'			,\
		GOODMAN_SPCONF	]
		
TableTranslate_OSIRIS = ['FILTERID' ,\
		'PREFLTID'			,\
		'SLITID'				,\
		'GRATNGID'			,\
		'CAMFOCUS'				,\
		None		,\
		'GRATTILT'		,\
		None			,\
		'CAMERAID'		,\
		'DECPANGL'	,\
		None]


TableTranslate_SOI = ['FILTER1' ,\
		'FILTER2'			,\
		None				,\
		None			,\
		'TELFOCUS'				,\
		None		,\
		None		,\
		None			,\
		'CCDSUM'		,\
		'DECPANG'	,\
		None]

TableTranslate_SPARTAN = [ 'FILTER' ,\
'MASK' ,\
None ,\
None ,\
'TELFOCUS' ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ]

TableTranslate_SBIG = [ None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
None ,\
]

dictTableHeaders = {'OSIRIS' : TableTranslate_OSIRIS, 'Goodman Spectrograph' : TableTranslate_GOODMAN , 'SOI' : TableTranslate_SOI ,\
'Spartan IR Camera' : TableTranslate_SPARTAN,\
'SBIG ST-L' : TableTranslate_SBIG }

	
#
#
##################################################################################################################################

##################################################################################################################################
#
# Return database entry with frame infos

def GetFrameInfos(filename):

	import numpy as np
	
	hdr = None
	hdr_out = {}
	hdr_inst = {}
	
	FExists = False
	
	try:
		hdulist = pyfits.open(filename,ignore_missing_end=True)		
	except IOError:
		print '[FAILED - IOError]: ',filename
		return -1 # Could not read file for some reason

	try:
		hdulist.verify('fix')
	except:
		#print '[FAILED - verify]: ',filename
		pass #return -1

	try:
		hdr = hdulist[1].header
	except IndexError:
		try:
			hdr = hdulist[0].header
		except:
			return -1
	except:
		return -1

	hdulist.close()
		
	instru_try = np.unique(_INSTRUME.values())
	
	INSTRUMENT = None
	
	for i in instru_try:
		Success = True
		try:
			INSTRUMENT = hdr[i]
		except KeyError:
			Success = False
			pass
		if Success:
			break
	if INSTRUMENT == None:
		os.utime(filename,None)
		return -1
	
	TRANSLATE_CID = INSTRUMENT_TRANSLATE[INSTRUMENT]
	PARTICULAR_DB = INSTRUMENT_TV[INSTRUMENT]
	
	#
	# Get all info on file header (error free)
	#
	for key in hdr.keys():
		if key != 'FILENAME':
			try:
				if str(hdr[key]).find('.core.Undef') > 0:
					hdr_out[key] = 0
				else:
					hdr_out[key] = hdr[key]
			except:
				hdr_out[key] = -1

	#
	# Build info for TableViewDatabase (tvDB)
	#
	for key in tvDB.keys():
		hdr_inst[key] = ''
	
	for key in TRANSLATE_CID.keys():
		if key != 'FILENAME':
		
			try:
				if str(hdr[TRANSLATE_CID[key]]).find('.core.Undef') > 0:
					hdr_inst[key] = 0
				else:
					hdr_inst[key] = hdr[TRANSLATE_CID[key]]
			except KeyError,ValueError:
				print '--> Exception on CID:',sys.exc_info()[1],key
				hdr_inst[key] = '0'


	for key in PARTICULAR_DB.keys():
		if key != 'FILENAME' or key != 'PATH':
			try:
				if type(PARTICULAR_DB[key]) == type('aa'):
					hdr_inst[key] = hdr[PARTICULAR_DB[key]]
				if type(PARTICULAR_DB[key]) == type(['aa']):
					for itr_info in range(len(PARTICULAR_DB[key])):
						hdr_inst[key] += hdr[PARTICULAR_DB[key][itr_info]]
				if type(PARTICULAR_DB[key]) == type(GOODMAN_RDMODE):
					hdr_inst[key] = PARTICULAR_DB[key](hdr)
			except:
				print '--> Exception',sys.exc_info()[1]
				hdr_inst[key] = ''
				pass
			
	hdr_out['FILENAME'] = filename
	hdr_inst['OBSNOTES'] = ''
	hdr_inst['FILENAME'] = os.path.basename(filename)
	hdr_inst['PATH'] = os.path.dirname(filename)	
	return hdr_out,hdr_inst #filename,INSTRUMENT
#
#
##################################################################################################################################

##################################################################################################################################
#
#

def frameLog(dbEntry):
	
	temp = '''
		{time}LT File:\t{FILENAME}
		\tOBJECT: {OBJECT} 
		\tNotes: {OBSNOTES}
		\tX={AIRMASS} Exptime:{EXPTIME} s sm= {SEEING}
		'''

	#
	# If frame is SPARTAN only keep up if this is d3
	#
	#	if dbEntry.INSTRUME == SPARTAN:
		
	
	
	if dbEntry.INSTRUME in dictTableHeaders.keys():
		print dbEntry.INSTRUME
		return '\n'
	
	else:
		print 'Instrument {} not recognized'.format(dbEntry.INSTRUME)
		return '\n'

	
