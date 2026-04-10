#ifndef WIN_RAWINPUT_SHARED_H
#define WIN_RAWINPUT_SHARED_H

#ifndef _WINDOWS_
#include <windows.h>
#endif

#include "../ui/keycodes.h"

#define QLR_WIN32_RAW_INPUT_MAX_EVENTS 12

typedef struct {
	LONG	dx;
	LONG	dy;
	USHORT	buttonFlags;
	SHORT	wheelDelta;
} qlr_win32_raw_mouse_sample_t;

/*
==================
QLR_Win32RawInputBuildRegistration
==================
*/
static inline void QLR_Win32RawInputBuildRegistration( RAWINPUTDEVICE *device, HWND windowHandle,
	int useWindowHandle, int removeDevice ) {
	if ( !device ) {
		return;
	}

	device->usUsagePage = 1;
	device->usUsage = 2;
	device->dwFlags = removeDevice ? RIDEV_REMOVE : 0;
	device->hwndTarget = ( removeDevice || !useWindowHandle ) ? NULL : windowHandle;
}

/*
==================
QLR_Win32RawInputExtractMouseSample
==================
*/
static inline int QLR_Win32RawInputExtractMouseSample( const RAWINPUT *rawInput,
	qlr_win32_raw_mouse_sample_t *sample ) {
	if ( !rawInput || !sample || rawInput->header.dwType != RIM_TYPEMOUSE ) {
		return 0;
	}

	sample->dx = rawInput->data.mouse.lLastX;
	sample->dy = rawInput->data.mouse.lLastY;
	sample->buttonFlags = rawInput->data.mouse.usButtonFlags;
	sample->wheelDelta = (SHORT)rawInput->data.mouse.usButtonData;
	return 1;
}

/*
==================
QLR_Win32RawInputTranslateButtonFlags
==================
*/
static inline int QLR_Win32RawInputTranslateButtonFlags( USHORT buttonFlags, SHORT wheelDelta,
	int *outKeys, int *outDown, int maxEvents ) {
	int	count;

	count = 0;

#define QLR_APPEND_RAW_EVENT(flag, key, down) \
	if ( ( buttonFlags & (flag) ) != 0 && count < maxEvents ) { \
		outKeys[count] = (key); \
		outDown[count] = (down); \
		count++; \
	}

	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_1_DOWN, K_MOUSE1, 1 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_1_UP, K_MOUSE1, 0 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_2_DOWN, K_MOUSE2, 1 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_2_UP, K_MOUSE2, 0 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_3_DOWN, K_MOUSE3, 1 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_3_UP, K_MOUSE3, 0 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_4_DOWN, K_MOUSE4, 1 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_4_UP, K_MOUSE4, 0 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_5_DOWN, K_MOUSE5, 1 );
	QLR_APPEND_RAW_EVENT( RI_MOUSE_BUTTON_5_UP, K_MOUSE5, 0 );

	if ( ( buttonFlags & RI_MOUSE_WHEEL ) != 0 ) {
		if ( wheelDelta > 0 && count + 1 < maxEvents ) {
			outKeys[count] = K_MWHEELUP;
			outDown[count] = 1;
			count++;
			outKeys[count] = K_MWHEELUP;
			outDown[count] = 0;
			count++;
		} else if ( wheelDelta < 0 && count + 1 < maxEvents ) {
			outKeys[count] = K_MWHEELDOWN;
			outDown[count] = 1;
			count++;
			outKeys[count] = K_MWHEELDOWN;
			outDown[count] = 0;
			count++;
		}
	}

#undef QLR_APPEND_RAW_EVENT

	return count;
}

#endif
