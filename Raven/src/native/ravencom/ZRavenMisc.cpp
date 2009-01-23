// ZRavenMisc.cpp

#include "Python.h"
#include "PyWinTypes.h"

#include "windows.h"
#include "comdef.h"
#include "Mshtml.h"

#include "ZRavenMisc.h"

/**
 * Called by the Python drop target to move the caret position during
 * a drag/drop operation.  This gives the user some feedback as they
 * drag around within the document.
 *
 * The following python params are passed to this function:
 *   @param PyIDispatch - the python wrapped mshtml control
 *   @param x - the x location (absolute coords) of the cursor
 *   @param y - the y location (absolute coords) of the cursor
 */
PyObject *SetMSHTMLCaretPosition(PyObject * self, PyObject *args)
{
	PyObject * pyIDispatch;
	IHTMLDocument2 * pHtmlDocument;
	int x;
	int y;
	if ( !PyArg_ParseTuple(args, "Oii", &pyIDispatch, &x, &y) )
		return NULL;

	// Get the IHTMLDocument2 interface from the PyIDispatch python object.
	if (!PyCom_InterfaceFromPyInstanceOrObject(pyIDispatch, IID_IHTMLDocument2, (void **)&pHtmlDocument, TRUE /* bNoneOK */))
		return NULL;

	// Get the display services from the html document interface
	IDisplayServices * displayServices;
	HRESULT result = pHtmlDocument->QueryInterface(IID_IDisplayServices, (void**) &displayServices);
	if (result != S_OK)
		return NULL;
	// Get the html doc's insertion point
	IHTMLCaret * caret;
	result = displayServices->GetCaret(&caret);
	if (result != S_OK)
		return NULL;
	// Create a display pointer
	IDisplayPointer * displayPointer;
	result = displayServices->CreateDisplayPointer(&displayPointer);
	if (result != S_OK)
		return NULL;
	// Move the display pointer based on the cursor coords
	POINT absPoint;
	absPoint.x = x;
	absPoint.y = y;
	DWORD movePtResult = -1;
	result = displayPointer->MoveToPoint(absPoint, COORD_SYSTEM_GLOBAL, NULL, 0, &movePtResult);
	if (result != S_OK)
		return NULL;
	// Finally, move the caret to the display pointer.
	result = caret->MoveCaretToPointerEx(displayPointer, TRUE, TRUE, CARET_DIRECTION_INDETERMINATE);
	if (result != S_OK)
		return NULL;

	caret->Show(FALSE);

	// Return some result
	PyObject * rval = Py_BuildValue("i", (int) movePtResult);
	return rval;
}
