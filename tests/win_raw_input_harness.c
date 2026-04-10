#include "win_rawinput_shared.h"

#if defined(_WIN32)
#define QLR_TEST_EXPORT __declspec(dllexport)
#else
#define QLR_TEST_EXPORT
#endif

/*
==================
QLR_WinRawInputBuildRegistration

Wrapper used by the Python harness to exercise the shared Win32 raw-input registration helper.
==================
*/
QLR_TEST_EXPORT void QLR_WinRawInputBuildRegistration( RAWINPUTDEVICE *device, void *windowHandle,
	int useWindowHandle, int removeDevice )
{
	QLR_Win32RawInputBuildRegistration( device, ( HWND )windowHandle, useWindowHandle, removeDevice );
}

/*
==================
QLR_WinRawInputExtractMouseSampleFromFields

Wrapper used by the Python harness to exercise the shared Win32 raw-input sample extraction helper from a synthetic RAWINPUT packet.
==================
*/
QLR_TEST_EXPORT int QLR_WinRawInputExtractMouseSampleFromFields( LONG dx, LONG dy, USHORT buttonFlags,
	USHORT buttonData, qlr_win32_raw_mouse_sample_t *sample )
{
	RAWINPUT rawInput;

	ZeroMemory( &rawInput, sizeof( rawInput ) );
	rawInput.header.dwType = RIM_TYPEMOUSE;
	rawInput.data.mouse.lLastX = dx;
	rawInput.data.mouse.lLastY = dy;
	rawInput.data.mouse.usButtonFlags = buttonFlags;
	rawInput.data.mouse.usButtonData = buttonData;

	return QLR_Win32RawInputExtractMouseSample( &rawInput, sample );
}

/*
==================
QLR_WinRawInputTranslateButtonFlags

Wrapper used by the Python harness to exercise the shared Win32 raw-input button-flag translation helper.
==================
*/
QLR_TEST_EXPORT int QLR_WinRawInputTranslateButtonFlags( USHORT buttonFlags, SHORT wheelDelta,
	int *outKeys, int *outDown, int maxEvents )
{
	return QLR_Win32RawInputTranslateButtonFlags( buttonFlags, wheelDelta, outKeys, outDown, maxEvents );
}

/*
==================
QLR_WinRawInputKeyMouse1

Wrapper used by the Python harness to expose the retained mouse key-code base.
==================
*/
QLR_TEST_EXPORT int QLR_WinRawInputKeyMouse1( void )
{
	return K_MOUSE1;
}

/*
==================
QLR_WinRawInputKeyWheelDown

Wrapper used by the Python harness to expose the retained mouse-wheel-down key code.
==================
*/
QLR_TEST_EXPORT int QLR_WinRawInputKeyWheelDown( void )
{
	return K_MWHEELDOWN;
}

/*
==================
QLR_WinRawInputKeyWheelUp

Wrapper used by the Python harness to expose the retained mouse-wheel-up key code.
==================
*/
QLR_TEST_EXPORT int QLR_WinRawInputKeyWheelUp( void )
{
	return K_MWHEELUP;
}
