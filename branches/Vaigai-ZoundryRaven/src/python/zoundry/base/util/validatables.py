
#------------------------------------------------------------------------
# This module contains a set of general purpose interfaces
# to allow object (contents) to be validated and report errors or warnings.
#-------------------------------------------------------------------------

#-------------------------------------------------------------------------
# Defines an inferface this is responsible for validating its contents 
# and or  config data such as publish settings.
#-------------------------------------------------------------------------
class IZConfigValidatable:
    
    def validateConfiguration(self, validationReporter): #@UnusedVariable
        u"""validateConfiguration(IZConfigValidationReporter) -> void
        """ #$NON-NLS-1$
        pass
    # end validateConfiguration()
# end IZConfigurationValidatable


#-------------------------------------------------------------------------
# Validation reporter
#-------------------------------------------------------------------------
class IZConfigValidationReporter:

    def addInfo(self, category, message): #@UnusedVariable
        pass
    # end addInfo()

    def addWarning(self, category, message): #@UnusedVariable
        pass
    #end addWarning()
        
    def addError(self, category, message): #@UnusedVariable
        pass
    # end addError()
    
    def listReports(self):
        return []
    # end getInfoReportList()
    
    def hasWarnings(self):
        return False
    # end hasWarnings() 
        
    def hasErrors(self):
        return False
    # end hasErrors()    
# end IZConfigValidationReporter

#-------------------------------------------------------------------------
# Report entry
#-------------------------------------------------------------------------
class ZValidationReportEntry:
    # entry types
    INFO = 0
    WARNING = 1
    ERROR = 2
    
    def __init__(self, entryType,  category, message):
        self.entryType = entryType
        self.category = category
        self.message = message
    # end __init__()
    
    def getType(self):
        return self.entryType
    # end getType()
    
    def getCategory(self):
        return self.category
    # end getCategory()
    
    def getMessage(self):
        return self.message
    # end getMessage()
# end ZValidationReportEntry

#-------------------------------------------------------------------------
# Validation reporter implementation
#-------------------------------------------------------------------------
class ZConfigValidationReporter(IZConfigValidationReporter):

    def __init__(self):
        self.reportList = []
        self.errorCount = 0
        self.warningCount = 0
    # end __init__()
    
    def _add(self, entryType,  category, message):
        self.reportList.append( ZValidationReportEntry(entryType,  category, message) )
    # end _add
    
    def listReports(self):
        return self.reportList
    # end getInfoReportList()
    
    def hasWarnings(self):
        return self.warningCount > 0
    # end hasWarnings()    
    
    def hasErrors(self):
        return self.errorCount > 0
    # end hasErrors()
        
    def addInfo(self, category, message):
        self._add(ZValidationReportEntry.INFO, category, message)
    # end addInfo()
    
    def addWarning(self, category, message):
        self.warningCount = self.warningCount + 1
        self._add(ZValidationReportEntry.WARNING, category, message)
    #end addWarning()
    
    def addError(self, category, message):
        self.errorCount = self.errorCount + 1
        self._add(ZValidationReportEntry.ERROR, category, message)
    # end addError()
        
# end ZConfigValidationReporter


