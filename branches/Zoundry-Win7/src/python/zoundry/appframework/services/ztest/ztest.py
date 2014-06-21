from zoundry.base.util.zthread import IZRunnable

# FIXME repackage this out of services and into something else (core?)

# ------------------------------------------------------------------------------------------
# A test listener interface.  The test dialog (or anyone else, for that matter) will listen
# to the events thrown by a IZTest while it runs.
# ------------------------------------------------------------------------------------------
class IZTestListener:

    def onTestStart(self, test):
        u"Called when a test is started." #$NON-NLS-1$
    # end onTestStart()

    def onStepStart(self, test, step):
        u"Called when a test Step is started." #$NON-NLS-1$
    # end onStepStart()

    def onStepPass(self, test, step):
        u"Called when a Step passes." #$NON-NLS-1$
    # end onStepPass()

    def onStepFail(self, test, step, error):
        u"Called when a Step fails (the test will stop - no more steps will run)." #$NON-NLS-1$
    # end onStepError()

    def onTestComplete(self, test):
        u"Called when the test completes (called even if a Step fails)." #$NON-NLS-1$
    # end onTestComplete()

# end IZTestListener


# ------------------------------------------------------------------------------------------
# Interface that declares a test step.  A test step is a single step in a multi-step test
# of some part of the application.  All tests are made up of a list of steps, each of 
# which is executed when the test is run.
# ------------------------------------------------------------------------------------------
class IZTestStep:

    def getDescription(self):
        u"Returns a description of the step, typically for display or logging purposes." #$NON-NLS-1$
    # end getDescription()
    
    def isExecuting(self):
        u"Returns True if the step is currently executing." #$NON-NLS-1$
    # end isExecuting()

    def isComplete(self):
        u"Returns True if the step is complete (True if either isPass or isFail returns True)." #$NON-NLS-1$
    # end isComplete()

    def isPass(self):
        u"Returns True if the step passed." #$NON-NLS-1$
    # end isPass()

    def isFail(self):
        u"Returns True if the step failed." #$NON-NLS-1$
    # end isFail()
    
    def getError(self):
        u"Returns the reason for a failure." #$NON-NLS-1$
    # end getError()
    
    def setPassed(self):
        u"Called when a step passes." #$NON-NLS-1$
    # end setPassed()
    
    def setFailed(self, error):
        u"Called when a step fails." #$NON-NLS-1$
    # end setFailed()

    def setCurrent(self):
        u"Called when a step starts executing." #$NON-NLS-1$
    # end setCurrent()

# end IZTestStep


# ------------------------------------------------------------------------------------------
# Interface that must be implemented by all Zoundry tests.  A test in Zoundry Raven is 
# something that is run on behalf of the user in order to determine if the settings for
# something are correct.  For example, after the user configures a new FTP Media Storage in
# the application, they can choose to test those settings.  When that happens, an instance
# of IZTest is created and given to a test dialog.  The test is run and the dialog displays
# the result of each step as they happen.
# ------------------------------------------------------------------------------------------
class IZTest(IZRunnable):

    def getSteps(self):
        u"Returns a list of IZTestStep instances which represent the steps in the test." #$NON-NLS-1$
    # end getSteps()

    def cancel(self):
        u"Called to cancel the test." #$NON-NLS-1$
    # end cancel()

# end IZTest
