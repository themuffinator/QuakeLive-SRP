#include <math.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef _WIN32
#define QLR_TEST_EXPORT __declspec(dllexport)
#define QLR_STRICMP _stricmp
#else
#define QLR_TEST_EXPORT
#define QLR_STRICMP strcasecmp
#endif

#include "../src/code/game/q_shared.h"
#include "../src/code/qcommon/qcommon.h"
#include "../src/code/qcommon/cm_local.h"

static jmp_buf qlr_error_jmp;
static qboolean qlr_error_jmp_active = qfalse;
static char qlr_last_error[1024];
static char qlr_captured_log[4096];
static size_t qlr_captured_log_len = 0;
static void *qlr_hunk_allocations[1024];
static int qlr_hunk_allocation_count = 0;

static cvar_t qlr_stub_curve_clip = {
	.name = "cm_playerCurveClip",
	.string = "1",
	.resetString = "1",
	.flags = 0,
	.value = 1.0f,
	.integer = 1,
};
static cvar_t qlr_stub_zero_cvar = {
	.name = "qlr_zero",
	.string = "0",
	.resetString = "0",
	.flags = 0,
	.value = 0.0f,
	.integer = 0,
};
static cvar_t qlr_stub_debug_surface = {
	.name = "r_debugSurface",
	.string = "0",
	.resetString = "0",
	.flags = 0,
	.value = 0.0f,
	.integer = 0,
};
static cvar_t qlr_stub_debug_surface_update = {
	.name = "r_debugSurfaceUpdate",
	.string = "0",
	.resetString = "0",
	.flags = 0,
	.value = 0.0f,
	.integer = 0,
};
static cvar_t qlr_stub_debug_size = {
	.name = "cm_debugSize",
	.string = "2",
	.resetString = "2",
	.flags = 0,
	.value = 2.0f,
	.integer = 2,
};

/*
=============
QLR_ClearCapturedLog
=============
*/
static void QLR_ClearCapturedLog( void ) {
	qlr_captured_log[0] = '\0';
	qlr_captured_log_len = 0;
}

/*
=============
QLR_AppendCapturedLog
=============
*/
static void QLR_AppendCapturedLog( const char *text ) {
	size_t available;
	size_t textLength;

	if ( !text || !*text || qlr_captured_log_len >= sizeof( qlr_captured_log ) - 1 ) {
		return;
	}

	available = sizeof( qlr_captured_log ) - qlr_captured_log_len - 1;
	textLength = strlen( text );
	if ( textLength > available ) {
		textLength = available;
	}

	memcpy( qlr_captured_log + qlr_captured_log_len, text, textLength );
	qlr_captured_log_len += textLength;
	qlr_captured_log[qlr_captured_log_len] = '\0';
}

/*
=============
QLR_FormatLastError
=============
*/
static void QLR_FormatLastError( const char *fmt, va_list args ) {
	vsnprintf( qlr_last_error, sizeof( qlr_last_error ), fmt, args );
	QLR_AppendCapturedLog( qlr_last_error );
}

/*
=============
QLR_ResetErrorState
=============
*/
static void QLR_ResetErrorState( void ) {
	qlr_last_error[0] = '\0';
}

/*
=============
QLR_BeginProtectedCall
=============
*/
static int QLR_BeginProtectedCall( void ) {
	QLR_ResetErrorState();
	if ( setjmp( qlr_error_jmp ) != 0 ) {
		qlr_error_jmp_active = qfalse;
		return 0;
	}

	qlr_error_jmp_active = qtrue;
	return 1;
}

/*
=============
QLR_EndProtectedCall
=============
*/
static int QLR_EndProtectedCall( void ) {
	qlr_error_jmp_active = qfalse;
	return 1;
}

/*
=============
Com_Memset
=============
*/
void Com_Memset( void *dest, const int fill, const size_t count ) {
	memset( dest, fill, count );
}

/*
=============
Com_Memcpy
=============
*/
void Com_Memcpy( void *dest, const void *src, const size_t count ) {
	memcpy( dest, src, count );
}

/*
=============
Com_sprintf
=============
*/
int QDECL Com_sprintf( char *dest, int size, const char *fmt, ... ) {
	va_list args;
	int written;

	va_start( args, fmt );
	written = vsnprintf( dest, size, fmt, args );
	va_end( args );

	return written;
}

/*
=============
ClearBounds
=============
*/
void ClearBounds( vec3_t mins, vec3_t maxs ) {
	mins[0] = mins[1] = mins[2] = 99999.0f;
	maxs[0] = maxs[1] = maxs[2] = -99999.0f;
}

/*
=============
AddPointToBounds
=============
*/
void AddPointToBounds( const vec3_t v, vec3_t mins, vec3_t maxs ) {
	int i;

	for ( i = 0; i < 3; i++ ) {
		if ( v[i] < mins[i] ) {
			mins[i] = v[i];
		}
		if ( v[i] > maxs[i] ) {
			maxs[i] = v[i];
		}
	}
}

/*
=============
VectorNormalize2
=============
*/
vec_t VectorNormalize2( const vec3_t v, vec3_t out ) {
	vec_t length;

	length = sqrtf( v[0] * v[0] + v[1] * v[1] + v[2] * v[2] );
	if ( length == 0.0f ) {
		VectorClear( out );
		return 0.0f;
	}

	out[0] = v[0] / length;
	out[1] = v[1] / length;
	out[2] = v[2] / length;
	return length;
}

/*
=============
VectorNormalize
=============
*/
vec_t VectorNormalize( vec3_t v ) {
	return VectorNormalize2( v, v );
}

/*
=============
Com_Error
=============
*/
void QDECL Com_Error( int level, const char *error, ... ) {
	va_list args;

	(void)level;

	va_start( args, error );
	QLR_FormatLastError( error, args );
	va_end( args );

	if ( qlr_error_jmp_active ) {
		longjmp( qlr_error_jmp, 1 );
	}

	abort();
}

/*
=============
Com_Printf
=============
*/
void QDECL Com_Printf( const char *fmt, ... ) {
	va_list args;
	char message[1024];

	va_start( args, fmt );
	vsnprintf( message, sizeof( message ), fmt, args );
	va_end( args );

	QLR_AppendCapturedLog( message );
}

/*
=============
Com_DPrintf
=============
*/
void QDECL Com_DPrintf( const char *fmt, ... ) {
	va_list args;
	char message[1024];

	va_start( args, fmt );
	vsnprintf( message, sizeof( message ), fmt, args );
	va_end( args );

	QLR_AppendCapturedLog( message );
}

/*
=============
Z_Malloc
=============
*/
void *Z_Malloc( int size ) {
	return calloc( 1, (size_t)size );
}

/*
=============
Z_Free
=============
*/
void Z_Free( void *ptr ) {
	free( ptr );
}

/*
=============
Hunk_Alloc
=============
*/
void *Hunk_Alloc( int size, ha_pref preference ) {
	void *memory;

	(void)preference;

	if ( qlr_hunk_allocation_count >= (int)( sizeof( qlr_hunk_allocations ) / sizeof( qlr_hunk_allocations[0] ) ) ) {
		Com_Error( ERR_DROP, "QLR Hunk allocation tracker overflow" );
		return NULL;
	}

	memory = calloc( 1, (size_t)size );
	if ( !memory ) {
		Com_Error( ERR_DROP, "QLR Hunk allocation failed for %d bytes", size );
		return NULL;
	}

	qlr_hunk_allocations[ qlr_hunk_allocation_count++ ] = memory;
	return memory;
}

/*
=============
BotDrawDebugPolygons
=============
*/
void BotDrawDebugPolygons( void (*drawPoly)( int color, int numPoints, float *points ), int value ) {
	(void)drawPoly;
	(void)value;
}

/*
=============
Cvar_Get
=============
*/
cvar_t *Cvar_Get( const char *var_name, const char *value, int flags ) {
	(void)value;
	(void)flags;

	if ( !var_name ) {
		return &qlr_stub_zero_cvar;
	}

	if ( QLR_STRICMP( var_name, "cm_playerCurveClip" ) == 0 ) {
		return &qlr_stub_curve_clip;
	}
	if ( QLR_STRICMP( var_name, "r_debugSurface" ) == 0 ) {
		return &qlr_stub_debug_surface;
	}
	if ( QLR_STRICMP( var_name, "r_debugSurfaceUpdate" ) == 0 ) {
		return &qlr_stub_debug_surface_update;
	}
	if ( QLR_STRICMP( var_name, "cm_debugSize" ) == 0 ) {
		return &qlr_stub_debug_size;
	}

	return &qlr_stub_zero_cvar;
}

typedef struct {
	float plane[4];
	int signbits;
} patchPlane_t;

typedef struct {
	int surfacePlane;
	int numBorders;
	int borderPlanes[4 + 6 + 16];
	int borderInward[4 + 6 + 16];
	qboolean borderNoAdjust[4 + 6 + 16];
} facet_t;

typedef struct patchCollide_s {
	vec3_t bounds[2];
	int numPlanes;
	patchPlane_t *planes;
	int numFacets;
	facet_t *facets;
} patchCollide_t;

int CM_CheckFacetPlane( float *plane, vec3_t start, vec3_t end, float *enterFrac, float *leaveFrac, int *hit );

clipMap_t cm;
int c_pointcontents = 0;
int c_traces = 0;
int c_brush_traces = 0;
int c_patch_traces = 0;
cvar_t *cm_noAreas = &qlr_stub_zero_cvar;
cvar_t *cm_noCurves = &qlr_stub_zero_cvar;
cvar_t *cm_playerCurveClip = &qlr_stub_curve_clip;
vec3_t vec3_origin = { 0.0f, 0.0f, 0.0f };
vec3_t axisDefault[3] = {
	{ 1.0f, 0.0f, 0.0f },
	{ 0.0f, 1.0f, 0.0f },
	{ 0.0f, 0.0f, 1.0f },
};

/*
=============
QLR_FreeTrackedHunkAllocs
=============
*/
static void QLR_FreeTrackedHunkAllocs( void ) {
	int i;

	for ( i = 0; i < qlr_hunk_allocation_count; i++ ) {
		free( qlr_hunk_allocations[i] );
		qlr_hunk_allocations[i] = NULL;
	}

	qlr_hunk_allocation_count = 0;
}

/*
=============
QLR_ResetHarnessState
=============
*/
static void QLR_ResetHarnessState( void ) {
	QLR_FreeTrackedHunkAllocs();
	QLR_ClearCapturedLog();
	CM_ClearLevelPatches();
	Com_Memset( &cm, 0, sizeof( cm ) );
	c_pointcontents = 0;
	c_traces = 0;
	c_brush_traces = 0;
	c_patch_traces = 0;
	qlr_stub_curve_clip.integer = 1;
	qlr_stub_curve_clip.value = 1.0f;
	qlr_stub_curve_clip.string = "1";
}

/*
=============
QLR_InitBoxTraceWork
=============
*/
static void QLR_InitBoxTraceWork( traceWork_t *tw, const vec3_t start, const vec3_t mins, const vec3_t maxs ) {
	Com_Memset( tw, 0, sizeof( *tw ) );
	VectorCopy( start, tw->start );
	VectorCopy( start, tw->end );
	VectorCopy( mins, tw->size[0] );
	VectorCopy( maxs, tw->size[1] );
	tw->trace.fraction = 1.0f;
	tw->isPoint = qfalse;

	tw->offsets[0][0] = tw->size[0][0];
	tw->offsets[0][1] = tw->size[0][1];
	tw->offsets[0][2] = tw->size[0][2];
	tw->offsets[1][0] = tw->size[1][0];
	tw->offsets[1][1] = tw->size[0][1];
	tw->offsets[1][2] = tw->size[0][2];
	tw->offsets[2][0] = tw->size[0][0];
	tw->offsets[2][1] = tw->size[1][1];
	tw->offsets[2][2] = tw->size[0][2];
	tw->offsets[3][0] = tw->size[1][0];
	tw->offsets[3][1] = tw->size[1][1];
	tw->offsets[3][2] = tw->size[0][2];
	tw->offsets[4][0] = tw->size[0][0];
	tw->offsets[4][1] = tw->size[0][1];
	tw->offsets[4][2] = tw->size[1][2];
	tw->offsets[5][0] = tw->size[1][0];
	tw->offsets[5][1] = tw->size[0][1];
	tw->offsets[5][2] = tw->size[1][2];
	tw->offsets[6][0] = tw->size[0][0];
	tw->offsets[6][1] = tw->size[1][1];
	tw->offsets[6][2] = tw->size[1][2];
	tw->offsets[7][0] = tw->size[1][0];
	tw->offsets[7][1] = tw->size[1][1];
	tw->offsets[7][2] = tw->size[1][2];
}

/*
=============
QLR_FillFlatPatchPoints
=============
*/
static void QLR_FillFlatPatchPoints( vec3_t *points ) {
	static const vec3_t flatPatch[9] = {
		{ -16.0f, 16.0f, 0.0f }, { 0.0f, 16.0f, 0.0f }, { 16.0f, 16.0f, 0.0f },
		{ -16.0f, 0.0f, 0.0f }, { 0.0f, 0.0f, 0.0f }, { 16.0f, 0.0f, 0.0f },
		{ -16.0f, -16.0f, 0.0f }, { 0.0f, -16.0f, 0.0f }, { 16.0f, -16.0f, 0.0f },
	};

	Com_Memcpy( points, flatPatch, sizeof( flatPatch ) );
}

/*
=============
QLR_FillCurvedPatchPoints
=============
*/
static void QLR_FillCurvedPatchPoints( vec3_t *points ) {
	static const vec3_t curvedPatch[9] = {
		{ -16.0f, 16.0f, 0.0f }, { 0.0f, 16.0f, 32.0f }, { 16.0f, 16.0f, 0.0f },
		{ -16.0f, 0.0f, 32.0f }, { 0.0f, 0.0f, 64.0f }, { 16.0f, 0.0f, 32.0f },
		{ -16.0f, -16.0f, 0.0f }, { 0.0f, -16.0f, 32.0f }, { 16.0f, -16.0f, 0.0f },
	};

	Com_Memcpy( points, curvedPatch, sizeof( curvedPatch ) );
}

/*
=============
QLR_CM_TestLastError
=============
*/
QLR_TEST_EXPORT const char *QLR_CM_TestLastError( void ) {
	return qlr_last_error;
}

/*
=============
QLR_CM_TestCapturedLog
=============
*/
QLR_TEST_EXPORT const char *QLR_CM_TestCapturedLog( void ) {
	return qlr_captured_log;
}

/*
=============
QLR_CM_TestCurvedPatchStats
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestCurvedPatchStats( int *outNumPlanes, int *outNumFacets, float *outBounds ) {
	vec3_t points[9];
	const patchCollide_t *patch;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	QLR_FillCurvedPatchPoints( points );
	patch = CM_GeneratePatchCollide( 3, 3, points );

	if ( outNumPlanes ) {
		*outNumPlanes = patch->numPlanes;
	}
	if ( outNumFacets ) {
		*outNumFacets = patch->numFacets;
	}
	if ( outBounds ) {
		outBounds[0] = patch->bounds[0][0];
		outBounds[1] = patch->bounds[0][1];
		outBounds[2] = patch->bounds[0][2];
		outBounds[3] = patch->bounds[1][0];
		outBounds[4] = patch->bounds[1][1];
		outBounds[5] = patch->bounds[1][2];
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_CM_TestFlatPatchPointTrace
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestFlatPatchPointTrace( float *outFraction, float *outNormal, float *outDist ) {
	vec3_t points[9];
	traceWork_t tw;
	const patchCollide_t *patch;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	QLR_FillFlatPatchPoints( points );
	patch = CM_GeneratePatchCollide( 3, 3, points );

	Com_Memset( &tw, 0, sizeof( tw ) );
	VectorSet( tw.start, 0.0f, 0.0f, -32.0f );
	VectorSet( tw.end, 0.0f, 0.0f, 32.0f );
	tw.isPoint = qtrue;
	tw.trace.fraction = 1.0f;
	CM_TraceThroughPatchCollide( &tw, patch );

	if ( outFraction ) {
		*outFraction = tw.trace.fraction;
	}
	if ( outNormal ) {
		outNormal[0] = tw.trace.plane.normal[0];
		outNormal[1] = tw.trace.plane.normal[1];
		outNormal[2] = tw.trace.plane.normal[2];
	}
	if ( outDist ) {
		*outDist = tw.trace.plane.dist;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_CM_TestFlatPatchPositionTest
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestFlatPatchPositionTest( float startZ, int *outHit ) {
	vec3_t points[9];
	vec3_t start = { 0.0f, 0.0f, 0.0f };
	vec3_t mins = { -2.0f, -2.0f, -2.0f };
	vec3_t maxs = { 2.0f, 2.0f, 2.0f };
	traceWork_t tw;
	const patchCollide_t *patch;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	QLR_FillFlatPatchPoints( points );
	patch = CM_GeneratePatchCollide( 3, 3, points );

	start[2] = startZ;
	QLR_InitBoxTraceWork( &tw, start, mins, maxs );
	if ( outHit ) {
		*outHit = CM_PositionTestInPatchCollide( &tw, patch ) ? 1 : 0;
	}

	return QLR_EndProtectedCall();
}

/*
=============
QLR_CM_TestBaseWindingClip
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestBaseWindingClip( float *outArea, int *outNumPoints, float *outBounds ) {
	winding_t *winding;
	vec3_t mins;
	vec3_t maxs;
	vec3_t normal = { 0.0f, 0.0f, -1.0f };
	vec3_t clipNormal;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	winding = BaseWindingForPlane( normal, 0.0f );

	VectorSet( clipNormal, 1.0f, 0.0f, 0.0f );
	ChopWindingInPlace( &winding, clipNormal, -4.0f, 0.1f );
	VectorSet( clipNormal, -1.0f, 0.0f, 0.0f );
	ChopWindingInPlace( &winding, clipNormal, -4.0f, 0.1f );
	VectorSet( clipNormal, 0.0f, 1.0f, 0.0f );
	ChopWindingInPlace( &winding, clipNormal, -2.0f, 0.1f );
	VectorSet( clipNormal, 0.0f, -1.0f, 0.0f );
	ChopWindingInPlace( &winding, clipNormal, -2.0f, 0.1f );

	WindingBounds( winding, mins, maxs );
	if ( outArea ) {
		*outArea = WindingArea( winding );
	}
	if ( outNumPoints ) {
		*outNumPoints = winding->numpoints;
	}
	if ( outBounds ) {
		outBounds[0] = mins[0];
		outBounds[1] = mins[1];
		outBounds[2] = mins[2];
		outBounds[3] = maxs[0];
		outBounds[4] = maxs[1];
		outBounds[5] = maxs[2];
	}

	FreeWinding( winding );
	return QLR_EndProtectedCall();
}

/*
=============
QLR_CM_TestConvexHullMerge
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestConvexHullMerge( float *outArea, int *outNumPoints, float *outCenter ) {
	winding_t *triangleA;
	winding_t *triangleB;
	winding_t *hull = NULL;
	vec3_t center;
	vec3_t normal = { 0.0f, 0.0f, 1.0f };

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	triangleA = AllocWinding( 3 );
	triangleB = AllocWinding( 3 );

	VectorSet( triangleA->p[0], 0.0f, 0.0f, 0.0f );
	VectorSet( triangleA->p[1], 4.0f, 0.0f, 0.0f );
	VectorSet( triangleA->p[2], 0.0f, 4.0f, 0.0f );
	triangleA->numpoints = 3;

	VectorSet( triangleB->p[0], 4.0f, 0.0f, 0.0f );
	VectorSet( triangleB->p[1], 4.0f, 4.0f, 0.0f );
	VectorSet( triangleB->p[2], 0.0f, 4.0f, 0.0f );
	triangleB->numpoints = 3;

	AddWindingToConvexHull( triangleA, &hull, normal );
	AddWindingToConvexHull( triangleB, &hull, normal );

	WindingCenter( hull, center );
	if ( outArea ) {
		*outArea = WindingArea( hull );
	}
	if ( outNumPoints ) {
		*outNumPoints = hull->numpoints;
	}
	if ( outCenter ) {
		outCenter[0] = center[0];
		outCenter[1] = center[1];
		outCenter[2] = center[2];
	}

	FreeWinding( triangleA );
	FreeWinding( triangleB );
	FreeWinding( hull );
	return QLR_EndProtectedCall();
}

/*
=============
QLR_CM_TestCheckFacetPlane
=============
*/
QLR_TEST_EXPORT int QLR_CM_TestCheckFacetPlane( float *outEnterFrac, float *outLeaveFrac, int *outHit, int *outResult ) {
	float plane[4] = { 0.0f, 0.0f, -1.0f, 0.0f };
	vec3_t start = { 0.0f, 0.0f, -32.0f };
	vec3_t end = { 0.0f, 0.0f, 32.0f };
	float enterFrac = -1.0f;
	float leaveFrac = 1.0f;
	int hit = qfalse;
	int result;

	if ( !QLR_BeginProtectedCall() ) {
		return 0;
	}

	QLR_ResetHarnessState();
	result = CM_CheckFacetPlane( plane, start, end, &enterFrac, &leaveFrac, &hit );

	if ( outEnterFrac ) {
		*outEnterFrac = enterFrac;
	}
	if ( outLeaveFrac ) {
		*outLeaveFrac = leaveFrac;
	}
	if ( outHit ) {
		*outHit = hit;
	}
	if ( outResult ) {
		*outResult = result;
	}

	return QLR_EndProtectedCall();
}
