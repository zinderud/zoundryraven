from zoundry.appframework.constants import IZAppServiceIDs
from zoundry.appframework.global_services import getApplicationModel
from zoundry.appframework.ui.widgets.dialogs.standarddialogs import ZShowInfoMessage
from zoundry.appframework.services.validation.xhtmlvalidation import IZXhtmlSchemaVersion

# ------------------------------------------------------------------------------------
# Html schema related methods
# ------------------------------------------------------------------------------------
class ZXhtmlSchemaUiUtil:
    # Supported (subset) tags for the UI
    INLINE_TAGS = [u'span', u'tt', u'i', u'b', u'big', u'small', u'em', u'strong', u'code', u'q', u'samp', u'kbd', u'cite', u'abbr', u'acronym', u'sub', u'sup', u'ins', u'del'] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$ #$NON-NLS-9$ #$NON-NLS-10$ #$NON-NLS-11$ #$NON-NLS-12$ #$NON-NLS-13$ #$NON-NLS-14$ #$NON-NLS-15$ #$NON-NLS-16$ #$NON-NLS-17$ #$NON-NLS-18$ #$NON-NLS-19$
    BLOCK_TAGS = [u'p', u'div', u'h1', u'h2', u'h3', u'h4', u'h5', u'h6', u'ul', u'ol', u'dl', u'pre', u'hr', u'blockquote', u'address'] #$NON-NLS-1$ #$NON-NLS-2$ #$NON-NLS-3$ #$NON-NLS-4$ #$NON-NLS-5$ #$NON-NLS-6$ #$NON-NLS-7$ #$NON-NLS-8$ #$NON-NLS-9$ #$NON-NLS-10$ #$NON-NLS-11$ #$NON-NLS-12$ #$NON-NLS-13$ #$NON-NLS-14$ #$NON-NLS-15$ #$NON-NLS-16$ #$NON-NLS-17$ #$NON-NLS-18$ #$NON-NLS-19$   
    
    def getValidationService(self):
        valService = getApplicationModel().getEngine().getService(IZAppServiceIDs.XHTML_VALIDATION_SERVICE_ID)
        return valService
    # end getValidationService()
    
    def _showMessages(self, parentWindow, messageList):
        if parentWindow:
            s = u"Number of messages: %d\n" % len(messageList) #$NON-NLS-1$
            for m in messageList:
                s = s + u"%s\n" % unicode(m) #$NON-NLS-1$
            ZShowInfoMessage(parentWindow,s, u"Validation")   #$NON-NLS-1$    
    # end _showMessages()

    def validateHtmlBody(self, parentWindow, htmlBody, izXhtmlValidationListener = None):
        validator = self.getValidationService().getValidator(IZXhtmlSchemaVersion.XHTML_1_STRICT)
        msgs = validator.validateHtmlBody(htmlBody, izXhtmlValidationListener)
        self._showMessages(parentWindow, msgs)
        return msgs
    # end validateHtmlBody
    
    def getChildElementNames(self, parentElementName):
        schema = self.getValidationService().getSchema(IZXhtmlSchemaVersion.XHTML_1_STRICT)
        rval = []
        # return filtered/limited set for the ui (i.e. common elem names)
        for n in schema.getElementChildren(parentElementName):
            if n in ZXhtmlSchemaUiUtil.INLINE_TAGS or n in ZXhtmlSchemaUiUtil.BLOCK_TAGS:
                rval.append(n)
        rval.sort()
        return rval
    # end getChildElementNames
    
    def tidyHtmlBody(self, parentWindow, htmlBody, izXhtmlValidationListener=None):
        (success, htmlResult, messageList) = self.getValidationService().tidyHtmlBody(htmlBody, izXhtmlValidationListener)
        self._showMessages(parentWindow, messageList)
        return (success, htmlResult, messageList)
    # end tidyHtmlBody
# end ZXhtmlSchemaUIUtil