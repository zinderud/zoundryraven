from zoundry.base.util.text.unicodeutil import convertToUnicode
from Crypto.Hash import MD5
from Crypto.Cipher import Blowfish
import base64

# -------------------------------------------------------------------------------------
# Python has no itoa function - so create our own.  This function is used to convert the 
# signature to as small a string as is conveniently possible (by passing a radix of 36).
# -------------------------------------------------------------------------------------
ITOA = lambda i, radix = 10, c = (lambda i, radix, c: i and (c(i/radix, radix, c) + (i % radix < 10 and str(i % radix) or chr(i % radix - 10 + ord(u'A')))) or u''): c(i, radix, c) #$NON-NLS-2$ #$NON-NLS-1$


# -------------------------------------------------------------------------------------
# Encrypts some plain text with the given key.  The return value will be the cipher
# text, base64 encoded.
# -------------------------------------------------------------------------------------
def encryptPlainText(plaintext, key):
    obj = Blowfish.new(key, Blowfish.MODE_ECB)
    ciphertext = obj.encrypt(plaintext.ljust(((len(plaintext) / 8) + 1) * 8))
    return base64.encodestring(ciphertext).rstrip()
# end encryptPlainText()


# -------------------------------------------------------------------------------------
# Decrypts ciphertext that was created using the encryptPlainText() method.  Returns
# the plaintext.
# -------------------------------------------------------------------------------------
def decryptCipherText(ciphertext, key):
    obj = Blowfish.new(key, Blowfish.MODE_ECB)
    return convertToUnicode(obj.decrypt(base64.decodestring(ciphertext))).rstrip()
# end decryptCipherText()


# -------------------------------------------------------------------------------------
# This function takes a string password and returns the MD5 hash digest for it, base64
# encoded.
# -------------------------------------------------------------------------------------
def getPasswordDigest(password):
    if password:
        return base64.encodestring(MD5.new(password).digest()).strip()
# end getPasswordDigest()

