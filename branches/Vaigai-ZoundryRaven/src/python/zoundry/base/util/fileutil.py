from zoundry.base.util.streamutil import ZStreamWrapper
from shutil import Error
from zoundry.base.util.guid import generate
from zoundry.base.exceptions import ZException
from zoundry.base.messages import _extstr
from zoundry.base.util.dateutil import getDateTimeFromEpoch
from zoundry.base.util.schematypes import ZSchemaDateTime
import codecs
import os
import shutil
import stat
import threading

def true(path): #@UnusedVariable
    return True
# end true()

FILES_ONLY_FILTER = os.path.isfile
DIRECTORIES_ONLY_FILTER = os.path.isdir
EVERYTHING_FILTER = true

# -------------------------------------------------------------------------------
# Returns a listing of all the files/directories in the given directory.  This function
# returns a list of absolute paths to the contents of the directory.  An optional filter
# function can be supplied.  The filter function must take a single argument, which is
# the full path of a file/directory.  By default, the FILES_ONLY filter is applied.  To
# return all items, set the filter function to None.
# -------------------------------------------------------------------------------
def getDirectoryListing(directory, filterFunction = FILES_ONLY_FILTER, recurse = False):
    u"""getDirectoryListing(string, function, boolean) -> string []
    Gets a listing of all files and directories in the directory
    specified that match the specified filter.""" #$NON-NLS-1$

    rval = []
    subdirs = []
    if os.path.isdir(directory):
        names = os.listdir(directory)
        if names:
            for name in names:
                fullPath = os.path.join(directory, name)
                if filterFunction and filterFunction(fullPath):
                    rval.append(fullPath)
                if os.path.isdir(fullPath):
                    subdirs.append(fullPath)
    if recurse:
        for subdir in subdirs:
            rval = rval + getDirectoryListing(subdir, filterFunction, True)
    return rval
# end getDirectoryListing()


# -------------------------------------------------------------------------------
# Walks up the directory structure until it finds an existing directory.  Returns the
# first existing directory it finds.  This function will return the path unchanged
# if it is already an existing directory.
# -------------------------------------------------------------------------------
def findExistingParentDirectory(directory):
    path = directory
    while not os.path.isdir(path):
        path = os.path.dirname(path)
    return path
# end findExistingParentDirectory()


# -------------------------------------------------------------------------------
# Returns True if the directory is writable.
# -------------------------------------------------------------------------------
def isDirectoryWritable(directory):
    testFile = os.path.join(directory, u"_test_file._test") #$NON-NLS-1$
    try:
        try:
            f = open(testFile, u"w") #$NON-NLS-1$
            f.write(u"test data") #$NON-NLS-1$
            f.close()
        except:
            return False
    finally:
        try:
            deleteFile(testFile)
        except:
            return False
    return True
# end isDirectoryWritable()


# -------------------------------------------------------------------------------
# Copies all files from the source directory into the destination directory.
# -------------------------------------------------------------------------------
def copyFiles(sourceDirectory, destinationDirectory, alsoCopyDirectories = False):
    names = os.listdir(sourceDirectory)
    for srcFileName in names:
        srcFullPath = os.path.join(sourceDirectory, srcFileName)
        destFullPath = os.path.join(destinationDirectory, srcFileName)
        if os.path.isfile(srcFullPath):
            shutil.copy2(srcFullPath, destFullPath)
        if os.path.isdir(srcFullPath):
            os.mkdir(destFullPath)
            copyFiles(srcFullPath, destFullPath, alsoCopyDirectories)
# end copyFiles

# -------------------------------------------------------------------------------
# Copies a single file source path to destination path
# with optional IZStreamWrapperListener
# -------------------------------------------------------------------------------
def copyFile(sourcePath, destinationPath, zstreamWrapperListener = None):
    if not os.path.isfile(sourcePath):
        return    
    if not zstreamWrapperListener:
        shutil.copy2(sourcePath, destinationPath)
    else:
        #
        # equivalent code of shutil.copy2() except uses ZStreamWrapper
        #        
        if os.path.isdir(destinationPath):
            destinationPath = os.path.join(destinationPath, os.path.basename(sourcePath))
                
        if shutil._samefile(sourcePath, destinationPath):
            raise Error, u"`%s` and `%s` are the same file" % (sourcePath, destinationPath) #$NON-NLS-1$
        srcwrapper = None
        fdst = None
        try:
            fsrc = open(sourcePath, u'rb') #$NON-NLS-1$
            srcwrapper = ZStreamWrapper(fsrc, zstreamWrapperListener)
            fdst = open(destinationPath, u'wb') #$NON-NLS-1$
            shutil.copyfileobj(srcwrapper, fdst)
        finally:
            if fdst:
                fdst.close()
            if srcwrapper:
                srcwrapper.close()
        shutil.copystat(sourcePath, destinationPath)
# end copyFile


# -------------------------------------------------------------------------------
# Deletes a single file.  Throws an exception if it fails, otherwise returns nothing.
# -------------------------------------------------------------------------------
def deleteFile(path):
    # If the path does not exist, just return.
    if not os.path.exists(path):
        return

    # If the path exists but is not a file, that's an error.
    if not os.path.isfile(path):
        raise ZException(_extstr(u"fileutil.InvalidFilePath") % path) #$NON-NLS-1$

    os.remove(path)
# end deleteFile()


# -------------------------------------------------------------------------------
# Deletes all files in a given directory and (optionally) the directory itself.  This
# function returns the number of files deleted.
# -------------------------------------------------------------------------------
def deleteDirectory(path, alsoDeleteDir = True, deleteFilter = EVERYTHING_FILTER):
    u"""deleteDirectory(string, boolean?) -> None
    Recursively deletes the contents of the given directory.  If the
    alsoDeleteDir boolean flag is True, then the directory itself
    is also deleted.  If it is False, then only the contents of the
    directory are deleted.""" #$NON-NLS-1$

    # If the path doesn't exist, just return 0.
    if not os.path.exists(path):
        return 0

    # Throw if the root path is given as the param!
    if path == u"/" or path.endswith(u":/") or path.endswith(u":\\"): #$NON-NLS-3$ #$NON-NLS-2$ #$NON-NLS-1$
        raise ZException(_extstr(u"fileutil.FailedToDeleteRootPathMsg")) #$NON-NLS-1$

    # If the path exists, but is not a directory, that's an error.
    if not os.path.isdir(path):
        raise ZException(_extstr(u"fileutil.InvalidDirPath") % path) #$NON-NLS-1$

    try:
        count = 0
        files = os.listdir(path)
        for file in files:
            fullFile = os.path.join(path, file)
            if os.path.isfile(fullFile):
                if deleteFilter(fullFile):
                    deleteFile(fullFile)
                    count = count + 1
            else:
                shouldDeleteDir = deleteFilter(fullFile)
                count = count + deleteDirectory(fullFile, shouldDeleteDir, deleteFilter)

        if alsoDeleteDir:
            os.rmdir(path)
        return count
    except Exception, e:
        raise ZException(_extstr(u"fileutil.DirDeleteFailed") % path, e) #$NON-NLS-1$
# end deleteDirectory()


# -------------------------------------------------------------------------------
# Given a path to a file, returns some meta information about the file, as a tuple of the
# following format:
#
#   (shortFileName, absolutePath, fileSize, timeStamp)
# -------------------------------------------------------------------------------
def getFileMetaData(fileName):
    u"""getFileMetaData(string) -> (string, string, int, ZSchemaDateTime)
    Called to get meta information about a file.  Pass in the file
    name and get back a tuple of information:  (shortFileName, abs
    file name, file size, timestamp).""" #$NON-NLS-1$

    if not os.path.isfile(fileName):
        raise ZException(_extstr(u"fileutil.NotAValidFileError") % fileName) #$NON-NLS-1$
    shortName = os.path.basename(fileName)
    absPath = os.path.abspath(fileName)
    status = os.lstat(absPath)
    size = status[stat.ST_SIZE]
    modEpoch = status[stat.ST_MTIME]
    modifiedTimeDT = getDateTimeFromEpoch(modEpoch)
    return (shortName, absPath, size, ZSchemaDateTime(modifiedTimeDT))
# end getFileMetaData()

# ----------------------------------------------------------------------------------------
# Returns file extension if it exists, if not, returns None
# ----------------------------------------------------------------------------------------
def getFileExtension(fileName):
    if fileName:
        ext = os.path.splitext(fileName)[1]
        if ext:
            ext = ext[1:]
            return ext
    return None
# end getFileExtension()

# ------------------------------------------------------------------------------
# Checks to see if the given file exists, if not, raises exception.
# ------------------------------------------------------------------------------
def checkFile(fileName):
    if not os.path.isfile(fileName):
        raise ZException(_extstr(u"fileutil.InvalidFilePath") % fileName) #$NON-NLS-1$
# end checkFile()


# ------------------------------------------------------------------------------
# Checks to see if the given dir exists, if not, raises exception.
# ------------------------------------------------------------------------------
def checkDirectory(dirPath):
    if not os.path.isdir(dirPath):
        raise ZException(_extstr(u"fileutil.InvalidDirPath") % dirPath) #$NON-NLS-1$
# end checkDirectory()


def splitall(path):
    u"""Split a path into all of its parts.
    From: Python Cookbook, Credit: Trent Mick""" #$NON-NLS-1$
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
# end splitall()


# ------------------------------------------------------------------------------
# Creates a relative path.
# ------------------------------------------------------------------------------
def makeRelativePath(fromdir, tofile):
    u"""Find relative path from 'fromdir' to 'tofile'.
    An absolute path is returned if 'fromdir' and 'tofile'
    are on different drives. Martin Bless, 2004-03-22.""" #$NON-NLS-1$

    f1name = os.path.abspath(tofile)
    if os.path.splitdrive(f1name)[0]:
        hasdrive = True
    else:
        hasdrive = False
    f1basename = os.path.basename(tofile)
    f1dirname = os.path.dirname(f1name)
    f2dirname = os.path.abspath(fromdir)
    f1parts = splitall(f1dirname)
    f2parts = splitall(f2dirname)
    if hasdrive and (f1parts[0].lower() <> f2parts[0].lower()):
        # Return absolute path since we are on different drives.
        return f1name #$NON-NLS-1$
    while f1parts and f2parts:
        if hasdrive:
            if f1parts[0].lower() <> f2parts[0].lower():
                break
        else:
            if f1parts[0] <> f2parts[0]:
                break
        del f1parts[0]
        del f2parts[0]
    result = [u'..' for part in f2parts] #$NON-NLS-1$ @UnusedVariable
    result.extend(f1parts)
    result.append(f1basename)
    return os.sep.join(result)
# end makeRelativePath()


# ------------------------------------------------------------------------------
# Resolves a relative path.
# ------------------------------------------------------------------------------
def resolveRelativePath(fromdir, tofile):
    if os.path.isabs(tofile):
        return tofile
    path = os.path.join(fromdir, tofile)
    path = os.path.abspath(path)
    return path
# end resolvePath()


# ------------------------------------------------------------------------------
# Reads a file and returns its contents.
# ------------------------------------------------------------------------------
def getFileContents(filePath):
    fIn = codecs.open(filePath, u"r", u"utf-8") #$NON-NLS-2$ #$NON-NLS-1$
    try:
        return fIn.read()
    finally:
        fIn.close()
# end getFileContents()


# ------------------------------------------------------------------------------
# Renames the given file.
# ------------------------------------------------------------------------------
def renameFile(fromFile, toFile):
    shutil.move(fromFile, toFile)
# end renameFile()

# ------------------------------------------------------------------------------
# Returns true if path1 and path2 are located in the same
# drive or device.
# ------------------------------------------------------------------------------
def isSameDrive(path1, path2):
    if path1 and path2:
        try:
            stat1 = os.stat(path1)
            stat2 = os.stat(path2)
            return stat1[stat.ST_DEV] == stat2[stat.ST_DEV]
        except:
            pass
    return False
# end isSameDrive()

filename_count = 1
filename_lock = threading.RLock()

# ------------------------------------------------------------------------------
# Generates a unique filename.
# ------------------------------------------------------------------------------
def generateFilename(prefix, suffix):
    global filename_lock, filename_count
    num = 0
    try:
        filename_lock.acquire()
        num = filename_count
        filename_count = filename_count + 1 
    finally:
        filename_lock.release()
    if not prefix:
        prefix = u"zraven" #$NON-NLS-1$
    if not suffix:
        suffix = u".bin" #$NON-NLS-1$
    h = hash( generate() ) 
    hx = u"" #$NON-NLS-1$
    if h >= 0:
        hx = u"p%x" % h #$NON-NLS-1$
    else:    
        hx = u"n%x" % -h #$NON-NLS-1$
    name =  u"%s_%03d%s%s" % (prefix, num, hx, suffix) #$NON-NLS-1$
    return name
# end generateFilename()
