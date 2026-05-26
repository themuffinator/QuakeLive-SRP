from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_exposes_retail_memory_image_helper_family() -> None:
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "image_t\t\t*R_CreateImageWithTarget" in tr_local
	assert "int\t\t\tR_DetectImageTypeFromMemory( const byte *buffer, int bufferLength );" in tr_local
	assert "image_t\t\t*R_LoadImageFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipmap" in tr_local

	assert "image_t *R_CreateImageWithTarget( const char *name, const byte *pic, int width, int height," in tr_image
	assert "int R_DetectImageTypeFromMemory( const byte *buffer, int bufferLength ) {" in tr_image
	assert "image_t *R_LoadImageFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipmap, qboolean allowPicmip ) {" in tr_image


def test_public_image_constructor_wraps_target_aware_helper() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "return R_CreateImageWithTarget( name, pic, width, height, mipmap, allowPicmip, glWrapClampMode, GL_TEXTURE_2D );" in tr_image
	assert "qglTexParameterf( glTarget, GL_TEXTURE_WRAP_S, glWrapClampMode );" in tr_image
	assert "qglTexParameterf( glTarget, GL_TEXTURE_WRAP_T, glWrapClampMode );" in tr_image


def test_upload32_keeps_retail_target_and_forced_sample_details() -> None:
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_image = _read("src/code/renderer/tr_image.c")
	upload_block = tr_image[
		tr_image.index("static void Upload32( unsigned *data,"):
		tr_image.index("image_t *R_CreateImageWithTarget")
	]
	create_block = tr_image[
		tr_image.index("image_t *R_CreateImageWithTarget"):
		tr_image.index("image_t *R_CreateImage( const char *name")
	]
	update_block = tr_image[
		tr_image.index("image_t *R_UpdateImage("):
		tr_image.index("int R_DetectImageTypeFromMemory")
	]

	assert "#define GL_TEXTURE_RECTANGLE_ARB 0x84F5" in tr_local
	assert "static int R_ForcedImageSamples( const char *name ) {" in tr_image
	assert 'if ( name && !strcmp( name, "browser" ) ) {' in tr_image
	assert "void\tGL_BindToTarget( image_t *image, int glTarget );" in tr_local
	assert "GL_BindToTarget( image, glTarget );" in create_block
	assert "int forcedSamples," in upload_block
	assert "if ( glTarget != GL_TEXTURE_RECTANGLE_ARB ) {" in upload_block
	assert "scaled_width = width;" in upload_block
	assert "scaled_height = height;" in upload_block
	assert "if ( forcedSamples > 0 ) {" in upload_block
	assert "samples = forcedSamples;" in upload_block
	assert "qglGenTextures( 1, &image->texnum );" in create_block
	assert "image->texnum = 1024 + tr.numImages;" in create_block
	assert "forcedSamples = R_ForcedImageSamples( name );" in create_block
	assert "forcedSamples = R_ForcedImageSamples( name );" in update_block


def test_implicit_nomip_shaders_use_retail_edge_clamp() -> None:
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	assert "#define GL_CLAMP_TO_EDGE 0x812F" in tr_local
	assert "int\t\t\twrapClampMode;\t\t// GL_CLAMP, GL_CLAMP_TO_EDGE, or GL_REPEAT" in tr_local
	assert 'case GL_CLAMP_TO_EDGE:\n\t\t\tri.Printf( PRINT_ALL, "edge " );' in tr_image
	assert "image = R_FindImageFile( fileName, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP_TO_EDGE );" in tr_shader


def test_image_list_uses_retail_internal_format_labels() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	image_list_block = tr_image[
		tr_image.index("void R_ImageList_f( void ) {"):
		tr_image.index("//=======================================================================")
	]

	assert 'case GL_RGB8:\n\t\t\tri.Printf( PRINT_ALL, "RGB8 " );' in image_list_block
	assert 'ri.Printf( PRINT_ALL, "RGB8" );' not in image_list_block
	assert 'case GL_RGBA8:\n\t\t\tri.Printf( PRINT_ALL, "RGBA8" );' in image_list_block


def test_memory_loader_dispatches_buffer_decoders_and_warns_on_unknown_payloads() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")

	assert "switch ( R_DetectImageTypeFromMemory( buffer, bufferLength ) ) {" in tr_image
	assert "LoadJPGFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadBMPFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadTGAFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert "LoadPNGFromBuffer( name, buffer, bufferLength, &pic, &width, &height );" in tr_image
	assert 'ri.Printf( PRINT_WARNING, "WARNING: R_LoadImageFromMemory() Unable to detect image type.\\n" );' in tr_image
	assert "image = R_FindLoadedImage( name, mipmap, allowPicmip, GL_CLAMP );" in tr_image
	assert "image = R_CreateImageWithTarget( name, pic, width, height, mipmap, allowPicmip, GL_CLAMP, GL_TEXTURE_2D );" in tr_image


def test_memory_type_detector_uses_retail_selector_values_and_magic_offsets() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	detector_block = tr_image[
		tr_image.index("int R_DetectImageTypeFromMemory( const byte *buffer, int bufferLength ) {"):
		tr_image.index("image_t *R_LoadImageFromMemory")
	]

	assert "typedef enum {\n\tIMAGETYPE_MEMORY_JPG,\n\tIMAGETYPE_MEMORY_BMP,\n\tIMAGETYPE_MEMORY_TGA,\n\tIMAGETYPE_MEMORY_PNG,\n\tIMAGETYPE_MEMORY_UNKNOWN\n} imageMemoryType_t;" in tr_image
	assert "if ( bufferLength >= 4 && buffer[1] == 'P' && buffer[2] == 'N' && buffer[3] == 'G' ) {" in detector_block
	assert "if ( buffer[0] == 'B' && buffer[1] == 'M' ) {" in detector_block
	assert "if ( bufferLength >= 10 && buffer[6] == 'J' && buffer[7] == 'F' && buffer[8] == 'I' && buffer[9] == 'F' ) {" in detector_block
	assert "if ( buffer[1] == 0 &&" in detector_block
	assert "( buffer[2] == 3 || ( ( buffer[2] == 2 || buffer[2] == 10 ) && ( buffer[16] == 24 || buffer[16] == 32 ) ) ) ) {" in detector_block
	assert "pngSignature" not in detector_block
	assert "png_sig_cmp" not in detector_block


def test_disk_tga_path_prefers_retail_jpg_png_fallbacks_before_tga() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	load_block = tr_image[
		tr_image.index("void R_LoadImage( const char *name, byte **pic, int *width, int *height ) {"):
		tr_image.index("image_t\t*R_FindImageFile")
	]

	assert "char altname[MAX_QPATH];\t\t\t// try jpg / png in place of tga" in load_block
	assert load_block.index("altname[len-3] = 'j';") < load_block.index("LoadJPG( altname, pic, width, height );")
	assert load_block.index("LoadJPG( altname, pic, width, height );") < load_block.index("altname[len-3] = 'p';")
	assert load_block.index("altname[len-3] = 'p';") < load_block.index("LoadPNG( altname, pic, width, height );")
	assert load_block.index("LoadPNG( altname, pic, width, height );") < load_block.index("LoadTGA( name, pic, width, height );")


def test_png_memory_loader_keeps_retail_format_expansion_without_private_gamma_transform() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	png_block = tr_image[
		tr_image.index("static void LoadPNGFromBuffer( const char *name, const byte *buffer, int bufferLength, byte **pic, int *width, int *height ) {"):
		tr_image.index("static void LoadPNG( const char *name, byte **pic, int *width, int *height ) {")
	]

	assert "png_set_expand( png_ptr );" in png_block
	assert "png_set_gray_to_rgb( png_ptr );" in png_block
	assert "png_set_strip_16( png_ptr );" in png_block
	assert "png_set_filler( png_ptr, 0xff, PNG_FILLER_AFTER );" in png_block
	assert "png_read_update_info( png_ptr, info_ptr );" in png_block
	assert "png_set_gamma" not in png_block
	assert "png_get_gAMA" not in png_block
	assert "png_get_sRGB" not in png_block
	assert "png_set_sRGB_gAMA_and_cHRM" not in png_block


def test_live_client_resource_registration_uses_renderer_memory_lane() -> None:
	cl_main = _read("src/code/client/cl_main.c")
	steam_resources = _read("src/code/client/cl_steam_resources.c")

	assert "qhandle_t CL_RegisterShaderFromRGBA( const char *name, const byte *pic, int width, int height, qboolean mipRawImage ) {" in cl_main
	assert "qhandle_t CL_RegisterShaderFromMemory( const char *name, const byte *buffer, int bufferLength, qboolean mipRawImage ) {" in cl_main
	assert "image = R_CreateImage( name, pic, width, height, mipRawImage, mipRawImage, mipRawImage ? GL_REPEAT : GL_CLAMP );" in cl_main
	assert "image = R_LoadImageFromMemory( name, buffer, bufferLength, mipRawImage, mipRawImage );" in cl_main

	assert "CL_SteamResources_BuildRendererName( url, slot, rendererName, sizeof( rendererName ) );" in steam_resources
	assert "shader = CL_RegisterShaderFromRGBA( rendererName, rgbaPixels, width, height, qfalse );" in steam_resources
	assert "shader = CL_RegisterShaderFromMemory( rendererName, buffer, bufferLength, qfalse );" in steam_resources
	assert "CL_SteamResources_EncodeAvatarTGA" not in steam_resources
	assert "CL_SteamResources_WriteCacheFile" not in steam_resources
