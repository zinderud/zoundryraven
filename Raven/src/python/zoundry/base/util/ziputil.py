from zoundry.base.util.text.unicodeutil import convertToUnicode
import os
import zipfile


def _decodeZipFilename(filename):
    return convertToUnicode(filename, u"cp437") #$NON-NLS-1$
# end _decodeZipFilename()


# -------------------------------------------------------------------------------------
# Unpacks a zip to a given directory.  This method throws an exception if an error is 
# detected (but it DOES clean up the file handle(s) in that case).
#
# FIXME don't read the entire file into memory and then write it out - use a buffer
# -------------------------------------------------------------------------------------
def unpackZip(zipFileName, outputDirPath):
    u"""unpackZip(string, string) -> None
    Unpacks the given zip file into the given directory.  This method
    throws an exception if an error occurs.""" #$NON-NLS-1$

    zfile = zipfile.ZipFile(zipFileName)
    try:
        for info in zfile.infolist():
            decodedFilename = _decodeZipFilename(info.filename)
            ofilename = os.path.join(outputDirPath, decodedFilename)
            if ofilename.endswith(u'/'): #$NON-NLS-1$
                if not os.path.exists(ofilename):
                    os.makedirs(ofilename)
            else:
                parentDir = os.path.dirname(ofilename)
                if not os.path.exists(parentDir):
                    os.makedirs(parentDir)
                ofile = file(ofilename, u"wb") #$NON-NLS-1$
                try:
                    data = zfile.read(info.filename)
                    ofile.write(data)
                finally:
                    ofile.close()
    finally:
        zfile.close()
# end unpackZip()
