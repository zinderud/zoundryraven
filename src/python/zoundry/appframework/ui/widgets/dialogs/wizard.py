from zoundry.appframework.ui.events.commonevents import ZEVT_REFRESH
from zoundry.appframework.ui.util.uiutil import fireRefreshEvent
from zoundry.base.util.zthread import ZThread
from zoundry.base.util.zthread import IZRunnable
from zoundry.appframework.ui.widgets.controls.common.bitmap import ZStaticBitmap
from zoundry.appframework.messages import _extstr
from zoundry.appframework.resources.registry import getImageType
from zoundry.appframework.ui.events.validation import ZEVT_INVALID
from zoundry.appframework.ui.events.validation import ZEVT_VALID
from zoundry.appframework.ui.widgets.controls.validating.validatingpanel import ZValidatingPanel
from zoundry.appframework.ui.widgets.dialog import ZBaseDialog
from zoundry.base.exceptions import ZException
import os
import wx

ZID_NEXT = wx.NewId()
ZID_PREVIOUS = wx.NewId()
ZID_FINISH = ZID_NEXT



# ----------------------------------------------------------------------------
# Events wizard background tasks - event for Begin and event for End background task.
# ----------------------------------------------------------------------------
BEGIN_BG_EVENT = wx.NewEventType()
END_BG_EVENT = wx.NewEventType()

ZID_BEGIN_BG_TASK = wx.PyEventBinder(BEGIN_BG_EVENT, 1)
ZID_END_BG_TASK = wx.PyEventBinder(END_BG_EVENT, 1)

# ----------------------------------------------------------------------------
# start bg work event
# ----------------------------------------------------------------------------
class ZWizardBeginBackgroundTaskEvent(wx.PyCommandEvent):

    def __init__(self, windowID, wizardTask):
        self.eventType = BEGIN_BG_EVENT
        self.wizardTask = wizardTask
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def getTask(self):
        return self.wizardTask
    # end getTask()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

# end ZWizardBeginBackgroundTaskEvent


# ----------------------------------------------------------------------------
# end bg work event
# ----------------------------------------------------------------------------
class ZWizardEndBackgroundTaskEvent(wx.PyCommandEvent):

    def __init__(self, windowID, taskSuccessful):
        self.eventType = END_BG_EVENT
        self.taskSuccessful = taskSuccessful
        wx.PyCommandEvent.__init__(self, self.eventType, windowID)
    # end __init__()

    def isSuccessful(self):
        return self.taskSuccessful
    # end isSuccessful()

    def Clone(self):
        return self.__class__(self.GetId())
    # end Clone()

#end ZWizardEndBackgroundTaskEvent


#----------------------------------------------------
# Background task base class.
#----------------------------------------------------
class ZWizardBackroundTask(IZRunnable):

    def __init__(self, page, session):
        self.canceled = False
        self._page = page
        self._session = session
    # end __init__()

    def getPage(self):
        return self._page
    # end getPage()

    def getSession(self):
        return self._session
    # end getSession()

    def isCanceled(self):
        return self.canceled
    # end isCanceled()

    def refreshPage(self, eventType, eventData = None):
        if not self.isCanceled():
            self.getPage()._fireRefreshEvent(eventType, eventData)
    # end refreshPage()

    def cancel(self):
        self.canceled = True
    # end cancel()

    def run(self):
        success = False
        try:
            success = self._runTask()
        except Exception, e:
            zex = ZException(rootCause = e) #$NON-NLS-1$
            zex.printStackTrace()
        if not self.isCanceled():
            self.getPage()._fireEndBackgroundTaskEvent(success)
    # end run()

    def _runTask(self):
        u"Called by the thread to run background task. Must return true on success" #$NON-NLS-1$
        return True
    # end _runTask()

# end ZWizardBackgroundTask


# ---------------------------------------------------------------------------------------
# An interface that defines the type of object responsible for aggregating the results
# of a Wizard interaction.  The session object saves the values that the user enters
# into each of the wizard pages as the wizard progress through (and back) those pages.
# ---------------------------------------------------------------------------------------
class IZWizardSession:

    def onNext(self, currentPage, nextPage):
        u"Called by the wizard when the user clicks on the 'Next' button." #$NON-NLS-1$
    # end onNext()

    def onPrevious(self, currentPage, previousPage):
        u"Called by the wizard when the user clicks on the 'Previous' button." #$NON-NLS-1$
    # end onPrevious()

    def onFinish(self, allPages):
        u"Called by the wizard when the user clicks on the 'Finish' button." #$NON-NLS-1$
    # end onFinish()

# end IZWizardSession


# ------------------------------------------------------------------------------------------
# Base class for simple wizard session which is based on aggregating
# data from wizard pages and storing it in a map.
# ------------------------------------------------------------------------------------------
class ZAbstractPropertyWizardSession(IZWizardSession):

    def __init__(self):
        self.properties = {}
    # end __init__()

    def onNext(self, currentPage, nextPage): #@UnusedVariable
        self._aggregatePageData(currentPage)
    # end onNext()

    def onFinish(self, allPages):
        for page in allPages:
            self._aggregatePageData(page)
    # end onFinish()

    def getProperty(self, propertyName):
        if propertyName in self.properties:
            return self.properties[propertyName]
        return None
    # end getProperty()

    def setProperty(self, propertyName, propertyValue):
        u"""Sets the property value.""" #$NON-NLS-1$
        if propertyName:
            self.properties[propertyName] = propertyValue

    def _aggregatePageData(self, page):
        props = self._getPageProperties(page)
        if props:
            for key in props:
                self.properties[key] = props[key]
    # end _aggregatePageData()

    def _getPageProperties(self, page): #@UnusedVariable
        u"""Subclasses must implement this to return a dictionary of page session data.""" #$NON-NLS-1$
        if page and isinstance(page, ZAbstractPropertyBasedWizardPage):
            return page.getDataProperties()
        else:
            rval = {}
            return rval
    # end _getPageProperties()

# end ZAbstractPropertyWizardSession


# ---------------------------------------------------------------------------------------
# The base class for all wizard pages.
# ---------------------------------------------------------------------------------------
class ZWizardPage(ZValidatingPanel):
    # previous page button was press
    PREVIOUS = 0
    # next page button pressed
    NEXT     = 1

    def __init__(self, parent):
        self.wizard = parent

        ZValidatingPanel.__init__(self, parent)

        self._createWidgets()
        self._populateWidgets()
        self._bindWidgetEvents()
        self._layoutWidgets()
        self.Bind(ZEVT_REFRESH, self.onRefresh, self)
    # end __init__()

    def onRefresh(self, event):
        (type, data) = event.getData()
        self._refresh(type, data)
    # end onRefresh()

    def _refresh(self, eventType, eventData): #@UnusedVariable
        u"""Called when the page needs to be updated.""" #$NON-NLS-1$
        pass
    # end _refresh()

    def onEnter(self, session, eventDirection):
        u"""Called by the wizard when the page is entered (either when the user clicks Next or Previous.
        The eventDirection takes value of either PREVIOUS or NEXT to indicate the button user pressed.""" #$NON-NLS-1$
    # end onEnter()

    def onExit(self, session, eventDirection): #@UnusedVariable
        u"""Called by the wizard when the page is left (either when the user clicks Next or Previous.
        The eventDirection takes value of either PREVIOUS or NEXT to indicate the button user pressed
        This method must return boolean True to continue""" #$NON-NLS-1$
        return True
    # end onExit()

    def onCancel(self, session):
        u"""Called by the wizard when the Cancel button is pressed""" #$NON-NLS-1$
    # end onCancel()

    def onResize(self, event):
        u"Called by the wizard when the wizard is resized." #$NON-NLS-1$
    # end onResize()

    def getImage(self):
        raise ZException(u"Method must be implemented by subclasses.") #$NON-NLS-1$
    # end getImage()

    def _createWidgets(self):
        u"Can be overridden by subclasses." #$NON-NLS-1$
    # end _createWidgets()

    def _populateWidgets(self):
        u"Can be overridden by subclasses." #$NON-NLS-1$
    # end _populateWidgets()

    def _bindWidgetEvents(self):
        u"Can be overridden by subclasses." #$NON-NLS-1$
    # end _bindWidgetEvents()

    def _layoutWidgets(self):
        u"Can be overridden by subclasses." #$NON-NLS-1$
    # end _layoutWidgets()

    def _fireBeginBackgroundTaskEvent(self, wizardTask):
        event = ZWizardBeginBackgroundTaskEvent(self.GetId(), wizardTask)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireBeginBackgroundTaskEvent()

    def _fireEndBackgroundTaskEvent(self, successful):
        event = ZWizardEndBackgroundTaskEvent(self.GetId(), successful)
        self.GetEventHandler().AddPendingEvent(event)
    # end _fireEndBackgroundTaskEvent

    def _fireRefreshEvent(self, eventType, eventData = None):
        # wrap event type and data in tuple and fire event.
        if not eventType:
            eventType = u"_unknowntype_" #$NON-NLS-1$
        obj = (eventType, eventData)
        fireRefreshEvent(self, obj)
    # end _fireRefreshEvent()

# end ZWizardPage

#-------------------------------------------------------------------------------
# Base class for a wizard page which is required to return current ui data
# via a dictionary.
#-------------------------------------------------------------------------------
class ZAbstractPropertyBasedWizardPage(ZWizardPage):

    def __init__(self, model, parent):
        self.model = model

        ZWizardPage.__init__(self, parent)
    # end __init__()

    def _getModel(self):
        u"""Returns the data model, or None if a model is not available."""  #$NON-NLS-1$
        return self.model
    # end _getModel

    def getDataProperties(self):
        u"""Returns the page ui data as a dictionary."""  #$NON-NLS-1$
        return {}
    # end getDataProperties()

# end ZAbstractPropertyBasedWizardPage

# ---------------------------------------------------------------------------------------
# An implementation of a Zoundry Wizard.  A Wizard is a sequence of wizard pages that
# are strung together and navigable via Next, Previous, Cancel, and Finish buttons at
# the bottom of the dialog.
# ---------------------------------------------------------------------------------------
class ZWizard(ZBaseDialog):

    def __init__(self, parent, session, id, title, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, name = u"ZWizard"): #$NON-NLS-1$
        self.session = session
        self.images = []
        self.pages = []
        self.currentIdx = 0
        self.lastDirection = -1 # last know direction (WizarPage.PREVIOUS or WizardPage.NEXT) pressed
        self.bgTask = None # runnable bg task
        self.bgTaskPreviousButtonState = False
        self.bgTaskNextButtonState = False

        ZBaseDialog.__init__(self, parent, id, title, pos, size, style, name)
        self._createWizardPages()
    # end __init__()

    def getSession(self):
        return self.session
    # end getSession()

    def addPage(self, page, index = None):
        if index is None:
            self.pages.append(page)
        else:
            self.pages.insert(index, page)

        page.Show(False)
        self.wizardPagesSizer.Add(page, 1, wx.EXPAND)
        staticBitmap = self._createWizardImageControl(page.getImage())
        if staticBitmap is not None:
            staticBitmap.Show(False)
            self.imagesSizer.Add(staticBitmap, 0)
        if index is None:
            self.images.append(staticBitmap)
        else:
            self.images.insert(index, staticBitmap)

        self.Bind(ZEVT_VALID, self.onValid, page)
        self.Bind(ZEVT_INVALID, self.onInvalid, page)
        self.Bind(ZID_BEGIN_BG_TASK, self.onBeginBackroundTask, page)
        self.Bind(ZID_END_BG_TASK, self.onEndBackroundTask, page)
    # end addPage()

    def removePage(self, index):
        page = self.pages[index]
        image = self.images[index]
        self.pages.remove(page)
        self.images.remove(image)

        self.wizardPagesSizer.Remove(page)
        if image:
            self.imagesSizer.Remove(image)

        self.Unbind(ZEVT_VALID, page)
        self.Unbind(ZEVT_INVALID, page)
        self.Unbind(ZID_BEGIN_BG_TASK, page)
        self.Unbind(ZID_END_BG_TASK, page)
    # end removePage()

    def _cancelTask(self):
        # cancel task
        if self.bgTask:
            self.bgTask.cancel()
            self.bgTask = None
    # end _cancelTask()

    def onBeginBackroundTask(self, event): #@UnusedVariable
        self._cancelTask()
        # save button states
        self.bgTaskPreviousButtonState = self._isButtonEnabledById(ZID_PREVIOUS)
        self.bgTaskNextButtonState =  self._isButtonEnabledById(ZID_NEXT)
        # disable buttons
        self._enableNextButton(False)
        self._enablePreviousButton(False)

        self.bgTask = event.getTask()
#        wizardTask.run()
        thread = ZThread(self.bgTask, u"ZWizardTaskThread", True) #$NON-NLS-1$
        thread.start()
        event.Skip()
    # end onBeginBackroundTask()

    def onEndBackroundTask(self, event): #@UnusedVariable
        success = event.isSuccessful()
        # restore button states
        self._enableNextButton(self.bgTaskNextButtonState)
        self._enablePreviousButton(self.bgTaskPreviousButtonState)
        # if successful, then continue to next or previous page.
        if success:
            if self.lastDirection == ZWizardPage.NEXT:
                self._nextPage()
            elif self.lastDirection == ZWizardPage.PREVIOUS:
                self._previousPage()
        event.Skip()
    # end onEndBackroundTask()

    def onValid(self, event):
        currentPage = self._getCurrentPage()
        if currentPage.GetId() == event.GetId():
            self._enableNextButton(True)
        event.Skip()
    # end onValid()

    def onInvalid(self, event):
        currentPage = self._getCurrentPage()
        if currentPage.GetId() == event.GetId():
            self._enableNextButton(False)
        event.Skip()
    # end onInvalid()

    def onNext(self, event):
        self.lastDirection = ZWizardPage.NEXT
        if not self._isLastPage():
            currentPage = self._getCurrentPage()
            if not currentPage.onExit(self.session, ZWizardPage.NEXT):
                event.Skip()
                return
        self._nextPage()
        event.Skip()
    # end onNext()

    def _nextPage(self):
        if not self._isLastPage():
            currentPage = self._getCurrentPage()
            currentImage = self._getCurrentImage()
            self.currentIdx = self.currentIdx + 1
            nextPage = self._getCurrentPage()
            nextImage = self._getCurrentImage()
            self.session.onNext(currentPage, nextPage)
            nextPage.onEnter(self.session, ZWizardPage.NEXT)

            currentPage.Show(False)
            currentImage.Show(False)
            nextPage.Show(True)
            nextImage.Show(True)

            if self._isLastPage():
                self._setIsLastPage(True)
            if not self._isFirstPage():
                self._enablePreviousButton(True)

            self._enableNextButton(self._getCurrentPage().isValid())
            self.Layout()
        else:
            self._finish()
        self.lastDirection = -1
    # end _next()

    def onPrevious(self, event):
        self.lastDirection = ZWizardPage.PREVIOUS
        currentPage = self._getCurrentPage()
        if currentPage.onExit(self.session, ZWizardPage.PREVIOUS):
            self._previousPage()
        event.Skip()
    # end onPrevious()

    def _previousPage(self):
        currentPage = self._getCurrentPage()
        currentImage = self._getCurrentImage()
        self.currentIdx = self.currentIdx - 1
        prevPage = self._getCurrentPage()
        prevImage = self._getCurrentImage()
        self.session.onPrevious(currentPage, prevPage)
        prevPage.onEnter(self.session, ZWizardPage.PREVIOUS)

        currentPage.Show(False)
        currentImage.Show(False)
        prevPage.Show(True)
        prevImage.Show(True)

        self._setIsLastPage(True)
        if not self._isLastPage():
            self._setIsLastPage(False)
        if self._isFirstPage():
            self._enablePreviousButton(False)

        self._enableNextButton(self._getCurrentPage().isValid())
        self.Layout()
        self.lastDirection = -1
    # end onPrevious()

    def onCancel(self, event):
        self._cancelTask()
        for page in self.pages:
            page.onCancel(self.session)
        event.Skip()
    # end onCancel()

    def onFinish(self, event):
        self._finish()
        event.Skip()
    # end onFinish()

    def _finish(self):
        self._cancelTask()
        self._getCurrentPage().onExit(self.session, ZWizardPage.NEXT)
        self.session.onFinish(self.pages)
        self.EndModal(wx.ID_OK)
    # end onFinish()

    def showWizard(self):
        self.currentIdx = 0
        self._enablePreviousButton(False)
        self._hideAll()
        self._getCurrentPage().Show(True)
        self._getCurrentImage().Show(True)
        self._getCurrentPage().onEnter(self.session, ZWizardPage.NEXT)
        self.Layout()
        self.onResize(wx.SizeEvent())
        self.Layout()

        return self.ShowModal()
    # end showWizard()

    def _createWizardImageControl(self, imagePath):
        if imagePath is None:
            return None
        if not os.path.isfile(imagePath):
            return None
        image = wx.Image(imagePath, getImageType(imagePath))
        bitmap = image.ConvertToBitmap()
        zbitmap = ZStaticBitmap(self, bitmap)
        zbitmap.setBackgroundColor(wx.Color(255, 255, 255))
        return zbitmap
    # end _createWizardImageControl()

    def _createWizardPages(self):
        u"Called to create the wizard's pages (can be implemented by subclasses)." #$NON-NLS-1$
    # end _createWizardPages()

    def _createWidgets(self):
        self._createContent()
        self._createButtons()
    # end _createWidgets()

    def _createContent(self):
        self.defaultImagePath = self._getDefaultImage()
        self.defaultImage = self._createWizardImageControl(self.defaultImagePath)
        self.verticalLine = wx.StaticLine(self, style = wx.LI_VERTICAL)
    # end _createContent()

    def _getDefaultImage(self):
        u"Called to get the default image for the wizard (which will be displayed if an individual wizard page does not provide one).  Returns a path to an image." #$NON-NLS-1$
        return None
    # end _getDefaultImage()

    def _createButtons(self):
        self.prevButton = wx.Button(self, ZID_PREVIOUS, u"< " + _extstr(u"Back")) #$NON-NLS-1$ #$NON-NLS-2$
        self.nextButton = wx.Button(self, ZID_NEXT, _extstr(u"Next") + u" >") #$NON-NLS-2$ #$NON-NLS-1$
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, _extstr(u"Cancel")) #$NON-NLS-1$
    # end _createButtons()

    def _populateWidgets(self):
        pass
    # end _populateWidgets()

    def _layoutWidgets(self):
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttonSizer.Add(self.prevButton, 0)
        buttonSizer.Add(self.nextButton, 0)
        buttonSizer.Add(self.cancelButton, 0, wx.LEFT, 8)

        self.contentSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.imagesSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.wizardPagesSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.contentSizer.AddSizer(self.imagesSizer, 0, wx.EXPAND)
        self.contentSizer.Add(self.verticalLine, 0, wx.EXPAND)
        self.contentSizer.AddSizer(self.wizardPagesSizer, 1, wx.EXPAND)

        if self.defaultImage is not None:
            self.imagesSizer.Add(self.defaultImage, 1, wx.EXPAND)

        # Create the overall box sizer
        box = wx.BoxSizer(wx.VERTICAL)
        box.AddSizer(self.contentSizer, 1, wx.EXPAND)
        box.Add(wx.StaticLine(self), 0, wx.EXPAND)
        box.AddSizer(buttonSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.SetAutoLayout(True)
        self.SetSizer(box)
        self.Layout()
    # end _layoutWidgets()

    def _bindWidgetEvents(self):
        self.Bind(wx.EVT_BUTTON, self.onPrevious, self.prevButton)
        self.Bind(wx.EVT_BUTTON, self.onNext, self.nextButton)
        self.Bind(wx.EVT_BUTTON, self.onCancel, self.cancelButton)
        self.Bind(wx.EVT_SIZE, self.onResize, self)
    # end _bindWidgetEvents()

    def onResize(self, event):
        for page in self.pages:
            page.onResize(event)
        event.Skip()
    # end onResize()

    def _setInitialFocus(self):
        u"Called to set the focus on some initial widget." #$NON-NLS-1$
    # end _setInitialFocus()

    def _isLastPage(self):
        return self.currentIdx == (len(self.pages) - 1)
    # end _isLastPage()

    def _isFirstPage(self):
        return self.currentIdx == 0
    # end _isFirstPage()

    def _setIsLastPage(self, flag):
        if flag:
            self.nextButton.SetLabel(_extstr(u"Finish")) #$NON-NLS-1$
        else:
            self.nextButton.SetLabel(_extstr(u"Next") + u" >") #$NON-NLS-2$ #$NON-NLS-1$
    # end _setIsLasPage()

    def _enableNextButton(self, enable = True):
        self._enableButtonById(ZID_NEXT, enable)
    # end _enableNextButton()

    def _enablePreviousButton(self, enable = True):
        self._enableButtonById(ZID_PREVIOUS, enable)
    # end _enablePreviousButton()

    def _enableButtonById(self, buttonId, enable = True):
        button = self.FindWindowById(buttonId)
        if button:
            button.Enable(enable)
    # end _enableButtonById()

    def _isButtonEnabledById(self, buttonId):
        button = self.FindWindowById(buttonId)
        if button:
            return button.IsEnabled()
        else:
            return False
    # end _isButtonEnabledById()

    def _getCurrentPage(self):
        return self.pages[self.currentIdx]
    # end _getCurrentPage()

    def _getCurrentImage(self):
        img = self.images[self.currentIdx]
        if img is None:
            img = self.defaultImage
        return img
    # end _getCurrentImage()

    def _hideAll(self):
        for image in self.images:
            if image is not None:
                image.Show(False)
        for page in self.pages:
            page.Show(False)
    # end _hideAll()

# end ZWizard
