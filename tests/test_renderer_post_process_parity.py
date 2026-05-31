from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def _read(rel_path: str) -> str:
	return (REPO_ROOT / rel_path).read_text(encoding="utf-8")


def test_renderer_post_process_pipeline_uses_retail_shader_family() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")

	assert '"scripts/brightpass.fs"' in tr_backend
	assert '"scripts/downsample1.fs"' in tr_backend
	assert '"scripts/blurvertical.fs"' in tr_backend
	assert '"scripts/blurhoriz.fs"' in tr_backend
	assert '"scripts/combine.fs"' in tr_backend
	assert '"scripts/colorcorrect.fs"' in tr_backend
	assert '"scripts/posteffect.vs"' in tr_backend
	assert "GL_TEXTURE_RECTANGLE_ARB" in tr_backend
	assert "sampler2DRect" in tr_backend
	assert 'ri.Printf( PRINT_WARNING, "Post Process Failure - unable to create FBO : %d (%x)\\n", status, status );' in tr_backend
	assert 'ri.Printf( PRINT_WARNING, "GL_ARB_Multitexture is either not supported, or is disabled by r_ext_multiTexture. Post processing is disabled.\\n" );' in tr_backend


def test_runtime_probes_keep_multitexture_enabled_for_post_process() -> None:
	client_probe = _read("tools/client/run_client_runtime_probe.ps1")
	qcommon_probe = _read("tools/qcommon/run_qcommon_runtime_probe.ps1")

	assert "'+set', 'r_ext_multitexture', '1'" in client_probe
	assert "'+set', 'r_ext_multitexture', '1'" in qcommon_probe
	assert "'+set', 'r_ext_multitexture', '0'" not in client_probe
	assert "'+set', 'r_ext_multitexture', '0'" not in qcommon_probe


def test_color_correct_is_shader_backed_and_surfaces_retail_controls() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	color_uniform_block = _extract_function_block(tr_backend, "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {")
	color_uniform_from_cvars_block = _extract_function_block(tr_backend, "void RBPP_SetColorCorrectUniformsFromCvars( void ) {")
	color_correct_pass_block = _extract_function_block(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")
	color_correct_init_block = _extract_function_block(tr_backend, "static qboolean RBPP_InitColorCorrectResources( void ) {")

	assert "qglGetTexImage(" not in tr_backend
	assert "qglCopyTexSubImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, 0, 0, 0, 0, glConfig.vidWidth, glConfig.vidHeight );" in tr_backend
	assert '"p_gammaRecip"' in tr_backend
	assert '"p_overbright"' in tr_backend
	assert '"p_contrast"' in tr_backend
	assert 'r_contrast = ri.Cvar_Get( "r_contrast", "1.0", CVAR_ARCHIVE | CVAR_CLOUD );' in tr_init
	assert 'web_browserActive = ri.Cvar_Get( "web_browserActive", "0", CVAR_ROM );' in tr_init
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {" in color_uniform_block
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_contrast ) {" in color_uniform_block
	assert "\t\tcontrast = r_contrast->value;" in color_uniform_block
	assert "overbright = 2.0f * r_overBrightBits->integer;" in color_uniform_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.gammaRecipUniform, gammaRecip );" in color_uniform_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.overbrightUniform, overbright );" in color_uniform_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.colorCorrectProgram.contrastUniform, contrast );" in color_uniform_block
	assert "if ( !RBPP_ColorCorrectEnabled() ) {" in color_uniform_from_cvars_block
	assert "RBPP_SetColorCorrectUniforms( qtrue );" in color_uniform_from_cvars_block
	assert "RBPP_SetColorCorrectUniforms( qfalse );" in color_correct_init_block
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in color_correct_pass_block
	assert "qglUniform1fARBFunc" not in color_correct_pass_block
	assert "color *= p_overbright;" in tr_backend


def test_bloom_controls_and_active_mirrors_are_backend_validated() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_public = _read("src/code/renderer/tr_public.h")
	cl_main = _read("src/code/client/cl_main.c")
	bloom_enabled_block = _extract_function_block(tr_backend, "static qboolean RBPP_BloomEnabled( void ) {")
	bloom_init_block = _extract_function_block(tr_backend, "static qboolean RBPP_InitBloomResources( void ) {")
	bloom_shutdown_block = _extract_function_block(tr_backend, "static void RBPP_ShutdownBloomResources( void ) {")
	rebuild_block = _extract_function_block(tr_backend, "static void RBPP_RebuildState( void ) {")
	bloom_command_block = _extract_function_block(tr_backend, "static const void *RB_BloomPostProcessCommand( const void *data ) {")
	color_command_block = _extract_function_block(tr_backend, "static const void *RB_ColorCorrectPostProcessCommand( const void *data ) {")

	assert 'cvar_t\t*(*Cvar_GetBounded)( const char *name, const char *value, const char *minValue, const char *maxValue, int flags );' in tr_public
	assert "ri.Cvar_GetBounded = Cvar_GetBounded;" in cl_main
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' in tr_init
	assert 'r_bloomPasses = ri.Cvar_GetBounded( "r_bloomPasses", "1", "1", "2", CVAR_ARCHIVE | CVAR_LATCH | CVAR_PROTECTED | CVAR_VM_CREATED | CVAR_BOUNDED_DISCRETE | CVAR_CLOUD );' not in tr_init
	assert "AssertCvarRange( r_enableBloom, 0, 2, qtrue );" in tr_init
	assert "static int RBPP_GetBloomMode( void ) {" in tr_backend
	assert "bloomMode = RBPP_GetBloomMode();" in tr_backend
	assert "if ( bloomMode == 2 ) {" in tr_backend
	assert "if ( !RB_PostProcessEnabled() ) {" in bloom_enabled_block
	assert "if ( !s_postProcess.supported ) {" in bloom_enabled_block
	assert "if ( !r_bloomActive || !r_bloomActive->integer ) {" in bloom_enabled_block
	assert "RBPP_CreateRenderTarget( &s_postProcess.sceneTarget, width, height, qfalse )" in bloom_init_block
	assert "targets[0] = &s_postProcess.sceneTarget;" in bloom_shutdown_block
	assert bloom_shutdown_block.index("RBPP_DestroyBloomPrograms();") < bloom_shutdown_block.index("qglDeleteTextures") < bloom_shutdown_block.index("qglDeleteFramebuffersEXTFunc") < bloom_shutdown_block.index("qglDeleteRenderbuffersEXTFunc")
	assert 'ri.Cvar_Set( "r_bloomActive", "0" );' in bloom_shutdown_block
	assert "RBPP_CreateRenderTarget( &s_postProcess.sceneTarget" not in rebuild_block
	assert "if ( cmd->sceneTexture && RBPP_BloomEnabled() && s_postProcess.sceneTarget.initialized ) {" in bloom_command_block
	assert '"p_blurStep"' not in tr_backend
	assert '"p_blurFalloff"' not in tr_backend
	assert "tr.postProcessActive = backEnd.postProcessActive;" in tr_backend
	assert "tr.bloomActive = backEnd.bloomActive;" in tr_backend
	assert "tr.colorCorrectActive = backEnd.colorCorrectActive;" in tr_backend
	assert 'ri.Cvar_Set( "r_postProcessActive", backEnd.postProcessActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_bloomActive", backEnd.bloomActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_colorCorrectActive", backEnd.colorCorrectActive ? "1" : "0" );' in tr_backend
	assert 'ri.Cvar_Set( "r_postProcessActive", tr.postProcessActive ? "1" : "0" );' not in tr_init
	assert 'ri.Cvar_Set( "r_bloomActive", tr.bloomActive ? "1" : "0" );' not in tr_init
	assert 'ri.Cvar_Set( "r_colorCorrectActive", tr.colorCorrectActive ? "1" : "0" );' not in tr_init
	assert 'passes = ( r_bloomPasses && r_bloomPasses->integer > 0 ) ? r_bloomPasses->integer : 1;' not in tr_backend
	assert "RBPP_BindRenderTarget( &s_postProcess.bloomDownsampleTarget );" in tr_backend
	assert "RBPP_BindRenderTarget( &s_postProcess.bloomQuarterDownsampleTarget );" in tr_backend
	assert "qglOrtho( 0, width, height, 0, 0, 1 );" in tr_backend
	assert "RB_SetGL2D();" not in _extract_function_block(tr_backend, "static void RBPP_Set2DState( int width, int height ) {")
	assert "if ( cmd->colorCorrectTexture && cmd->colorCorrectProgram && RBPP_ColorCorrectEnabled() ) {" in color_command_block
	assert "\t\tRBPP_ApplyColorCorrectPass( cmd );" in color_command_block
	assert "qglBindTexture( GL_TEXTURE_RECTANGLE_ARB, cmd->colorCorrectTexture );" in tr_backend
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->colorCorrectProgram );" in tr_backend
	assert "approximate Quake Live" not in tr_backend


def test_post_process_commands_match_retail_backend_command_wiring() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_cmds = _read("src/code/renderer/tr_cmds.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_shader = _read("src/code/renderer/tr_shader.c")

	command_enum = tr_local[tr_local.index("typedef enum {"):tr_local.index("} renderCommand_t;")]
	for earlier, later in (
		("RC_SCREENSHOT", "RC_SUB_IMAGE"),
		("RC_SUB_IMAGE", "RC_ADVERTISEMENT_QUERIES"),
		("RC_ADVERTISEMENT_QUERIES", "RC_COLOR_CORRECT_POST_PROCESS"),
		("RC_COLOR_CORRECT_POST_PROCESS", "RC_BLOOM_POST_PROCESS"),
		("RC_BLOOM_POST_PROCESS", "RC_BIND_SCENE_RENDER_TARGET"),
	):
		assert command_enum.index(earlier) < command_enum.index(later)

	assert "typedef struct {\n\tint\t\tcommandId;\n\tGLuint\tcolorCorrectTexture;\n\tGLuint\tcolorCorrectProgram;\n\tint\t\tpad;\n} colorCorrectPostProcessCommand_t;" in tr_local
	assert "typedef struct {\n\tint\t\tcommandId;\n} bindSceneRenderTargetCommand_t;" in tr_local
	assert "GLuint\tcombineProgram;" in tr_local

	bind_emit_block = _extract_function_block(tr_backend, "void R_AddBindSceneRenderTargetCommand( void ) {")
	bloom_emit_block = _extract_function_block(tr_backend, "void R_AddBloomPostProcessCommand( void ) {")
	color_emit_block = _extract_function_block(tr_backend, "void R_AddColorCorrectPostProcessCommand( void ) {")
	bloom_command_block = _extract_function_block(tr_backend, "static const void *RB_BloomPostProcessCommand( const void *data ) {")
	color_command_block = _extract_function_block(tr_backend, "static const void *RB_ColorCorrectPostProcessCommand( const void *data ) {")
	apply_bloom_block = _extract_function_block(tr_backend, "static qboolean RBPP_ApplyBloom( const bloomPostProcessCommand_t *cmd ) {")
	apply_color_block = _extract_function_block(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")
	end_frame_block = _extract_function_block(tr_cmds, "void RE_EndFrame( int *frontEndMsec, int *backEndMsec ) {")
	draw_surf_cmd_block = _extract_function_block(tr_cmds, "void\tR_AddDrawSurfCmd( drawSurf_t *drawSurfs, int numDrawSurfs ) {")
	swap_block = _extract_function_block(tr_backend, "const void\t*RB_SwapBuffers( const void *data ) {")

	assert "cmd = R_GetCommandBuffer( sizeof( *cmd ) );" in bind_emit_block
	assert "cmd->commandId = RC_BIND_SCENE_RENDER_TARGET;" in bind_emit_block
	assert "if ( !RBPP_BloomEnabled() || !s_postProcess.sceneTarget.initialized ) {" in bloom_emit_block
	assert "cmd->commandId = RC_BLOOM_POST_PROCESS;" in bloom_emit_block
	assert "cmd->combineProgram = s_postProcess.combineProgram.programObject;" in bloom_emit_block
	assert "cmd->commandId = RC_COLOR_CORRECT_POST_PROCESS;" in color_emit_block
	assert "cmd->colorCorrectTexture = s_postProcess.colorCorrectTexture;" in color_emit_block
	assert "RBPP_ApplyBloom( cmd )" in bloom_command_block
	assert "RBPP_BlitSceneTarget( cmd->sceneTexture );" in bloom_command_block
	assert "RBPP_ApplyColorCorrectPass( cmd );" in color_command_block
	assert "cmd->downsampleProgram" in apply_bloom_block
	assert "cmd->brightPassProgram" in apply_bloom_block
	assert "cmd->blurVerticalProgram" in apply_bloom_block
	assert "cmd->blurHorizontalProgram" in apply_bloom_block
	assert "cmd->combineProgram" in apply_bloom_block
	assert "cmd->colorCorrectTexture" in apply_color_block
	assert "cmd->colorCorrectProgram" in apply_color_block
	assert "R_AddBindSceneRenderTargetCommand();" in draw_surf_cmd_block
	assert end_frame_block.index("R_AddBloomPostProcessCommand();") < end_frame_block.index("R_AddColorCorrectPostProcessCommand();") < end_frame_block.index("cmd = R_GetCommandBuffer( sizeof( *cmd ) );")
	assert "RB_SubmitPostProcess();" not in swap_block
	assert "re.RetailPostProcessCapture = R_AddBindSceneRenderTargetCommand;" in tr_init
	assert "re.RetailBloomPostProcessCommand = R_AddBloomPostProcessCommand;" in tr_init

	for expected in (
		"case RC_COLOR_CORRECT_POST_PROCESS:",
		"data = RB_ColorCorrectPostProcessCommand( data );",
		"case RC_BLOOM_POST_PROCESS:",
		"data = RB_BloomPostProcessCommand( data );",
		"case RC_BIND_SCENE_RENDER_TARGET:",
		"data = RB_BindSceneRenderTargetCommand( data );",
	):
		assert expected in tr_backend

	for expected in (
		"case RC_COLOR_CORRECT_POST_PROCESS:",
		"const colorCorrectPostProcessCommand_t *cc_cmd = (const colorCorrectPostProcessCommand_t *)curCmd;",
		"case RC_BLOOM_POST_PROCESS:",
		"const bloomPostProcessCommand_t *bp_cmd = (const bloomPostProcessCommand_t *)curCmd;",
		"case RC_BIND_SCENE_RENDER_TARGET:",
		"const bindSceneRenderTargetCommand_t *bst_cmd = (const bindSceneRenderTargetCommand_t *)curCmd;",
	):
		assert expected in tr_shader


def test_post_process_refexport_tail_sets_bloom_uniforms_like_retail() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_public = _read("src/code/renderer/tr_public.h")

	set_uniforms_block = _extract_function_block(tr_backend, "static void RBPP_SetBloomUniforms( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {")
	set_from_cvars_block = _extract_function_block(tr_backend, "void RBPP_SetBloomUniformsFromCvars( void ) {")
	set_params_block = _extract_function_block(tr_backend, "void R_SetPostProcessBloomParameters( float brightThreshold, float bloomSaturation, float bloomIntensity, float sceneSaturation, float sceneIntensity ) {")
	bloom_command_block = _extract_function_block(tr_backend, "static const void *RB_BloomPostProcessCommand( const void *data ) {")
	apply_bloom_block = _extract_function_block(tr_backend, "static qboolean RBPP_ApplyBloom( const bloomPostProcessCommand_t *cmd ) {")

	assert "void\t(*RetailBloomPostProcessCommand)( void );" in tr_public
	assert tr_public.index("(*RetailPostProcessCapture)") < tr_public.index("(*RetailBloomPostProcessCommand)") < tr_public.index("(*PostProcessRestart)") < tr_public.index("(*RetailPostProcessPass)")
	assert "re.RetailBloomPostProcessCommand = R_AddBloomPostProcessCommand;" in tr_init
	assert "re.RetailPostProcessPass = R_SetPostProcessBloomParameters;" in tr_init
	assert "s_bloomUniformsDirty = qtrue;" in set_params_block
	assert "RBPP_SetBloomUniforms( brightThreshold, bloomSaturation, bloomIntensity, sceneSaturation, sceneIntensity );" in set_params_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( s_postProcess.brightPassProgram.programObject );" in set_uniforms_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.brightPassProgram.brightThresholdUniform, brightThreshold );" in set_uniforms_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomSaturationUniform, bloomSaturation );" in set_uniforms_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneSaturationUniform, sceneSaturation );" in set_uniforms_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.bloomIntensityUniform, bloomIntensity );" in set_uniforms_block
	assert "s_postProcess.procs.qglUniform1fARBFunc( s_postProcess.combineProgram.sceneIntensityUniform, sceneIntensity );" in set_uniforms_block
	assert set_uniforms_block.index("combineProgram.bloomSaturationUniform") < set_uniforms_block.index("combineProgram.sceneSaturationUniform") < set_uniforms_block.index("combineProgram.bloomIntensityUniform") < set_uniforms_block.index("combineProgram.sceneIntensityUniform")
	assert "if ( brightThreshold < 0.0f ) {" in set_from_cvars_block
	assert "if ( s_bloomUniformsDirty ) {" in bloom_command_block
	assert "RBPP_SetBloomUniformsFromCvars();" in bloom_command_block
	assert "s_bloomUniformsDirty = qfalse;" in bloom_command_block
	assert "RBPP_SetBloomUniforms( brightThreshold, bloomSaturation, bloomIntensity, sceneSaturation, sceneIntensity );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->downsampleProgram );" in apply_bloom_block
	assert "RBPP_BindRectangleTexture( 0, cmd->sceneTexture );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->brightPassProgram );" in apply_bloom_block
	assert "RBPP_BindRectangleTexture( 0, cmd->bloomDownsampleTexture );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->blurVerticalProgram );" in apply_bloom_block
	assert "RBPP_BindRectangleTexture( 0, cmd->bloomBrightTexture );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->blurHorizontalProgram );" in apply_bloom_block
	assert "RBPP_BindRectangleTexture( 0, cmd->bloomBlurVerticalTexture );" in apply_bloom_block
	assert "s_postProcess.procs.qglUseProgramObjectARBFunc( cmd->combineProgram );" in apply_bloom_block
	assert "RBPP_BindRectangleTexture( 1, finalBloomTexture );" in apply_bloom_block


def test_hardware_gamma_color_mapping_matches_retail_color_correct_owner() -> None:
	tr_image = _read("src/code/renderer/tr_image.c")
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")

	color_mapping_block = _extract_function_block(tr_image, "void R_SetColorMappings( void ) {")
	light_scale_block = _extract_function_block(tr_image, "void R_LightScaleTexture (unsigned *in, int inwidth, int inheight, qboolean only_gamma )")
	color_correct_enabled_block = _extract_function_block(tr_backend, "qboolean RBPP_ColorCorrectEnabled( void ) {")
	color_correct_uniform_block = _extract_function_block(tr_backend, "static void RBPP_SetColorCorrectUniforms( qboolean browserOverride ) {")
	color_correct_block = _extract_function_block(tr_backend, "static void RBPP_ApplyColorCorrectPass( const colorCorrectPostProcessCommand_t *cmd ) {")
	restart_block = _extract_function_block(tr_init, "static void R_PostProcessRestart( void ) {")

	assert "if ( !RBPP_ColorCorrectEnabled() && !glConfig.deviceSupportsGamma ) {" in color_mapping_block
	assert "if ( !RBPP_ColorCorrectEnabled() && glConfig.deviceSupportsGamma )" in color_mapping_block
	assert "GLimp_SetGamma( s_gammatable, s_gammatable, s_gammatable );" in color_mapping_block
	assert "if ( RBPP_ColorCorrectEnabled() ) {\n\t\treturn;\n\t}" in light_scale_block
	assert light_scale_block.index("if ( RBPP_ColorCorrectEnabled() )") < light_scale_block.index("if ( only_gamma )")
	assert "if ( !RB_PostProcessEnabled() ) {" in color_correct_enabled_block
	assert "if ( !s_postProcess.supported ) {" in color_correct_enabled_block
	assert "if ( !r_colorCorrectActive || !r_colorCorrectActive->integer ) {" in color_correct_enabled_block
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_gamma && r_gamma->value > 0.0f ) {" in color_correct_uniform_block
	assert "if ( ( !browserOverride || !web_browserActive || !web_browserActive->integer ) && r_contrast ) {" in color_correct_uniform_block
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in color_correct_block
	assert "R_SyncRenderThread();" in restart_block
	assert "RB_ShutdownRenderTargets();" in restart_block
	assert "RB_InitRenderTargets();" in restart_block
	assert "R_SetColorMappings();" in restart_block


def test_win32_hardware_gamma_ramp_matches_retail_contract() -> None:
	win_gamma = _read("src/code/win32/win_gamma.c")
	win_glimp = _read("src/code/win32/win_glimp.c")

	check_block = _extract_function_block(win_gamma, "void WG_CheckHardwareGamma( void )\n{")
	set_block = _extract_function_block(win_gamma, "void GLimp_SetGamma( unsigned char red[256], unsigned char green[256], unsigned char blue[256] ) {")
	restore_block = _extract_function_block(win_gamma, "void WG_RestoreGamma( void )\n{")
	extensions_block = _extract_function_block(win_glimp, "static void GLW_InitExtensions( void )")
	shutdown_block = _extract_function_block(win_glimp, "void GLimp_Shutdown( void )\n{")

	assert "glConfig.deviceSupportsGamma = qfalse;" in check_block
	assert "qwglGetDeviceGammaRamp3DFX( hDC, s_oldHardwareGamma );" in check_block
	assert "if ( glConfig.driverType == GLDRV_STANDALONE )" in check_block
	assert "if ( !r_ignorehwgamma->integer )" in check_block
	assert "GetDeviceGammaRamp( hDC, s_oldHardwareGamma );" in check_block
	assert "HIBYTE( s_oldHardwareGamma[0][255] ) <= HIBYTE( s_oldHardwareGamma[0][0] )" in check_block
	assert 'ri.Printf( PRINT_WARNING, "WARNING: suspicious gamma tables, using linear ramp for restoration\\n" );' in check_block
	assert "for ( g = 0; g < 255; g++ )" in check_block

	assert "if ( !glConfig.deviceSupportsGamma || r_ignorehwgamma->integer || !glw_state.hDC ) {" in set_block
	assert "table[0][i] = ( ( ( unsigned short ) red[i] ) << 8 ) | red[i];" in set_block
	assert 'Com_DPrintf( "performing W2K gamma clamp.\\n" );' in set_block
	assert 'Com_DPrintf( "skipping W2K gamma clamp.\\n" );' in set_block
	assert "if ( table[j][i] < table[j][i-1] ) {" in set_block
	assert "qwglSetDeviceGammaRamp3DFX( glw_state.hDC, table );" in set_block
	assert "SetDeviceGammaRamp( glw_state.hDC, table );" in set_block

	assert "qwglSetDeviceGammaRamp3DFX( glw_state.hDC, s_oldHardwareGamma );" in restore_block
	assert "SetDeviceGammaRamp( hDC, s_oldHardwareGamma );" in restore_block
	assert 'if ( !r_ignorehwgamma->integer && r_ext_gamma_control->integer )' in extensions_block
	assert shutdown_block.index("WG_RestoreGamma();") < shutdown_block.index("qwglMakeCurrent( NULL, NULL )")


def _extract_function_block(source: str, signature: str) -> str:
	start = source.index(signature)
	depth = 0
	for offset, char in enumerate(source[start:]):
		if char == "{":
			depth += 1
		elif char == "}":
			depth -= 1
			if depth == 0:
				return source[start : start + offset + 1]
	raise AssertionError(f"could not extract function block for {signature}")


def test_post_process_render_targets_match_retail_fbo_format_lane() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	create_block = _extract_function_block(tr_backend, "static qboolean RBPP_CreateRenderTarget( ppRenderTarget_t *target, int width, int height, qboolean linearFilter ) {")
	renderbuffer_block = _extract_function_block(tr_backend, "static GLuint RBPP_CreateDepthStencilRenderbuffer( int width, int height ) {")
	swap_block = _extract_function_block(tr_backend, "const void\t*RB_SwapBuffers( const void *data ) {")
	execute_block = _extract_function_block(tr_backend, "void RB_ExecuteRenderCommands( const void *data ) {")

	assert 'r_floatingPointFBOs = ri.Cvar_Get( "r_floatingPointFBOs", "0", CVAR_ARCHIVE | CVAR_LATCH );' in tr_init
	assert "extern cvar_t\t*r_floatingPointFBOs;" in tr_local
	assert "internalFormat = GL_RGBA8;" in tr_backend
	assert "pixelType = GL_UNSIGNED_BYTE;" in tr_backend
	assert "if ( r_floatingPointFBOs && r_floatingPointFBOs->integer ) {" in tr_backend
	assert "\t\tinternalFormat = GL_RGBA16;" in tr_backend
	assert "\t\tpixelType = GL_FLOAT;" in tr_backend
	assert "qglTexImage2D( GL_TEXTURE_RECTANGLE_ARB, 0, internalFormat, width, height, 0, GL_RGBA, pixelType, NULL );" in tr_backend
	assert "s_postProcess.procs.qglFramebufferRenderbufferEXTFunc( GL_FRAMEBUFFER_EXT, GL_STENCIL_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, target->depthBuffer );" in tr_backend
	assert "GL_TEXTURE_2D" not in create_block
	assert "GL_DEPTH24_STENCIL8_EXT" in renderbuffer_block
	assert "if ( GL_CheckErrors() ) {" in create_block
	assert "qglGetError()" not in create_block
	assert "s_postProcess.procs.qglBindRenderbufferEXTFunc" not in create_block
	assert "glFramebufferProcs_t" not in tr_backend
	assert "renderTarget_t" not in tr_backend
	assert "s_fboProcs" not in tr_backend
	assert "s_sceneRenderTarget" not in tr_backend
	assert "static qboolean RB_CreateRenderTarget( void )" not in tr_backend
	assert "static void RB_DestroyRenderTarget( void )" not in tr_backend
	assert "static void RB_ReleaseOffscreenRenderTarget( void )" not in tr_backend
	assert "static void RB_ResetPostProcessState( void )" not in tr_backend
	assert "static image_t *RB_UploadBloomScratch" not in tr_backend
	assert "static void RB_DrawBloomPass" not in tr_backend
	assert "RBPP_ReleaseSceneRenderTarget();" in swap_block
	assert "RBPP_ResetIfNeeded();" in execute_block


def test_live_post_process_tuning_cvars_consume_retail_modified_flags() -> None:
	tr_backend = _read("src/code/renderer/tr_backend.c")
	tr_init = _read("src/code/renderer/tr_init.c")
	tr_local = _read("src/code/renderer/tr_local.h")
	tr_cmds = _read("src/code/renderer/tr_cmds.c")

	live_block = _extract_function_block(tr_cmds, "static void R_RefreshLivePostProcessCvars( void ) {")

	assert "static void R_ClearLivePostProcessModifiedFlags( void ) {" not in tr_init
	assert "R_ClearLivePostProcessModifiedFlags();" not in tr_init
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void );" in tr_local
	assert "void RBPP_SetBloomUniformsFromCvars( void );" in tr_local
	assert "void RBPP_SetColorCorrectUniformsFromCvars( void ) {" in tr_backend
	assert "void RBPP_SetBloomUniformsFromCvars( void ) {" in tr_backend
	assert "( r_gamma && r_gamma->modified ) ||" in live_block
	assert "( r_contrast && r_contrast->modified )" in live_block
	assert "\t\t\tr_contrast->modified = qfalse;" in live_block
	assert "r_gamma->modified = qfalse;" not in live_block
	assert "RBPP_SetColorCorrectUniformsFromCvars();" in live_block
	assert "( r_bloomBrightThreshold && r_bloomBrightThreshold->modified ) ||" in live_block
	assert "\t\t\tr_bloomBrightThreshold->modified = qfalse;" in live_block
	assert "( r_bloomSaturation && r_bloomSaturation->modified ) ||" in live_block
	assert "\t\t\tr_bloomSaturation->modified = qfalse;" in live_block
	assert "( r_bloomSceneSaturation && r_bloomSceneSaturation->modified ) ||" in live_block
	assert "\t\t\tr_bloomSceneSaturation->modified = qfalse;" in live_block
	assert "( r_bloomIntensity && r_bloomIntensity->modified ) ||" in live_block
	assert "\t\t\tr_bloomIntensity->modified = qfalse;" in live_block
	assert "( r_bloomSceneIntensity && r_bloomSceneIntensity->modified )" in live_block
	assert "\t\t\tr_bloomSceneIntensity->modified = qfalse;" in live_block
	assert "RBPP_SetBloomUniformsFromCvars();" in live_block
	assert tr_cmds.index("R_RefreshLivePostProcessCvars();") < tr_cmds.index("if ( r_gamma->modified ) {")
	assert "if ( r_gamma->modified ) {" in tr_cmds
