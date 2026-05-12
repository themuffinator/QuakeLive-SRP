/*
===========================================================================
Copyright (C) 1999-2005 Id Software, Inc.

This file is part of Quake III Arena source code.

Quake III Arena source code is free software; you can redistribute it
and/or modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 2 of the License,
or (at your option) any later version.

Quake III Arena source code is distributed in the hope that it will be
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
===========================================================================
*/
#include "tr_local.h"



/*
=================
R_CullTriSurf

Returns true if the grid is completely culled away.
Also sets the clipped hint bit in tess
=================
*/
static qboolean	R_CullTriSurf( srfTriangles_t *cv ) {
	int 	boxCull;

	boxCull = R_CullLocalBox( cv->bounds );

	if ( boxCull == CULL_OUT ) {
		return qtrue;
	}
	return qfalse;
}

/*
=================
R_CullGrid

Returns true if the grid is completely culled away.
Also sets the clipped hint bit in tess
=================
*/
static qboolean	R_CullGrid( srfGridMesh_t *cv ) {
	int 	boxCull;
	int 	sphereCull;

	if ( r_nocurves->integer ) {
		return qtrue;
	}

	if ( tr.currentEntityNum != ENTITYNUM_WORLD ) {
		sphereCull = R_CullLocalPointAndRadius( cv->localOrigin, cv->meshRadius );
	} else {
		sphereCull = R_CullPointAndRadius( cv->localOrigin, cv->meshRadius );
	}
	boxCull = CULL_OUT;
	
	// check for trivial reject
	if ( sphereCull == CULL_OUT )
	{
		tr.pc.c_sphere_cull_patch_out++;
		return qtrue;
	}
	// check bounding box if necessary
	else if ( sphereCull == CULL_CLIP )
	{
		tr.pc.c_sphere_cull_patch_clip++;

		boxCull = R_CullLocalBox( cv->meshBounds );

		if ( boxCull == CULL_OUT ) 
		{
			tr.pc.c_box_cull_patch_out++;
			return qtrue;
		}
		else if ( boxCull == CULL_IN )
		{
			tr.pc.c_box_cull_patch_in++;
		}
		else
		{
			tr.pc.c_box_cull_patch_clip++;
		}
	}
	else
	{
		tr.pc.c_sphere_cull_patch_in++;
	}

	return qfalse;
}


/*
================
R_CullSurface

Tries to back face cull surfaces before they are lighted or
added to the sorting list.

This will also allow mirrors on both sides of a model without recursion.
================
*/
static qboolean	R_CullSurface( surfaceType_t *surface, shader_t *shader ) {
	srfSurfaceFace_t *sface;
	float			d;

	if ( r_nocull->integer ) {
		return qfalse;
	}

	if ( *surface == SF_GRID ) {
		return R_CullGrid( (srfGridMesh_t *)surface );
	}

	if ( *surface == SF_TRIANGLES ) {
		return R_CullTriSurf( (srfTriangles_t *)surface );
	}

	if ( *surface != SF_FACE ) {
		return qfalse;
	}

	if ( shader->cullType == CT_TWO_SIDED ) {
		return qfalse;
	}

	// face culling
	if ( !r_facePlaneCull->integer ) {
		return qfalse;
	}

	sface = ( srfSurfaceFace_t * ) surface;
	d = DotProduct (tr.or.viewOrigin, sface->plane.normal);

	// don't cull exactly on the plane, because there are levels of rounding
	// through the BSP, ICD, and hardware that may cause pixel gaps if an
	// epsilon isn't allowed here 
	if ( shader->cullType == CT_FRONT_SIDED ) {
		if ( d < sface->plane.dist - 8 ) {
			return qtrue;
		}
	} else {
		if ( d > sface->plane.dist + 8 ) {
			return qtrue;
		}
	}

	return qfalse;
}


static int R_DlightFace( srfSurfaceFace_t *face, int dlightBits ) {
	float		d;
	int			i;
	dlight_t	*dl;

	for ( i = 0 ; i < tr.refdef.num_dlights ; i++ ) {
		if ( ! ( dlightBits & ( 1 << i ) ) ) {
			continue;
		}
		dl = &tr.refdef.dlights[i];
		d = DotProduct( dl->origin, face->plane.normal ) - face->plane.dist;
		if ( d < -dl->radius || d > dl->radius ) {
			// dlight doesn't reach the plane
			dlightBits &= ~( 1 << i );
		}
	}

	if ( !dlightBits ) {
		tr.pc.c_dlightSurfacesCulled++;
	}

	face->dlightBits[ tr.smpFrame ] = dlightBits;
	return dlightBits;
}

static int R_DlightGrid( srfGridMesh_t *grid, int dlightBits ) {
	int			i;
	dlight_t	*dl;

	for ( i = 0 ; i < tr.refdef.num_dlights ; i++ ) {
		if ( ! ( dlightBits & ( 1 << i ) ) ) {
			continue;
		}
		dl = &tr.refdef.dlights[i];
		if ( dl->origin[0] - dl->radius > grid->meshBounds[1][0]
			|| dl->origin[0] + dl->radius < grid->meshBounds[0][0]
			|| dl->origin[1] - dl->radius > grid->meshBounds[1][1]
			|| dl->origin[1] + dl->radius < grid->meshBounds[0][1]
			|| dl->origin[2] - dl->radius > grid->meshBounds[1][2]
			|| dl->origin[2] + dl->radius < grid->meshBounds[0][2] ) {
			// dlight doesn't reach the bounds
			dlightBits &= ~( 1 << i );
		}
	}

	if ( !dlightBits ) {
		tr.pc.c_dlightSurfacesCulled++;
	}

	grid->dlightBits[ tr.smpFrame ] = dlightBits;
	return dlightBits;
}


static int R_DlightTrisurf( srfTriangles_t *surf, int dlightBits ) {
	// FIXME: more dlight culling to trisurfs...
	surf->dlightBits[ tr.smpFrame ] = dlightBits;
	return dlightBits;
#if 0
	int			i;
	dlight_t	*dl;

	for ( i = 0 ; i < tr.refdef.num_dlights ; i++ ) {
		if ( ! ( dlightBits & ( 1 << i ) ) ) {
			continue;
		}
		dl = &tr.refdef.dlights[i];
		if ( dl->origin[0] - dl->radius > grid->meshBounds[1][0]
			|| dl->origin[0] + dl->radius < grid->meshBounds[0][0]
			|| dl->origin[1] - dl->radius > grid->meshBounds[1][1]
			|| dl->origin[1] + dl->radius < grid->meshBounds[0][1]
			|| dl->origin[2] - dl->radius > grid->meshBounds[1][2]
			|| dl->origin[2] + dl->radius < grid->meshBounds[0][2] ) {
			// dlight doesn't reach the bounds
			dlightBits &= ~( 1 << i );
		}
	}

	if ( !dlightBits ) {
		tr.pc.c_dlightSurfacesCulled++;
	}

	grid->dlightBits[ tr.smpFrame ] = dlightBits;
	return dlightBits;
#endif
}

/*
====================
R_DlightSurface

The given surface is going to be drawn, and it touches a leaf
that is touched by one or more dlights, so try to throw out
more dlights if possible.
====================
*/
static int R_DlightSurface( msurface_t *surf, int dlightBits ) {
	if ( *surf->data == SF_FACE ) {
		dlightBits = R_DlightFace( (srfSurfaceFace_t *)surf->data, dlightBits );
	} else if ( *surf->data == SF_GRID ) {
		dlightBits = R_DlightGrid( (srfGridMesh_t *)surf->data, dlightBits );
	} else if ( *surf->data == SF_TRIANGLES ) {
		dlightBits = R_DlightTrisurf( (srfTriangles_t *)surf->data, dlightBits );
	} else {
		dlightBits = 0;
	}

	if ( dlightBits ) {
		tr.pc.c_dlightSurfaces++;
	}

	return dlightBits;
}



/*
======================
R_AddWorldSurface
======================
*/
static void R_AddWorldSurface( msurface_t *surf, int dlightBits ) {
	if ( surf->viewCount == tr.viewCount ) {
		return;		// already in this view
	}

	surf->viewCount = tr.viewCount;
	// FIXME: bmodel fog?

	// try to cull before dlighting or adding
	if ( R_CullSurface( surf->data, surf->shader ) ) {
		return;
	}

	// check for dlighting
	if ( dlightBits ) {
		dlightBits = R_DlightSurface( surf, dlightBits );
		dlightBits = ( dlightBits != 0 );
	}

	R_AddDrawSurf( surf->data, surf->shader, surf->fogIndex, dlightBits );
}

/*
=============================================================

	BRUSH MODELS

=============================================================
*/

/*
=================
R_AddBrushModelSurfaces
=================
*/
void R_AddBrushModelSurfaces ( trRefEntity_t *ent ) {
	bmodel_t	*bmodel;
	int			clip;
	model_t		*pModel;
	int			i;

	pModel = R_GetModelByHandle( ent->e.hModel );

	bmodel = pModel->bmodel;

	clip = R_CullLocalBox( bmodel->bounds );
	if ( clip == CULL_OUT ) {
		return;
	}
	
	R_DlightBmodel( bmodel );

	for ( i = 0 ; i < bmodel->numSurfaces ; i++ ) {
		R_AddWorldSurface( bmodel->firstSurface + i, tr.currentEntity->needDlights );
	}
}

/*
=================
R_CullAdvertisementQuad
=================
*/
static int R_CullAdvertisementQuad( const vec3_t points[4] ) {
	cplane_t	*frust;
	float		dist;
	int			anyBack;
	int			front;
	int			back;
	int			i;
	int			j;

	if ( r_nocull->integer ) {
		return CULL_CLIP;
	}

	anyBack = 0;
	for ( i = 0 ; i < 4 ; i++ ) {
		frust = &tr.viewParms.frustum[i];
		front = 0;
		back = 0;

		for ( j = 0 ; j < 4 ; j++ ) {
			dist = DotProduct( points[j], frust->normal ) - frust->dist;
			if ( dist > 0.0f ) {
				front = 1;
				if ( back ) {
					break;
				}
			} else {
				back = 1;
			}
		}

		if ( !front ) {
			return CULL_OUT;
		}

		anyBack |= back;
	}

	if ( !anyBack ) {
		return CULL_IN;
	}

	return CULL_CLIP;
}

/*
=================
R_AddAdvertisementSurface
=================
*/
static int R_AddAdvertisementSurface( qlAdvertisement_t *advertisement ) {
	msurface_t	*surface;
	vec3_t		viewDelta;
	int			cull;

	if ( !advertisement->bmodel || advertisement->bmodel->numSurfaces <= 0 ) {
		return CULL_OUT;
	}

	surface = advertisement->bmodel->firstSurface;
	if ( surface->viewCount == tr.viewCount ) {
		return advertisement->cullState;
	}

	VectorSubtract( tr.refdef.vieworg, advertisement->center, viewDelta );
	if ( DotProduct( advertisement->normal, viewDelta ) <= 0.0f ) {
		return CULL_OUT;
	}

	surface->viewCount = tr.viewCount;
	cull = R_CullAdvertisementQuad( advertisement->points );
	if ( cull == CULL_OUT ) {
		return cull;
	}

	R_AddDrawSurf( surface->data, surface->shader, surface->fogIndex, qfalse );
	return cull;
}

static advertisementQueryEntry_t	r_advertisementQueryEntries[MAX_MAP_ADVERTISEMENTS];
static int							r_numAdvertisementQueryEntries;

static const vec4_t				r_advertisementDebugPalette[3] = {
	{ 0.5f, 0.0f, 0.0f, 1.0f },
	{ 0.5f, 0.5f, 0.0f, 1.0f },
	{ 0.0f, 0.5f, 0.0f, 1.0f }
};

#define R_DEBUG_ADVERTISEMENT_TEXT_X		25
#define R_DEBUG_ADVERTISEMENT_TEXT_Y		256
#define R_DEBUG_ADVERTISEMENT_TEXT_STEP	16
#define R_DEBUG_ADVERTISEMENT_TEXT_SCALE	( 16.0f / 48.0f )

/*
=================
R_UpdateAdvertisements
=================
*/
void R_UpdateAdvertisements( void ) {
	qlAdvertisement_t	*advertisement;
	advertisementQueryEntry_t	*entry;
	int					cull;
	int					i;

	r_numAdvertisementQueryEntries = 0;

	if ( !tr.world || tr.world->numAdvertisements <= 0 ) {
		return;
	}

	tr.currentEntity = &tr.worldEntity;

	for ( i = 0 ; i < tr.world->numAdvertisements ; i++ ) {
		advertisement = &tr.world->advertisements[i];
		if ( tr.frameSceneNum == 1 ) {
			advertisement->cullState = CULL_OUT;
			advertisement->queryListIndex = -1;
			advertisement->viewArea = 0;
			advertisement->projectedNormalX = 0.0f;
			advertisement->projectedNormalY = 0.0f;
		}

		if ( !advertisement->bmodel ) {
			continue;
		}

		if ( !R_inPVS( tr.refdef.vieworg, advertisement->center ) ) {
			continue;
		}

		cull = R_AddAdvertisementSurface( advertisement );
		if ( tr.frameSceneNum != 1 || cull == CULL_OUT ) {
			continue;
		}

		advertisement->cullState = cull;
		advertisement->viewArea = tr.refdef.width * tr.refdef.height;
		advertisement->projectedNormalX = DotProduct( tr.refdef.viewaxis[1], advertisement->normal );
		advertisement->projectedNormalY = DotProduct( tr.refdef.viewaxis[2], advertisement->normal );

		if ( !qglBeginQueryARB || !qglEndQueryARB || cull != CULL_IN ||
			r_numAdvertisementQueryEntries >= MAX_MAP_ADVERTISEMENTS ) {
			continue;
		}

		entry = &r_advertisementQueryEntries[r_numAdvertisementQueryEntries];
		entry->occlusionQueryIds[0] = advertisement->occlusionQueryIds[0];
		entry->occlusionQueryIds[1] = advertisement->occlusionQueryIds[1];
		Com_Memcpy( entry->points, advertisement->points, sizeof( entry->points ) );

		advertisement->queryListIndex = r_numAdvertisementQueryEntries;
		r_numAdvertisementQueryEntries++;
	}
}

/*
=================
R_QueueAdvertisementQueryCmd
=================
*/
void R_QueueAdvertisementQueryCmd( void ) {
	if ( r_numAdvertisementQueryEntries <= 0 ) {
		return;
	}

	R_AddAdvertisementQueryCmd( r_advertisementQueryEntries, r_numAdvertisementQueryEntries );
}

/*
=================
R_ShutdownAdvertisements
=================
*/
void R_ShutdownAdvertisements( void ) {
	qlAdvertisement_t	*advertisement;
	int					i;

	r_numAdvertisementQueryEntries = 0;

	if ( !tr.world || !tr.world->advertisements || tr.world->numAdvertisements <= 0 ) {
		return;
	}

	for ( i = 0 ; i < tr.world->numAdvertisements ; i++ ) {
		advertisement = &tr.world->advertisements[i];
		if ( qglDeleteQueriesARB && advertisement->occlusionQueryIds[0] != 0 ) {
			qglDeleteQueriesARB( 2, advertisement->occlusionQueryIds );
		}

		advertisement->cullState = CULL_OUT;
		advertisement->occlusionQueryIds[0] = 0;
		advertisement->occlusionQueryIds[1] = 0;
		advertisement->queryListIndex = -1;
		advertisement->viewArea = 0;
		advertisement->projectedNormalX = 0.0f;
		advertisement->projectedNormalY = 0.0f;
	}
}

/*
=================
R_GetAdvertisementDebugColor
=================
*/
static const vec4_t *R_GetAdvertisementDebugColor( int displayState ) {
	if ( displayState < 0 || displayState >= 3 ) {
		return &r_advertisementDebugPalette[0];
	}

	return &r_advertisementDebugPalette[displayState];
}

/*
=================
R_DrawAdvertisementDebugText
=================
*/
static void R_DrawAdvertisementDebugText( int y, const char *text, const vec4_t color ) {
	if ( !text || !text[0] ) {
		return;
	}

	RE_DrawScaledText( R_DEBUG_ADVERTISEMENT_TEXT_X, y, text,
		0, R_DEBUG_ADVERTISEMENT_TEXT_SCALE, 0, NULL, qtrue, color );
}

/*
=================
R_DrawAdvertisementDebugQuad
=================
*/
static void R_DrawAdvertisementDebugQuad( const vec3_t points[4], const vec4_t color ) {
	int		i;

	qglColor4f( color[0], color[1], color[2], color[3] );
	qglBegin( GL_LINE_LOOP );
	for ( i = 0 ; i < 4 ; i++ ) {
		qglVertex3fv( points[i] );
	}
	qglEnd();
}

/*
=================
R_DrawAdvertisementDebugNormal
=================
*/
static void R_DrawAdvertisementDebugNormal( const qlAdvertisement_t *advertisement ) {
	vec3_t		endPoint;

	if ( !advertisement ) {
		return;
	}

	VectorMA( advertisement->center, 100.0f, advertisement->normal, endPoint );

	qglColor4f( 1.0f, 1.0f, 1.0f, 1.0f );
	qglBegin( GL_LINES );
	qglVertex3fv( advertisement->center );
	qglVertex3fv( endPoint );
	qglEnd();
}

/*
=================
R_DebugAdvertisements
=================
*/
void R_DebugAdvertisements( void ) {
	qlAdvertisement_t	*advertisement;
	const vec4_t		*color;
	char				buffer[256];
	int					count;
	int					displayState;
	int					i;
	int					lineY;

	if ( !r_debugAds || !r_debugAds->integer || tr.viewParms.frameSceneNum != 1 ) {
		return;
	}

	if ( !tr.world || tr.world->numAdvertisements <= 0 ) {
		return;
	}

	R_SyncRenderThread();
	GL_Bind( tr.whiteImage );
	GL_Cull( CT_TWO_SIDED );

	lineY = R_DEBUG_ADVERTISEMENT_TEXT_Y;

	for ( i = 0 ; i < tr.world->numAdvertisements ; i++ ) {
		advertisement = &tr.world->advertisements[i];
		if ( advertisement->cullState == CULL_OUT ) {
			continue;
		}

		displayState = 0;
		if ( ri.AdvertisementBridge_GetCellDisplayState ) {
			displayState = ri.AdvertisementBridge_GetCellDisplayState( advertisement->cellId );
		}
		color = R_GetAdvertisementDebugColor( displayState );

		buffer[0] = '\0';
		if ( ri.AdvertisementBridge_GetCellLabel ) {
			ri.AdvertisementBridge_GetCellLabel( advertisement->cellId, buffer, sizeof( buffer ) );
		}
		R_DrawAdvertisementDebugText( lineY, buffer, *color );
		lineY += R_DEBUG_ADVERTISEMENT_TEXT_STEP;

		GL_State( GLS_SRCBLEND_ONE | GLS_DSTBLEND_ONE );
		R_DrawAdvertisementDebugQuad( advertisement->points, *color );
		GL_State( GLS_SRCBLEND_SRC_ALPHA | GLS_DSTBLEND_ONE_MINUS_SRC_ALPHA );
		R_DrawAdvertisementDebugNormal( advertisement );
	}

	if ( ri.AdvertisementBridge_GetLabelList1Count && ri.AdvertisementBridge_GetLabelList1Entry ) {
		count = ri.AdvertisementBridge_GetLabelList1Count();
		for ( i = 0 ; i < count ; i++ ) {
			buffer[0] = '\0';
			ri.AdvertisementBridge_GetLabelList1Entry( i, buffer, sizeof( buffer ) );
			R_DrawAdvertisementDebugText( lineY, buffer, colorWhite );
			lineY += R_DEBUG_ADVERTISEMENT_TEXT_STEP;
		}
	}

	if ( ri.AdvertisementBridge_GetLabelList2Count && ri.AdvertisementBridge_GetLabelList2Entry ) {
		count = ri.AdvertisementBridge_GetLabelList2Count();
		for ( i = 0 ; i < count ; i++ ) {
			buffer[0] = '\0';
			ri.AdvertisementBridge_GetLabelList2Entry( i, buffer, sizeof( buffer ) );
			R_DrawAdvertisementDebugText( lineY, buffer, colorWhite );
			lineY += R_DEBUG_ADVERTISEMENT_TEXT_STEP;
		}
	}

	GL_Cull( CT_BACK_SIDED );
	GL_State( GLS_DEFAULT );
}

/*
=================
R_AdvertisementList_f
=================
*/
void R_AdvertisementList_f( void ) {
	qlAdvertisement_t	*advertisement;
	bmodel_t			*bmodel;
	msurface_t			*surface;
	const char			*shaderName;
	int					bmodelIndex;
	int					i;

	if ( !tr.world ) {
		ri.Printf( PRINT_ALL, "advertlist: no world model loaded\n" );
		return;
	}

	if ( tr.world->numAdvertisements <= 0 ) {
		ri.Printf( PRINT_ALL, "advertlist: world=%s loaded=0\n", tr.world->name );
		return;
	}

	ri.Printf( PRINT_ALL, "advertlist: world=%s loaded=%d\n",
		tr.world->name,
		tr.world->numAdvertisements );

	for ( i = 0 ; i < tr.world->numAdvertisements ; i++ ) {
		advertisement = &tr.world->advertisements[i];
		bmodel = advertisement->bmodel;
		surface = ( bmodel && bmodel->numSurfaces > 0 ) ? bmodel->firstSurface : NULL;
		shaderName = ( surface && surface->shader && surface->shader->name[0] ) ? surface->shader->name : "<null>";
		bmodelIndex = bmodel ? (int)( bmodel - tr.world->bmodels ) : -1;

		ri.Printf( PRINT_ALL,
			"advertlist: [%d] cellId=%d sourceIndex=%d model=*%d surfaces=%d shader=%s center=(%.1f %.1f %.1f) normal=(%.3f %.3f %.3f)\n",
			i,
			advertisement->cellId,
			advertisement->sourceIndex,
			bmodelIndex,
			bmodel ? bmodel->numSurfaces : 0,
			shaderName,
			advertisement->center[0],
			advertisement->center[1],
			advertisement->center[2],
			advertisement->normal[0],
			advertisement->normal[1],
			advertisement->normal[2] );
		ri.Printf( PRINT_ALL,
			"advertlist:      points=(%.1f %.1f %.1f) (%.1f %.1f %.1f) (%.1f %.1f %.1f) (%.1f %.1f %.1f)\n",
			advertisement->points[0][0],
			advertisement->points[0][1],
			advertisement->points[0][2],
			advertisement->points[1][0],
			advertisement->points[1][1],
			advertisement->points[1][2],
			advertisement->points[2][0],
			advertisement->points[2][1],
			advertisement->points[2][2],
			advertisement->points[3][0],
			advertisement->points[3][1],
			advertisement->points[3][2] );
	}
}


/*
=============================================================

	WORLD MODEL

=============================================================
*/


/*
================
R_RecursiveWorldNode
================
*/
static void R_RecursiveWorldNode( mnode_t *node, int planeBits, int dlightBits ) {

	do {
		int			newDlights[2];

		// if the node wasn't marked as potentially visible, exit
		if (node->visframe != tr.visCount) {
			return;
		}

		// if the bounding volume is outside the frustum, nothing
		// inside can be visible OPTIMIZE: don't do this all the way to leafs?

		if ( !r_nocull->integer ) {
			int		r;

			if ( planeBits & 1 ) {
				r = BoxOnPlaneSide(node->mins, node->maxs, &tr.viewParms.frustum[0]);
				if (r == 2) {
					return;						// culled
				}
				if ( r == 1 ) {
					planeBits &= ~1;			// all descendants will also be in front
				}
			}

			if ( planeBits & 2 ) {
				r = BoxOnPlaneSide(node->mins, node->maxs, &tr.viewParms.frustum[1]);
				if (r == 2) {
					return;						// culled
				}
				if ( r == 1 ) {
					planeBits &= ~2;			// all descendants will also be in front
				}
			}

			if ( planeBits & 4 ) {
				r = BoxOnPlaneSide(node->mins, node->maxs, &tr.viewParms.frustum[2]);
				if (r == 2) {
					return;						// culled
				}
				if ( r == 1 ) {
					planeBits &= ~4;			// all descendants will also be in front
				}
			}

			if ( planeBits & 8 ) {
				r = BoxOnPlaneSide(node->mins, node->maxs, &tr.viewParms.frustum[3]);
				if (r == 2) {
					return;						// culled
				}
				if ( r == 1 ) {
					planeBits &= ~8;			// all descendants will also be in front
				}
			}

		}

		if ( node->contents != -1 ) {
			break;
		}

		// node is just a decision point, so go down both sides
		// since we don't care about sort orders, just go positive to negative

		// determine which dlights are needed
		newDlights[0] = 0;
		newDlights[1] = 0;
		if ( dlightBits ) {
			int	i;

			for ( i = 0 ; i < tr.refdef.num_dlights ; i++ ) {
				dlight_t	*dl;
				float		dist;

				if ( dlightBits & ( 1 << i ) ) {
					dl = &tr.refdef.dlights[i];
					dist = DotProduct( dl->origin, node->plane->normal ) - node->plane->dist;
					
					if ( dist > -dl->radius ) {
						newDlights[0] |= ( 1 << i );
					}
					if ( dist < dl->radius ) {
						newDlights[1] |= ( 1 << i );
					}
				}
			}
		}

		// recurse down the children, front side first
		R_RecursiveWorldNode (node->children[0], planeBits, newDlights[0] );

		// tail recurse
		node = node->children[1];
		dlightBits = newDlights[1];
	} while ( 1 );

	{
		// leaf node, so add mark surfaces
		int			c;
		msurface_t	*surf, **mark;

		tr.pc.c_leafs++;

		// add to z buffer bounds
		if ( node->mins[0] < tr.viewParms.visBounds[0][0] ) {
			tr.viewParms.visBounds[0][0] = node->mins[0];
		}
		if ( node->mins[1] < tr.viewParms.visBounds[0][1] ) {
			tr.viewParms.visBounds[0][1] = node->mins[1];
		}
		if ( node->mins[2] < tr.viewParms.visBounds[0][2] ) {
			tr.viewParms.visBounds[0][2] = node->mins[2];
		}

		if ( node->maxs[0] > tr.viewParms.visBounds[1][0] ) {
			tr.viewParms.visBounds[1][0] = node->maxs[0];
		}
		if ( node->maxs[1] > tr.viewParms.visBounds[1][1] ) {
			tr.viewParms.visBounds[1][1] = node->maxs[1];
		}
		if ( node->maxs[2] > tr.viewParms.visBounds[1][2] ) {
			tr.viewParms.visBounds[1][2] = node->maxs[2];
		}

		// add the individual surfaces
		mark = node->firstmarksurface;
		c = node->nummarksurfaces;
		while (c--) {
			// the surface may have already been added if it
			// spans multiple leafs
			surf = *mark;
			R_AddWorldSurface( surf, dlightBits );
			mark++;
		}
	}

}


/*
===============
R_PointInLeaf
===============
*/
static mnode_t *R_PointInLeaf( const vec3_t p ) {
	mnode_t		*node;
	float		d;
	cplane_t	*plane;
	
	if ( !tr.world ) {
		ri.Error (ERR_DROP, "R_PointInLeaf: bad model");
	}

	node = tr.world->nodes;
	while( 1 ) {
		if (node->contents != -1) {
			break;
		}
		plane = node->plane;
		d = DotProduct (p,plane->normal) - plane->dist;
		if (d > 0) {
			node = node->children[0];
		} else {
			node = node->children[1];
		}
	}
	
	return node;
}

/*
==============
R_ClusterPVS
==============
*/
static const byte *R_ClusterPVS (int cluster) {
	if (!tr.world || !tr.world->vis || cluster < 0 || cluster >= tr.world->numClusters ) {
		return tr.world->novis;
	}

	return tr.world->vis + cluster * tr.world->clusterBytes;
}

/*
=================
R_inPVS
=================
*/
qboolean R_inPVS( const vec3_t p1, const vec3_t p2 ) {
	mnode_t *leaf;
	byte	*vis;

	leaf = R_PointInLeaf( p1 );
	vis = CM_ClusterPVS( leaf->cluster );
	leaf = R_PointInLeaf( p2 );

	if ( !(vis[leaf->cluster>>3] & (1<<(leaf->cluster&7))) ) {
		return qfalse;
	}
	return qtrue;
}

/*
===============
R_MarkLeaves

Mark the leaves and nodes that are in the PVS for the current
cluster
===============
*/
static void R_MarkLeaves (void) {
	const byte	*vis;
	mnode_t	*leaf, *parent;
	int		i;
	int		cluster;

	// lockpvs lets designers walk around to determine the
	// extent of the current pvs
	if ( r_lockpvs->integer ) {
		return;
	}

	// current viewcluster
	leaf = R_PointInLeaf( tr.viewParms.pvsOrigin );
	cluster = leaf->cluster;

	// if the cluster is the same and the area visibility matrix
	// hasn't changed, we don't need to mark everything again

	// if r_showcluster was just turned on, remark everything 
	if ( tr.viewCluster == cluster && !tr.refdef.areamaskModified 
		&& !r_showcluster->modified ) {
		return;
	}

	if ( r_showcluster->modified || r_showcluster->integer ) {
		r_showcluster->modified = qfalse;
		if ( r_showcluster->integer ) {
			ri.Printf( PRINT_ALL, "cluster:%i  area:%i\n", cluster, leaf->area );
		}
	}

	tr.visCount++;
	tr.viewCluster = cluster;

	if ( r_novis->integer || tr.viewCluster == -1 ) {
		for (i=0 ; i<tr.world->numnodes ; i++) {
			if (tr.world->nodes[i].contents != CONTENTS_SOLID) {
				tr.world->nodes[i].visframe = tr.visCount;
			}
		}
		return;
	}

	vis = R_ClusterPVS (tr.viewCluster);
	
	for (i=0,leaf=tr.world->nodes ; i<tr.world->numnodes ; i++, leaf++) {
		cluster = leaf->cluster;
		if ( cluster < 0 || cluster >= tr.world->numClusters ) {
			continue;
		}

		// check general pvs
		if ( !(vis[cluster>>3] & (1<<(cluster&7))) ) {
			continue;
		}

		// check for door connection
		if ( (tr.refdef.areamask[leaf->area>>3] & (1<<(leaf->area&7)) ) ) {
			continue;		// not visible
		}

		parent = leaf;
		do {
			if (parent->visframe == tr.visCount)
				break;
			parent->visframe = tr.visCount;
			parent = parent->parent;
		} while (parent);
	}
}


/*
=============
R_AddWorldSurfaces
=============
*/
void R_AddWorldSurfaces (void) {
	if ( !r_drawworld->integer ) {
		return;
	}

	if ( tr.refdef.rdflags & RDF_NOWORLDMODEL ) {
		return;
	}

	tr.currentEntityNum = ENTITYNUM_WORLD;
	tr.currentEntity = &tr.worldEntity;
	tr.shiftedEntityNum = tr.currentEntityNum << QSORT_ENTITYNUM_SHIFT;

	// determine which leaves are in the PVS / areamask
	R_MarkLeaves ();

	// clear out the visible min/max
	ClearBounds( tr.viewParms.visBounds[0], tr.viewParms.visBounds[1] );

	// perform frustum culling and add all the potentially visible surfaces
	if ( tr.refdef.num_dlights > 32 ) {
		tr.refdef.num_dlights = 32 ;
	}
	R_RecursiveWorldNode( tr.world->nodes, 15, ( 1 << tr.refdef.num_dlights ) - 1 );
}
