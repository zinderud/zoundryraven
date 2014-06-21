from zoundry.appframework.services.ztest.ztest import IZTest
from zoundry.appframework.services.ztest.ztest import IZTestStep
from zoundry.base.exceptions import ZException
from zoundry.base.util.collections import ZListenerSet

# ------------------------------------------------------------------------------------------
# Simple implementation of a IZTestStep.  Most likely will be used as a base class for 
# a specific test's IZTestStep impl.
# ------------------------------------------------------------------------------------------
class ZTestStep(IZTestStep):

    def __init__(self, description):
        self.description = description
        self.current = False
        self.passed = False
        self.failed = False
        self.error = None
    # end __init__()

    def getDescription(self):
        return self.description
    # end getDescription()

    def isExecuting(self):
        return self.current
    # end isExecuting()

    def isComplete(self):
        return self.isPass() or self.isFail()
    # end isComplete()

    def isPass(self):
        return self.passed
    # end isPass()

    def isFail(self):
        return self.failed
    # end isFail()
    
    def getError(self):
        return self.error
    # end getError()

    def setPassed(self):
        self.passed = True
        self.current = False
    # end setPassed()
    
    def setFailed(self, error):
        self.error = error
        self.failed = True
        self.current = False
    # end setFailed()

    def setCurrent(self):
        self.current = True
    # end setCurrent()

# end IZTestStep


# ------------------------------------------------------------------------------------------
# Simple implementation of a IZTest.  This class is intended to be the base class of a real
# test.
# ------------------------------------------------------------------------------------------
class ZTest(IZTest):

    def __init__(self):
        self.steps = []
        self.listeners = ZListenerSet()
        self.cancelled = False
    # end __init__()

    def getSteps(self):
        return self.steps
    # end getSteps()

    def addStep(self, step):
        self.steps.append(step)
    # end addStep()

    def addListener(self, listener):
        self.listeners.append(listener)
    # end addListener()

    def removeListener(self, listener):
        self.listeners.remove(listener)
    # end removeListener()

    def cancel(self):
        self.cancelled = True
    # end cancel()

    def run(self):
        for listener in self.listeners:
            listener.onTestStart(self)

        for step in self.steps:
            if self.cancelled:
                return
            try:
                step.setCurrent()
                for listener in self.listeners:
                    listener.onStepStart(self, step)

                # Now actually run the step
                self._runStep(step)

                step.setPassed()
                for listener in self.listeners:
                    listener.onStepPass(self, step)
            except Exception, e:
                ze = ZException(unicode(e), rootCause = e)
                step.setFailed(ze)
                for listener in self.listeners:
                    listener.onStepFail(self, step, ze)
                break

        for listener in self.listeners:
            listener.onTestComplete(self)
    # end run()

    def _runStep(self, step):
        raise ZException(u"Method '_runStep' must be implemented by subclass.") #$NON-NLS-1$
    # end _runStep()

# end ZTest
