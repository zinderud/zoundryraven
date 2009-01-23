# Conversions to/from base64 transport encoding as per RFC-1521
# Modified 04-Oct-95 by Jack to use binascii module

import binascii

__all__ = [u"encode",u"decode",u"encodestring",u"decodestring"]

MAXLINESIZE = 76 # Excluding the CRLF
MAXBINSIZE = (MAXLINESIZE//4)*3
BUFSIZE = 4096

class BufferedReaderFile:
    def __init__(self, aFile):
        self.bSize = BUFSIZE
        self.mFile = aFile
        self.data = None
        self.idx = 0
        
    def read(self, sz):
        if not self.data:
            self.data = self.mFile.read(self.bSize)
            self.idx = 0
        if not self.data:
            return [] 
        rem = len(self.data) -  self.idx
        if rem < sz:
            d = self.mFile.read(self.bSize)            
            self.data = self.data[self.idx : len(self.data)] + d
            self.idx = 0
            rem = len(self.data)
        if rem < sz:
            return self.data[self.idx : len(self.data)]
        else:
            st = self.idx
            self.idx = self.idx + sz
            return self.data[st : self.idx]
                
def encode(aInput, output):
    u"""Encode a file.""" #$NON-NLS-1$
    input = BufferedReaderFile(aInput)
    while 1:
        s = input.read(MAXBINSIZE)   
        if not s: break        
        while len(s) < MAXBINSIZE:
            ns = input.read(MAXBINSIZE-len(s))
            if not ns: break
            s = s + ns
        line = binascii.b2a_base64(s)
        output.write(line)
        

def decode(input, output):
    u"""Decode a file."""  #$NON-NLS-1$
    while 1:
        line = input.readline()
        if not line: break
        s = binascii.a2b_base64(line)
        output.write(s)

def encodestring(s):
    u"""Encode a string."""  #$NON-NLS-1$
    pieces = []
    for i in range(0, len(s), MAXBINSIZE):
        chunk = s[i : i + MAXBINSIZE]
        pieces.append(binascii.b2a_base64(chunk))
    return "".join(pieces)

def decodestring(s):
    u"""Decode a string."""  #$NON-NLS-1$
    return binascii.a2b_base64(s)
