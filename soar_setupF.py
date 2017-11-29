import pyfits

GOODMAN = 'GOODMAN'
OSIRIS = 'OSIRIS'
SOI = 'SOI'


class SoarSetup():
    # def __init__(self):

    SetupOPT = {GOODMAN: 'INSTRUME',
                OSIRIS: 'INSTRUME',
                }

    GDMN_HDR = {'Instrument': 'INSTRUME',
                'OBJECT': 'OBJECT',
                'OBSTIME': 'UT',
                'AIRMASS': 'AIRMASS',
                'EXPTIME': 'EXPTIME',
                'Seeing': None,
                }

    OSRS_HDR = {'Instrument': 'INSTRUME',
                'OBJECT': 'OBJECT',
                'OBSTIME': 'TIME-OBS',
                'AIRMASS': 'SECZ',
                'EXPTIME': 'EXPTIME',
                'Seeing': None,
                }

    def GetHeaderKeys(self, imhdr):

        # for hdr in self.SetupOPT.keys():

        Val = imhdr['INSTRUME']
        return self.HeaderKeys(Val)

    def HeaderKeys(self, opt):

        if opt == GOODMAN:

            return self.GDMN_HDR

        elif opt == OSIRIS:

            return self.OSRS_HDR
