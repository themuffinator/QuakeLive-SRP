#include "win_clipboard_shared.h"

#if defined(_WIN32)
#define QLR_TEST_EXPORT __declspec(dllexport)
#else
#define QLR_TEST_EXPORT
#endif

/*
=============
QLR_WinClipboardWideToUtf8ByteCount

Wrapper used by the Python harness to exercise the shared Win32 clipboard UTF-16 sizing helper.
=============
*/
QLR_TEST_EXPORT int QLR_WinClipboardWideToUtf8ByteCount( const WCHAR *text ) {
	return QLR_Win32ClipboardWideToUtf8ByteCount( text );
}

/*
=============
QLR_WinClipboardWideToUtf8

Wrapper used by the Python harness to exercise the shared Win32 clipboard UTF-16-to-UTF-8 conversion helper.
=============
*/
QLR_TEST_EXPORT int QLR_WinClipboardWideToUtf8( const WCHAR *text, char *buffer, int bufferBytes ) {
	return QLR_Win32ClipboardWideToUtf8( text, buffer, bufferBytes );
}

/*
=============
QLR_WinClipboardTrimText

Wrapper used by the Python harness to exercise the shared Win32 clipboard control-character trimming helper.
=============
*/
QLR_TEST_EXPORT void QLR_WinClipboardTrimText( char *text ) {
	QLR_Win32ClipboardTrimText( text );
}
