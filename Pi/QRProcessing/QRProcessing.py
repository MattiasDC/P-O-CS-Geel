from base64 import b64decode
from base64 import b64encode
import qrcode
import zbar
import rsa

class QRProcessing(object):
    _public = None                  # Public key
    _private = rsa.PrivateKey(148891693498983048340684619534280726114560285106633675357529441992124307524775391171067890402345079318268577183206753619577909598265619024402097714459434586646717682022429184894358872433191942168805427544264054017340474208878286033676498007829631050869601288737752461936711335062550336605428357062839523325469, 65537, 72924828259210169349949427078305034218094673110423643824119772929874698982830542765157212170604005386836490211693449264306137299460275951970382116500414363637286365676955274486590818690649390722927881633372134159448812208426752275977111869224920183753938617991477120336527394308581430103064012380446933452353, 55059214762051034432258478190210231975954242526048671655782227117624013589345193582833588936443734646901279463842804889046115340058701622378864394709408895282827281, 2704210260579397699789672830562685733548811927626455742282804798408327320417224564694694910952668044074549213394782015805192215734965781036732749)                    # Private key
    _bits = 512                         # Key encryption size

    _error_correction_code = 'L'        # QR error code

    def __init__(self):
        pass
        #self._public, self._private = rsa.newkeys(self._bits)

    def get_public_key(self):
        return self._public

    def get_public_key_pem(self):
        return self._public.save_pkcs1(format='PEM')

    def decrypt(self, message):
        if message is None:
            return None
        try:
            return rsa.decrypt(message, self._private)
        except Exception:
            return None

    def _decode_pil(self, pil):
        scanner = zbar.ImageScanner()
        scanner.parse_config('enable')

        pil = pil.convert(self._error_correction_code)
        width, height = pil.size
        # wrap image data
        image = zbar.Image(width, height, 'Y800', pil.tostring())
        # scan the image for barcodes
        result = scanner.scan(image)

        _last_qr = None
        if result == 0:
            print "No QR codes found"
        else:
            for symbol in image:
                # Zbar scans the image from bottom to top -> all qr codes are found if they can be read BUT when
                # multiple QR codes on a picture it is less accurate (doesn't find hard to read QR codes)
                _last_qr = symbol.data
                print 'test1'
                print _last_qr
                print 'test2'

        # cleanup
        del image
        return _last_qr

    def decrypt_pil(self, pil):
        qr_string = self._decode_pil(pil)
        print 'test3'
        print qr_string
        print 'test4'
        if not qr_string is None:
            return self.decrypt(b64decode(qr_string))
        return None
