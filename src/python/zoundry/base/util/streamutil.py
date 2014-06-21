
# ----------------------------------------------------------------------------------------------
# This interface must be implemented by classes that wish to listen in on events fired by the
# ZStreamWrapper class.
# ----------------------------------------------------------------------------------------------
class IZStreamWrapperListener:

    def streamRead(self, blockSize, data):
        u"Called when the stream is read from." #$NON-NLS-1$
    # end streamRead()

    def streamWrite(self, blockSize, data):
        u"Called when the stream is written to." #$NON-NLS-1$
    # end streamWrite()

# end IZStreamWrapperListener


# ----------------------------------------------------------------------------------------------
# This class is a wrapper around a python stream (typically a file stream).  The wrapper
# simply delegates the i/o calls (read, write) to a delegate stream.  It provides a callback
# mechanism each time a read or write is done.  This is primarily useful for creating progress
# meters and such, as it may be the only way to know how quickly a 3rd party library is
# reading from or writing to a stream.
# ----------------------------------------------------------------------------------------------
class ZStreamWrapper:

    def __init__(self, stream, listener = None):
        self.stream = stream
        self.listener = listener
    # end __init__()

    def read(self, blocksize = -1):
        rval = self.stream.read(blocksize)
        if rval:
            self._readBlock(len(rval), rval)
        return rval
    # end read()

    def readline(self, size = -1):
        rval = self.stream.readline(size)
        if rval:
            self._readBlock(len(rval), rval)
        return rval
    # end readline()

    def readlines(self, sizehint = -1):
        rval = self.stream.readlines(sizehint)
        if rval:
            size = 0
            for line in rval:
                size = size + len(line)
            self._readBlock(size, rval)
        return rval
    # end readlines()

    def write(self, data):
        self.stream.write(data)
        self._writeBlock(len(data), data)
    # end write()

    def writelines(self, lines):
        self.stream.writelines(lines)
        size = 0
        for line in lines:
            size = size + len(line)
        self.writeBlock(size, lines)
    # end writelines()

    def close(self):
        self.stream.close()
    # end close()

    def flush(self):
        self.stream.flush()
    # end flush()

    def fileno(self):
        return self.stream.fileno()
    # end fileno()

    def _readBlock(self, size, data):
        if self.listener is not None:
            self.listener.streamRead(size, data)
    # end _readBlock()

    def _writeBlock(self, size, data):
        if self.listener is not None:
            self.listener.streamWrite(size, data)
    # end _writeBlock()

    def __getattr__(self, name):
        return getattr(self.stream, name)
    #end __getattr__

# end ZStreamWrapper
