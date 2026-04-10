#ifndef WIN_CLIPBOARD_SHARED_H
#define WIN_CLIPBOARD_SHARED_H

#ifndef _WINDOWS_
#include <windows.h>
#endif

/*
==================
QLR_Win32ClipboardTrimText
==================
*/
static inline void QLR_Win32ClipboardTrimText( char *text ) {
	char *cursor;

	if ( !text ) {
		return;
	}

	for ( cursor = text; *cursor; cursor++ ) {
		if ( *cursor == '\n' || *cursor == '\r' || *cursor == '\b' ) {
			*cursor = '\0';
			break;
		}
	}
}

/*
==================
QLR_Win32ClipboardWideToUtf8ByteCount
==================
*/
static inline int QLR_Win32ClipboardWideToUtf8ByteCount( const WCHAR *text ) {
	if ( !text ) {
		return 0;
	}

	return WideCharToMultiByte( CP_UTF8, 0, text, -1, NULL, 0, NULL, NULL );
}

/*
==================
QLR_Win32ClipboardWideToUtf8
==================
*/
static inline int QLR_Win32ClipboardWideToUtf8( const WCHAR *text, char *buffer, int bufferBytes ) {
	if ( !text || !buffer || bufferBytes <= 0 ) {
		return 0;
	}

	return WideCharToMultiByte( CP_UTF8, 0, text, -1, buffer, bufferBytes, NULL, NULL );
}

#endif
