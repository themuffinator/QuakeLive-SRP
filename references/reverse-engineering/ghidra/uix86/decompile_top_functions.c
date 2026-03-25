/*
Program: uix86.dll
Functions decompiled: top 180 by body size
*/

/* FUN_1000b0e0 @ 1000b0e0 size 8704 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1000b0e0(undefined4 param_1)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  int extraout_ECX;
  int iVar8;
  float10 fVar9;
  char *pcVar10;
  undefined *puVar11;
  char *local_4b4;
  char *local_4b0;
  char acStack_4ac [4];
  undefined1 uStack_4a8;
  char local_498 [39];
  undefined1 local_471;
  char local_470 [39];
  undefined1 local_449;
  char local_448 [4];
  char acStack_444 [4];
  char acStack_440 [4];
  char acStack_43c [1016];
  uint local_44;
  
  local_44 = DAT_1002a000 ^ (uint)&local_4b4;
  pcVar2 = (char *)FUN_10001500(param_1,0);
  if ((pcVar2 == (char *)0x0) || (*pcVar2 == '\0')) goto LAB_1000d2ce;
  pcVar2 = (char *)FUN_10014560();
  iVar8 = 0;
  if (pcVar2 == (char *)0x0) {
LAB_1000d2c0:
    pcVar10 = "unknown UI script %s\n";
LAB_1000d2c6:
    FUN_10001ee0(pcVar10,pcVar2);
LAB_1000d2ce:
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    (*(code *)DAT_106b40a8[7])("cg_thirdPerson",&DAT_100252c0);
    (*(code *)DAT_106b40a8[7])("cg_cameraOrbit",&DAT_100252c0);
    (*(code *)DAT_106b40a8[7])("ui_singlePlayerActive",&DAT_100252c0);
    local_4b0 = (char *)(float)_DAT_10766d6c;
    if (0.0 <= (float)local_4b0) {
      if ((float)DAT_10029358 < (float)local_4b0) {
        local_4b0 = DAT_10029358;
      }
    }
    else {
      local_4b0 = (char *)0x0;
    }
    (*(code *)DAT_106b40a8[8])("dedicated",local_4b0);
    local_4b4 = (char *)(float)(int)(&DAT_107596ac)[DAT_1074502c * 2];
    if (0.0 <= (float)local_4b4) {
      local_4b0 = local_4b4;
      if (_DAT_10029460 < (double)(int)(&DAT_107596ac)[DAT_1074502c * 2]) {
        local_4b0 = DAT_10029504;
      }
    }
    else {
      local_4b0 = (char *)0x0;
    }
    (*(code *)DAT_106b40a8[8])("g_gametype",local_4b0);
    (*(code *)DAT_106b40a8[9])("ui_teamName",&DAT_10042f38,0x400);
    (*(code *)DAT_106b40a8[7])("g_redTeam",&DAT_10042f38);
    (*(code *)DAT_106b40a8[9])("ui_opponentName",&DAT_10042f38,0x400);
    (*(code *)DAT_106b40a8[7])("g_blueTeam",&DAT_10042f38);
    puVar6 = DAT_106b40a8;
    uVar4 = FUN_10001900("wait ; wait ; map %s\n",(&DAT_1075add8)[DAT_10742f8c * 0x19]);
    (*(code *)puVar6[0x14])(uVar4);
    fVar9 = (float10)(*(code *)DAT_106b40a8[10])("g_spSkill");
    local_4b0 = (char *)(float)fVar9;
    (*(code *)DAT_106b40a8[10])("sv_maxClients");
    local_4b4 = (char *)FUN_10021270();
    pcVar2 = (char *)0x0;
    iVar8 = 5;
    iVar3 = 1;
    do {
      uVar4 = FUN_10001900("ui_blueteam%i",iVar3);
      (*(code *)DAT_106b40a8[10])(uVar4);
      iVar5 = FUN_10021270();
      if (-1 < iVar5) {
        pcVar2 = pcVar2 + 1;
      }
      uVar4 = FUN_10001900("ui_redteam%i",iVar3);
      (*(code *)DAT_106b40a8[10])(uVar4);
      iVar5 = FUN_10021270();
      puVar6 = DAT_106b40a8;
      if (-1 < iVar5) {
        pcVar2 = pcVar2 + 1;
      }
      iVar3 = iVar3 + 1;
      iVar8 = iVar8 + -1;
    } while (iVar8 != 0);
    if (pcVar2 == (char *)0x0) {
      pcVar2 = (char *)0x8;
    }
    if ((int)pcVar2 < (int)local_4b4) {
      pcVar2 = local_4b4;
    }
    uVar4 = FUN_10001900(&DAT_10025d20,pcVar2);
    (*(code *)puVar6[7])("sv_maxClients",uVar4);
    iVar8 = 1;
    local_4b4 = (char *)0x5;
    do {
      puVar6 = DAT_106b40a8;
      uVar4 = FUN_10001900("ui_blueteam%i",iVar8);
      (*(code *)puVar6[10])(uVar4);
      iVar3 = FUN_10021270();
      if (1 < iVar3) {
        if (DAT_1076742c < 3) {
          iVar3 = iVar3 + -2;
          if ((iVar3 < 0) || (DAT_10769814 <= iVar3)) {
            uVar4 = FUN_10001900("^1Invalid bot number: %i\n",iVar3);
            (*(code *)*DAT_106b40a8)(uVar4);
LAB_1000b430:
            pcVar2 = "Sarge";
          }
          else {
            if ((&DAT_10044340)[iVar3] == 0) goto LAB_1000b430;
            pcVar2 = (char *)FUN_10001940();
          }
          FUN_10001830(local_448,0x400,"addbot %s %f \n",pcVar2,(double)(float)local_4b0);
        }
        else {
          FUN_10001830(local_448,0x400,"addbot %s %f %s\n",
                       *(undefined4 *)(&DAT_1075827c + iVar3 * 0x14),(double)(float)local_4b0,
                       &DAT_10026ce0);
        }
        (*(code *)DAT_106b40a8[0x14])(local_448);
      }
      puVar6 = DAT_106b40a8;
      uVar4 = FUN_10001900("ui_redteam%i",iVar8);
      (*(code *)puVar6[10])(uVar4);
      iVar3 = FUN_10021270();
      if (1 < iVar3) {
        if (DAT_1076742c < 3) {
          iVar3 = iVar3 + -2;
          if ((iVar3 < 0) || (DAT_10769814 <= iVar3)) {
            uVar4 = FUN_10001900("^1Invalid bot number: %i\n",iVar3);
            (*(code *)*DAT_106b40a8)(uVar4);
LAB_1000b511:
            pcVar2 = "Sarge";
          }
          else {
            if ((&DAT_10044340)[iVar3] == 0) goto LAB_1000b511;
            pcVar2 = (char *)FUN_10001940();
          }
          FUN_10001830(local_448,0x400,"addbot %s %f \n",pcVar2,(double)(float)local_4b0);
        }
        else {
          FUN_10001830(local_448,0x400,"addbot %s %f %s\n",
                       *(undefined4 *)(&DAT_1075827c + iVar3 * 0x14),(double)(float)local_4b0,
                       &DAT_10026cdc);
        }
        (*(code *)DAT_106b40a8[0x14])(local_448);
      }
      iVar8 = iVar8 + 1;
      local_4b4 = local_4b4 + -1;
      if (local_4b4 == (char *)0x0) {
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
    } while( true );
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    (*(code *)DAT_106b40a8[0x14])("exec default.cfg\n");
    (*(code *)DAT_106b40a8[0x14])("cvar_restart\n");
    puVar6 = &DAT_1002a0e0;
    do {
      *puVar6 = puVar6[-2];
      puVar6[1] = puVar6[-1];
      puVar6 = puVar6 + 6;
    } while ((int)puVar6 < 0x1002a878);
    puVar11 = &DAT_1002729c;
    pcVar2 = "com_introPlayed";
LAB_1000bb57:
    (*(code *)DAT_106b40a8[7])(pcVar2,puVar11);
    (*(code *)DAT_106b40a8[0x14])("vid_restart\n");
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    (*(code *)DAT_106b40a8[0x44])(local_448,0x11);
    (*(code *)DAT_106b40a8[7])("cdkey1",&DAT_100239ab);
    (*(code *)DAT_106b40a8[7])("cdkey2",&DAT_100239ab);
    (*(code *)DAT_106b40a8[7])("cdkey3",&DAT_100239ab);
    (*(code *)DAT_106b40a8[7])("cdkey4",&DAT_100239ab);
    pcVar2 = local_448;
    do {
      cVar1 = *pcVar2;
      pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    if ((int)pcVar2 - (int)(local_448 + 1) == 0x10) {
      strncpy(acStack_4ac,local_448,4);
      uStack_4a8 = 0;
      (*(code *)DAT_106b40a8[7])("cdkey1",acStack_4ac);
      strncpy(acStack_4ac,acStack_444,4);
      uStack_4a8 = 0;
      (*(code *)DAT_106b40a8[7])("cdkey2",acStack_4ac);
      strncpy(acStack_4ac,acStack_440,4);
      uStack_4a8 = 0;
      (*(code *)DAT_106b40a8[7])("cdkey3",acStack_4ac);
      strncpy(acStack_4ac,acStack_43c,4);
      uStack_4a8 = 0;
      (*(code *)DAT_106b40a8[7])("cdkey4",acStack_4ac);
      __security_check_cookie(local_44 ^ (uint)&local_4b4);
      return;
    }
    goto LAB_1000d2ce;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    local_448[0] = '\0';
    uVar4 = FUN_10001f50();
    FUN_10001750(uVar4);
    uVar4 = FUN_10001f50();
    FUN_10001750(uVar4);
    uVar4 = FUN_10001f50();
    FUN_10001750(uVar4);
    uVar4 = FUN_10001f50();
    FUN_10001750(uVar4);
    (*(code *)DAT_106b40a8[7])("cdkey",local_448);
    puVar6 = DAT_106b40a8;
    uVar4 = FUN_10001f50();
    iVar8 = (*(code *)puVar6[0x4f])(local_448,uVar4);
    if (iVar8 == 0) {
      (*(code *)DAT_106b40a8[7])("ui_cdkeyvalid","CD Key does not appear to be valid.");
      __security_check_cookie(local_44 ^ (uint)&local_4b4);
      return;
    }
    (*(code *)DAT_106b40a8[7])("ui_cdkeyvalid","CD Key Appears to be valid.");
    (*(code *)DAT_106b40a8[0x45])(local_448);
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    FUN_10003190();
    FUN_1000d3c0(0);
    FUN_1001d3d0(4);
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    FUN_1001b1e0();
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    FUN_1001b0c0();
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
LAB_1000b91b:
    (*(code *)DAT_106b40a8[7])("com_errorMessage",&DAT_100239ab);
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    FUN_1000f6d0();
    FUN_10002350();
    __security_check_cookie(local_44 ^ (uint)&local_4b4);
    return;
  }
  iVar3 = FUN_100016c0();
  if (iVar3 == 0) {
    uVar4 = 1;
  }
  else {
    iVar3 = FUN_100016c0();
    if (iVar3 != 0) {
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if (DAT_10758294 != 0) {
          puVar11 = (undefined *)(&DAT_107596ac)[DAT_1074220c * 2];
          pcVar2 = (char *)(&DAT_1075add8)[DAT_10744ccc * 0x19];
          pcVar10 = "demo %s_%i\n";
LAB_1000c28a:
          puVar6 = DAT_106b40a8;
          uVar4 = FUN_10001900(pcVar10,pcVar2,puVar11);
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_1000acf0();
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_1000ac00();
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_1000a9d0();
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if (-1 < DAT_10761bf0) {
          (*(code *)DAT_106b40a8[0x4a])(DAT_10761bf0);
        }
        puVar6 = DAT_106b40a8;
        uVar4 = FUN_10001900("cinematic %s.roq 2\n",(&DAT_107617e8)[DAT_10761bec]);
        (*(code *)puVar6[0x14])(uVar4);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        puVar11 = (undefined *)(&DAT_107611d8)[DAT_107613dc * 2];
        pcVar2 = "fs_game";
        goto LAB_1000bb57;
      }
      iVar3 = FUN_100016c0();
      puVar6 = DAT_106b40a8;
      if (iVar3 == 0) {
        uVar4 = FUN_10001900("demo %s\n",(&DAT_107613e0)[DAT_107617e4]);
        (*(code *)puVar6[0x14])(uVar4);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[7])("fs_game",&DAT_100239ab);
        (*(code *)DAT_106b40a8[0x14])("vid_restart\n");
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if (DAT_10762498 == 0) {
          FUN_100161b0();
          FUN_1001d4a0(&DAT_10027618);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        FUN_100118f0();
        DAT_107644a8 = 0;
        DAT_10765614 = 0;
        DAT_10766ae4 = 0;
        goto LAB_1000b9cf;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_100118f0();
        DAT_107644a8 = 0;
        DAT_10765614 = 0;
        DAT_10766ae4 = 0;
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if (DAT_1074148c == 0) {
          FUN_10011a30(1);
        }
        FUN_1000d740();
        FUN_1000eba0(DAT_10029358,0,0);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[0x32])(DAT_1074148c,(&DAT_107624a0)[DAT_1076249c],&DAT_107648d0,0x40)
        ;
        FUN_1000e3b0(1);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        iVar8 = DAT_10766adc * 0x40;
        if (&DAT_107662dc + iVar8 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(&DAT_107648d0,&DAT_107662dc + iVar8,0x3f);
        DAT_1076490f = 0;
        FUN_1000e3b0(1);
        FUN_1001d3d0(0xe);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_1000deb0(1);
        DAT_10765610 = 0;
        FUN_1001d3d0(0xe);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[7])("cg_thirdPerson",&DAT_100252c0);
        (*(code *)DAT_106b40a8[7])("cg_cameraOrbit",&DAT_100252c0);
        (*(code *)DAT_106b40a8[7])("ui_singlePlayerActive",&DAT_100252c0);
        if ((-1 < DAT_1076249c) && (DAT_1076249c < DAT_107644a0)) {
          (*(code *)DAT_106b40a8[0x32])(DAT_1074148c,(&DAT_107624a0)[DAT_1076249c],local_448,0x400);
          puVar6 = DAT_106b40a8;
          uVar4 = FUN_10001900("connect %s\n",local_448);
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[7])("ui_singlePlayerActive",&DAT_100252c0);
        puVar6 = DAT_106b40a8;
        if ((-1 < DAT_10766adc) && (DAT_10766adc < DAT_10766ae0)) {
          uVar4 = FUN_10001900("connect %s\n",&DAT_107662dc + DAT_10766adc * 0x40);
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[7])("ui_singlePlayerActive",&DAT_100252c0);
        (*(code *)DAT_106b40a8[0x14])(&DAT_100276a8);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[7])("cl_paused",&DAT_1002729c);
        (*(code *)DAT_106b40a8[0x2c])(2);
        FUN_10016220();
        FUN_1001d4a0("setup_menu2");
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        (*(code *)DAT_106b40a8[0x14])("disconnect\n");
        (*(code *)DAT_106b40a8[0x2c])(2);
        FUN_10016220();
        FUN_1001d4a0(&DAT_10027618);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) goto LAB_1000b91b;
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        iVar8 = FUN_10014ab0(&local_4b4);
        if (iVar8 != 0) {
          if (local_4b4 == DAT_1076248c) {
            DAT_10762490 = (uint)(DAT_10762490 == 0);
          }
          DAT_1076248c = local_4b4;
          qsort(&DAT_107624a0,DAT_107644a0,4,(_PtFuncCompare *)&LAB_1000a990);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        puVar6 = DAT_106b40a8 + 0x2c;
        uVar7 = (*(code *)DAT_106b40a8[0x2b])();
        (*(code *)*puVar6)(uVar7 & 0xfffffffd);
        (*(code *)DAT_106b40a8[0x2a])();
        FUN_10016220();
        (*(code *)DAT_106b40a8[0x55])();
        (*(code *)DAT_106b40a8[7])("cl_paused",&DAT_100252c0);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        puVar11 = &DAT_1002729c;
LAB_1000c1f4:
        (*(code *)DAT_106b40a8[7])("r_fullScreen",puVar11);
        puVar6 = DAT_106b40a8;
        uVar4 = FUN_10001900("vid_restart fast\n");
        (*(code *)puVar6[0x14])(uVar4);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        puVar11 = &DAT_100252c0;
        goto LAB_1000c1f4;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        fVar9 = (float10)(*(code *)DAT_106b40a8[10])("r_fullScreen");
        if (fVar9 == (float10)0) {
          puVar11 = &DAT_1002729c;
        }
        else {
          puVar11 = &DAT_100252c0;
        }
        pcVar2 = "r_fullScreen";
        (*(code *)DAT_106b40a8[7])("r_fullScreen",puVar11);
        pcVar10 = "vid_restart fast\n";
        goto LAB_1000c28a;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        FUN_1000eba0(_DAT_10029368,0,0);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if ((-1 < DAT_10742f8c) && (DAT_10742f8c < DAT_1075add0)) {
          if (DAT_10741c6c == -1) {
            puVar11 = &DAT_100239ab;
            iVar8 = DAT_10742f8c;
          }
          else {
            puVar11 = (undefined *)FUN_10001000();
            iVar8 = extraout_ECX;
          }
          puVar6 = DAT_106b40a8;
          uVar4 = FUN_10001900("callvote map %s %s\n",(&DAT_1075add8)[iVar8 * 0x19],puVar11);
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
          pcVar2 = strstr(&DAT_107597cc + DAT_107597c0 * 0x28," ");
          puVar6 = DAT_106b40a8;
          if (pcVar2 == (char *)0x0) {
            pcVar2 = (char *)0x0;
          }
          else {
            pcVar2 = pcVar2 + DAT_107597c0 * -0x28 + -0x107597cc;
          }
          uVar4 = FUN_10001900("callvote kick %s\n",
                               pcVar2 + (int)(&DAT_107597cc + DAT_107597c0 * 0x28));
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      puVar6 = DAT_106b40a8;
      if (iVar3 == 0) {
        if ((-1 < DAT_1074502c) && (DAT_1074502c < DAT_107596a4)) {
          uVar4 = FUN_10001900("callvote g_gametype %i\n",(&DAT_107596ac)[DAT_1074502c * 2]);
          (*(code *)puVar6[0x14])(uVar4);
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        goto LAB_1000d2ce;
      }
      iVar3 = FUN_100016c0();
      puVar6 = DAT_106b40a8;
      if (iVar3 == 0) {
        puVar11 = &DAT_10026cdc;
        if (DAT_107597ac != 0) {
          puVar11 = &DAT_10026ce0;
        }
        uVar4 = FUN_100038c0(DAT_107611d4 + 1,puVar11);
        uVar4 = FUN_10001900("addbot %s %i %s\n",uVar4);
        (*(code *)puVar6[0x14])(uVar4);
        __security_check_cookie(local_44 ^ (uint)&local_4b4);
        return;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        if (DAT_1074148c == 3) goto LAB_1000d2ce;
        (*(code *)DAT_106b40a8[0x33])(DAT_1074148c,(&DAT_107624a0)[DAT_1076249c],local_448,0x400);
        local_470[0] = '\0';
        local_498[0] = '\0';
        pcVar2 = (char *)FUN_10001940();
        if (pcVar2 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(local_498,pcVar2,0x27);
        local_471 = 0;
        pcVar2 = (char *)FUN_10001940();
        if (pcVar2 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(local_470,pcVar2,0x27);
        pcVar2 = local_498;
        local_449 = 0;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        if (pcVar2 == local_498 + 1) goto LAB_1000d2ce;
        pcVar2 = local_470;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        if (pcVar2 == local_470 + 1) goto LAB_1000d2ce;
        iVar8 = (*(code *)DAT_106b40a8[0x3e])(3,local_498,local_470);
        if (iVar8 == 0) {
LAB_1000c5f5:
          FUN_10001ee0("Favorite already in list\n");
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        if (iVar8 == -1) {
LAB_1000c61c:
          FUN_10001ee0("Favorite list full\n");
          __security_check_cookie(local_44 ^ (uint)&local_4b4);
          return;
        }
        pcVar2 = local_470;
        pcVar10 = "Added favorite server %s\n";
      }
      else {
        iVar3 = FUN_100016c0();
        if (iVar3 == 0) {
          if (DAT_1074148c == 3) {
            (*(code *)DAT_106b40a8[0x33])(3,(&DAT_107624a0)[DAT_1076249c],local_448,0x400);
            local_498[0] = '\0';
            pcVar2 = (char *)FUN_10001940();
            if (pcVar2 == (char *)0x0) {
              FUN_10001e70(0,"Q_strncpyz: NULL src");
            }
            strncpy(local_498,pcVar2,0x27);
            pcVar2 = local_498;
            local_471 = 0;
            do {
              cVar1 = *pcVar2;
              pcVar2 = pcVar2 + 1;
            } while (cVar1 != '\0');
            if (pcVar2 != local_498 + 1) {
              (*(code *)DAT_106b40a8[0x3f])(3,local_498);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
          }
          goto LAB_1000d2ce;
        }
        iVar3 = FUN_100016c0();
        if (iVar3 != 0) {
          iVar3 = FUN_100016c0();
          if (iVar3 == 0) {
            iVar3 = FUN_10014c30(&local_4b0);
            if (iVar3 != 0) {
              (*(code *)DAT_106b40a8[10])("cg_selectedPlayer");
              iVar3 = FUN_10021270();
              puVar6 = DAT_106b40a8;
              if (iVar3 < DAT_107597b4) {
                iVar8 = -(int)local_4b0;
                do {
                  cVar1 = *local_4b0;
                  local_4b0[(int)(local_448 + iVar8)] = cVar1;
                  local_4b0 = local_4b0 + 1;
                } while (cVar1 != '\0');
                uVar4 = FUN_10001900(local_448,(&DAT_1075accc)[iVar3]);
                (*(code *)puVar6[0x14])(uVar4);
                (*(code *)DAT_106b40a8[0x14])(&DAT_100278b8);
              }
              else if (0 < DAT_107597b4) {
                puVar11 = &DAT_1075a1cc;
                pcVar2 = local_4b0;
                do {
                  FUN_10001f50();
                  iVar3 = FUN_10001730();
                  puVar6 = DAT_106b40a8;
                  if (iVar3 != 0) {
                    iVar3 = -(int)pcVar2;
                    do {
                      cVar1 = *pcVar2;
                      pcVar2[(int)(local_448 + iVar3)] = cVar1;
                      pcVar2 = pcVar2 + 1;
                    } while (cVar1 != '\0');
                    uVar4 = FUN_10001900(local_448,puVar11);
                    (*(code *)puVar6[0x14])(uVar4);
                    (*(code *)DAT_106b40a8[0x14])(&DAT_100278b8);
                    pcVar2 = local_4b0;
                  }
                  iVar8 = iVar8 + 1;
                  puVar11 = puVar11 + 0x28;
                } while (iVar8 < DAT_107597b4);
              }
              puVar6 = DAT_106b40a8 + 0x2c;
              uVar7 = (*(code *)DAT_106b40a8[0x2b])();
              (*(code *)*puVar6)(uVar7 & 0xfffffffd);
              (*(code *)DAT_106b40a8[0x2a])();
              (*(code *)DAT_106b40a8[0x55])();
              (*(code *)DAT_106b40a8[7])("cl_paused",&DAT_100252c0);
              FUN_10016220();
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            iVar8 = FUN_10014c30(&local_4b4);
            if (iVar8 != 0) {
              (*(code *)DAT_106b40a8[10])("cg_selectedPlayer");
              iVar8 = FUN_10021270();
              if (iVar8 == DAT_107597b4) {
                (*(code *)DAT_106b40a8[0x14])(local_4b4);
                (*(code *)DAT_106b40a8[0x14])(&DAT_100278b8);
              }
              puVar6 = DAT_106b40a8 + 0x2c;
              uVar7 = (*(code *)DAT_106b40a8[0x2b])();
              (*(code *)*puVar6)(uVar7 & 0xfffffffd);
              (*(code *)DAT_106b40a8[0x2a])();
              (*(code *)DAT_106b40a8[0x55])();
              (*(code *)DAT_106b40a8[7])("cl_paused",&DAT_100252c0);
              FUN_10016220();
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            iVar8 = FUN_10014c30(&local_4b4);
            if (iVar8 != 0) {
              (*(code *)DAT_106b40a8[10])("cg_selectedPlayer");
              iVar8 = FUN_10021270();
              puVar6 = DAT_106b40a8;
              if (iVar8 < DAT_107597b4) {
                iVar3 = -(int)local_4b4;
                do {
                  cVar1 = *local_4b4;
                  local_4b4[(int)(local_448 + iVar3)] = cVar1;
                  local_4b4 = local_4b4 + 1;
                } while (cVar1 != '\0');
                uVar4 = FUN_10001900(local_448,(&DAT_1075accc)[iVar8]);
                (*(code *)puVar6[0x14])(uVar4);
                (*(code *)DAT_106b40a8[0x14])(&DAT_100278b8);
              }
              puVar6 = DAT_106b40a8 + 0x2c;
              uVar7 = (*(code *)DAT_106b40a8[0x2b])();
              (*(code *)*puVar6)(uVar7 & 0xfffffffd);
              (*(code *)DAT_106b40a8[0x2a])();
              (*(code *)DAT_106b40a8[0x55])();
              (*(code *)DAT_106b40a8[7])("cl_paused",&DAT_100252c0);
              FUN_10016220();
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            iVar8 = FUN_10014c30(&local_4b4);
            if (iVar8 != 0) {
              FUN_1000ae50();
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            (*(code *)DAT_106b40a8[7])("ui_teamHeadColor",&DAT_100278f4);
            (*(code *)DAT_106b40a8[7])("ui_teamUpperColor",&DAT_100278f4);
            (*(code *)DAT_106b40a8[7])("ui_teamLowerColor",&DAT_100278f4);
            __security_check_cookie(local_44 ^ (uint)&local_4b4);
            return;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            (*(code *)DAT_106b40a8[7])("ui_enemyHeadColor",&DAT_10027948);
            (*(code *)DAT_106b40a8[7])("ui_enemyUpperColor",&DAT_10027948);
            (*(code *)DAT_106b40a8[7])("ui_enemyLowerColor",&DAT_10027948);
            __security_check_cookie(local_44 ^ (uint)&local_4b4);
            return;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            FUN_10011660(&DAT_10767540);
            __security_check_cookie(local_44 ^ (uint)&local_4b4);
            return;
          }
          iVar8 = FUN_100016c0();
          if ((iVar8 == 0) || (iVar8 = FUN_100016c0(), iVar8 == 0)) {
            FUN_10011630(&DAT_10745b60);
            __security_check_cookie(local_44 ^ (uint)&local_4b4);
            return;
          }
          iVar8 = FUN_100016c0();
          if (iVar8 == 0) {
            DAT_1002aedc = 1;
            __security_check_cookie(local_44 ^ (uint)&local_4b4);
            return;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("callvote clientkick %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("clientviewprofile %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("clientfriendinvite %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("tempban %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("ban %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("clientmute %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("mute %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("unmute %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("addmod %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("addadmin %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("demote %i\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("put %i r\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("put %i b\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          iVar8 = FUN_100016c0();
          puVar6 = DAT_106b40a8;
          if (iVar8 == 0) {
            if ((-1 < DAT_107597c0) && (DAT_107597c0 < DAT_107597b0)) {
              uVar4 = FUN_10001900("put %i s\n",(&DAT_1075abcc)[DAT_107597c0]);
              (*(code *)puVar6[0x14])(uVar4);
              __security_check_cookie(local_44 ^ (uint)&local_4b4);
              return;
            }
            goto LAB_1000d2ce;
          }
          goto LAB_1000d2c0;
        }
        if (DAT_1074148c != 3) goto LAB_1000d2ce;
        local_470[0] = '\0';
        local_498[0] = '\0';
        pcVar2 = (char *)FUN_10001f50();
        if (pcVar2 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(local_498,pcVar2,0x27);
        local_471 = 0;
        pcVar2 = (char *)FUN_10001f50();
        if (pcVar2 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(local_470,pcVar2,0x27);
        pcVar2 = local_498;
        local_449 = 0;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        if (pcVar2 == local_498 + 1) goto LAB_1000d2ce;
        pcVar2 = local_470;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        if (pcVar2 == local_470 + 1) goto LAB_1000d2ce;
        iVar8 = (*(code *)DAT_106b40a8[0x3e])(3,local_498,local_470);
        if (iVar8 == 0) goto LAB_1000c5f5;
        if (iVar8 == -1) goto LAB_1000c61c;
        pcVar2 = local_470;
        pcVar10 = "Added favorite server %s\n";
      }
      goto LAB_1000d2c6;
    }
    uVar4 = 0;
  }
  FUN_10011a30(uVar4);
LAB_1000b9cf:
  FUN_1000d740();
  __security_check_cookie(local_44 ^ (uint)&local_4b4);
  return;
}



/* FUN_10007030 @ 10007030 size 5861 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10007030(float *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  char cVar5;
  uint uVar6;
  uint uVar7;
  float fStack_101c;
  float fStack_1018;
  float fStack_1014;
  uint uStack_1010;
  int iStack_100c;
  int iStack_1008;
  undefined1 local_1004 [1024];
  char acStack_c04 [1024];
  undefined1 auStack_804 [1024];
  undefined1 auStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&fStack_101c;
  (**(code **)(DAT_106b40a8 + 0xc0))(0,local_1004,0x400);
  (**(code **)(DAT_106b40a8 + 0xc0))(0x2a9,auStack_404,0x400);
  (**(code **)(DAT_106b40a8 + 0xc0))(0x2aa,auStack_804,0x400);
  (**(code **)(DAT_106b40a8 + 0xc0))(0x2c0,acStack_c04,0x400);
  uStack_1010 = atoi(acStack_c04);
  pcVar1 = (char *)FUN_10001940();
  iStack_1008 = atoi(pcVar1);
  fStack_1018 = *param_1;
  fStack_101c = param_1[1];
  FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
  fStack_101c = fStack_101c + (float)_DAT_10029310;
  pcVar1 = (char *)FUN_10001940();
  iVar2 = atoi(pcVar1);
  FUN_10001900("Time Limit: %i",iVar2,0,0,param_4);
  FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
  fStack_101c = fStack_101c + (float)_DAT_10029310;
  uVar7 = 2;
  if (iStack_1008 < 4) {
    pcVar1 = (char *)FUN_10001940();
    iVar2 = atoi(pcVar1);
    FUN_10001900("Frag Limit: %i",iVar2,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = 3;
  }
  pcVar1 = (char *)FUN_10001940();
  iVar3 = atoi(pcVar1);
  iVar2 = iStack_1008;
  if ((iVar3 != 0) && (2 < iStack_1008)) {
    FUN_10001900("Mercy Limit: %i",iVar3,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (iVar2 == 5) {
    pcVar1 = (char *)FUN_10001940();
    iVar2 = atoi(pcVar1);
    FUN_10001900("Capture Limit: %i",iVar2,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
    iVar2 = iStack_1008;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  switch(iVar2) {
  case 4:
  case 9:
  case 0xb:
  case 0xc:
    if ((iVar2 < 10) || (0xb < iVar2)) {
      pcVar1 = (char *)FUN_10001940();
      iVar2 = atoi(pcVar1);
      FUN_10001900("Round Limit: %i",iVar2,0,0,param_4);
      FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
      fStack_101c = fStack_101c + (float)_DAT_10029310;
      uVar7 = uVar7 + 1;
      iVar2 = iStack_1008;
    }
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((9 < iVar2) && (iVar2 < 0xc)) {
    pcVar1 = (char *)FUN_10001940();
    iVar2 = atoi(pcVar1);
    FUN_10001900("Score Limit: %i",iVar2,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  uVar6 = uStack_1010;
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x2000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uVar6 & 0x4000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  pcVar1 = (char *)FUN_10001940();
  iVar2 = atoi(pcVar1);
  if (iVar2 != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x10000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  pcVar1 = (char *)FUN_10001940();
  iVar2 = atoi(pcVar1);
  if (iVar2 != 3) {
    pcVar1 = (char *)FUN_10001940();
    iVar2 = atoi(pcVar1);
    FUN_10001900("%ix Quad",iVar2,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x8000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  pcVar1 = (char *)FUN_10001940();
  iStack_100c = atoi(pcVar1);
  if (iStack_100c != 800) {
    pcVar1 = (char *)FUN_10001940();
    iStack_100c = atoi(pcVar1);
    FUN_10001900("Gravity %i",iStack_100c,0,0,param_4);
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  fStack_1014 = (float)(uStack_1010 & 0x20000);
  if (fStack_1014 != 0.0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x40000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if ((iStack_1008 == 0xc) && ((uStack_1010 & 0x4000000) != 0)) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x80000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if (((uStack_1010 & 0x100000) != 0) && (fStack_1014 == 0.0)) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x200000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x400000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x800000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  if ((uStack_1010 & 0x1000000) != 0) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    fStack_101c = fStack_101c + (float)_DAT_10029310;
    uVar7 = uVar7 + 1;
  }
  if (7 < uVar7) {
    uVar7 = 0;
    fStack_1018 = fStack_1018 + (float)_DAT_10029478;
    fStack_101c = fStack_101c - (float)_DAT_10029470;
  }
  uVar6 = uStack_1010 & 1;
  if (((uVar6 != 0) || ((uStack_1010 & 0xfe) != 0)) || ((uStack_1010 & 0x1f00) != 0)) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    if (8 < uVar7) goto LAB_100086fd;
    fStack_101c = fStack_101c + (float)_DAT_10029300;
    if (uVar6 != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_gauntlet.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
    }
    uVar7 = uStack_1010;
    uVar6 = (uint)(uVar6 != 0);
    cVar5 = (char)uStack_1010;
    if ((uStack_1010 & 2) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_machinegun.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if (((uVar7 & 4) != 0) && (iStack_100c != 2)) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_shotgun.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if (((uVar7 & 8) != 0) && (iStack_100c != 2)) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_grenade.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if (((uVar7 & 0x10) != 0) && (iStack_100c != 2)) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_rocket.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if ((uVar7 & 0x20) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_lightning.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if (((uVar7 & 0x40) != 0) && (iStack_100c != 2)) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_railgun.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      uVar6 = uVar6 + 1;
    }
    if ((cVar5 < '\0') && (iStack_100c != 2)) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_plasma.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      uVar6 = uVar6 + 1;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        uVar6 = 0;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
    if ((uVar7 & 0x100) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_bfg.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      uVar6 = uVar6 + 1;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        uVar6 = 0;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
    if ((uVar7 & 0x200) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_grapple.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      uVar6 = uVar6 + 1;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        uVar6 = 0;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
    if ((uVar7 & 0x400) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_nailgun.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      uVar6 = uVar6 + 1;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        uVar6 = 0;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
    if ((uVar7 & 0x800) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_proxlauncher.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      uVar6 = uVar6 + 1;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        uVar6 = 0;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
    if ((uVar7 & 0x1000) != 0) {
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_chaingun.tga");
      FUN_10002c50(fStack_1018,fStack_101c,_DAT_1002941c,_DAT_1002941c,uVar4);
      uVar4 = (**(code **)(DAT_106b40a8 + 0x5c))("icons/modified.tga");
      fStack_1014 = fStack_1018 + (float)_DAT_10029300;
      FUN_10002c50(fStack_1014,fStack_101c + (float)_DAT_10029260,_DAT_1002936c,_DAT_1002936c,uVar4)
      ;
      fStack_1018 = fStack_1018 + (float)_DAT_10029310;
      if (7 < uVar6 + 1) {
        fStack_101c = (float)_DAT_10029310 + fStack_101c;
        fStack_1018 = fStack_1018 - (float)_DAT_10029218;
      }
    }
  }
  if (fStack_101c == param_1[1]) {
    FUN_10003ec0(fStack_1018,fStack_101c,param_2,param_3);
    __security_check_cookie(local_4 ^ (uint)&fStack_101c);
    return;
  }
LAB_100086fd:
  __security_check_cookie(local_4 ^ (uint)&fStack_101c);
  return;
}



/* FUN_10012d90 @ 10012d90 size 2737 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_10012d90(int param_1,float param_2,float param_3,float param_4,float param_5)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int *unaff_EBX;
  float10 fVar4;
  float fVar5;
  int iVar6;
  int iVar7;
  undefined1 auStack_548 [4];
  double dStack_544;
  undefined4 local_53c;
  float fStack_538;
  undefined1 auStack_534 [4];
  undefined4 uStack_530;
  int iStack_52c;
  float fStack_528;
  float fStack_524;
  float fStack_520;
  float fStack_518;
  float fStack_514;
  float fStack_510;
  float fStack_50c;
  float fStack_508;
  float fStack_504;
  float fStack_500;
  float fStack_4fc;
  float fStack_4f8;
  undefined4 uStack_4f4;
  float fStack_4f0;
  float fStack_4ec;
  float fStack_4e8;
  undefined1 auStack_4e4 [4];
  float fStack_4e0;
  float fStack_4dc;
  float fStack_4d8;
  undefined1 auStack_4d4 [4];
  undefined1 auStack_4d0 [8];
  int iStack_4c8;
  undefined1 auStack_4a4 [4];
  undefined4 uStack_4a0;
  int iStack_49c;
  float fStack_498;
  float fStack_494;
  float fStack_490;
  undefined1 auStack_488 [52];
  undefined1 auStack_454 [16];
  undefined1 auStack_444 [4];
  undefined1 auStack_440 [8];
  int iStack_438;
  undefined1 auStack_414 [8];
  float fStack_40c;
  undefined1 auStack_3e4 [4];
  undefined4 uStack_3e0;
  int iStack_3dc;
  float fStack_3d8;
  float fStack_3d4;
  float fStack_3d0;
  undefined1 auStack_3c8 [80];
  int iStack_378;
  undefined1 auStack_354 [4];
  undefined4 uStack_350;
  int iStack_34c;
  float fStack_348;
  float fStack_344;
  float fStack_340;
  int iStack_2c4;
  int iStack_2c0;
  int iStack_2bc;
  int iStack_2b8;
  float fStack_2b4;
  float fStack_2b0;
  undefined4 uStack_2a0;
  undefined4 uStack_29c;
  undefined4 uStack_298;
  undefined4 uStack_294;
  undefined4 uStack_290;
  undefined4 uStack_28c;
  undefined4 uStack_288;
  undefined4 uStack_284;
  undefined4 uStack_280;
  int iStack_27c;
  undefined4 uStack_278;
  undefined1 auStack_154 [4];
  undefined4 uStack_150;
  int iStack_14c;
  float fStack_148;
  float fStack_144;
  float fStack_140;
  undefined1 auStack_c4 [4];
  undefined4 uStack_c0;
  int iStack_bc;
  float fStack_b8;
  float fStack_b4;
  float fStack_b0;
  undefined1 auStack_80 [80];
  float fStack_30;
  float fStack_2c;
  float fStack_28;
  double local_24;
  float fStack_1c;
  undefined1 local_14 [12];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_548;
  local_53c = DAT_10029234;
  if (((((*unaff_EBX != 0) && (unaff_EBX[0xe] != 0)) && (unaff_EBX[0x1c] != 0)) &&
      ((unaff_EBX[0x1f] != 0 && (param_4 != 0.0)))) && (param_5 != 0.0)) {
    if (unaff_EBX[0x11a] != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("r_colorCorrectActive");
      if (fVar4 == (float10)0) {
        local_53c = DAT_10029358;
      }
    }
    (**(code **)(DAT_106b40a8 + 0x7c))(unaff_EBX[0x1c],local_14,&local_24);
    (**(code **)(DAT_106b40a8 + 0x84))
              (auStack_414,*unaff_EBX,unaff_EBX[0xa2],unaff_EBX[0xa2],0x3f800000,"tag_torso");
    dStack_544._0_4_ = fStack_40c + (float)_DAT_100294b0;
    (**(code **)(DAT_106b40a8 + 0x84))
              (auStack_414,unaff_EBX[0xe],unaff_EBX[0x60],unaff_EBX[0x60],0x3f800000,"tag_head");
    iVar1 = unaff_EBX[0x10e];
    dStack_544._0_4_ = fStack_1c + fStack_40c + dStack_544._0_4_;
    fStack_538 = ((float)_DAT_100293e8 / dStack_544._0_4_) * (float)_DAT_100294a8;
    DAT_1004fe5c = param_1;
    if ((iVar1 != -1) && (unaff_EBX[0x10f] < param_1)) {
      unaff_EBX[0x10c] = iVar1;
      unaff_EBX[0x10d] = iVar1;
      unaff_EBX[0x10e] = -1;
      unaff_EBX[0x10f] = 0;
      if (unaff_EBX[0x109] != unaff_EBX[0x10c]) {
        (**(code **)(DAT_106b40a8 + 0x88))(DAT_1073fba0,1);
      }
    }
    FUN_10002bf0(&param_2,&param_3,&param_4,&param_5);
    param_3 = param_3 - _DAT_1004f9dc;
    memset(&iStack_2c4,0,0x170);
    memset(auStack_534,0,0x8c);
    memset(auStack_4a4,0,0x8c);
    memset(auStack_3e4,0,0x8c);
    iStack_2bc = (int)param_4;
    iStack_2c4 = (int)param_2;
    iStack_2c0 = (int)param_3;
    iStack_2b8 = (int)param_5;
    uStack_278 = 1;
    uStack_2a0 = DAT_10029234;
    uStack_29c = 0;
    uStack_298 = 0;
    uStack_294 = 0;
    uStack_290 = DAT_10029234;
    uStack_28c = 0;
    uStack_288 = 0;
    uStack_284 = 0;
    uStack_280 = DAT_10029234;
    iVar1 = FUN_10021270();
    fStack_2b4 = (float)iVar1;
    local_24 = (double)iStack_2b8;
    dStack_544 = (double)iStack_2bc;
    fVar4 = (float10)_CItan();
    dStack_544._0_4_ = (float)((float10)dStack_544 / fVar4);
    fVar4 = (float10)_CIatan2();
    dStack_544 = (double)CONCAT44(dStack_544._4_4_,(float)fVar4);
    fStack_2b0 = (float)fVar4 * (float)_DAT_10029498;
    fVar4 = (float10)_CItan();
    fStack_28 = DAT_10029484;
    iStack_27c = DAT_1004fe5c;
    fStack_30 = (float)((float10)_DAT_10029488 / fVar4);
    fStack_2c = (float)_DAT_10029278 * 0.0;
    (**(code **)(DAT_106b40a8 + 0x60))();
    FUN_10012900(auStack_488,auStack_3c8);
    FUN_10012490(auStack_4d4,auStack_4e4,auStack_4d0,auStack_444,auStack_454,auStack_440);
    fStack_4f0 = fStack_30;
    iStack_52c = *unaff_EBX;
    iStack_4c8 = unaff_EBX[1];
    fStack_4ec = fStack_2c;
    fStack_528 = fStack_30;
    fStack_524 = fStack_2c;
    fStack_4e0 = fStack_30;
    fStack_4e8 = fStack_28;
    fStack_520 = fStack_28;
    fStack_4dc = fStack_2c;
    uStack_530 = 0xc0;
    fStack_4d8 = fStack_28;
    if (unaff_EBX[0x11a] != 0) {
      FUN_10001e20();
    }
    if (unaff_EBX[0x11e] != 0) {
      uStack_4f4 = 1;
      fStack_518 = fStack_538 * fStack_518;
      fStack_514 = fStack_514 * fStack_538;
      fStack_510 = fStack_510 * fStack_538;
      fStack_50c = fStack_50c * fStack_538;
      fStack_508 = fStack_508 * fStack_538;
      fStack_504 = fStack_504 * fStack_538;
      fStack_500 = fStack_500 * fStack_538;
      fStack_4fc = fStack_4fc * fStack_538;
      fStack_4f8 = fStack_538 * fStack_4f8;
    }
    (**(code **)(DAT_106b40a8 + 100))(auStack_534);
    if ((iStack_52c != 0) && (iStack_49c = unaff_EBX[0xe], iStack_49c != 0)) {
      iStack_438 = unaff_EBX[0xf];
      fStack_498 = fStack_30;
      fStack_494 = fStack_2c;
      fStack_490 = fStack_28;
      FUN_10012290("tag_torso");
      uStack_4a0 = 0xc0;
      if (unaff_EBX[0x11a] != 0) {
        FUN_10001e20();
      }
      (**(code **)(DAT_106b40a8 + 100))(auStack_4a4);
      iStack_3dc = unaff_EBX[0x1c];
      if (iStack_3dc != 0) {
        iStack_378 = unaff_EBX[0x1d];
        fStack_3d8 = fStack_30;
        fStack_3d4 = fStack_2c;
        fStack_3d0 = fStack_28;
        FUN_10012290("tag_head");
        uStack_3e0 = 0xc0;
        if (unaff_EBX[0x11a] != 0) {
          FUN_10001e20();
        }
        (**(code **)(DAT_106b40a8 + 100))(auStack_3e4);
        if (unaff_EBX[0x109] != 0) {
          memset(auStack_354,0,0x8c);
          iStack_34c = unaff_EBX[0xfc];
          fStack_348 = fStack_30;
          fStack_344 = fStack_2c;
          fStack_340 = fStack_28;
          FUN_10012190("tag_weapon");
          uStack_350 = 0xc0;
          (**(code **)(DAT_106b40a8 + 100))(auStack_354);
        }
        iVar1 = unaff_EBX[0x119];
        if (((iVar1 == 2) || (iVar1 == 1)) || (iVar1 == 9)) {
          memset(auStack_154,0,0x8c);
          iStack_14c = unaff_EBX[0xfd];
          fStack_148 = fStack_30;
          fStack_144 = fStack_2c;
          fStack_140 = fStack_28;
          fVar5 = 0.0;
          uStack_150 = 0xc0;
          local_24 = 0.0;
          FUN_10012ca0();
          if ((unaff_EBX[0x119] == 1) || (fStack_1c = fVar5, unaff_EBX[0x119] == 9)) {
            local_24 = (double)CONCAT44(local_24._4_4_,fVar5);
            fStack_1c = 0.0;
          }
          FUN_100010f0();
          FUN_10012290("tag_barrel");
          (**(code **)(DAT_106b40a8 + 100))(auStack_154);
        }
        if (DAT_1004fe5c <= unaff_EBX[0x102]) {
          iVar1 = unaff_EBX[0xfe];
          if (iVar1 != 0) {
            memset(auStack_c4,0,0x8c);
            fStack_b8 = fStack_30;
            fStack_b4 = fStack_2c;
            fStack_b0 = fStack_28;
            iStack_bc = iVar1;
            FUN_10012190("tag_flash");
            uStack_c0 = 0xc0;
            (**(code **)(DAT_106b40a8 + 100))(auStack_c4);
          }
          iVar1 = DAT_106b40a8;
          fVar5 = (float)unaff_EBX[0xff];
          fStack_538 = fVar5;
          if (((fVar5 != 0.0) || ((float)unaff_EBX[0x100] != 0.0)) ||
             ((float)unaff_EBX[0x101] != 0.0)) {
            iVar7 = unaff_EBX[0x101];
            iVar6 = unaff_EBX[0x100];
            uVar2 = rand();
            (**(code **)(iVar1 + 0x6c))(auStack_80,(float)((uVar2 & 0x1f) + 200),fVar5,iVar6,iVar7);
          }
        }
        if (unaff_EBX[0x114] != 0) {
          uVar3 = (**(code **)(DAT_106b40a8 + 0x5c))("sprites/balloon3");
          FUN_10012c00(uVar3);
        }
        fVar5 = (float)_DAT_10029378;
        fStack_30 = fStack_30 - fVar5;
        fStack_2c = fStack_2c + fVar5;
        fStack_28 = fVar5 + fStack_28;
        (**(code **)(DAT_106b40a8 + 0x6c))
                  (&fStack_30,_DAT_10029480,0x3f800000,0x3f800000,0x3f800000);
        fVar5 = (float)_DAT_10029378;
        fStack_30 = fStack_30 - fVar5;
        fStack_2c = fStack_2c - fVar5;
        fStack_28 = fStack_28 - fVar5;
        (**(code **)(DAT_106b40a8 + 0x6c))(&fStack_30,_DAT_10029480,0x3f800000,0,0);
        (**(code **)(DAT_106b40a8 + 0x70))(&iStack_2c4);
      }
    }
  }
  __security_check_cookie(local_8 ^ (uint)auStack_548);
  return;
}



/* FUN_1001bfb0 @ 1001bfb0 size 2691 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001bfb0(void)

{
  float fVar1;
  int *piVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  undefined4 uVar6;
  int iVar7;
  int iVar8;
  uint uVar9;
  int *piVar10;
  float *unaff_ESI;
  float fVar11;
  float *pfVar12;
  float fStack_20;
  float fStack_1c;
  float fStack_18;
  float fStack_14;
  float fStack_10;
  int iStack_c;
  double dStack_8;
  
  piVar2 = (int *)unaff_ESI[0xa2];
  iVar7 = (**(code **)(DAT_106b40d0 + 0x7c))(unaff_ESI[0xa0]);
  fVar11 = (float)iVar7;
  if (((uint)unaff_ESI[0x12] & 0x400) == 0) {
    fVar3 = ((unaff_ESI[2] + *unaff_ESI) - (float)_DAT_10029320) - 1.0;
    fVar1 = unaff_ESI[1];
    if (piVar2[0x69] == 0) {
      (**(code **)(DAT_106b40d0 + 8))
                (fVar3,fVar1 + 1.0,DAT_10029390,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf1dc))
      ;
    }
    uVar6 = DAT_10029390;
    fVar4 = fVar1 + 1.0 + (float)_DAT_10029440;
    piVar2[1] = *piVar2;
    fVar1 = unaff_ESI[3];
    fVar5 = (float)_DAT_10029318;
    if (piVar2[0x69] == 0) {
      (**(code **)(DAT_106b40d0 + 8))
                (fVar3,fVar4,uVar6,(fVar1 - fVar5) + 1.0,*(undefined4 *)(DAT_106b40d0 + 0xf1ec));
      uVar6 = DAT_10029390;
    }
    fVar4 = fVar4 + ((fVar1 - fVar5) - 1.0);
    if (piVar2[0x69] == 0) {
      (**(code **)(DAT_106b40d0 + 8))
                (fVar3,fVar4,uVar6,uVar6,*(undefined4 *)(DAT_106b40d0 + 0xf1e0));
    }
    iVar8 = FUN_10017310();
    fStack_14 = (float)iVar8;
    fVar1 = (fVar4 - (float)_DAT_10029320) - (float)_DAT_10029228;
    if (fVar1 < fStack_14) {
      fStack_14 = fVar1;
    }
    if (piVar2[0x69] == 0) {
      (**(code **)(DAT_106b40d0 + 8))
                (fVar3,fStack_14,DAT_10029390,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf1f0));
    }
    fVar1 = (float)_DAT_100292f0;
    fStack_14 = unaff_ESI[3] - fVar1;
    if (piVar2[6] == 1) {
      fVar1 = *unaff_ESI;
      fStack_20 = unaff_ESI[1] + 1.0;
      fStack_18 = (float)*piVar2;
      dStack_8 = (double)iVar7;
      if (fStack_18 < fVar11) {
        while( true ) {
          iVar7 = (**(code **)(DAT_106b40d0 + 0x84))(unaff_ESI[0xa0],(int)fStack_18);
          if (iVar7 != 0) {
            (**(code **)(DAT_106b40d0 + 8))
                      (fVar1 + 1.0 + 1.0,fStack_20 + 1.0,(float)piVar2[4] - (float)_DAT_100292f0,
                       (float)piVar2[5] - (float)_DAT_100292f0,iVar7);
          }
          if (fStack_18 == (float)(int)unaff_ESI[0xa1]) {
            (**(code **)(DAT_106b40d0 + 0x28))
                      (fVar1 + 1.0,fStack_20,(float)piVar2[4] - 1.0,(float)piVar2[5] - 1.0,
                       unaff_ESI[0x11],unaff_ESI + 0x26);
          }
          piVar2[1] = piVar2[1] + 1;
          fStack_14 = fStack_14 - (float)piVar2[4];
          if (fStack_14 < (float)piVar2[5]) break;
          fStack_20 = (float)piVar2[5] + fStack_20;
          fStack_18 = fStack_18 + (float)_DAT_10029228;
          if ((float)dStack_8 <= fStack_18) {
            return;
          }
        }
        iVar7 = FUN_10021270();
        piVar2[2] = iVar7;
        return;
      }
    }
    else {
      fVar3 = *unaff_ESI + 1.0;
      fStack_20 = unaff_ESI[1] + 1.0;
      fStack_18 = (float)*piVar2;
      dStack_8 = (double)iVar7;
      if (fStack_18 < fVar11) {
        while( true ) {
          fVar11 = (float)_DAT_10029300;
          if (fStack_18 == (float)(int)unaff_ESI[0xa1]) {
            if (unaff_ESI[0x3b] == 0.0) {
              (**(code **)(DAT_106b40d0 + 0x24))
                        (fVar3 + fVar1,fStack_20 + fVar11,
                         (unaff_ESI[2] - (float)_DAT_10029320) - fVar11,piVar2[5],unaff_ESI + 0x2a);
            }
            else {
              (**(code **)(DAT_106b40d0 + 8))
                        (fVar3 + fVar1,fStack_20 + fVar11,
                         (unaff_ESI[2] - (float)_DAT_10029320) - fVar11,piVar2[5],unaff_ESI[0x3b]);
            }
          }
          else {
            uVar9 = (int)fStack_18 & 0x80000001;
            if ((int)uVar9 < 0) {
              uVar9 = (uVar9 - 1 | 0xfffffffe) + 1;
            }
            if (uVar9 != 0) {
              (**(code **)(DAT_106b40d0 + 0x24))
                        (fVar3 + fVar1,fStack_20 + fVar11,
                         (unaff_ESI[2] - (float)_DAT_10029320) - fVar11,piVar2[5],unaff_ESI + 0x2e);
            }
          }
          if (piVar2[7] < 1) {
            iVar7 = (**(code **)(DAT_106b40d0 + 0x80))(unaff_ESI[0xa0],(int)fStack_18,0,&iStack_c);
            if ((iStack_c < 0) && (iVar7 != 0)) {
              (**(code **)(DAT_106b40d0 + 0x10))
                        (fVar3 + (float)_DAT_10029260,(float)piVar2[5] + fStack_20,unaff_ESI[0x49],
                         unaff_ESI[0x4a],unaff_ESI + 0x1e,iVar7,0,0,unaff_ESI[0x4b]);
            }
          }
          else {
            iVar7 = 0;
            if (0 < piVar2[7]) {
              piVar10 = piVar2 + 10;
              do {
                iVar8 = (**(code **)(DAT_106b40d0 + 0x80))
                                  (unaff_ESI[0xa0],(int)fStack_18,iVar7,&iStack_c);
                if (iStack_c < 0) {
                  if (iVar8 != 0) {
                    if (fStack_18 == (float)(int)unaff_ESI[0xa1]) {
                      pfVar12 = unaff_ESI + 0x36;
                      fVar11 = (float)piVar2[5];
                      fStack_10 = fVar3 + (float)_DAT_10029260 + (float)piVar10[-2];
                    }
                    else {
                      pfVar12 = unaff_ESI + 0x32;
                      fVar11 = (float)piVar2[5];
                      fStack_10 = fVar3 + (float)_DAT_10029260 + (float)piVar10[-2];
                    }
                    (**(code **)(DAT_106b40d0 + 0x10))
                              (fStack_10,fVar11 + fStack_20,unaff_ESI[0x49],unaff_ESI[0x4a],pfVar12,
                               iVar8,0,*piVar10,unaff_ESI[0x4b]);
                  }
                }
                else {
                  (**(code **)(DAT_106b40d0 + 8))
                            (fVar3 + (float)_DAT_10029260 + (float)piVar10[-2],
                             (fStack_20 - (float)_DAT_100292f0) +
                             (float)piVar2[5] * (float)_DAT_10029278,(float)piVar10[-1],
                             (float)piVar10[-1],iStack_c);
                }
                iVar7 = iVar7 + 1;
                piVar10 = piVar10 + 3;
              } while (iVar7 < piVar2[7]);
            }
          }
          fVar11 = (float)piVar2[5];
          fStack_14 = fStack_14 - fVar11;
          if (fStack_14 < fVar11) break;
          piVar2[1] = piVar2[1] + 1;
          fStack_20 = fVar11 + fStack_20;
          fStack_18 = fStack_18 + (float)_DAT_10029228;
          if ((float)dStack_8 <= fStack_18) {
            return;
          }
          fVar1 = (float)_DAT_100292f0;
        }
        iVar7 = FUN_10021270();
        piVar2[2] = iVar7;
        return;
      }
    }
  }
  else {
    fVar1 = *unaff_ESI;
    fVar3 = ((unaff_ESI[3] + unaff_ESI[1]) - (float)_DAT_10029320) - 1.0;
    (**(code **)(DAT_106b40d0 + 8))
              (fVar1 + 1.0,fVar3,DAT_10029390,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf1e4));
    fVar4 = fVar1 + 1.0 + (float)_DAT_10029440;
    fVar1 = unaff_ESI[2];
    fVar5 = (float)_DAT_10029318;
    (**(code **)(DAT_106b40d0 + 8))
              (fVar4,fVar3,(fVar1 - fVar5) + (float)_DAT_10029228,DAT_10029390,
               *(undefined4 *)(DAT_106b40d0 + 0xf1ec));
    fVar4 = ((fVar1 - fVar5) - (float)_DAT_10029228) + fVar4;
    (**(code **)(DAT_106b40d0 + 8))
              (fVar4,fVar3,DAT_10029390,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf1e8));
    iVar8 = FUN_10017310();
    fStack_14 = (float)iVar8;
    fVar1 = (fVar4 - (float)_DAT_10029320) - (float)_DAT_10029228;
    if (fVar1 < fStack_14) {
      fStack_14 = fVar1;
    }
    (**(code **)(DAT_106b40d0 + 8))
              (fStack_14,fVar3,DAT_10029390,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf1f0));
    piVar2[1] = *piVar2;
    fStack_14 = unaff_ESI[2] - (float)_DAT_100292f0;
    if (piVar2[6] == 1) {
      fStack_1c = *unaff_ESI + 1.0;
      fVar1 = unaff_ESI[1];
      fStack_18 = (float)*piVar2;
      dStack_8 = (double)iVar7;
      if (fStack_18 < fVar11) {
        while( true ) {
          iVar7 = (**(code **)(DAT_106b40d0 + 0x84))(unaff_ESI[0xa0],(int)fStack_18);
          if (iVar7 != 0) {
            (**(code **)(DAT_106b40d0 + 8))
                      (fStack_1c + 1.0,fVar1 + 1.0 + 1.0,(float)piVar2[4] - (float)_DAT_100292f0,
                       (float)piVar2[5] - (float)_DAT_100292f0,iVar7);
          }
          if (fStack_18 == (float)(int)unaff_ESI[0xa1]) {
            (**(code **)(DAT_106b40d0 + 0x28))
                      (fStack_1c,fVar1 + 1.0,(float)piVar2[4] - 1.0,(float)piVar2[5] - 1.0,
                       unaff_ESI[0x11],unaff_ESI + 0x26);
          }
          fVar11 = (float)piVar2[4];
          fStack_14 = fStack_14 - fVar11;
          if (fStack_14 < fVar11) break;
          fStack_1c = fVar11 + fStack_1c;
          piVar2[1] = piVar2[1] + 1;
          fStack_18 = fStack_18 + (float)_DAT_10029228;
          if ((float)dStack_8 <= fStack_18) {
            return;
          }
        }
        piVar2[2] = (int)fStack_14;
        return;
      }
    }
  }
  return;
}



/* FUN_1000eba0 @ 1000eba0 size 1425 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_1000eba0(int param_1,float param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  char *pcVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  
  if ((param_2 == _DAT_10029214) || (param_2 == _DAT_10029370)) {
    iVar6 = 0;
    iVar5 = 0;
    iVar3 = 0;
    if (0 < DAT_1075829c) {
      piVar4 = &DAT_107582b4;
      do {
        if (*piVar4 != 0) {
          if (iVar6 == param_3) {
            iVar5 = iVar3;
            if (iVar3 < 0) {
              return;
            }
            break;
          }
          iVar6 = iVar6 + 1;
        }
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 5;
      } while (iVar3 < DAT_1075829c);
      if (iVar5 < DAT_1075829c) {
        iVar3 = (&DAT_107582a4)[iVar5 * 5];
        if ((iVar3 != 0) && (iVar6 = FUN_100016c0(), iVar6 == 0)) {
          if (param_4 != 0) {
            (**(code **)(DAT_106b40a8 + 0x1c))(param_4);
            DAT_1002aedc = 1;
            return;
          }
          (**(code **)(DAT_106b40a8 + 0x1c))("model",(&DAT_107582b0)[iVar5 * 5]);
          (**(code **)(DAT_106b40a8 + 0x1c))("headmodel",(&DAT_107582b0)[iVar5 * 5]);
          DAT_1002aedc = 1;
          return;
        }
        iVar6 = DAT_106b40a8;
        if (param_4 != 0) {
          uVar1 = FUN_10001900("%s/%s",(&DAT_107582b0)[iVar5 * 5],iVar3);
          (**(code **)(iVar6 + 0x1c))(param_4,uVar1);
          DAT_1002aedc = 1;
          return;
        }
        uVar1 = FUN_10001900("%s/%s",(&DAT_107582b0)[iVar5 * 5],iVar3);
        (**(code **)(iVar6 + 0x1c))("model",uVar1);
        iVar3 = DAT_106b40a8;
        uVar1 = FUN_10001900("%s/%s",(&DAT_107582b0)[iVar5 * 5],(&DAT_107582a4)[iVar5 * 5]);
        (**(code **)(iVar3 + 0x1c))("headmodel",uVar1);
        DAT_1002aedc = 1;
        return;
      }
    }
    return;
  }
  if (param_2 != _DAT_1002936c) {
    if (param_2 == DAT_10029234) {
      iVar5 = DAT_10744ccc;
      if (param_2 != _DAT_10029368) goto LAB_1000ee58;
    }
    else if (param_2 != _DAT_10029368) {
      if (param_2 == DAT_10029358) {
        DAT_1076249c = param_3;
        (**(code **)(DAT_106b40a8 + 0xcc))
                  (DAT_1074148c,(&DAT_107624a0)[param_3],&DAT_10046040,0x400);
        iVar5 = DAT_106b40a8;
        uVar1 = FUN_10001940();
        uVar1 = FUN_10001900("levelshots/%s",uVar1);
        DAT_107644b0 = (**(code **)(iVar5 + 0x5c))(uVar1);
        if (-1 < DAT_107644b4) {
          (**(code **)(DAT_106b40a8 + 0x128))(DAT_107644b4);
          DAT_107644b4 = -1;
        }
        pcVar2 = (char *)FUN_10001940();
        iVar5 = DAT_106b40a8;
        if (pcVar2 == (char *)0x0) {
          return;
        }
        if (*pcVar2 == '\0') {
          return;
        }
        uVar1 = FUN_10001900("%s.roq",pcVar2,0,0,0,0,10);
        DAT_107644b4 = (**(code **)(iVar5 + 0x124))(uVar1);
        return;
      }
      if (param_2 == (float)_DAT_10029460) {
        return;
      }
      if (param_2 == (float)_DAT_10029410) {
        DAT_10766adc = param_3;
        if (DAT_10766ae0 + -1 <= param_3) {
          return;
        }
        if (&DAT_107662dc + param_3 * 0x40 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(&DAT_107648d0,&DAT_107662dc + param_3 * 0x40,0x3f);
        DAT_1076490f = 0;
        FUN_1001d3d0(0xd);
        FUN_1000e3b0(1);
        return;
      }
      if (param_2 == (float)_DAT_10029458) {
        DAT_107597c0 = param_3;
        return;
      }
      if (param_2 == _DAT_1002941c) {
        _DAT_107597b8 = param_3;
        return;
      }
      if (param_2 == _DAT_10029454) {
        DAT_107613dc = param_3;
        return;
      }
      if (param_2 != (float)_DAT_10029440) {
        if (param_2 != DAT_10029238) {
          return;
        }
        DAT_107617e4 = param_3;
        return;
      }
      DAT_10761bec = param_3;
      if (-1 < DAT_10761bf0) {
        (**(code **)(DAT_106b40a8 + 0x128))(DAT_10761bf0);
      }
      DAT_10761bf0 = -1;
      return;
    }
  }
  iVar5 = DAT_10742f8c;
LAB_1000ee58:
  iVar3 = (&DAT_1075adec)[iVar5 * 0x19];
  if (-1 < iVar3) {
    (**(code **)(DAT_106b40a8 + 0x128))(iVar3);
    (&DAT_1075adec)[iVar5 * 0x19] = -1;
  }
  (**(code **)(DAT_106b40a8 + 0x18))(&DAT_10741c60);
  FUN_1000d300();
  FUN_1000e600();
  iVar5 = DAT_106b40a8;
  _DAT_1074340c = param_3;
  uVar1 = FUN_10001900(&DAT_10025d20,param_3);
  (**(code **)(iVar5 + 0x1c))("ui_mapIndex",uVar1);
  iVar5 = DAT_106b40a8;
  if (param_2 == DAT_10029234) {
    DAT_10744ccc = param_1;
    uVar1 = FUN_10001900(&DAT_10025d20,param_1);
    (**(code **)(iVar5 + 0x1c))("ui_currentMap",uVar1);
    iVar3 = DAT_10744ccc;
    iVar5 = DAT_106b40a8;
    uVar1 = FUN_10001900("%s.roq",(&DAT_1075add8)[DAT_10744ccc * 0x19],0,0,0,0,10);
    uVar1 = (**(code **)(iVar5 + 0x124))(uVar1);
    (&DAT_1075adec)[iVar3 * 0x19] = uVar1;
    FUN_10002350();
    (**(code **)(DAT_106b40a8 + 0x1c))("ui_opponentModel",(&DAT_1075ade0)[DAT_10744ccc * 0x19]);
    DAT_1002af44 = 1;
    return;
  }
  if (DAT_10766b00 != 0) {
    DAT_10742f8c = param_1;
    uVar1 = FUN_10001900(&DAT_10025d20,param_1);
    (**(code **)(iVar5 + 0x1c))("ui_currentNetMap",uVar1);
    return;
  }
  DAT_10766b00 = 1;
  return;
}



/* FUN_10002550 @ 10002550 size 1380 */

void FUN_10002550(void)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined1 auStack_524 [4];
  undefined4 uStack_520;
  int iStack_51c;
  double dStack_518;
  int iStack_510;
  int iStack_50c;
  int iStack_508;
  int iStack_504;
  int iStack_500;
  int iStack_4fc;
  int iStack_4f8;
  int iStack_4f4;
  int iStack_4f0;
  int iStack_4ec;
  int iStack_4e8;
  int iStack_4e4;
  int iStack_4e0;
  int iStack_4dc;
  int iStack_4d8;
  int iStack_4d4;
  int aiStack_4d0 [11];
  int iStack_4a4;
  char acStack_490 [63];
  undefined1 uStack_451;
  undefined1 auStack_450 [64];
  undefined1 local_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_524;
  (**(code **)(DAT_106b40a8 + 0xc0))(0,local_410,0x400);
  pcVar1 = (char *)FUN_10001940();
  if (pcVar1 == (char *)0x0) {
    FUN_10001e70(0,"Q_strncpyz: NULL src");
  }
  strncpy(acStack_490,pcVar1,0x3f);
  uStack_451 = 0;
  pcVar1 = (char *)FUN_10001940();
  iVar2 = atoi(pcVar1);
  FUN_10001830(auStack_450,0x40,"games/%s_%i.game",acStack_490,iVar2);
  memset(aiStack_4d0,0,0x40);
  iVar3 = (**(code **)(DAT_106b40a8 + 0x38))(auStack_450,&uStack_520,0);
  if (-1 < iVar3) {
    iStack_51c = 0;
    (**(code **)(DAT_106b40a8 + 0x3c))(&iStack_51c,4,uStack_520);
    if (iStack_51c == 0x40) {
      (**(code **)(DAT_106b40a8 + 0x3c))(aiStack_4d0,0x40,uStack_520);
    }
    (**(code **)(DAT_106b40a8 + 0x44))(uStack_520);
  }
  (**(code **)(DAT_106b40a8 + 0x30))(3,&DAT_10042b38,0x400);
  iStack_500 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(4,&DAT_10042b38,0x400);
  iStack_4fc = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(5,&DAT_10042b38,0x400);
  iStack_4f8 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(6,&DAT_10042b38,0x400);
  iStack_4f4 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(7,&DAT_10042b38,0x400);
  iStack_4f0 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(8,&DAT_10042b38,0x400);
  iStack_4ec = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(9,&DAT_10042b38,0x400);
  iStack_4d4 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(10,&DAT_10042b38,0x400);
  iStack_504 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(0xb,&DAT_10042b38,0x400);
  iStack_50c = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(0xc,&DAT_10042b38,0x400);
  iStack_508 = atoi(&DAT_10042b38);
  (**(code **)(DAT_106b40a8 + 0x30))(0xd,&DAT_10042b38,0x400);
  iVar3 = atoi(&DAT_10042b38);
  dStack_518 = (double)CONCAT44(dStack_518._4_4_,iVar3);
  (**(code **)(DAT_106b40a8 + 0x30))(0xe,&DAT_10042b38,0x400);
  iStack_4e8 = atoi(&DAT_10042b38);
  dStack_518 = (double)dStack_518._0_4_;
  (**(code **)(DAT_106b40a8 + 0x28))("ui_matchStartTime");
  iStack_4e4 = FUN_10021270();
  if (iStack_4e4 < *(int *)(&DAT_1075adf0 + (DAT_10744ccc * 0x19 + iVar2) * 4)) {
    iStack_4e0 = (*(int *)(&DAT_1075adf0 + (DAT_10744ccc * 0x19 + iVar2) * 4) - iStack_4e4) * 10;
  }
  else {
    iStack_4e0 = 0;
  }
  if ((iStack_50c <= iStack_508) || (iStack_4dc = 100, 0 < iStack_508)) {
    iStack_4dc = 0;
  }
  (**(code **)(DAT_106b40a8 + 0x28))("g_spSkill");
  iStack_4d8 = FUN_10021270();
  if (iStack_4d8 < 1) {
    iStack_4d8 = 1;
  }
  iStack_510 = (iStack_4e0 + iStack_4dc + iStack_4d4) * iStack_4d8;
  if ((iStack_508 < iStack_50c) &&
     (iStack_510 - aiStack_4d0[0] != 0 && aiStack_4d0[0] <= iStack_510)) {
    DAT_10758284 = DAT_10746428 + 20000;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x38))(auStack_450,&uStack_520,1);
    if (-1 < iVar2) {
      iStack_51c = 0x40;
      (**(code **)(DAT_106b40a8 + 0x40))(&iStack_51c,4,uStack_520);
      (**(code **)(DAT_106b40a8 + 0x40))(&iStack_510,0x40,uStack_520);
      (**(code **)(DAT_106b40a8 + 0x44))(uStack_520);
    }
  }
  if (iStack_4e4 < iStack_4a4) {
    DAT_10758288 = DAT_10746428 + 20000;
  }
  (**(code **)(DAT_106b40a8 + 0x24))("ui_saveCaptureLimit",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("capturelimit",&DAT_10042f38);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_saveFragLimit",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("fraglimit",&DAT_10042f38);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_doWarmup",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("g_doWarmup",&DAT_10042f38);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_Warmup",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("g_Warmup",&DAT_10042f38);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_pure",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("sv_pure",&DAT_10042f38);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_friendlyFire",&DAT_10042f38,0x400);
  (**(code **)(DAT_106b40a8 + 0x1c))("g_friendlyFire",&DAT_10042f38);
  FUN_10001f70(1);
  __security_check_cookie(local_c ^ (uint)auStack_524);
  return;
}



/* FUN_100045b0 @ 100045b0 size 1379 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100045b0(undefined4 param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_844 [4];
  undefined4 uStack_840;
  undefined4 uStack_83c;
  undefined4 uStack_838;
  undefined4 uStack_834;
  undefined1 local_830 [1040];
  undefined1 auStack_420 [1044];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_844;
  iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_830);
  if ((iVar1 == 0) || (iVar1 = FUN_100016c0(), iVar1 != 0)) {
LAB_10004ae2:
    __security_check_cookie(local_c ^ (uint)auStack_844);
    return;
  }
  memset(local_830,0,0x410);
  iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_830);
joined_r0x10004633:
  if (iVar1 == 0) goto LAB_10004ae2;
  iVar1 = FUN_100016c0();
  if (iVar1 == 0) {
    __security_check_cookie(local_c ^ (uint)auStack_844);
    return;
  }
  iVar1 = FUN_100016c0();
  if (iVar1 == 0) {
    iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,auStack_420);
    if (iVar1 == 0) goto LAB_10004ae2;
    FUN_100016c0();
    uVar2 = FUN_10014560();
    uStack_840 = uVar2;
    iVar1 = FUN_10014ae0();
    if (iVar1 == 0) goto LAB_10004ae2;
    (**(code **)(DAT_106b40a8 + 0x118))(uVar2,uStack_834,&DAT_10746448);
    _DAT_10755580 = 1;
  }
  else {
    iVar1 = FUN_100016c0();
    if (iVar1 == 0) {
      iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,auStack_420);
      if (iVar1 == 0) goto LAB_10004ae2;
      FUN_100016c0();
      uVar2 = FUN_10014560();
      uStack_840 = uVar2;
      iVar1 = FUN_10014ae0();
      if (iVar1 == 0) goto LAB_10004ae2;
      (**(code **)(DAT_106b40a8 + 0x118))(uVar2,uStack_83c,&DAT_1074b48c);
    }
    else {
      iVar1 = FUN_100016c0();
      if (iVar1 == 0) {
        iVar1 = FUN_10014c60();
        if ((iVar1 == 0) || (iVar1 = FUN_10014ae0(), iVar1 == 0)) goto LAB_10004ae2;
        (**(code **)(DAT_106b40a8 + 0x118))(uStack_840,uStack_838,&DAT_107504d0);
      }
      else {
        iVar1 = FUN_100016c0();
        if (iVar1 == 0) {
          iVar1 = FUN_10014c60();
          if (iVar1 == 0) goto LAB_10004ae2;
          _DAT_10755518 = (**(code **)(DAT_106b40a8 + 0x5c))(uStack_840);
        }
        else {
          iVar1 = FUN_100016c0();
          if (iVar1 == 0) {
            iVar1 = FUN_10014c60();
            if (iVar1 == 0) goto LAB_10004ae2;
            _DAT_10755548 = (**(code **)(DAT_106b40a8 + 0x8c))(uStack_840);
          }
          else {
            iVar1 = FUN_100016c0();
            if (iVar1 == 0) {
              iVar1 = FUN_10014c60();
              if (iVar1 == 0) goto LAB_10004ae2;
              _DAT_1075554c = (**(code **)(DAT_106b40a8 + 0x8c))(uStack_840);
            }
            else {
              iVar1 = FUN_100016c0();
              if (iVar1 == 0) {
                iVar1 = FUN_10014c60();
                if (iVar1 == 0) goto LAB_10004ae2;
                _DAT_10755554 = (**(code **)(DAT_106b40a8 + 0x8c))(uStack_840);
              }
              else {
                iVar1 = FUN_100016c0();
                if (iVar1 == 0) {
                  iVar1 = FUN_10014c60();
                  if (iVar1 == 0) goto LAB_10004ae2;
                  _DAT_10755550 = (**(code **)(DAT_106b40a8 + 0x8c))(uStack_840);
                }
                else {
                  iVar1 = FUN_100016c0();
                  if (iVar1 == 0) {
                    iVar1 = FUN_10014c60();
                    if (iVar1 == 0) goto LAB_10004ae2;
                    _DAT_10755514 = (**(code **)(DAT_106b40a8 + 0x5c))(DAT_10746440);
                  }
                  else {
                    iVar1 = FUN_100016c0();
                    if (iVar1 == 0) {
LAB_10004a6b:
                      iVar1 = FUN_100148d0();
                    }
                    else {
                      iVar1 = FUN_100016c0();
                      if (iVar1 != 0) {
                        iVar1 = FUN_100016c0();
                        if (((iVar1 == 0) || (iVar1 = FUN_100016c0(), iVar1 == 0)) ||
                           (iVar1 = FUN_100016c0(), iVar1 == 0)) goto LAB_10004a6b;
                        iVar1 = FUN_100016c0();
                        if (iVar1 != 0) goto LAB_10004ab2;
                        iVar1 = FUN_100149d0(param_1);
                        if (iVar1 == 0) goto LAB_10004ae2;
                        _DAT_1075557c = DAT_10755578;
                        goto LAB_10004ab2;
                      }
                      iVar1 = FUN_10014ae0();
                    }
                    if (iVar1 == 0) goto LAB_10004ae2;
                  }
                }
              }
            }
          }
        }
      }
    }
  }
LAB_10004ab2:
  memset(local_830,0,0x410);
  iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_830);
  goto joined_r0x10004633;
}



/* FUN_100108d0 @ 100108d0 size 1353 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_100108d0(undefined4 param_1,float param_2,float param_3,undefined4 param_4)

{
  double dVar1;
  float fVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined8 uVar7;
  longlong lVar8;
  undefined1 auStack_17c [4];
  float fStack_178;
  float fStack_174;
  uint uStack_170;
  uint uStack_16c;
  uint uStack_168;
  uint uStack_164;
  undefined8 uStack_160;
  undefined4 uStack_158;
  undefined4 uStack_154;
  undefined1 auStack_150 [64];
  undefined1 auStack_110 [64];
  char local_d0 [128];
  undefined1 auStack_50 [68];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_17c;
  (**(code **)(DAT_106b40a8 + 0x24))("cl_downloadItem",local_d0,0x40);
  sscanf(local_d0,"%llu",&uStack_158);
  (**(code **)(DAT_106b40a8 + 0x180))(uStack_158,uStack_154,&uStack_168,&uStack_170);
  (**(code **)(DAT_106b40a8 + 0x28))("cl_downloadTime");
  uStack_160 = FUN_100212a6();
  (**(code **)(DAT_106b40a8 + 0x74))(&DAT_1002be24);
  FUN_10003d90(0,param_4);
  fStack_174 = param_3 + (float)_DAT_100294f0;
  fStack_178 = param_2 - (float)((int)fStack_178 / 2);
  FUN_10003ec0(fStack_178,fStack_174,0,param_4,&DAT_1002be24,s_Downloading__1002af9c,0,0,6);
  FUN_10003d90(0,param_4);
  fStack_178 = param_2 - (float)((int)fStack_174 / 2);
  FUN_10003ec0(fStack_178,param_3 + (float)_DAT_100294e8,0,param_4,&DAT_1002be24,
               s_Estimated_time_left__1002afac,0,0,6);
  FUN_10003d90(0,param_4);
  fStack_178 = param_2 - (float)((int)fStack_174 / 2);
  FUN_10003ec0(fStack_178,param_3 + (float)_DAT_100294e0,0,param_4,&DAT_1002be24,
               s_Transfer_rate__1002afc4,0,0,6);
  uVar4 = uStack_16c;
  uVar3 = uStack_170;
  if ((uStack_16c != 0) || (uStack_170 != 0)) {
    uVar7 = __allmul(uStack_168,uStack_164,100,0);
    uVar7 = __aulldiv(uVar7,uVar3,uVar4);
    FUN_10001900("%s (%d%%)",param_1,uVar7);
  }
  fStack_178 = param_3 + (float)_DAT_100294d8;
  FUN_100105f0(param_2,fStack_178,param_4);
  FUN_100103f0();
  FUN_100103f0();
  uVar4 = uStack_164;
  uVar3 = uStack_168;
  if (((uStack_164 == 0) && (uStack_168 < 0x1000)) || (uStack_160 == 0)) {
    fStack_178 = param_3 + (float)_DAT_100294d0;
    FUN_100105f0(_DAT_100294c8,fStack_178,param_4);
    FUN_10001900("(%s of %s copied)",auStack_150,auStack_110);
    dVar1 = _DAT_100294c0;
  }
  else {
    lVar8 = __aulldiv(DAT_10746428 - (uint)uStack_160,
                      (((int)DAT_10746428 >> 0x1f) - uStack_160._4_4_) -
                      (uint)(DAT_10746428 < (uint)uStack_160),1000,0);
    if (lVar8 == 0) {
      fStack_174 = 0.0;
    }
    else {
      fStack_174 = (float)__aulldiv(uVar3,uVar4,lVar8);
    }
    fVar2 = fStack_174;
    FUN_100103f0();
    if ((uStack_170 == 0 && uStack_16c == 0) || (fVar2 == 0.0)) {
      fStack_178 = param_3 + (float)_DAT_100294d0;
      FUN_100105f0(_DAT_100294c8,fStack_178,param_4);
      if (uStack_170 == 0 && uStack_16c == 0) {
        FUN_10001900("(%s copied)",auStack_150);
        fStack_178 = param_3 + (float)_DAT_100294c0;
      }
      else {
        FUN_10001900("(%s of %s copied)",auStack_150,auStack_110);
        fStack_178 = param_3 + (float)_DAT_100294c0;
      }
    }
    else {
      iVar5 = __aulldiv(uStack_170,uStack_16c,fVar2,(int)fVar2 >> 0x1f);
      uVar7 = __allmul(uStack_168 >> 10 | uStack_164 << 0x16,uStack_164 >> 10,iVar5,iVar5 >> 0x1f);
      iVar6 = __aulldiv(uVar7,uStack_170 >> 10 | uStack_16c << 0x16,uStack_16c >> 10);
      FUN_10010540((iVar5 - iVar6) * 1000);
      fStack_178 = param_3 + (float)_DAT_100294d0;
      FUN_100105f0(_DAT_100294c8,fStack_178,param_4);
      FUN_10001900("(%s of %s copied)",auStack_150,auStack_110);
      fStack_178 = param_3 + (float)_DAT_100294c0;
    }
    FUN_100105f0(_DAT_100294c8,fStack_178,param_4);
    if (fStack_174 == 0.0) goto LAB_10010e04;
    FUN_10001900("%s/Sec",auStack_50);
    dVar1 = _DAT_100294b8;
  }
  fStack_178 = param_3 + (float)dVar1;
  FUN_100105f0(_DAT_100294c8,fStack_178,param_4);
LAB_10010e04:
  __security_check_cookie(local_c ^ (uint)auStack_17c);
  return;
}



/* FUN_10014f00 @ 10014f00 size 1284 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10014f00(undefined4 param_1,undefined4 param_2)

{
  float fVar1;
  float *pfVar2;
  float *unaff_EBX;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_28;
  local_28 = *unaff_EBX;
  local_24 = unaff_EBX[1];
  local_20 = unaff_EBX[2];
  local_1c = unaff_EBX[3];
  if (DAT_106b40ec != 0) {
    local_8 = DAT_10029234;
    local_c = DAT_10029234;
    local_10 = DAT_10029234;
    local_14 = DAT_10029234;
    (**(code **)(DAT_106b40d0 + 0x28))
              (*unaff_EBX,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],0x3f800000,&local_14);
  }
  fVar1 = unaff_EBX[0xc];
  if ((fVar1 != 0.0) || (unaff_EBX[0xd] != 0.0)) {
    if (unaff_EBX[0xd] != 0.0) {
      local_18 = unaff_EBX[0x11];
      local_28 = local_18 + local_28;
      local_24 = local_18 + local_24;
      local_20 = local_20 - (local_18 + (float)_DAT_10029228);
      local_1c = local_1c - (local_18 + (float)_DAT_10029228);
    }
    if (fVar1 == 1.4013e-45) {
      if (unaff_EBX[0x3a] == 0.0) {
        (**(code **)(DAT_106b40d0 + 0x24))(local_28,local_24,local_20,local_1c,unaff_EBX + 0x22);
      }
      else {
        FUN_10014ea0(param_2,param_1);
        (**(code **)(DAT_106b40d0 + 4))(unaff_EBX + 0x22);
        (**(code **)(DAT_106b40d0 + 8))(local_28,local_24,local_20,local_1c,unaff_EBX[0x3a]);
        (**(code **)(DAT_106b40d0 + 4))(0);
      }
    }
    else if (fVar1 == 2.8026e-45) {
      FUN_10014e50();
    }
    else if (fVar1 == 4.2039e-45) {
      if (((uint)unaff_EBX[0x12] & 0x200) != 0) {
        (**(code **)(DAT_106b40d0 + 4))(unaff_EBX + 0x1e);
      }
      (**(code **)(DAT_106b40d0 + 8))(local_28,local_24,local_20,local_1c,unaff_EBX[0x3a]);
      (**(code **)(DAT_106b40d0 + 4))(0);
    }
    else if (fVar1 == 5.60519e-45) {
      if (*(code **)(DAT_106b40d0 + 0x54) != (code *)0x0) {
        (**(code **)(DAT_106b40d0 + 0x54))(&local_14);
        (**(code **)(DAT_106b40d0 + 0x24))(local_28,local_24,local_20,local_1c,&local_14);
      }
    }
    else if (fVar1 == 7.00649e-45) {
      if (unaff_EBX[0xb] == -NAN) {
        fVar1 = (float)(**(code **)(DAT_106b40d0 + 0xb8))
                                 (unaff_EBX[10],local_28,local_24,local_20,local_1c);
        unaff_EBX[0xb] = fVar1;
        if (fVar1 == -NAN) {
          unaff_EBX[0xb] = -NAN;
        }
      }
      if (-1 < (int)unaff_EBX[0xb]) {
        (**(code **)(DAT_106b40d0 + 0xc4))(unaff_EBX[0xb]);
        (**(code **)(DAT_106b40d0 + 0xc0))(unaff_EBX[0xb],local_28,local_24,local_20,local_1c);
      }
    }
    fVar1 = unaff_EBX[0xd];
    if (fVar1 == 1.4013e-45) {
      if (unaff_EBX[0xc] == 5.60519e-45) {
        local_10 = DAT_10029328;
        if (local_14 <= _DAT_10029214) {
          local_c = DAT_10029234;
          local_14 = DAT_10029328;
          local_8 = DAT_10029234;
          pfVar2 = &local_14;
        }
        else {
          local_14 = DAT_10029234;
          local_c = DAT_10029328;
          local_8 = DAT_10029234;
          pfVar2 = &local_14;
        }
      }
      else {
        pfVar2 = unaff_EBX + 0x26;
      }
      (**(code **)(DAT_106b40d0 + 0x28))
                (*unaff_EBX,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],unaff_EBX[0x11],pfVar2);
      __security_check_cookie(local_4 ^ (uint)&local_28);
      return;
    }
    if (fVar1 == 2.8026e-45) {
      (**(code **)(DAT_106b40d0 + 4))(unaff_EBX + 0x26);
      (**(code **)(DAT_106b40d0 + 0x30))
                (*unaff_EBX,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],unaff_EBX[0x11]);
      (**(code **)(DAT_106b40d0 + 4))(0);
      __security_check_cookie(local_4 ^ (uint)&local_28);
      return;
    }
    if (fVar1 == 4.2039e-45) {
      (**(code **)(DAT_106b40d0 + 4))(unaff_EBX + 0x26);
      (**(code **)(DAT_106b40d0 + 0x2c))
                (*unaff_EBX,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],unaff_EBX[0x11]);
      (**(code **)(DAT_106b40d0 + 4))(0);
      __security_check_cookie(local_4 ^ (uint)&local_28);
      return;
    }
    if (fVar1 == 5.60519e-45) {
      local_28 = *unaff_EBX;
      local_24 = unaff_EBX[1];
      local_20 = unaff_EBX[2];
      local_1c = unaff_EBX[0x11];
      FUN_10014e50();
      local_24 = (unaff_EBX[3] + unaff_EBX[1]) - (float)_DAT_10029228;
      FUN_10014e50();
    }
  }
  __security_check_cookie(local_4 ^ (uint)&local_28);
  return;
}



/* FUN_10017b90 @ 10017b90 size 1284 */

undefined4 FUN_10017b90(void)

{
  float *pfVar1;
  float *pfVar2;
  float fVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int unaff_EBX;
  float fVar7;
  float *unaff_EDI;
  
  pfVar2 = (float *)unaff_EDI[0xa2];
  iVar4 = (**(code **)(DAT_106b40d0 + 0x7c))(unaff_EDI[0xa0]);
  if ((float)*(int *)(DAT_106b40d0 + 0xf0) <= *unaff_EDI) {
    return 0;
  }
  if (unaff_EDI[2] + *unaff_EDI <= (float)*(int *)(DAT_106b40d0 + 0xf0)) {
    return 0;
  }
  if ((float)*(int *)(DAT_106b40d0 + 0xf4) <= unaff_EDI[1]) {
    return 0;
  }
  if (unaff_EDI[3] + unaff_EDI[1] <= (float)*(int *)(DAT_106b40d0 + 0xf4)) {
    return 0;
  }
  if (((uint)unaff_EDI[0x12] & 2) == 0) {
    return 0;
  }
  (**(code **)(DAT_106b40d0 + 0x7c))(unaff_EDI[0xa0]);
  fVar3 = unaff_EDI[0x12];
  uVar5 = FUN_10021270();
  fVar7 = (float)(((int)uVar5 < 0) - 1 & uVar5);
  if (((uint)fVar3 & 0x400) == 0) {
    iVar6 = FUN_10021270();
    if ((unaff_EBX == 0x84) || (unaff_EBX == 0xa1)) goto LAB_1001801e;
    if ((unaff_EBX == 0x85) || (unaff_EBX == 0xa7)) {
      if (pfVar2[0x69] == 0.0) {
        pfVar2[3] = (float)((int)pfVar2[3] + 1);
        fVar3 = pfVar2[3];
        if ((int)fVar3 < (int)*pfVar2) {
          *pfVar2 = fVar3;
        }
        if (iVar4 <= (int)fVar3) {
          pfVar2[3] = (float)(iVar4 + -1);
        }
        fVar3 = pfVar2[3];
        if ((int)*pfVar2 + iVar6 <= (int)fVar3) {
          *pfVar2 = (float)(((int)fVar3 - iVar6) + 1);
        }
        unaff_EDI[0xa1] = fVar3;
        (**(code **)(DAT_106b40d0 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
        return 1;
      }
      goto LAB_10017efb;
    }
LAB_10017d85:
    if ((unaff_EBX == 0xb2) || (unaff_EBX == 0xb3)) {
      fVar3 = unaff_EDI[0x12];
      if (((uint)fVar3 & 0x800) != 0) goto LAB_1001807f;
      if (((uint)fVar3 & 0x1000) != 0) {
LAB_10017efb:
        *pfVar2 = (float)((int)*pfVar2 + 1);
        if ((int)*pfVar2 <= (int)fVar7) {
          return 1;
        }
        *pfVar2 = fVar7;
        return 1;
      }
      if (((uint)fVar3 & 0x4000) == 0) {
        if (((uint)fVar3 & 0x8000) == 0) {
          if (((uint)fVar3 & 0x2000) != 0) {
            return 1;
          }
          if ((*(int *)(DAT_106b40d0 + 0xe8) < DAT_106b40f0) && (pfVar2[0x68] != 0.0)) {
            FUN_10016d70();
          }
          iVar4 = DAT_106b40d0;
          fVar3 = pfVar2[3];
          DAT_106b40f0 = *(int *)(DAT_106b40d0 + 0xe8) + 300;
          if (unaff_EDI[0xa1] == fVar3) {
            return 1;
          }
          unaff_EDI[0xa1] = fVar3;
          (**(code **)(iVar4 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
          return 1;
        }
        goto LAB_10017e68;
      }
    }
    else {
      if ((unaff_EBX == 0x8f) || (unaff_EBX == 0xa0)) goto LAB_10018083;
      if ((unaff_EBX == 0x90) || (unaff_EBX == 0xa6)) goto LAB_10017e72;
      if ((unaff_EBX != 0x8e) && (unaff_EBX != 0xa2)) {
        if ((unaff_EBX != 0x8d) && (unaff_EBX != 0xa8)) {
          return 0;
        }
        if (pfVar2[0x69] == 0.0) {
          pfVar2[3] = (float)((int)pfVar2[3] + iVar6);
          fVar3 = pfVar2[3];
          if ((int)fVar3 < (int)*pfVar2) {
            *pfVar2 = fVar3;
          }
          if (iVar4 <= (int)fVar3) {
            pfVar2[3] = (float)(iVar4 + -1);
          }
          fVar3 = pfVar2[3];
          if ((int)*pfVar2 + iVar6 <= (int)fVar3) {
            *pfVar2 = (float)(((int)fVar3 - iVar6) + 1);
          }
          unaff_EDI[0xa1] = fVar3;
          (**(code **)(DAT_106b40d0 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
          return 1;
        }
LAB_10017e68:
        *pfVar2 = (float)((int)*pfVar2 + iVar6);
        if ((int)*pfVar2 <= (int)fVar7) {
          return 1;
        }
LAB_10017e72:
        *pfVar2 = fVar7;
        return 1;
      }
      if (pfVar2[0x69] == 0.0) {
        pfVar1 = pfVar2 + 3;
        *pfVar1 = (float)((int)*pfVar1 - iVar6);
        if ((int)*pfVar1 < 0) {
          pfVar2[3] = 0.0;
        }
        fVar3 = pfVar2[3];
        if ((int)fVar3 < (int)*pfVar2) {
          *pfVar2 = fVar3;
        }
        if ((int)*pfVar2 + iVar6 <= (int)fVar3) {
          *pfVar2 = (float)(((int)fVar3 - iVar6) + 1);
        }
        unaff_EDI[0xa1] = fVar3;
        (**(code **)(DAT_106b40d0 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
        return 1;
      }
    }
    *pfVar2 = (float)((int)*pfVar2 - iVar6);
    fVar3 = *pfVar2;
  }
  else {
    iVar6 = FUN_10021270();
    if ((unaff_EBX != 0x86) && (unaff_EBX != 0xa3)) {
      if ((unaff_EBX == 0x87) || (unaff_EBX == 0xa5)) {
        if (pfVar2[0x69] == 0.0) {
          pfVar2[3] = (float)((int)pfVar2[3] + 1);
          fVar3 = pfVar2[3];
          if ((int)fVar3 < (int)*pfVar2) {
            *pfVar2 = fVar3;
          }
          if (iVar4 <= (int)fVar3) {
            pfVar2[3] = (float)(iVar4 + -1);
          }
          fVar3 = pfVar2[3];
          if ((int)*pfVar2 + iVar6 <= (int)fVar3) {
            *pfVar2 = (float)(((int)fVar3 - iVar6) + 1);
          }
          unaff_EDI[0xa1] = fVar3;
          (**(code **)(DAT_106b40d0 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
          return 1;
        }
        *pfVar2 = (float)((int)*pfVar2 + 1);
        if ((int)*pfVar2 < iVar4) {
          return 1;
        }
        *pfVar2 = (float)(iVar4 + -1);
        return 1;
      }
      goto LAB_10017d85;
    }
LAB_1001801e:
    if (pfVar2[0x69] == 0.0) {
      pfVar1 = pfVar2 + 3;
      *pfVar1 = (float)((int)*pfVar1 + -1);
      if ((int)*pfVar1 < 0) {
        pfVar2[3] = 0.0;
      }
      fVar3 = pfVar2[3];
      if ((int)fVar3 < (int)*pfVar2) {
        *pfVar2 = fVar3;
      }
      if ((int)*pfVar2 + iVar6 <= (int)fVar3) {
        *pfVar2 = (float)(((int)fVar3 - iVar6) + 1);
      }
      unaff_EDI[0xa1] = fVar3;
      (**(code **)(DAT_106b40d0 + 0x88))(unaff_EDI[0xa0],fVar3,unaff_EDI[0x56]);
      return 1;
    }
LAB_1001807f:
    *pfVar2 = (float)((int)*pfVar2 + -1);
    fVar3 = *pfVar2;
  }
  if (-1 < (int)fVar3) {
    return 1;
  }
LAB_10018083:
  *pfVar2 = 0.0;
  return 1;
}



/* FUN_1000deb0 @ 1000deb0 size 1267 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1000deb0(int param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  char *pcVar5;
  int *piVar6;
  undefined *puVar7;
  undefined4 *puVar8;
  char *pcVar9;
  undefined4 *local_1148;
  int local_1144;
  undefined4 local_10f8 [814];
  int local_440;
  char local_434 [41];
  undefined1 local_40b;
  undefined1 auStack_408 [1028];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_1148;
  if (param_1 == 0) {
    if ((DAT_10766ae4 == 0) || (DAT_10746428 < DAT_10766ae4)) goto LAB_1000e38a;
  }
  else {
    memset(&DAT_10765618,0,0x8c4);
    DAT_10766ae0 = 0;
    DAT_10766adc = 0;
    (**(code **)(DAT_106b40a8 + 0x24))("ui_findPlayer",&DAT_10765edc,0x400);
    pcVar5 = (char *)FUN_100017e0();
    pcVar9 = pcVar5 + 1;
    do {
      cVar1 = *pcVar5;
      pcVar5 = pcVar5 + 1;
    } while (cVar1 != '\0');
    if (pcVar5 == pcVar9) {
      DAT_10766ae4 = 0;
      goto LAB_1000e38a;
    }
    iVar2 = DAT_1076778c / 2 + -10;
    if (iVar2 < 0x32) {
      iVar2 = 0x32;
    }
    uVar3 = FUN_10001900(&DAT_10025d20,iVar2);
    (**(code **)(DAT_106b40a8 + 0x1c))("cl_serverStatusResendTime",uVar3);
    (**(code **)(DAT_106b40a8 + 0x104))(0,0,0);
    DAT_10766ae0 = 1;
    FUN_10001830(&DAT_107666dc,0x40,"searching %d...",DAT_10765618);
    _DAT_1004f55c = _DAT_1004f55c + 1;
    DAT_1004603c = 0;
  }
  pcVar9 = &DAT_1076561c;
  do {
    if ((*(int *)(pcVar9 + 0x88) != 0) && (iVar2 = FUN_1000db60(), iVar2 != 0)) {
      DAT_1004603c = DAT_1004603c + 1;
      local_1144 = 0;
      iVar2 = DAT_10766ae0;
      if (0 < local_440) {
        puVar8 = local_10f8;
        do {
          if (((char *)*puVar8 != (char *)0x0) && (*(char *)*puVar8 != '\0')) {
            pcVar5 = (char *)puVar8[1];
            local_1148 = puVar8;
            if (pcVar5 == (char *)0x0) {
              FUN_10001e70(0,"Q_strncpyz: NULL src");
            }
            strncpy(local_434,pcVar5,0x29);
            local_40b = 0;
            uVar3 = FUN_100017e0();
            iVar4 = FUN_1000de40(uVar3,&DAT_10765edc);
            iVar2 = DAT_10766ae0;
            if (iVar4 != 0) {
              if (DAT_10766ae0 < 0xf) {
                iVar2 = DAT_10766ae0 * 0x40;
                if (&DAT_1076629c + iVar2 == (char *)0x0) {
                  FUN_10001e70(0,"Q_strncpyz: NULL dest");
                }
                if (pcVar9 == (char *)0x0) {
                  FUN_10001e70(0,"Q_strncpyz: NULL src");
                }
                strncpy(&DAT_1076629c + iVar2,pcVar9,0x3f);
                (&DAT_107662db)[iVar2] = 0;
                iVar2 = DAT_10766ae0 * 0x40;
                if (&DAT_1076669c + iVar2 == (char *)0x0) {
                  FUN_10001e70(0,"Q_strncpyz: NULL dest");
                }
                if (pcVar9 + 0x40 == (char *)0x0) {
                  FUN_10001e70(0,"Q_strncpyz: NULL src");
                }
                strncpy(&DAT_1076669c + iVar2,pcVar9 + 0x40,0x3f);
                (&DAT_107666db)[iVar2] = 0;
                DAT_10766ae0 = DAT_10766ae0 + 1;
                iVar2 = DAT_10766ae0;
                puVar8 = local_1148;
              }
              else {
                DAT_10765618 = DAT_107644a0;
              }
            }
          }
          local_1144 = local_1144 + 1;
          puVar8 = puVar8 + 4;
          local_1148 = puVar8;
        } while (local_1144 < local_440);
      }
      FUN_10001830(&DAT_1076669c + iVar2 * 0x40,0x40,"searching %d/%d...",DAT_10765618,DAT_1004603c)
      ;
      pcVar9[0x88] = '\0';
      pcVar9[0x89] = '\0';
      pcVar9[0x8a] = '\0';
      pcVar9[0x8b] = '\0';
    }
    if (*(int *)(pcVar9 + 0x88) == 0) {
LAB_1000e1a4:
      (**(code **)(DAT_106b40a8 + 0x104))(pcVar9,0,0);
      pcVar9[0x88] = '\0';
      pcVar9[0x89] = '\0';
      pcVar9[0x8a] = '\0';
      pcVar9[0x8b] = '\0';
      if (DAT_10765618 < DAT_107644a0) {
        *(int *)(pcVar9 + 0x80) = DAT_10746428;
        (**(code **)(DAT_106b40a8 + 200))(DAT_1074148c,(&DAT_107624a0)[DAT_10765618],pcVar9,0x40);
        (**(code **)(DAT_106b40a8 + 0xcc))
                  (DAT_1074148c,(&DAT_107624a0)[DAT_10765618],auStack_408,0x400);
        pcVar5 = (char *)FUN_10001940();
        if (pcVar9 + 0x40 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL dest");
        }
        if (pcVar5 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(pcVar9 + 0x40,pcVar5,0x3f);
        iVar2 = DAT_1004603c;
        pcVar9[0x7f] = '\0';
        pcVar9[0x88] = '\x01';
        pcVar9[0x89] = '\0';
        pcVar9[0x8a] = '\0';
        pcVar9[0x8b] = '\0';
        DAT_10765618 = DAT_10765618 + 1;
        FUN_10001830(&DAT_1076669c + DAT_10766ae0 * 0x40,0x40,"searching %d/%d...",DAT_10765618,
                     iVar2);
      }
    }
    else if (*(int *)(pcVar9 + 0x80) < DAT_10746428 - DAT_1076778c) {
      if (*(int *)(pcVar9 + 0x88) != 0) {
        _DAT_1004f55c = _DAT_1004f55c + 1;
      }
      goto LAB_1000e1a4;
    }
    pcVar9 = pcVar9 + 0x8c;
  } while ((int)pcVar9 < 0x10765edc);
  iVar2 = 0;
  piVar6 = &DAT_10765730;
  do {
    if (piVar6[-0x23] != 0) {
LAB_1000e325:
      if (iVar2 < 0x10) {
        DAT_10766ae4 = DAT_10746428 + 0x19;
        goto LAB_1000e38a;
      }
      break;
    }
    if (*piVar6 != 0) {
      iVar2 = iVar2 + 1;
      goto LAB_1000e325;
    }
    if (piVar6[0x23] != 0) {
      iVar2 = iVar2 + 2;
      goto LAB_1000e325;
    }
    if (piVar6[0x46] != 0) {
      iVar2 = iVar2 + 3;
      goto LAB_1000e325;
    }
    piVar6 = piVar6 + 0x8c;
    iVar2 = iVar2 + 4;
  } while ((int)piVar6 < 0x10765ff0);
  if (DAT_10766ae0 == 0) {
    FUN_10001830(&DAT_1076669c,0x40,"no servers found");
  }
  else {
    puVar7 = &DAT_100239ab;
    if (DAT_10766ae0 != 2) {
      puVar7 = &DAT_10027c8c;
    }
    FUN_10001830(&DAT_1076669c + DAT_10766ae0 * 0x40,0x40,"%d server%s found with player %s",
                 DAT_10766ae0 + -1,puVar7,&DAT_10765edc);
  }
  DAT_10766ae4 = 0;
  FUN_1000eba0(_DAT_100294f8,DAT_10766adc,0);
LAB_1000e38a:
  __security_check_cookie(local_4 ^ (uint)&local_1148);
  return;
}



/* FUN_100097b0 @ 100097b0 size 1212 */

void FUN_100097b0(float param_1,float param_2,undefined4 param_3,undefined4 param_4,float param_5,
                 float param_6,undefined4 param_7)

{
  undefined4 in_stack_00000030;
  undefined4 in_stack_00000034;
  undefined4 in_stack_00000038;
  undefined4 in_stack_0000003c;
  undefined4 in_stack_00000040;
  undefined4 in_stack_00000044;
  float local_18;
  float local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  local_18 = param_1 + param_5;
  local_10 = param_3;
  local_14 = param_2 + param_6;
  local_c = param_4;
  switch(param_7) {
  case 0x201:
    FUN_10005100(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x202:
    FUN_10005690(&local_18);
    return;
  case 0x203:
    FUN_10005220(in_stack_00000034,in_stack_00000038);
    return;
  case 0x204:
    FUN_100053c0();
    return;
  case 0x205:
    FUN_10005350(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x206:
    FUN_10006550(in_stack_00000034,in_stack_00000038);
    return;
  case 0x207:
    FUN_100065b0();
    return;
  case 0x208:
    FUN_100066d0(in_stack_00000034,in_stack_00000038);
    return;
  case 0x20a:
    FUN_10006730();
    return;
  case 0x210:
    FUN_10006890(in_stack_00000034,in_stack_00000038,1);
    return;
  case 0x211:
    FUN_100068f0(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x213:
    FUN_10006b30(in_stack_00000030,in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x214:
    FUN_10006bc0(in_stack_00000030,in_stack_00000034,in_stack_00000038);
    return;
  case 0x215:
    FUN_10006c10(in_stack_00000030,in_stack_00000034,in_stack_00000038);
    return;
  case 0x216:
    FUN_10006c60(in_stack_00000034);
    return;
  case 0x217:
    FUN_10008e90(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x218:
    FUN_10005560();
    return;
  case 0x219:
    FUN_10005260(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x21a:
    FUN_10006600();
    return;
  case 0x21b:
    FUN_10008f20(in_stack_00000034);
    return;
  case 0x21c:
    FUN_10009080(in_stack_00000034,in_stack_00000038);
    return;
  case 0x21d:
    FUN_100093b0(in_stack_00000034,in_stack_00000040);
    return;
  case 0x21e:
    FUN_100092f0(in_stack_00000034);
    return;
  case 0x220:
    FUN_100054a0(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x221:
    FUN_100052e0(in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x223:
    FUN_10005560();
    return;
  case 0x224:
    if ((-1 < DAT_10744ccc) && (DAT_10744ccc < DAT_1075add0)) {
      FUN_10003ec0(local_18,local_14,0,in_stack_00000034,in_stack_00000038,
                   (&DAT_1075add4)[DAT_10744ccc * 0x19],0,0,in_stack_00000040);
      return;
    }
    break;
  case 0x225:
    FUN_10009340(in_stack_0000003c,in_stack_00000044);
    return;
  case 0x226:
    FUN_10009660(in_stack_00000038);
    return;
  case 0x227:
    FUN_10006ea0(in_stack_00000034,in_stack_00000040);
    return;
  case 0x228:
    FUN_10006f30(&local_18,in_stack_00000034,in_stack_00000038,in_stack_00000040);
    return;
  case 0x229:
    FUN_10005850(&local_18);
    return;
  case 0x22a:
    FUN_10005c20(&local_18);
    return;
  case 0x22b:
    FUN_10005ff0(&local_18);
    return;
  case 0x22c:
    FUN_100062a0(&local_18);
    return;
  case 0x22d:
    FUN_10007030(&local_18,in_stack_00000030,in_stack_00000034,in_stack_00000040);
    return;
  case 0x22e:
    FUN_10008730(in_stack_00000034,in_stack_00000038,in_stack_00000040);
  }
  return;
}



/* FUN_10003190 @ 10003190 size 1189 */

void FUN_10003190(void)

{
  char cVar1;
  int iVar2;
  char *pcVar3;
  char *pcVar4;
  undefined4 uVar5;
  char *pcVar6;
  uint uVar7;
  char *pcVar8;
  char *pcVar9;
  int iStack_59c;
  undefined1 local_598 [275];
  char cStack_485;
  char acStack_484 [4];
  char acStack_480 [4];
  char cStack_47c;
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&iStack_59c;
  if (DAT_1075adcc != 1) {
    DAT_1075add0 = 0;
    DAT_10044338 = 0;
    (*(code *)DAT_106b40a8[4])(local_598,"g_arenasFile",&DAT_100239ab,0x50);
    FUN_10003070();
    iVar2 = (*(code *)DAT_106b40a8[0x13])("scripts",".arena",acStack_404,0x400);
    pcVar3 = acStack_404;
    pcVar6 = pcVar3;
    if (0 < iVar2) {
      do {
        do {
          iStack_59c = iVar2;
          cVar1 = *pcVar3;
          pcVar3 = pcVar3 + 1;
          iVar2 = iStack_59c;
        } while (cVar1 != '\0');
        acStack_484[0] = s_scripts__10025da0[0];
        acStack_484[1] = s_scripts__10025da0[1];
        acStack_484[2] = s_scripts__10025da0[2];
        acStack_484[3] = s_scripts__10025da0[3];
        acStack_480[0] = s_scripts__10025da0[4];
        acStack_480[1] = s_scripts__10025da0[5];
        acStack_480[2] = s_scripts__10025da0[6];
        acStack_480[3] = s_scripts__10025da0[7];
        cStack_47c = s_scripts__10025da0[8];
        pcVar4 = pcVar6;
        do {
          cVar1 = *pcVar4;
          pcVar4 = pcVar4 + 1;
        } while (cVar1 != '\0');
        pcVar9 = &cStack_485;
        do {
          pcVar8 = pcVar9 + 1;
          pcVar9 = pcVar9 + 1;
        } while (*pcVar8 != '\0');
        pcVar8 = pcVar6;
        for (uVar7 = (uint)((int)pcVar4 - (int)pcVar6) >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
          *(undefined4 *)pcVar9 = *(undefined4 *)pcVar8;
          pcVar8 = pcVar8 + 4;
          pcVar9 = pcVar9 + 4;
        }
        for (uVar7 = (int)pcVar4 - (int)pcVar6 & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
          *pcVar9 = *pcVar8;
          pcVar8 = pcVar8 + 1;
          pcVar9 = pcVar9 + 1;
        }
        FUN_10003070();
        iStack_59c = iStack_59c + -1;
        iVar2 = iStack_59c;
        pcVar6 = pcVar3;
      } while (iStack_59c != 0);
    }
    if (DAT_106b3058 != 0) {
      (*(code *)*DAT_106b40a8)("^3WARNING: not enough memory in pool to load all arenas\n");
    }
    iVar2 = 0;
    if (0 < DAT_10044338) {
      do {
        (&DAT_1075adec)[DAT_1075add0 * 0x19] = 0xffffffff;
        FUN_10001940();
        uVar5 = FUN_10014560();
        (&DAT_1075add8)[DAT_1075add0 * 0x19] = uVar5;
        FUN_10001940();
        uVar5 = FUN_10014560();
        (&DAT_1075add4)[DAT_1075add0 * 0x19] = uVar5;
        (&DAT_1075ae30)[DAT_1075add0 * 0x19] = 0xffffffff;
        FUN_10001900("levelshots/preview/%s",(&DAT_1075add8)[DAT_1075add0 * 0x19]);
        uVar5 = FUN_10014560();
        (&DAT_1075addc)[DAT_1075add0 * 0x19] = uVar5;
        (&DAT_1075ade8)[DAT_1075add0 * 0x19] = 0;
        pcVar3 = (char *)FUN_10001940();
        if (*pcVar3 == '\0') {
          (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 1;
        }
        else {
          pcVar6 = strstr(pcVar3,"ffa");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 1;
          }
          pcVar6 = strstr(pcVar3,"tourney");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 2;
          }
          pcVar6 = strstr(pcVar3,"duel");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 2;
          }
          pcVar6 = strstr(pcVar3,"race");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 4;
          }
          pcVar6 = strstr(pcVar3,"tdm");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 8;
          }
          pcVar6 = strstr(pcVar3,"ca");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x10;
          }
          pcVar6 = strstr(pcVar3,"ctf");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x20;
          }
          pcVar6 = strstr(pcVar3,"oneflag");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x40;
          }
          pcVar6 = strstr(pcVar3,"overload");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x80;
          }
          pcVar6 = strstr(pcVar3,"hh");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x100;
          }
          pcVar6 = strstr(pcVar3,"har");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x100;
          }
          pcVar6 = strstr(pcVar3,"ft");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x200;
          }
          pcVar6 = strstr(pcVar3,"dom");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x400;
          }
          pcVar6 = strstr(pcVar3,"ad");
          if (pcVar6 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x800;
          }
          pcVar3 = strstr(pcVar3,"rr");
          if (pcVar3 != (char *)0x0) {
            (&DAT_1075ade8)[DAT_1075add0 * 0x19] = (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 0x1000;
          }
        }
        DAT_1075add0 = DAT_1075add0 + 1;
      } while ((DAT_1075add0 < 0x100) && (iVar2 = iVar2 + 1, iVar2 < DAT_10044338));
    }
    DAT_1075adcc = 1;
  }
  __security_check_cookie(local_4 ^ (uint)&iStack_59c);
  return;
}



/* FUN_1000fab0 @ 1000fab0 size 1156 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1000fab0(void)

{
  undefined *puVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  float10 fVar6;
  
  FUN_10011730();
  DAT_10050054 = 0;
  DAT_106b3058 = 0;
  FUN_1000f9f0();
  (**(code **)(DAT_106b40a8 + 0x148))();
  iVar4 = DAT_106b40a8;
  _DAT_10746340 = *(undefined4 *)(DAT_106b40a8 + 0x5c);
  _DAT_10746344 = &LAB_10002e10;
  _DAT_10746348 = FUN_10002c50;
  _DAT_1074634c = *(undefined4 *)(DAT_106b40a8 + 0x78);
  _DAT_10746350 = FUN_10003ec0;
  _DAT_10746354 = &LAB_10003e60;
  _DAT_10746358 = &LAB_10003e90;
  _DAT_1074635c = *(undefined4 *)(DAT_106b40a8 + 0x54);
  _DAT_10746360 = *(undefined4 *)(DAT_106b40a8 + 0x7c);
  _DAT_10746364 = FUN_10002d60;
  _DAT_10746368 = &LAB_10003d10;
  _DAT_10746370 = FUN_10003c20;
  _DAT_10746374 = *(undefined4 *)(DAT_106b40a8 + 0x60);
  _DAT_1074636c = FUN_10003b30;
  _DAT_10746378 = *(undefined4 *)(DAT_106b40a8 + 100);
  _DAT_1074637c = *(undefined4 *)(DAT_106b40a8 + 0x70);
  _DAT_10746380 = *(undefined4 *)(DAT_106b40a8 + 0x118);
  _DAT_10746384 = FUN_100097b0;
  _DAT_10746388 = &LAB_1000a980;
  _DAT_1074638c = FUN_10009d30;
  _DAT_10746390 = FUN_1000b0e0;
  _DAT_10746394 = &DAT_1000d2f0;
  _DAT_107463a0 = *(undefined4 *)(DAT_106b40a8 + 0x1c);
  _DAT_10746398 = *(undefined4 *)(DAT_106b40a8 + 0x24);
  _DAT_1074639c = *(undefined4 *)(DAT_106b40a8 + 0x28);
  _DAT_107463a4 = *(undefined4 *)(DAT_106b40a8 + 0x10);
  _DAT_107463a8 = FUN_10004070;
  _DAT_107463ac = *(undefined4 *)(DAT_106b40a8 + 0xa4);
  _DAT_107463b0 = *(undefined4 *)(DAT_106b40a8 + 0xa0);
  _DAT_107463b4 = *(undefined4 *)(DAT_106b40a8 + 0x88);
  _DAT_107463b8 = FUN_1000a820;
  _DAT_107463bc = &LAB_1000e470;
  _DAT_107463c4 = &LAB_1000ea80;
  _DAT_107463c0 = &LAB_1000e640;
  _DAT_107463c8 = FUN_1000eba0;
  _DAT_107463d4 = *(undefined4 *)(DAT_106b40a8 + 0x98);
  DAT_107463d0 = *(int *)(DAT_106b40a8 + 0x94);
  _DAT_107463cc = *(undefined4 *)(DAT_106b40a8 + 0x90);
  _DAT_107463d8 = *(undefined4 *)(DAT_106b40a8 + 0x50);
  _DAT_107463dc = FUN_10001e70;
  _DAT_107463e0 = FUN_10001ee0;
  _DAT_107463e4 = &LAB_1000f7b0;
  _DAT_107463e8 = &LAB_10006950;
  _DAT_107463ec = *(undefined4 *)(DAT_106b40a8 + 0x8c);
  _DAT_107463f0 = *(undefined4 *)(DAT_106b40a8 + 0x120);
  _DAT_107463f4 = *(undefined4 *)(DAT_106b40a8 + 0x11c);
  _DAT_107463f8 = &LAB_1000f830;
  _DAT_107463fc = &LAB_1000f870;
  _DAT_10746400 = &LAB_1000f900;
  _DAT_10746404 = &LAB_1000f950;
  _DAT_10746408 = *(undefined4 *)(DAT_106b40a8 + 0x140);
  _DAT_1074640c = *(undefined4 *)(DAT_106b40a8 + 0x144);
  _DAT_10746410 = *(undefined4 *)(DAT_106b40a8 + 0x150);
  _DAT_10746414 = FUN_10002bf0;
  DAT_106b40d0 = &DAT_10746340;
  puVar5 = &DAT_10051058;
  for (iVar3 = 0x800; iVar3 != 0; iVar3 = iVar3 + -1) {
    *puVar5 = 0;
    puVar5 = puVar5 + 1;
  }
  _DAT_106b40f8 = 0;
  DAT_106b40f4 = 0;
  DAT_106b40e4 = 0;
  DAT_106b40e8 = 0;
  DAT_10050054 = 0;
  DAT_106b3058 = 0;
  FUN_1001f730();
  FUN_10020100();
  if (DAT_107463d0 != 0) {
    FUN_1001b0c0();
    iVar4 = DAT_106b40a8;
  }
  _DAT_1075827c = (**(code **)(iVar4 + 0x5c))("menu/art/3_cursor2");
  DAT_10758274 = (**(code **)(DAT_106b40a8 + 0x5c))("white");
  FUN_10003990();
  (**(code **)(DAT_106b40a8 + 8))();
  DAT_1075829c = 0;
  memset(&DAT_107582a4,0,0x1400);
  DAT_1075adcc = 0;
  FUN_1000f2b0();
  (**(code **)(DAT_106b40a8 + 0x24))("ui_menuFiles",&DAT_10042f38,0x400);
  FUN_10004e10(1);
  FUN_10004e10(0);
  FUN_10016220();
  (**(code **)(DAT_106b40a8 + 0xe4))();
  FUN_10002350();
  FUN_10003770();
  fVar6 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("m_pitch");
  puVar1 = &DAT_100252c0;
  if (fVar6 < (float10)0) {
    puVar1 = &DAT_1002729c;
  }
  (**(code **)(DAT_106b40a8 + 0x1c))("ui_mousePitch",puVar1);
  DAT_107644b4 = 0xffffffff;
  DAT_10761bf0 = 0xffffffff;
  (**(code **)(DAT_106b40a8 + 0x10))(0,"debug_protocol",&DAT_100239ab,0);
  iVar4 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025d20,DAT_1074502c);
  (**(code **)(iVar4 + 0x1c))("ui_actualNetGameType",uVar2);
  (**(code **)(DAT_106b40a8 + 0x10))
            (&DAT_10742c20,"ui_version","1069 win-x86 Jun  3 2016 16:09:57",0x40);
  iVar3 = (**(code **)(DAT_106b40a8 + 0x174))(0x53dcc);
  iVar4 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,(iVar3 != 0) + '\x01');
  (**(code **)(iVar4 + 0x1c))("ui_gibs",uVar2);
  (**(code **)(DAT_106b40a8 + 0x1c))("ui_cvGameType",&DAT_10027e68);
  return;
}



/* FUN_1001ca50 @ 1001ca50 size 1144 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001ca50(void)

{
  int iVar1;
  int iVar2;
  float *pfVar3;
  undefined4 *unaff_EBX;
  float10 fVar4;
  undefined1 auStack_30 [4];
  code *local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  float local_18;
  float local_14;
  float fStack_10;
  float fStack_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_30;
  if ((unaff_EBX == (undefined4 *)0x0) || (*(int *)(DAT_106b40d0 + 0x44) == 0)) goto LAB_1001ceb6;
  iVar1 = unaff_EBX[0x4d];
  FUN_10014ea0(*(undefined4 *)(iVar1 + 0x11c),*(undefined4 *)(iVar1 + 0x120));
  local_28 = unaff_EBX[0x1e];
  local_24 = unaff_EBX[0x1f];
  local_20 = unaff_EBX[0x20];
  local_1c = unaff_EBX[0x21];
  if ((0 < (int)unaff_EBX[99]) &&
     (local_2c = *(code **)(DAT_106b40d0 + 0x48), local_2c != (code *)0x0)) {
    fVar4 = (float10)(*local_2c)(unaff_EBX[0xe]);
    local_2c = (code *)(float)fVar4;
    iVar2 = 0;
    if (0 < (int)unaff_EBX[99]) {
      pfVar3 = (float *)(unaff_EBX + 0x69);
      do {
        if ((pfVar3[-1] <= (float)local_2c) && ((float)local_2c <= *pfVar3)) {
          local_28 = unaff_EBX[iVar2 * 6 + 100];
          local_24 = unaff_EBX[iVar2 * 6 + 0x65];
          local_20 = unaff_EBX[iVar2 * 6 + 0x66];
          local_1c = unaff_EBX[iVar2 * 6 + 0x67];
          break;
        }
        iVar2 = iVar2 + 1;
        pfVar3 = pfVar3 + 6;
      } while (iVar2 < (int)unaff_EBX[99]);
    }
  }
  if ((*(byte *)(unaff_EBX + 0x12) & 2) == 0) {
    if ((unaff_EBX[0x4b] == 1) && ((*(int *)(DAT_106b40d0 + 0xe8) / 200 & 1U) == 0)) {
      fStack_c = (float)_DAT_10029448;
      local_18 = (float)unaff_EBX[0x1e] * fStack_c;
      local_14 = (float)unaff_EBX[0x1f] * fStack_c;
      local_2c = (code *)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
      fStack_10 = (float)unaff_EBX[0x20] * fStack_c;
      fStack_c = fStack_c * (float)unaff_EBX[0x21];
      fVar4 = (float10)_CIsin();
      fVar4 = (float10)_DAT_10029278 + fVar4 * (float10)_DAT_10029278;
      goto LAB_1001cc6a;
    }
  }
  else {
    fStack_c = (float)_DAT_10029448;
    local_18 = *(float *)(iVar1 + 0x134) * fStack_c;
    local_14 = *(float *)(iVar1 + 0x138) * fStack_c;
    local_2c = (code *)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fStack_10 = *(float *)(iVar1 + 0x13c) * fStack_c;
    fStack_c = fStack_c * *(float *)(iVar1 + 0x140);
    fVar4 = (float10)_CIsin();
    fVar4 = (float10)_DAT_10029278 + fVar4 * (float10)_DAT_10029278;
LAB_1001cc6a:
    local_2c = (code *)(float)fVar4;
    FUN_100147a0(local_2c);
  }
  if (((*(byte *)(unaff_EBX + 0x5f) & 3) != 0) && (iVar2 = FUN_10016e70(1), iVar2 == 0)) {
    local_28 = *(undefined4 *)(iVar1 + 0x144);
    local_24 = *(undefined4 *)(iVar1 + 0x148);
    local_20 = *(undefined4 *)(iVar1 + 0x14c);
    local_1c = *(undefined4 *)(iVar1 + 0x150);
  }
  if (unaff_EBX[0x4c] != 0) {
    FUN_1001a7e0();
    if (*(char *)unaff_EBX[0x4c] == '\0') {
      local_2c = (code *)((float)unaff_EBX[0x42] + (float)unaff_EBX[0x40]);
      (**(code **)(DAT_106b40d0 + 0x44))
                (local_2c,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],0,unaff_EBX[0x48],unaff_EBX[0xe],
                 unaff_EBX[0xf],unaff_EBX[0x10],unaff_EBX[0x45],unaff_EBX[0xa0],unaff_EBX[0x49],
                 unaff_EBX[0x4a],&local_28,unaff_EBX[0x3a],unaff_EBX[0x4b],unaff_EBX[0xa3]);
      __security_check_cookie(local_8 ^ (uint)auStack_30);
      return;
    }
    local_2c = (code *)((float)unaff_EBX[0x42] + (float)unaff_EBX[0x40] + (float)_DAT_10029220);
    (**(code **)(DAT_106b40d0 + 0x44))
              (local_2c,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],0,unaff_EBX[0x48],unaff_EBX[0xe],
               unaff_EBX[0xf],unaff_EBX[0x10],unaff_EBX[0x45],unaff_EBX[0xa0],unaff_EBX[0x49],
               unaff_EBX[0x4a],&local_28,unaff_EBX[0x3a],unaff_EBX[0x4b],unaff_EBX[0xa3]);
    __security_check_cookie(local_8 ^ (uint)auStack_30);
    return;
  }
  (**(code **)(DAT_106b40d0 + 0x44))
            (*unaff_EBX,unaff_EBX[1],unaff_EBX[2],unaff_EBX[3],unaff_EBX[0x47],unaff_EBX[0x48],
             unaff_EBX[0xe],unaff_EBX[0xf],unaff_EBX[0x10],unaff_EBX[0x45],unaff_EBX[0xa0],
             unaff_EBX[0x49],unaff_EBX[0x4a],&local_28,unaff_EBX[0x3a],unaff_EBX[0x4b],
             unaff_EBX[0xa3]);
LAB_1001ceb6:
  __security_check_cookie(local_8 ^ (uint)auStack_30);
  return;
}



/* FUN_1001ced0 @ 1001ced0 size 1140 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_1001ced0(int param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  code *pcVar5;
  float fVar6;
  int iVar7;
  undefined4 *puVar8;
  int extraout_EDX;
  float10 fVar9;
  undefined1 auStack_3c [4];
  float local_38;
  float local_34;
  float local_30;
  float local_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  uint local_8;
  
  iVar7 = DAT_106b40d0;
  local_8 = DAT_1002a000 ^ (uint)auStack_3c;
  iVar3 = *(int *)(param_1 + 0x134);
  if (((*(uint *)(param_1 + 0x48) & 0x10000) != 0) &&
     (*(int *)(param_1 + 0x74) < *(int *)(DAT_106b40d0 + 0xe8))) {
    local_28 = (float)_DAT_10029278;
    local_2c = *(float *)(param_1 + 0x18) * local_28;
    *(int *)(param_1 + 0x74) = *(int *)(param_1 + 0x70) + *(int *)(DAT_106b40d0 + 0xe8);
    local_28 = local_28 * *(float *)(param_1 + 0x1c);
    local_30 = *(float *)(param_1 + 0x50);
    local_20 = (local_2c + *(float *)(param_1 + 0x10)) - local_30;
    local_34 = *(float *)(param_1 + 0x54);
    local_38 = (local_28 + *(float *)(param_1 + 0x14)) - local_34;
    fVar9 = (float10)_CIcos();
    local_24 = (float)fVar9;
    fVar9 = (float10)_CIsin();
    local_1c = (float)fVar9;
    *(float *)(param_1 + 0x10) = ((local_20 * local_24 - local_38 * local_1c) + local_30) - local_2c
    ;
    *(float *)(param_1 + 0x14) = (local_24 * local_38 + local_20 * local_1c + local_34) - local_28;
    FUN_10015470();
  }
  if (((*(uint *)(param_1 + 0x48) & 0x100) != 0) &&
     (iVar4 = *(int *)(iVar7 + 0xe8), *(int *)(param_1 + 0x74) < iVar4)) {
    fVar1 = *(float *)(param_1 + 0x10);
    local_30 = *(float *)(param_1 + 0x50);
    *(int *)(param_1 + 0x74) = *(int *)(param_1 + 0x70) + iVar4;
    if (fVar1 != local_30) {
      if (local_30 <= fVar1) {
        fVar1 = fVar1 - *(float *)(param_1 + 0x60);
        *(float *)(param_1 + 0x10) = fVar1;
        fVar2 = local_30;
      }
      else {
        fVar2 = *(float *)(param_1 + 0x60) + fVar1;
        *(float *)(param_1 + 0x10) = fVar2;
        fVar1 = local_30;
      }
      if (fVar1 < fVar2) {
        *(float *)(param_1 + 0x10) = local_30;
      }
    }
    fVar1 = *(float *)(param_1 + 0x14);
    fVar2 = *(float *)(param_1 + 0x54);
    if (fVar1 != fVar2) {
      if (fVar2 <= fVar1) {
        fVar1 = fVar1 - *(float *)(param_1 + 100);
        *(float *)(param_1 + 0x14) = fVar1;
        fVar6 = fVar2;
      }
      else {
        fVar6 = *(float *)(param_1 + 100) + fVar1;
        *(float *)(param_1 + 0x14) = fVar6;
        fVar1 = fVar2;
      }
      if (fVar1 < fVar6) {
        *(float *)(param_1 + 0x14) = fVar2;
      }
    }
    fVar1 = *(float *)(param_1 + 0x18);
    fVar2 = *(float *)(param_1 + 0x58);
    if (fVar1 != fVar2) {
      if (fVar2 <= fVar1) {
        fVar1 = fVar1 - *(float *)(param_1 + 0x68);
        *(float *)(param_1 + 0x18) = fVar1;
        fVar6 = fVar2;
      }
      else {
        fVar6 = *(float *)(param_1 + 0x68) + fVar1;
        *(float *)(param_1 + 0x18) = fVar6;
        fVar1 = fVar2;
      }
      if (fVar1 < fVar6) {
        *(float *)(param_1 + 0x18) = fVar2;
      }
    }
    local_38 = *(float *)(param_1 + 0x1c);
    local_34 = *(float *)(param_1 + 0x5c);
    if (local_38 != local_34) {
      if (local_34 <= local_38) {
        fVar1 = local_38 - *(float *)(param_1 + 0x6c);
        *(float *)(param_1 + 0x1c) = fVar1;
        fVar2 = local_34;
        local_38 = fVar1;
      }
      else {
        fVar2 = *(float *)(param_1 + 0x6c) + local_38;
        *(float *)(param_1 + 0x1c) = fVar2;
        fVar1 = local_34;
        local_38 = fVar2;
      }
      if (fVar1 < fVar2) {
        *(float *)(param_1 + 0x1c) = local_34;
      }
    }
    FUN_10015470();
    if (extraout_EDX == 4) {
      *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xfffffeff;
    }
  }
  if (((*(int *)(param_1 + 0x3c) != 0) || (*(int *)(param_1 + 0x40) != 0)) &&
     (pcVar5 = *(code **)(iVar7 + 0x4c), pcVar5 != (code *)0x0)) {
    iVar7 = (*pcVar5)(*(int *)(param_1 + 0x3c),*(undefined4 *)(param_1 + 0x40));
    if (iVar7 == 0) {
      *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xfffffffb;
    }
    else {
      *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 4;
    }
  }
  if ((((*(byte *)(param_1 + 0x17c) & 0xc) == 0) || (iVar7 = FUN_10016e70(4), iVar7 != 0)) &&
     ((*(byte *)(param_1 + 0x48) & 4) != 0)) {
    if ((*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) && (*(int *)(param_1 + 0x298) != 0)) {
      (**(code **)(DAT_106b40d0 + 0xd8))(*(undefined4 *)(param_1 + 0x294));
    }
    FUN_10014f00(*(undefined4 *)(iVar3 + 0x120),*(undefined4 *)(iVar3 + 0x11c),
                 (float)*(int *)(iVar3 + 0x118));
    if (DAT_106b40ec != 0) {
      puVar8 = (undefined4 *)FUN_10019970();
      uStack_c = DAT_10029234;
      uStack_14 = DAT_10029234;
      uStack_10 = 0;
      uStack_18 = 0;
      (**(code **)(DAT_106b40d0 + 0x28))
                (*puVar8,puVar8[1],puVar8[2],puVar8[3],0x3f800000,&uStack_18);
    }
    switch(*(undefined4 *)(param_1 + 0x110)) {
    case 0:
    case 1:
      if (*(int *)(param_1 + 0x38) == 0) {
        FUN_1001a7e0();
      }
      else {
        FUN_1001ca50();
      }
      break;
    case 4:
    case 9:
      FUN_1001a8e0();
      break;
    case 6:
      FUN_1001bfb0();
      break;
    case 7:
      FUN_1001bc30(param_1);
      break;
    case 8:
      FUN_1001ca50();
      break;
    case 10:
      FUN_1001b3d0();
      break;
    case 0xb:
      FUN_1001ab30();
      break;
    case 0xc:
      FUN_1001ad40();
      break;
    case 0xd:
      FUN_1001b7c0();
      break;
    case 0xe:
      FUN_1001b5c0();
      break;
    case 0x10:
      FUN_1001af00();
    }
    if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
      (**(code **)(DAT_106b40d0 + 0xd8))(*(undefined4 *)(iVar3 + 0x108));
    }
  }
  __security_check_cookie(local_8 ^ (uint)auStack_3c);
  return;
}



/* FUN_10019a10 @ 10019a10 size 1072 */

void FUN_10019a10(int param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  code *pcVar4;
  int iVar5;
  float fVar6;
  float fVar7;
  undefined8 uVar8;
  char *pcVar9;
  int local_2b4;
  undefined1 local_2b0 [308];
  int local_17c;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)&local_2b4;
  iVar5 = 0;
  local_2b4 = param_1;
  if ((DAT_106b40d4 != 0) && (param_3 != 0)) {
    FUN_1001b9e0(param_3,param_4);
    __security_check_cookie(local_c ^ (uint)&local_2b4);
    return;
  }
  if ((DAT_106b40d8 != 0) && (param_3 != 0)) {
    iVar1 = FUN_10018870(param_2,param_4);
    if (iVar1 == 0) {
      DAT_106b40d8 = iVar1;
      DAT_106b40e0 = iVar1;
      __security_check_cookie(local_c ^ (uint)&local_2b4);
      return;
    }
    if (((param_2 == 0xb2) || (param_2 == 0xb3)) || (param_2 == 0xb4)) {
      DAT_106b40d8 = 0;
      DAT_106b40e0 = 0;
      FUN_10020740();
      param_1 = local_2b4;
    }
    else {
      if ((param_2 == 9) || (param_2 == 0x84)) goto switchD_10019c4c_caseD_a;
      if (param_2 == 0x85) {
        __security_check_cookie(local_c ^ (uint)&local_2b4);
        return;
      }
    }
  }
  if (param_1 == 0) goto switchD_10019c4c_caseD_a;
  iVar1 = DAT_106b40d0;
  if ((param_3 != 0) && ((*(uint *)(param_1 + 0x48) & 0x200000) == 0)) {
    uVar8 = FUN_10015c00((float)*(int *)(DAT_106b40d0 + 0xf0),(float)*(int *)(DAT_106b40d0 + 0xf4));
    iVar1 = (int)((ulonglong)uVar8 >> 0x20);
    if ((((int)uVar8 == 0) && (DAT_106b40fc == 0)) &&
       (((param_2 == 0xb2 || (param_2 == 0xb3)) || (param_2 == 0xb4)))) {
      DAT_106b40fc = 1;
      FUN_10019790(param_2,param_3,param_4);
      DAT_106b40fc = 0;
      __security_check_cookie(local_c ^ (uint)&local_2b4);
      return;
    }
  }
  iVar3 = *(int *)(param_1 + 0x10c);
  local_17c = param_1;
  if (0 < iVar3) {
    piVar2 = (int *)(param_1 + 0x154);
    do {
      if ((*(byte *)(*piVar2 + 0x48) & 2) != 0) {
        iVar5 = *piVar2;
      }
      piVar2 = piVar2 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    iVar1 = DAT_106b40d0;
    local_17c = local_2b4;
    if ((iVar5 != 0) &&
       (iVar3 = FUN_10019350(param_3,param_4), iVar1 = DAT_106b40d0, local_17c = local_2b4,
       iVar3 != 0)) goto LAB_10019d2e;
  }
  if (param_3 == 0) goto switchD_10019c4c_caseD_a;
  switch(param_2) {
  case 9:
  case 0x85:
  case 0xa7:
    FUN_100195b0();
    __security_check_cookie(local_c ^ (uint)&local_2b4);
    return;
  case 0xd:
  case 0xa9:
    if (iVar5 == 0) break;
    if ((*(int *)(iVar5 + 0x110) != 4) && (*(int *)(iVar5 + 0x110) != 9)) {
LAB_10019d2e:
      FUN_10016d70(iVar5);
      __security_check_cookie(local_c ^ (uint)&local_2b4);
      return;
    }
    *(undefined4 *)(iVar5 + 0x284) = 0;
    pcVar4 = *(code **)(iVar1 + 0x6c);
    DAT_106b40d8 = 1;
    pcVar9 = (char *)0x0;
    DAT_106b40e0 = iVar5;
    goto LAB_10019e26;
  case 0x1b:
    if ((DAT_106b40d4 == 0) && (*(int *)(local_17c + 300) != 0)) {
      FUN_10016d70(local_2b0);
      __security_check_cookie(local_c ^ (uint)&local_2b4);
      return;
    }
    break;
  case 0x84:
  case 0xa1:
    FUN_100194b0();
    __security_check_cookie(local_c ^ (uint)&local_2b4);
    return;
  case 0x9c:
    pcVar4 = *(code **)(iVar1 + 0x98);
    pcVar9 = "screenshotJPEG\n";
LAB_10019e26:
    (*pcVar4)(pcVar9);
    break;
  case 0xb2:
  case 0xb3:
    if (iVar5 != 0) {
      iVar3 = *(int *)(iVar5 + 0x110);
      if (iVar3 == 0) {
        fVar6 = (float)*(int *)(iVar1 + 0xf4);
        fVar7 = (float)*(int *)(iVar1 + 0xf0);
        FUN_10019970(fVar7,fVar6);
      }
      else {
        if ((iVar3 == 4) || (iVar3 == 9)) {
          uVar8 = FUN_10015c00((float)*(int *)(iVar1 + 0xf0),(float)*(int *)(iVar1 + 0xf4));
          if ((int)uVar8 != 0) {
            *(undefined4 *)(iVar5 + 0x284) = 0;
            DAT_106b40d8 = 1;
            DAT_106b40e0 = iVar5;
            (**(code **)((int)((ulonglong)uVar8 >> 0x20) + 0x6c))(0);
            __security_check_cookie(local_c ^ (uint)&local_2b4);
            return;
          }
          break;
        }
        fVar6 = (float)*(int *)(iVar1 + 0xf4);
        fVar7 = (float)*(int *)(iVar1 + 0xf0);
      }
      iVar1 = FUN_10015c00(fVar7,fVar6);
      if (iVar1 != 0) goto LAB_10019d2e;
    }
  }
switchD_10019c4c_caseD_a:
  __security_check_cookie(local_c ^ (uint)&local_2b4);
  return;
}



/* FUN_10008730 @ 10008730 size 1063 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10008730(float param_1,float param_2,undefined4 param_3)

{
  int iVar1;
  float fVar2;
  uint uVar3;
  float *unaff_ESI;
  int iVar4;
  float10 fVar5;
  float fStack_4e8;
  float local_4e4;
  float local_4e0;
  uint uStack_4dc;
  int aiStack_4d8 [16];
  undefined1 auStack_498 [16];
  float fStack_488;
  undefined1 auStack_484 [128];
  char local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&fStack_4e8;
  local_4e4 = param_2;
  local_4e0 = 0.0;
  (**(code **)(DAT_106b40a8 + 0xc0))(0x2c9,local_404,0x400);
  uStack_4dc = atoi(local_404);
  aiStack_4d8[1] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_gauntlet.tga");
  aiStack_4d8[2] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_machinegun.tga");
  aiStack_4d8[3] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_shotgun.tga");
  aiStack_4d8[4] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_grenade.tga");
  aiStack_4d8[5] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_rocket.tga");
  aiStack_4d8[6] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_lightning.tga");
  aiStack_4d8[7] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_railgun.tga");
  aiStack_4d8[8] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_plasma.tga");
  aiStack_4d8[9] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_bfg.tga");
  aiStack_4d8[10] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_grapple.tga");
  aiStack_4d8[0xb] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_nailgun.tga");
  aiStack_4d8[0xc] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_proxlauncher.tga");
  aiStack_4d8[0xd] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/iconw_chaingun.tga");
  aiStack_4d8[0xe] = (**(code **)(DAT_106b40a8 + 0x5c))("icons/weap_hmg.tga");
  iVar4 = 1;
  uVar3 = 2;
  do {
    if (((uStack_4dc & (uVar3 >> 1 | (uint)((uVar3 & 1) != 0) << 0x1f)) != 0) &&
       (iVar1 = aiStack_4d8[iVar4], iVar1 != 0)) {
      (**(code **)(DAT_106b40a8 + 0x74))(&DAT_1002be24);
      fStack_4e8 = *unaff_ESI + local_4e0;
      FUN_10002c50(fStack_4e8,unaff_ESI[1],unaff_ESI[2],unaff_ESI[3],iVar1);
      local_4e0 = unaff_ESI[2] * (float)_DAT_10029468 + local_4e0;
      (**(code **)(DAT_106b40a8 + 0x74))(0);
    }
    iVar4 = iVar4 + 1;
    uVar3 = uVar3 << 1 | (uint)((int)uVar3 < 0);
  } while (iVar4 < 0xf);
  fVar5 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_loadout");
  if (fVar5 == (float10)1) {
    if (DAT_106b40a4 == _DAT_10029214) {
      DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
    }
    fStack_4e8 = DAT_106b40a4 * param_1;
    (**(code **)(DAT_106b40a8 + 0x17c))(&DAT_10027088,0,0,fStack_4e8,0xffffffff,auStack_498);
    if (DAT_106b40a4 == _DAT_10029214) {
      DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
    }
    fStack_4e8 = DAT_106b40a4 * param_1;
    (**(code **)(DAT_106b40a8 + 0x17c))(&DAT_10027088,0,0,fStack_4e8,0xffffffff,auStack_498);
    fVar2 = local_4e4;
    fStack_4e8 = (float)(int)(fStack_488 / _DAT_1074641c);
    local_4e4 = *unaff_ESI + local_4e0;
    FUN_10003ec0(local_4e4,
                 (float)_DAT_10029278 * (float)(int)fStack_4e8 +
                 unaff_ESI[1] + unaff_ESI[3] * (float)_DAT_10029278,0,param_1,fVar2,&DAT_10027088,0,
                 0,param_3);
    local_4e0 = unaff_ESI[2] + local_4e0;
    (**(code **)(DAT_106b40a8 + 0x24))("cg_weaponPrimaryQueued",auStack_484,0x80);
    iVar4 = FUN_10001090(auStack_484);
    if ((iVar4 < 1) || (0xe < iVar4)) {
      iVar4 = 0xe;
    }
    iVar4 = aiStack_4d8[iVar4];
    if (iVar4 != 0) {
      (**(code **)(DAT_106b40a8 + 0x74))(&DAT_1002be24);
      local_4e4 = *unaff_ESI + local_4e0;
      FUN_10002c50(local_4e4,unaff_ESI[1],unaff_ESI[2],unaff_ESI[3],iVar4);
      (**(code **)(DAT_106b40a8 + 0x74))(0);
    }
  }
  __security_check_cookie(local_4 ^ (uint)&fStack_4e8);
  return;
}



/* FUN_10001f70 @ 10001f70 size 992 */

void FUN_10001f70(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *unaff_ESI;
  
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025904,unaff_ESI[4]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreAccuracy",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[5]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreImpressives",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[6]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreExcellents",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[7]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreDefends",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[8]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreAssists",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[9]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreGauntlets",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,*unaff_ESI);
  (**(code **)(iVar1 + 0x1c))("ui_scoreScore",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[3]);
  (**(code **)(iVar1 + 0x1c))("ui_scorePerfect",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900("%i to %i",unaff_ESI[1],unaff_ESI[2]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreTeam",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xf]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreBase",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xc]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreTimeBonus",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xe]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreSkillBonus",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xd]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreShutoutBonus",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900("%02i:%02i",(int)unaff_ESI[0xb] / 0x3c,(int)unaff_ESI[0xb] % 0x3c);
  (**(code **)(iVar1 + 0x1c))("ui_scoreTime",uVar2);
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[10]);
  (**(code **)(iVar1 + 0x1c))("ui_scoreCaptures",uVar2);
  iVar1 = DAT_106b40a8;
  if (param_1 != 0) {
    uVar2 = FUN_10001900(&DAT_10025904,unaff_ESI[4]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreAccuracy2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[5]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreImpressives2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[6]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreExcellents2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[7]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreDefends2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[8]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreAssists2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[9]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreGauntlets2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,*unaff_ESI);
    (**(code **)(iVar1 + 0x1c))("ui_scoreScore2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[3]);
    (**(code **)(iVar1 + 0x1c))("ui_scorePerfect2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900("%i to %i",unaff_ESI[1],unaff_ESI[2]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreTeam2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xf]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreBase2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xc]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreTimeBonus2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xe]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreSkillBonus2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[0xd]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreShutoutBonus2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900("%02i:%02i",(int)unaff_ESI[0xb] / 0x3c,(int)unaff_ESI[0xb] % 0x3c);
    (**(code **)(iVar1 + 0x1c))("ui_scoreTime2",uVar2);
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900(&DAT_10025920,unaff_ESI[10]);
    (**(code **)(iVar1 + 0x1c))("ui_scoreCaptures2",uVar2);
  }
  return;
}



/* FUN_10013e70 @ 10013e70 size 986 */

void __fastcall FUN_10013e70(undefined4 param_1,undefined4 param_2,int *param_3,char *param_4)

{
  char *pcVar1;
  int iVar2;
  undefined4 local_14c;
  char *local_148;
  undefined1 local_144 [64];
  char local_104;
  undefined1 auStack_103 [62];
  undefined1 local_c5;
  char local_c4 [63];
  undefined1 local_85;
  char local_84 [63];
  undefined1 local_45;
  char local_44 [63];
  undefined1 local_5;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_14c;
  param_3[0xe] = 0;
  param_3[0x1c] = 0;
  local_14c = param_2;
  if (*param_4 == '\0') {
    __security_check_cookie(local_4 ^ (uint)&local_14c);
    return;
  }
  strncpy(local_c4,param_4,0x3f);
  local_85 = 0;
  pcVar1 = strchr(local_c4,0x2f);
  if (pcVar1 == (char *)0x0) {
    strncpy(local_84,"default",0x3f);
  }
  else {
    if (pcVar1 == (char *)0xffffffff) {
      FUN_10001e70(0,"Q_strncpyz: NULL src");
    }
    strncpy(local_84,pcVar1 + 1,0x3f);
    *pcVar1 = '\0';
  }
  local_45 = 0;
  if (local_148 == (char *)0x0) {
    FUN_10001e70(0,"Q_strncpyz: NULL src");
  }
  strncpy(&local_104,local_148,0x3f);
  local_c5 = 0;
  pcVar1 = strchr(&local_104,0x2f);
  if (pcVar1 == (char *)0x0) {
    strncpy(local_44,"default",0x3f);
  }
  else {
    if (pcVar1 == (char *)0xffffffff) {
      FUN_10001e70(0,"Q_strncpyz: NULL src");
    }
    strncpy(local_44,pcVar1 + 1,0x3f);
    *pcVar1 = '\0';
  }
  local_5 = 0;
  FUN_10001830(local_144,0x40,"models/players/%s/lower.md3",local_c4);
  iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
  *param_3 = iVar2;
  if (iVar2 == 0) {
    FUN_10001830(local_144,0x40,"models/players/characters/%s/lower.md3",local_c4);
    iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
    *param_3 = iVar2;
    if (iVar2 == 0) {
      FUN_10001ee0("Failed to load model file %s\n",local_144);
      goto LAB_10014231;
    }
  }
  FUN_10001830(local_144,0x40,"models/players/%s/upper.md3",local_c4);
  iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
  param_3[0xe] = iVar2;
  if (iVar2 == 0) {
    FUN_10001830(local_144,0x40,"models/players/characters/%s/upper.md3",local_c4);
    iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
    param_3[0xe] = iVar2;
    if (iVar2 != 0) goto LAB_100140b1;
  }
  else {
LAB_100140b1:
    if (local_104 == '*') {
      FUN_10001830(local_144,0x40,"models/players/heads/%s/%s.md3",auStack_103,auStack_103);
    }
    else {
      FUN_10001830(local_144,0x40,"models/players/%s/head.md3",&local_104);
    }
    iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
    param_3[0x1c] = iVar2;
    if ((iVar2 == 0) && (local_104 != '*')) {
      FUN_10001830(local_144,0x40,"models/players/heads/%s/%s.md3",&local_104,&local_104);
      iVar2 = (**(code **)(DAT_106b40a8 + 0x54))(local_144);
      param_3[0x1c] = iVar2;
    }
    if (param_3[0x1c] != 0) {
      iVar2 = FUN_100139a0(param_3,&local_104);
      if ((iVar2 == 0) && (iVar2 = FUN_100139a0(param_3,&local_104), iVar2 == 0)) {
        FUN_10001ee0("Failed to load skin file: %s : %s\n",local_c4,local_84);
      }
      else {
        FUN_10001830(local_144,0x40,"models/players/%s/animation.cfg",local_c4);
        iVar2 = FUN_10013ba0(param_3 + 0x1e);
        if (iVar2 == 0) {
          FUN_10001830(local_144,0x40,"models/players/characters/%s/animation.cfg",local_c4);
          iVar2 = FUN_10013ba0(param_3 + 0x1e);
          if (iVar2 == 0) {
            FUN_10001ee0("Failed to load animation file %s\n",local_144);
          }
        }
      }
      goto LAB_10014231;
    }
  }
  FUN_10001ee0("Failed to load model file %s\n",local_144);
LAB_10014231:
  __security_check_cookie(local_4 ^ (uint)&local_14c);
  return;
}



/* FUN_10018870 @ 10018870 size 981 */

void FUN_10018870(int param_1,int param_2)

{
  undefined4 *puVar1;
  int *piVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  char *pcVar7;
  int iVar8;
  char local_40c [1028];
  uint local_8;
  
  iVar5 = DAT_106b40e0;
  local_8 = DAT_1002a000 ^ (uint)local_40c;
  iVar6 = *(int *)(DAT_106b40e0 + 0x158);
  iVar4 = *(int *)(DAT_106b40e0 + 0x288);
  piVar2 = (int *)(DAT_106b40e0 + 0x158);
  if (iVar6 == 0) goto LAB_10018ab7;
  memset(local_40c,0,0x400);
  (**(code **)(DAT_106b40d0 + 0x58))(iVar6,local_40c,0x400);
  pcVar7 = local_40c;
  do {
    cVar3 = *pcVar7;
    pcVar7 = pcVar7 + 1;
  } while (cVar3 != '\0');
  iVar6 = *(int *)(iVar4 + 0x10);
  iVar8 = (int)pcVar7 - (int)(local_40c + 1);
  if ((iVar6 != 0) && (iVar6 < iVar8)) {
    iVar8 = iVar6;
  }
  if (param_2 == 0) {
    if ((param_1 == 0x8c) || (param_1 == 0xab)) {
      iVar6 = *(int *)(iVar5 + 0x284);
      if (iVar6 < iVar8) {
        memmove(local_40c + iVar6,local_40c + iVar6 + 1,iVar8 - iVar6);
        (**(code **)(DAT_106b40d0 + 0x60))(*piVar2,local_40c);
      }
      goto LAB_10018ab7;
    }
    if ((param_1 == 0x87) || (param_1 == 0xa5)) {
      if ((*(int *)(iVar4 + 0x14) == 0) ||
         ((iVar6 = *(int *)(iVar5 + 0x284), iVar6 < *(int *)(iVar4 + 0x14) || (iVar8 <= iVar6)))) {
        if (*(int *)(iVar5 + 0x284) < iVar8) {
          *(int *)(iVar5 + 0x284) = *(int *)(iVar5 + 0x284) + 1;
        }
      }
      else {
        *(int *)(iVar5 + 0x284) = iVar6 + 1;
        *(int *)(iVar4 + 0x18) = *(int *)(iVar4 + 0x18) + 1;
      }
      goto LAB_10018ab7;
    }
    if ((param_1 == 0x86) || (param_1 == 0xa3)) {
      if (0 < *(int *)(iVar5 + 0x284)) {
        *(int *)(iVar5 + 0x284) = *(int *)(iVar5 + 0x284) + -1;
      }
      if (*(int *)(iVar5 + 0x284) < *(int *)(iVar4 + 0x18)) {
        *(int *)(iVar4 + 0x18) = *(int *)(iVar4 + 0x18) + -1;
      }
      goto LAB_10018ab7;
    }
    if ((param_1 == 0x8f) || (param_1 == 0xa0)) {
      *(undefined4 *)(iVar5 + 0x284) = 0;
      *(undefined4 *)(iVar4 + 0x18) = 0;
      goto LAB_10018ab7;
    }
    if ((param_1 == 0x90) || (param_1 == 0xa6)) {
      *(int *)(iVar5 + 0x284) = iVar8;
      if (*(int *)(iVar4 + 0x14) < iVar8) {
        *(int *)(iVar4 + 0x18) = iVar8 - *(int *)(iVar4 + 0x14);
      }
      goto LAB_10018ab7;
    }
    if ((param_1 == 0x8b) || (param_1 == 0xaa)) {
      puVar1 = (undefined4 *)(DAT_106b40d0 + 0x6c);
      iVar6 = (**(code **)(DAT_106b40d0 + 0x70))();
      (*(code *)*puVar1)(iVar6 == 0);
      goto LAB_10018ab7;
    }
  }
  else {
    if (param_1 == 8) {
      iVar6 = *(int *)(iVar5 + 0x284);
      if (0 < iVar6) {
        memmove(local_40c + iVar6 + -1,local_40c + iVar6,(iVar8 - iVar6) + 1);
        *(int *)(iVar5 + 0x284) = *(int *)(iVar5 + 0x284) + -1;
        if (*(int *)(iVar5 + 0x284) < *(int *)(iVar4 + 0x18)) {
          *(int *)(iVar4 + 0x18) = *(int *)(iVar4 + 0x18) + -1;
        }
      }
      (**(code **)(DAT_106b40d0 + 0x60))(*piVar2,local_40c);
      goto LAB_10018ab7;
    }
    if (((param_1 < 0x20) || (*piVar2 == 0)) ||
       ((*(int *)(iVar5 + 0x110) == 9 && ((param_1 < 0x30 || (0x39 < param_1))))))
    goto LAB_10018ab7;
    iVar6 = (**(code **)(DAT_106b40d0 + 0x70))();
    if (iVar6 == 0) {
      if ((iVar8 == 0xff) || ((*(int *)(iVar4 + 0x10) != 0 && (*(int *)(iVar4 + 0x10) <= iVar8))))
      goto LAB_10018ab7;
      iVar6 = *(int *)(iVar5 + 0x284);
      memmove(local_40c + iVar6 + 1,local_40c + iVar6,(iVar8 - iVar6) + 1);
    }
    else if ((*(int *)(iVar4 + 0x10) != 0) && (*(int *)(iVar4 + 0x10) <= *(int *)(iVar5 + 0x284)))
    goto LAB_10018ab7;
    local_40c[*(int *)(iVar5 + 0x284)] = (char)param_1;
    (**(code **)(DAT_106b40d0 + 0x60))(*piVar2,local_40c);
    if (*(int *)(iVar5 + 0x284) < iVar8 + 1) {
      iVar6 = *(int *)(iVar5 + 0x284) + 1;
      *(int *)(iVar5 + 0x284) = iVar6;
      if ((*(int *)(iVar4 + 0x14) != 0) && (*(int *)(iVar4 + 0x14) < iVar6)) {
        *(int *)(iVar4 + 0x18) = *(int *)(iVar4 + 0x18) + 1;
      }
    }
  }
  if (((((param_1 == 9) || (param_1 == 0x85)) || (param_1 == 0xa7)) &&
      (iVar6 = FUN_100195b0(), iVar6 != 0)) &&
     ((*(int *)(iVar6 + 0x110) == 4 || (*(int *)(iVar6 + 0x110) == 9)))) {
    DAT_106b40e0 = iVar6;
  }
  if (((param_1 == 0x84) || (param_1 == 0xa1)) &&
     ((iVar6 = FUN_100194b0(), iVar6 != 0 &&
      ((*(int *)(iVar6 + 0x110) == 4 || (*(int *)(iVar6 + 0x110) == 9)))))) {
    DAT_106b40e0 = iVar6;
  }
LAB_10018ab7:
  __security_check_cookie(local_8 ^ (uint)local_40c);
  return;
}



/* FUN_10005c20 @ 10005c20 size 965 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10005c20(undefined4 *param_1)

{
  char cVar1;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  char *pcVar5;
  undefined2 *puVar6;
  int aiStack_3d8 [3];
  undefined1 auStack_3cc [4];
  char acStack_3c8 [63];
  undefined1 uStack_389;
  char acStack_388 [127];
  undefined1 uStack_309;
  char acStack_308 [255];
  undefined1 uStack_209;
  char acStack_208 [255];
  undefined1 uStack_109;
  undefined1 auStack_108 [260];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)aiStack_3d8;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceEnemyModel",&DAT_10042f38,0x400);
  strncpy(acStack_3c8,&DAT_10042f38,0x3f);
  uStack_389 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceEnemyModel",&DAT_10042f38,0x400);
  strncpy(acStack_308,&DAT_10042f38,0xff);
  uStack_209 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceEnemySkin",&DAT_10042f38,0x400);
  strncpy(acStack_208,&DAT_10042f38,0xff);
  uStack_109 = 0;
  auStack_108[0] = 0;
  if (acStack_3c8[0] == '\0') {
    if (acStack_208[0] == '\0') goto LAB_10005fcc;
    strncpy(acStack_3c8,"sarge",0x3f);
    uStack_389 = 0;
  }
  if (acStack_208[0] != '\0') {
    strncpy(acStack_388,acStack_3c8,0x7f);
    uStack_309 = 0;
    pcVar2 = strtok(acStack_388,"/");
    if (pcVar2 == (char *)0x0) {
      FUN_10001e70(0,"Q_strncpyz: NULL src");
    }
    strncpy(acStack_3c8,pcVar2,0x3f);
    uStack_389 = 0;
    puVar6 = (undefined2 *)(auStack_3cc + 3);
    do {
      pcVar2 = (char *)((int)puVar6 + 1);
      puVar6 = (undefined2 *)((int)puVar6 + 1);
    } while (*pcVar2 != '\0');
    *puVar6 = DAT_10026b48;
    pcVar2 = acStack_208;
    do {
      cVar1 = *pcVar2;
      pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    uVar3 = (int)pcVar2 - (int)acStack_208;
    pcVar2 = auStack_3cc + 3;
    do {
      pcVar5 = pcVar2 + 1;
      pcVar2 = pcVar2 + 1;
    } while (*pcVar5 != '\0');
    pcVar5 = acStack_208;
    for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *(undefined4 *)pcVar2 = *(undefined4 *)pcVar5;
      pcVar5 = pcVar5 + 4;
      pcVar2 = pcVar2 + 4;
    }
    for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *pcVar2 = *pcVar5;
      pcVar5 = pcVar5 + 1;
      pcVar2 = pcVar2 + 1;
    }
    strncpy(acStack_308,acStack_3c8,0xff);
    uStack_209 = 0;
  }
  if (DAT_106b40b4 == 0) {
    DAT_106b40b4 = 1;
    DAT_1002af38 = 1;
LAB_10005df9:
    auStack_108[0] = 0;
    memset(&DAT_1004f9e0,0,0x47c);
    aiStack_3d8[2] = DAT_100294fc;
    aiStack_3d8[1] = 0;
    auStack_3cc = (undefined1  [4])0x0;
    FUN_10014250(acStack_308,auStack_108);
    FUN_100142e0();
    DAT_1002af38 = 0;
  }
  else if (DAT_1002af38 != 0) goto LAB_10005df9;
  _DAT_1004fe48 = 1;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyHeadColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004fe4c = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004fe4c = aiStack_3d8[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyUpperColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004fe50 = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004fe50 = aiStack_3d8[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyLowerColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004fe54 = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004fe54 = aiStack_3d8[0];
  }
  FUN_10012d90(*param_1,param_1[1],param_1[2],param_1[3]);
LAB_10005fcc:
  __security_check_cookie(local_4 ^ (uint)aiStack_3d8);
  return;
}



/* FUN_10005850 @ 10005850 size 962 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10005850(undefined4 *param_1)

{
  char cVar1;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  char *pcVar5;
  undefined2 *puVar6;
  int aiStack_3d8 [3];
  undefined1 auStack_3cc [4];
  char acStack_3c8 [63];
  undefined1 uStack_389;
  char acStack_388 [127];
  undefined1 uStack_309;
  char acStack_308 [255];
  undefined1 uStack_209;
  char acStack_208 [255];
  undefined1 uStack_109;
  undefined1 auStack_108 [260];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)aiStack_3d8;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_3c8,&DAT_10042f38,0x3f);
  uStack_389 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_308,&DAT_10042f38,0xff);
  uStack_209 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceTeamSkin",&DAT_10042f38,0x400);
  strncpy(acStack_208,&DAT_10042f38,0xff);
  uStack_109 = 0;
  if (acStack_3c8[0] == '\0') {
    if (acStack_208[0] == '\0') goto LAB_10005bfc;
    strncpy(acStack_3c8,"sarge",0x3f);
    uStack_389 = 0;
  }
  if (acStack_208[0] != '\0') {
    strncpy(acStack_388,acStack_3c8,0x7f);
    uStack_309 = 0;
    pcVar2 = strtok(acStack_388,"/");
    if (pcVar2 == (char *)0x0) {
      FUN_10001e70(0,"Q_strncpyz: NULL src");
    }
    strncpy(acStack_3c8,pcVar2,0x3f);
    uStack_389 = 0;
    puVar6 = (undefined2 *)(auStack_3cc + 3);
    do {
      pcVar2 = (char *)((int)puVar6 + 1);
      puVar6 = (undefined2 *)((int)puVar6 + 1);
    } while (*pcVar2 != '\0');
    *puVar6 = DAT_10026b48;
    pcVar2 = acStack_208;
    do {
      cVar1 = *pcVar2;
      pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    uVar3 = (int)pcVar2 - (int)acStack_208;
    pcVar2 = auStack_3cc + 3;
    do {
      pcVar5 = pcVar2 + 1;
      pcVar2 = pcVar2 + 1;
    } while (*pcVar5 != '\0');
    pcVar5 = acStack_208;
    for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *(undefined4 *)pcVar2 = *(undefined4 *)pcVar5;
      pcVar5 = pcVar5 + 4;
      pcVar2 = pcVar2 + 4;
    }
    for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *pcVar2 = *pcVar5;
      pcVar5 = pcVar5 + 1;
      pcVar2 = pcVar2 + 1;
    }
    strncpy(acStack_308,acStack_3c8,0xff);
    uStack_209 = 0;
  }
  if (DAT_106b40b0 == 0) {
    DAT_106b40b0 = 1;
    DAT_1002af34 = 1;
LAB_10005a29:
    auStack_108[0] = 0;
    memset(&DAT_1004f0e0,0,0x47c);
    aiStack_3d8[2] = DAT_100294fc;
    aiStack_3d8[1] = 0;
    auStack_3cc = (undefined1  [4])0x0;
    FUN_10014250(acStack_308,auStack_108);
    FUN_100142e0();
    DAT_1002af34 = 0;
  }
  else if (DAT_1002af34 != 0) goto LAB_10005a29;
  _DAT_1004f548 = 1;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamHeadColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004f54c = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004f54c = aiStack_3d8[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamUpperColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004f550 = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004f550 = aiStack_3d8[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamLowerColor",acStack_388,0x40);
  pcVar2 = strstr(acStack_388,"0x");
  if (pcVar2 == (char *)0x0) {
    _DAT_1004f554 = atoi(acStack_388);
  }
  else {
    aiStack_3d8[0] = 0;
    sscanf(acStack_388,"0x%08x",aiStack_3d8);
    _DAT_1004f554 = aiStack_3d8[0];
  }
  FUN_10012d90(*param_1,param_1[1],param_1[2],param_1[3]);
LAB_10005bfc:
  __security_check_cookie(local_4 ^ (uint)aiStack_3d8);
  return;
}



/* FUN_100203a0 @ 100203a0 size 928 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100203a0(void)

{
  undefined4 *puVar1;
  float fVar2;
  uint uVar3;
  int iVar4;
  undefined4 uVar5;
  uint *puVar6;
  float10 fVar7;
  undefined1 auStack_b4 [56];
  float fStack_7c;
  uint local_78;
  int local_74;
  float fStack_70;
  float fStack_6c;
  float fStack_68;
  undefined4 uStack_64;
  undefined4 uStack_60;
  undefined4 uStack_5c;
  undefined4 uStack_58;
  undefined4 uStack_54;
  undefined4 uStack_50;
  undefined4 uStack_4c;
  undefined4 uStack_48;
  uint local_44;
  
  local_44 = DAT_1002a000 ^ (uint)auStack_b4;
  local_78 = 0;
  if (DAT_106b40c4 != (code *)0x0) {
    (*DAT_106b40c4)(DAT_106b40c8);
  }
  local_74 = 0;
  if (0 < DAT_106b40e4) {
    puVar6 = &DAT_106b4968;
    do {
      if (puVar6 == (uint *)0x48) {
        uVar3 = 0;
      }
      else if ((*puVar6 & 4) == 0) {
        *puVar6 = *puVar6 & 0xffefffff;
        FUN_100155a0();
        uVar3 = 0;
      }
      else {
        if (((puVar6[-3] != 0) || (puVar6[-2] != 0)) &&
           (*(code **)(DAT_106b40d0 + 0x4c) != (code *)0x0)) {
          iVar4 = (**(code **)(DAT_106b40d0 + 0x4c))(puVar6[-3],puVar6[-2]);
          uVar3 = 0;
          if (iVar4 == 0) goto LAB_1002067c;
        }
        fVar7 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))("web_browserActive");
        if (fVar7 == (float10)0) {
          FUN_100155a0();
          FUN_100156b0();
          if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
            (**(code **)(DAT_106b40d0 + 0xd8))(puVar6[0x30]);
          }
          if (puVar6[0x2f] != 0) {
            fStack_6c = (float)puVar6[0x2c];
            if (fStack_6c <= _DAT_10029214) {
              (**(code **)(DAT_106b40d0 + 8))(0,0,DAT_10029398,DAT_10029394,puVar6[0x28]);
            }
            else {
              fStack_68 = (float)*(int *)(DAT_106b40d0 + 0x11f0c);
              fVar2 = ((fStack_6c -
                       (float)*(int *)(DAT_106b40d0 + 0x11f08) * ((float)puVar6[0x2d] / fStack_68))
                      / fStack_6c) * (float)_DAT_10029278;
              fStack_7c = 1.0 - fVar2;
              fStack_70 = fStack_6c;
              (**(code **)(DAT_106b40d0 + 0xc))
                        (0,0,(float)*(int *)(DAT_106b40d0 + 0x11f08),fStack_68,fVar2,0,fStack_7c,
                         0x3f800000,puVar6[0x28]);
            }
          }
          FUN_10014f00(puVar6[0x36],puVar6[0x35],(float)(int)puVar6[0x34]);
          iVar4 = 0;
          if (0 < (int)puVar6[0x31]) {
            do {
              if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
                (**(code **)(DAT_106b40d0 + 0xd8))(puVar6[0x30]);
              }
              FUN_1001ced0();
              iVar4 = iVar4 + 1;
            } while (iVar4 < (int)puVar6[0x31]);
          }
          if (DAT_106b40ec != 0) {
            uStack_58 = DAT_10029234;
            uStack_5c = DAT_10029234;
            uStack_64 = DAT_10029234;
            uStack_60 = 0;
            (**(code **)(DAT_106b40d0 + 0x28))
                      (puVar6[-0x12],puVar6[-0x11],puVar6[-0x10],puVar6[-0xf],0x3f800000,&uStack_64)
            ;
          }
          if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
            (**(code **)(DAT_106b40d0 + 0xd8))(0);
          }
          uVar3 = 1;
        }
        else {
          uVar3 = 0;
        }
      }
LAB_1002067c:
      local_78 = local_78 | uVar3;
      local_74 = local_74 + 1;
      puVar6 = puVar6 + 0x455;
    } while (local_74 < DAT_106b40e4);
  }
  if (DAT_106b40ec != 0) {
    uStack_54 = DAT_10029234;
    uStack_50 = DAT_10029234;
    uStack_4c = DAT_10029234;
    uStack_48 = DAT_10029234;
    puVar1 = (undefined4 *)(DAT_106b40d0 + 0x10);
    uVar5 = FUN_10001900("fps: %f",(double)*(float *)(DAT_106b40d0 + 0x11f40),0,0,0);
    (*(code *)*puVar1)(DAT_10029380,_DAT_100293d8,0,DAT_10029328,&uStack_54,uVar5);
  }
  __security_check_cookie(local_44 ^ (uint)auStack_b4);
  return;
}



/* FUN_1001bc30 @ 1001bc30 size 894 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001bc30(float *param_1)

{
  int *piVar1;
  int iVar2;
  float10 extraout_ST0;
  float10 extraout_ST1;
  float local_250;
  float local_24c;
  float local_248;
  float fStack_244;
  float fStack_240;
  float fStack_23c;
  undefined4 uStack_238;
  float fStack_234;
  undefined4 uStack_230;
  float fStack_22c;
  float fStack_228;
  float fStack_224;
  undefined1 auStack_220 [4];
  undefined4 uStack_21c;
  float fStack_218;
  float fStack_214;
  float fStack_210;
  float fStack_20c;
  float fStack_1f8;
  float fStack_1f4;
  float fStack_1f0;
  undefined1 auStack_1ec [16];
  float fStack_1dc;
  float fStack_1d8;
  float fStack_1d4;
  float fStack_1cc;
  float fStack_1c8;
  float fStack_1c4;
  undefined4 local_190;
  undefined4 local_18c;
  int local_188;
  int local_184;
  float fStack_180;
  float fStack_17c;
  undefined4 local_16c;
  undefined4 local_168;
  undefined4 local_164;
  undefined4 local_160;
  undefined4 local_15c;
  undefined4 local_158;
  undefined4 local_154;
  undefined4 local_150;
  undefined4 local_14c;
  undefined4 uStack_148;
  undefined4 local_144;
  undefined1 local_1c [4];
  float fStack_18;
  float fStack_14;
  undefined1 local_10 [4];
  float fStack_c;
  float fStack_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_250;
  piVar1 = (int *)param_1[0xa2];
  if (piVar1 != (int *)0x0) {
    memset(&local_190,0,0x170);
    iVar2 = DAT_106b40d0;
    local_144 = 1;
    local_16c = DAT_10029234;
    local_168 = 0;
    local_164 = 0;
    local_160 = 0;
    local_15c = DAT_10029234;
    local_158 = 0;
    local_154 = 0;
    local_248 = *(float *)(DAT_106b40d0 + 0xe0) * (param_1[2] - (float)_DAT_100292f0);
    local_150 = 0;
    local_14c = DAT_10029234;
    local_24c = *(float *)(DAT_106b40d0 + 0xdc) * (param_1[3] - (float)_DAT_100292f0);
    local_250 = (*param_1 + 1.0) * *(float *)(DAT_106b40d0 + 0xe0);
    local_190 = FUN_10021270();
    local_250 = (float)(extraout_ST0 * (float10)(float)((float10)param_1[1] + extraout_ST1));
    local_18c = FUN_10021270();
    local_188 = (int)local_248;
    local_184 = (int)local_24c;
    (**(code **)(iVar2 + 0x20))(param_1[0x4e],local_1c,local_10);
    fStack_23c = (fStack_14 + fStack_8) * (float)_DAT_100292e8;
    fStack_240 = (fStack_c + fStack_18) * (float)_DAT_10029278;
    local_250 = (fStack_8 - fStack_14) * (float)_DAT_10029278;
    fStack_244 = local_250 / (float)_DAT_100292e0;
    fStack_180 = (float)piVar1[4];
    if ((float)piVar1[4] == 0.0) {
      fStack_180 = local_248;
    }
    fStack_17c = (float)piVar1[5];
    if ((float)piVar1[5] == 0.0) {
      fStack_17c = local_24c;
    }
    (**(code **)(DAT_106b40d0 + 0x34))();
    iVar2 = DAT_106b40d0;
    uStack_148 = *(undefined4 *)(DAT_106b40d0 + 0xe8);
    memset(auStack_220,0,0x8c);
    if ((piVar1[6] != 0) && ((int)param_1[0x1d] < *(int *)(iVar2 + 0xe8))) {
      param_1[0x1d] = (float)(piVar1[6] + *(int *)(iVar2 + 0xe8));
      *piVar1 = (*piVar1 + 1) % 0x168;
    }
    fStack_234 = (float)*piVar1;
    uStack_238 = 0;
    uStack_230 = 0;
    FUN_100012a0(auStack_1ec);
    fStack_1f8 = DAT_106b4090 - fStack_22c;
    fStack_218 = param_1[0x4e];
    fStack_1f4 = DAT_106b4094 - fStack_228;
    fStack_1dc = fStack_244;
    fStack_1d8 = fStack_240;
    fStack_1f0 = DAT_106b4098 - fStack_224;
    fStack_1d4 = fStack_23c;
    fStack_214 = fStack_244;
    fStack_210 = fStack_240;
    fStack_20c = fStack_23c;
    uStack_21c = 0xc0;
    fStack_1cc = fStack_244;
    fStack_1c8 = fStack_240;
    fStack_1c4 = fStack_23c;
    (**(code **)(DAT_106b40d0 + 0x38))(auStack_220);
    (**(code **)(DAT_106b40d0 + 0x3c))(&local_190);
  }
  __security_check_cookie(local_4 ^ (uint)&local_250);
  return;
}



/* FUN_10008b60 @ 10008b60 size 802 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_10008b60(void)

{
  byte *pbVar1;
  byte bVar2;
  byte bVar3;
  char *pcVar4;
  byte *pbVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  byte *pbVar9;
  bool bVar10;
  int iStack_101c;
  int iStack_1018;
  int iStack_1014;
  undefined1 local_1010 [8];
  int iStack_1008;
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&iStack_101c;
  (**(code **)(DAT_106b40a8 + 0xb8))(local_1010);
  (**(code **)(DAT_106b40a8 + 0xc0))(iStack_1008 + 0x211,acStack_404,0x400);
  DAT_107597c4 = iStack_1008;
  pcVar4 = (char *)FUN_10001940();
  DAT_107597c8 = atoi(pcVar4);
  pcVar4 = (char *)FUN_10001940();
  iStack_1014 = atoi(pcVar4);
  (**(code **)(DAT_106b40a8 + 0xc0))(0,acStack_404,0x400);
  pcVar4 = (char *)FUN_10001940();
  iStack_1018 = atoi(pcVar4);
  iVar8 = 0;
  DAT_107597b0 = 0;
  DAT_107597b4 = 0;
  iStack_101c = 0;
  if (0 < iStack_1018) {
    do {
      (**(code **)(DAT_106b40a8 + 0xc0))(iVar8 + 0x211,acStack_404,0x400);
      if (acStack_404[0] != '\0') {
        pcVar4 = (char *)FUN_10001940();
        iVar6 = DAT_107597b0 * 0x28;
        if (&DAT_107597cc + iVar6 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL dest");
        }
        if (pcVar4 == (char *)0x0) {
          FUN_10001e70(0,"Q_strncpyz: NULL src");
        }
        strncpy(&DAT_107597cc + iVar6,pcVar4,0x27);
        (&DAT_107597f3)[iVar6] = 0;
        pbVar5 = &DAT_107597cc + DAT_107597b0 * 0x28;
        bVar2 = (&DAT_107597cc)[DAT_107597b0 * 0x28];
        pbVar9 = pbVar5;
        while (bVar2 != 0) {
          if ((((*pbVar5 == 0x5e) && (bVar3 = pbVar5[1], bVar3 != 0)) && ('/' < (char)bVar3)) &&
             ((char)bVar3 < '8')) {
            pbVar5 = pbVar5 + 1;
          }
          else if (0x1f < bVar2) {
            *pbVar9 = bVar2;
            pbVar9 = pbVar9 + 1;
          }
          pbVar1 = pbVar5 + 1;
          pbVar5 = pbVar5 + 1;
          bVar2 = *pbVar1;
        }
        if (*pbVar9 != 0) {
          *pbVar9 = 0;
        }
        (&DAT_1075abcc)[DAT_107597b0] = iVar8;
        DAT_107597b0 = DAT_107597b0 + 1;
        pcVar4 = (char *)FUN_10001940();
        iVar6 = atoi(pcVar4);
        if (iVar6 == iStack_1014) {
          pcVar4 = (char *)FUN_10001940();
          iVar6 = DAT_107597b4 * 0x28;
          if (&DAT_1075a1cc + iVar6 == (char *)0x0) {
            FUN_10001e70(0,"Q_strncpyz: NULL dest");
          }
          if (pcVar4 == (char *)0x0) {
            FUN_10001e70(0,"Q_strncpyz: NULL src");
          }
          strncpy(&DAT_1075a1cc + iVar6,pcVar4,0x27);
          (&DAT_1075a1f3)[iVar6] = 0;
          FUN_100017e0();
          (&DAT_1075accc)[DAT_107597b4] = iVar8;
          if (DAT_107597c4 == iVar8) {
            iStack_101c = DAT_107597b4;
          }
          DAT_107597b4 = DAT_107597b4 + 1;
        }
      }
      iVar8 = iVar8 + 1;
    } while (iVar8 < iStack_1018);
  }
  iVar8 = DAT_106b40a8;
  if (DAT_107597c8 == 0) {
    uVar7 = FUN_10001900(&DAT_10025d20,iStack_101c);
    (**(code **)(iVar8 + 0x1c))("cg_selectedPlayer",uVar7);
  }
  (**(code **)(DAT_106b40a8 + 0x28))("cg_selectedPlayer");
  iVar8 = FUN_10021270();
  if (-1 < iVar8) {
    bVar10 = SBORROW4(iVar8,DAT_107597b4);
    iVar6 = iVar8 - DAT_107597b4;
    if (iVar8 <= DAT_107597b4) goto LAB_10008e55;
  }
  iVar8 = 0;
  bVar10 = SBORROW4(0,DAT_107597b4);
  iVar6 = -DAT_107597b4;
LAB_10008e55:
  if (bVar10 != iVar6 < 0) {
    (**(code **)(DAT_106b40a8 + 0x1c))("cg_selectedPlayerName",&DAT_1075a1cc + iVar8 * 0x28);
  }
  __security_check_cookie(local_4 ^ (uint)&iStack_101c);
  return;
}



/* FUN_1000d740 @ 1000d740 size 789 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_1000d740(int param_1)

{
  undefined *puVar1;
  char *pcVar2;
  int iVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 *puVar8;
  int aiStack_40c [2];
  undefined1 auStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)aiStack_40c;
  if (param_1 == 0) {
    if (DAT_10746428 <= DAT_107644a8) goto LAB_1000da47;
  }
  else if (param_1 == 2) {
    param_1 = 0;
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cl_motdString",&DAT_107644d0,0x400);
  pcVar4 = (char *)&DAT_107644d0;
  do {
    pcVar2 = pcVar4;
    pcVar4 = pcVar2 + 1;
  } while (*pcVar2 != '\0');
  pcVar2 = pcVar2 + -0x107644d0;
  if (pcVar2 == (char *)0x0) {
    pcVar4 = "Welcome to Team Arena!";
    puVar8 = &DAT_107644d0;
    for (iVar7 = 5; iVar7 != 0; iVar7 = iVar7 + -1) {
      *puVar8 = *(undefined4 *)pcVar4;
      pcVar4 = pcVar4 + 4;
      puVar8 = puVar8 + 1;
    }
    *(undefined2 *)puVar8 = *(undefined2 *)pcVar4;
    *(char *)((int)puVar8 + 2) = pcVar4[2];
    pcVar4 = (char *)&DAT_107644d0;
    do {
      pcVar2 = pcVar4;
      pcVar4 = pcVar2 + 1;
    } while (*pcVar2 != '\0');
    pcVar2 = pcVar2 + -0x107644d0;
  }
  if (pcVar2 != DAT_107644b8) {
    DAT_107644bc = 0xffffffff;
    DAT_107644b8 = pcVar2;
  }
  if (param_1 != 0) {
    _DAT_100468bc = 0;
    DAT_107644a0 = 0;
    DAT_107644a4 = 0;
    FUN_1001d3d0(2);
    (**(code **)(DAT_106b40a8 + 0xec))(DAT_1074148c,0xffffffff,1);
  }
  aiStack_40c[0] = (**(code **)(DAT_106b40a8 + 0xc4))(DAT_1074148c);
  if ((aiStack_40c[0] == -1) || ((DAT_1074148c == 0 && (aiStack_40c[0] == 0)))) {
    DAT_107644a8 = DAT_10746428 + 500;
    DAT_107644a0 = 0;
    DAT_107644a4 = 0;
  }
  else {
    iVar7 = 0;
    if (0 < aiStack_40c[0]) {
      do {
        iVar3 = (**(code **)(DAT_106b40a8 + 0xf0))(DAT_1074148c,iVar7);
        if ((iVar3 != 0) &&
           ((iVar3 = (**(code **)(DAT_106b40a8 + 0xd0))(DAT_1074148c,iVar7), 0 < iVar3 ||
            (DAT_1074148c == 3)))) {
          (**(code **)(DAT_106b40a8 + 0xcc))(DAT_1074148c,iVar7,auStack_404,0x400);
          pcVar4 = (char *)FUN_10001940();
          iVar5 = atoi(pcVar4);
          DAT_107644a4 = DAT_107644a4 + iVar5;
          if ((DAT_10745a4c == 0) && (iVar5 == 0)) {
LAB_1000d903:
            (**(code **)(DAT_106b40a8 + 0xec))(DAT_1074148c,iVar7,0);
          }
          else {
            if (DAT_10767d2c == 0) {
              pcVar4 = (char *)FUN_10001940();
              iVar6 = atoi(pcVar4);
              if (iVar5 == iVar6) goto LAB_1000d903;
            }
            if ((&DAT_10759730)[DAT_1074580c * 2] == -1) {
LAB_1000d99b:
              if (0 < DAT_1074082c) {
                puVar1 = (&PTR_DAT_100239c0)[DAT_1074082c * 2];
                iVar5 = FUN_10001940();
                if (((iVar5 == 0) || (puVar1 == (undefined *)0x0)) ||
                   (iVar5 = FUN_100016c0(), iVar5 != 0)) goto LAB_1000d97f;
              }
              if (DAT_1074148c == 3) {
                FUN_1000d670();
              }
              FUN_1000d6c0(iVar7);
              if (0 < iVar3) {
                (**(code **)(DAT_106b40a8 + 0xec))(DAT_1074148c,iVar7,0);
                _DAT_100468bc = _DAT_100468bc + 1;
              }
            }
            else {
              pcVar4 = (char *)FUN_10001940();
              iVar5 = atoi(pcVar4);
              if (iVar5 == (&DAT_10759730)[DAT_1074580c * 2]) goto LAB_1000d99b;
LAB_1000d97f:
              (**(code **)(DAT_106b40a8 + 0xec))(DAT_1074148c,iVar7,0);
            }
          }
        }
        iVar7 = iVar7 + 1;
      } while (iVar7 < aiStack_40c[0]);
    }
    DAT_10762484 = DAT_10746428;
  }
LAB_1000da47:
  __security_check_cookie(local_4 ^ (uint)aiStack_40c);
  return;
}



/* FUN_10017570 @ 10017570 size 777 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_10017570(float param_1,float param_2)

{
  float fVar1;
  float fVar2;
  float *in_EAX;
  int iVar3;
  
  (**(code **)(DAT_106b40d0 + 0x7c))(in_EAX[0xa0]);
  if (((uint)in_EAX[0x12] & 0x400) == 0) {
    fVar2 = (float)_DAT_10029320;
    fVar1 = (in_EAX[2] + *in_EAX) - fVar2;
    if ((((fVar1 < param_1) && (param_1 < fVar1 + fVar2)) && (in_EAX[1] < param_2)) &&
       (param_2 < in_EAX[1] + fVar2)) {
      return 0x800;
    }
    iVar3 = FUN_10015c00(param_1,param_2);
    if (iVar3 == 0) {
      FUN_100171f0();
      iVar3 = FUN_10015c00(param_1,param_2);
      if (iVar3 != 0) {
        return 0x2000;
      }
      iVar3 = FUN_10015c00(param_1,param_2);
      goto joined_r0x10017848;
    }
  }
  else {
    fVar2 = (float)_DAT_10029320;
    fVar1 = (in_EAX[3] + in_EAX[1]) - fVar2;
    if (((*in_EAX < param_1) && (param_1 < *in_EAX + fVar2)) &&
       ((fVar1 < param_2 && (param_2 < fVar1 + fVar2)))) {
      return 0x800;
    }
    iVar3 = FUN_10015c00(param_1,param_2);
    if (iVar3 == 0) {
      FUN_100171f0();
      iVar3 = FUN_10015c00(param_1,param_2);
      if (iVar3 != 0) {
        return 0x2000;
      }
      iVar3 = FUN_10015c00(param_1,param_2);
joined_r0x10017848:
      if (iVar3 != 0) {
        return 0x4000;
      }
      iVar3 = FUN_10015c00(param_1,param_2);
      if (iVar3 == 0) {
        return 0;
      }
      return 0x8000;
    }
  }
  return 0x1000;
}



/* FUN_10009d30 @ 10009d30 size 773 */

undefined4 FUN_10009d30(uint param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  float10 fVar4;
  
  uVar3 = 1;
  if (param_1 == 0) {
    return 1;
  }
  while( true ) {
    if ((param_1 & 0x100) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("g_gametype");
      if (fVar4 != (float10)0) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffeff;
    }
    if ((param_1 & 0x200) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("g_gametype");
      if (fVar4 == (float10)0) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffdff;
    }
    if ((param_1 & 1) != 0) {
      if ((DAT_107597c8 == 0) ||
         ((DAT_107428cc < DAT_107597b4 && ((&DAT_1075accc)[DAT_107428cc] == DAT_107597c4)))) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffffe;
    }
    if ((param_1 & 2) != 0) {
      if ((DAT_107597c8 != 0) &&
         ((DAT_107597b4 <= DAT_107428cc || ((&DAT_1075accc)[DAT_107428cc] != DAT_107597c4)))) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffffd;
    }
    if ((param_1 & 4) != 0) {
      if (DAT_1074148c != 3) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffffb;
    }
    if ((param_1 & 0x1000) != 0) {
      if (DAT_1074148c == 3) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffffefff;
    }
    if ((param_1 & 0x2000) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_loadout");
      if (fVar4 != (float10)1) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffffdfff;
    }
    if ((param_1 & 0x4000) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_loadout");
      if (fVar4 == (float10)1) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffffbfff;
    }
    if ((param_1 & 0x8000) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("ui_intermission");
      if (fVar4 == (float10)1) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffff7fff;
    }
    if ((param_1 & 0x10000) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("ui_warmup");
      if ((float10)0 <= fVar4) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffeffff;
    }
    if ((param_1 & 0x20000) != 0) {
      fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("ui_warmup");
      if (fVar4 < (float10)0) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffdffff;
    }
    if ((param_1 & 0x10) != 0) {
      if ((int)(&DAT_107596ac)[DAT_1074220c * 2] < 4) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffffffef;
    }
    if ((param_1 & 8) != 0) {
      if (3 < (int)(&DAT_107596ac)[DAT_1074220c * 2]) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffff7;
    }
    if ((param_1 & 0x800) != 0) {
      if ((int)(&DAT_107596ac)[DAT_1074502c * 2] < 4) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffff7ff;
    }
    if ((param_1 & 0x400) != 0) {
      if (3 < (int)(&DAT_107596ac)[DAT_1074502c * 2]) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xfffffbff;
    }
    if ((param_1 & 0x20) != 0) {
      if (DAT_10758284 < DAT_10746428) {
        uVar3 = 0;
      }
      else if ((DAT_10758298 != 0) &&
              (fVar4 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("sv_killserver"),
              fVar4 == (float10)0)) {
        puVar1 = (undefined4 *)(DAT_106b40a8 + 0x88);
        uVar2 = (**(code **)(DAT_106b40a8 + 0x8c))("sound/feedback/voc_newhighscore.ogg",7);
        (*(code *)*puVar1)(uVar2);
        DAT_10758298 = 0;
      }
      param_1 = param_1 & 0xffffffdf;
    }
    if ((char)param_1 < '\0') {
      if (DAT_10758288 < DAT_10746428) {
        uVar3 = 0;
      }
      param_1 = param_1 & 0xffffff7f;
    }
    if ((param_1 & 0x40) == 0) break;
    if (DAT_10758294 == 0) {
      uVar3 = 0;
    }
    param_1 = param_1 & 0xffffffbf;
    if (param_1 == 0) {
      return uVar3;
    }
  }
  return uVar3;
}



/* FUN_10010e30 @ 10010e30 size 763 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10010e30(int param_1)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  char *pcVar4;
  int local_1510;
  undefined4 uStack_150c;
  undefined1 auStack_1504 [2048];
  undefined1 auStack_d04 [1024];
  char acStack_904 [256];
  undefined1 auStack_804 [1024];
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_1510;
  iVar2 = FUN_10016160();
  if (param_1 != 0) goto LAB_10011115;
  if (iVar2 != 0) {
    FUN_1001d7b0();
  }
  (**(code **)(DAT_106b40a8 + 0xb8))(&local_1510);
  auStack_804[0] = 0;
  iVar2 = (**(code **)(DAT_106b40a8 + 0xc0))(0,auStack_804,0x400);
  if (iVar2 != 0) {
    uVar3 = FUN_10001940();
    FUN_10001900("Loading %s",uVar3);
    FUN_100105f0(_DAT_100294c8,_DAT_10029550,DAT_10029328);
  }
  iVar2 = FUN_100016c0();
  if (iVar2 == 0) {
    FUN_10001900("Starting up...");
  }
  else {
    pcVar4 = (char *)FUN_10001900("Connecting to %s",auStack_1504);
    iVar2 = -(int)pcVar4;
    do {
      cVar1 = *pcVar4;
      pcVar4[(int)(acStack_904 + iVar2)] = cVar1;
      pcVar4 = pcVar4 + 1;
    } while (cVar1 != '\0');
  }
  FUN_100105f0(_DAT_100294c8,_DAT_10029540,DAT_10029328);
  FUN_10001940();
  FUN_100105f0(_DAT_100294c8,_DAT_1002954c,DAT_10029328);
  if (local_1510 < 5) {
    FUN_10010660(_DAT_100294c8,_DAT_10029544,_DAT_10029548,_DAT_1002951c,DAT_10029328,auStack_d04);
  }
  if (local_1510 < DAT_10045bbc) {
    DAT_1004e8e0 = 0;
  }
  DAT_10045bbc = local_1510;
  if (local_1510 == 3) {
    pcVar4 = "Awaiting connection...%i";
LAB_1001109f:
    FUN_10001900(pcVar4,uStack_150c);
  }
  else {
    if (local_1510 == 4) {
      pcVar4 = "Awaiting challenge...%i";
      goto LAB_1001109f;
    }
    if (local_1510 != 5) goto LAB_10011115;
    (**(code **)(DAT_106b40a8 + 0x24))("cl_downloadName",acStack_404,0x400);
    if (acStack_404[0] != '\0') {
      FUN_100108d0(_DAT_100294c8,_DAT_10029550,DAT_10029328);
      goto LAB_10011115;
    }
  }
  iVar2 = FUN_100016c0();
  if (iVar2 != 0) {
    FUN_100105f0(_DAT_100294c8,DAT_10029500,DAT_10029328);
  }
  FUN_100105f0(_DAT_100294c8,_DAT_10029530,DAT_10029328);
LAB_10011115:
  __security_check_cookie(local_4 ^ (uint)&local_1510);
  return;
}



/* FUN_10012900 @ 10012900 size 753 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_10012900(int param_1,int param_2,int param_3)

{
  float fVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  float fVar6;
  ushort uVar7;
  int in_EAX;
  float fVar8;
  float local_c;
  float local_8;
  float local_4;
  
  fVar1 = *(float *)(param_1 + 0x40c);
  uVar2 = *(undefined4 *)(param_1 + 0x414);
  uVar7 = FUN_10021270();
  fVar8 = 0.0;
  fVar6 = (float)uVar7 * (float)_DAT_100292b8;
  if (((*(uint *)(param_1 + 0x428) & 0xffffff7f) != 0x16) ||
     ((*(uint *)(param_1 + 0x42c) & 0xffffff7f) != 0xb)) {
    *(undefined4 *)(param_1 + 0x58) = 1;
    *(undefined4 *)(param_1 + 0x60) = 1;
    *(undefined4 *)(param_1 + 0x20) = 1;
  }
  FUN_10012760();
  FUN_10012550(fVar8 * (float)_DAT_100293d0 + fVar6,_DAT_100293d8,_DAT_100293dc,_DAT_100293e0);
  FUN_10012550(fVar8 + fVar6,DAT_100293c8,_DAT_100293dc,_DAT_100293e0);
  uVar3 = *(undefined4 *)(param_1 + 0x54);
  uVar4 = *(undefined4 *)(param_1 + 0x1c);
  fVar8 = fVar1;
  if (_DAT_100292d8 < fVar1) {
    fVar8 = fVar1 - (float)_DAT_100292d0;
  }
  FUN_10012550(fVar8 * (float)_DAT_100293c0,_DAT_100293b0,_DAT_100293b4,_DAT_100293b8);
  uVar5 = *(undefined4 *)(param_1 + 0x5c);
  FUN_10001140(fVar1,uVar5);
  FUN_10001140(fVar6,uVar3);
  FUN_10001140(uVar2,0);
  FUN_10001140(uVar5,0);
  FUN_10001140(uVar3,uVar4);
  FUN_10001140(0,0);
  FUN_100012a0(in_EAX + 0x18);
  *(float *)(in_EAX + 0xc) = DAT_106b4090 - local_c;
  *(float *)(in_EAX + 0x10) = DAT_106b4094 - local_8;
  *(float *)(in_EAX + 0x14) = DAT_106b4098 - local_4;
  FUN_100012a0(param_2 + 0x18);
  *(float *)(param_2 + 0xc) = DAT_106b4090 - local_c;
  *(float *)(param_2 + 0x10) = DAT_106b4094 - local_8;
  *(float *)(param_2 + 0x14) = DAT_106b4098 - local_4;
  FUN_100012a0(param_3 + 0x18);
  *(float *)(param_3 + 0xc) = DAT_106b4090 - local_c;
  *(float *)(param_3 + 0x10) = DAT_106b4094 - local_8;
  *(float *)(param_3 + 0x14) = DAT_106b4098 - local_4;
  return;
}



/* FUN_100156b0 @ 100156b0 size 747 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_100156b0(int param_1)

{
  byte bVar1;
  char cVar2;
  char *pcVar3;
  int iVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  char *pcVar8;
  byte *pbVar9;
  int iVar10;
  undefined4 *puVar11;
  bool bVar12;
  float10 fVar13;
  undefined1 auStack_474 [4];
  int *local_470;
  int iStack_46c;
  int iStack_468;
  int local_464;
  int iStack_460;
  int local_45c;
  int local_458;
  int local_454;
  float fStack_450;
  byte abStack_44c [64];
  undefined1 local_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_474;
  local_464 = 0;
  local_45c = param_1;
  if (0 < *(int *)(param_1 + 0x10c)) {
    local_470 = (int *)(param_1 + 0x154);
    do {
      local_458 = *local_470;
      if ((*(int *)(local_458 + 0x110) == 0x10) &&
         (iVar7 = *(int *)(local_458 + 0x288), local_454 = iVar7, iVar7 != 0)) {
        (**(code **)(DAT_106b40d0 + 0x58))(*(undefined4 *)(local_458 + 0x158),local_40c,0x400);
        iStack_468 = 0;
        if (0 < *(int *)(iVar7 + 0x180)) {
          do {
            iVar10 = iStack_468;
            if (((*(int *)(iVar7 + iStack_468 * 4) != 0) && (iVar4 = FUN_100016c0(), iVar4 == 0)) &&
               (iVar4 = FUN_10015ea0(param_1,*(undefined4 *)(iVar7 + 0x80 + iVar10 * 4)), iVar4 != 0
               )) {
              iVar4 = *(int *)(iVar4 + 0x288);
              iStack_46c = 0;
              iStack_460 = iVar4;
              if (0 < *(int *)(iVar4 + 0x180)) {
                puVar11 = (undefined4 *)(iVar4 + 0x80);
                do {
                  abStack_44c[0] = 0;
                  memset(abStack_44c + 1,0,0x3f);
                  (**(code **)(DAT_106b40d0 + 0x58))(puVar11[-0x20],abStack_44c,0x40);
                  pbVar9 = (byte *)*puVar11;
                  pbVar5 = abStack_44c;
                  do {
                    bVar1 = *pbVar5;
                    bVar12 = bVar1 < *pbVar9;
                    if (bVar1 != *pbVar9) {
LAB_10015802:
                      iVar6 = (1 - (uint)bVar12) - (uint)(bVar12 != 0);
                      goto LAB_10015807;
                    }
                    if (bVar1 == 0) break;
                    bVar1 = pbVar5[1];
                    bVar12 = bVar1 < pbVar9[1];
                    if (bVar1 != pbVar9[1]) goto LAB_10015802;
                    pbVar5 = pbVar5 + 2;
                    pbVar9 = pbVar9 + 2;
                  } while (bVar1 != 0);
                  iVar6 = 0;
LAB_10015807:
                  if (iVar6 != 0) {
                    (**(code **)(DAT_106b40d0 + 0x5c))(puVar11[-0x20]);
                    pbVar5 = abStack_44c;
                    do {
                      bVar1 = *pbVar5;
                      pbVar5 = pbVar5 + 1;
                    } while (bVar1 != 0);
                    iVar7 = (int)pbVar5 - (int)(abStack_44c + 1);
                    bVar12 = false;
                    if ((iVar7 < 1) || (abStack_44c[0] == 0)) {
LAB_1001587c:
                      pcVar3 = (char *)*puVar11;
                      pcVar8 = pcVar3;
                      do {
                        cVar2 = *pcVar8;
                        pcVar8 = pcVar8 + 1;
                      } while (cVar2 != '\0');
                      iVar7 = (int)pcVar8 - (int)(pcVar3 + 1);
                      bVar12 = false;
                      if (((pcVar3 != (char *)0x0) && (0 < iVar7)) && (*pcVar3 != '\0')) {
                        iVar10 = 0;
                        if (0 < iVar7) {
                          do {
                            if (9 < (int)pcVar3[iVar10] - 0x30U) {
                              if (pcVar3[iVar10] != '.') {
                                if (pcVar3[iVar10] != '\0') goto LAB_10015964;
                                break;
                              }
                              if (bVar12) goto LAB_10015964;
                              bVar12 = true;
                            }
                            iVar10 = iVar10 + 1;
                          } while (iVar10 < iVar7);
                        }
                        goto LAB_100158e1;
                      }
                    }
                    else {
                      iVar10 = 0;
                      if (0 < iVar7) {
                        do {
                          if (9 < (int)(char)abStack_44c[iVar10] - 0x30U) {
                            if (abStack_44c[iVar10] != 0x2e) {
                              if (abStack_44c[iVar10] != 0) goto LAB_1001587c;
                              break;
                            }
                            if (bVar12) goto LAB_1001587c;
                            bVar12 = true;
                          }
                          iVar10 = iVar10 + 1;
                        } while (iVar10 < iVar7);
                      }
LAB_100158e1:
                      fVar13 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(puVar11[-0x20]);
                      fStack_450 = (float)ABS(fVar13 - (float10)(float)puVar11[0x20]);
                      iVar10 = iStack_468;
                      iVar4 = iStack_460;
                      iVar7 = local_454;
                      if (fStack_450 <= _DAT_1002939c) goto LAB_1001591b;
                    }
LAB_10015964:
                    (**(code **)(DAT_106b40d0 + 0x60))(*(undefined4 *)(local_458 + 0x158),"Custom");
                    goto LAB_10015982;
                  }
LAB_1001591b:
                  iStack_46c = iStack_46c + 1;
                  puVar11 = puVar11 + 1;
                  param_1 = local_45c;
                } while (iStack_46c < *(int *)(iVar4 + 0x180));
              }
            }
            iStack_468 = iVar10 + 1;
          } while (iStack_468 < *(int *)(iVar7 + 0x180));
        }
      }
      local_470 = local_470 + 1;
      local_464 = local_464 + 1;
    } while (local_464 < *(int *)(param_1 + 0x10c));
  }
LAB_10015982:
  __security_check_cookie(local_8 ^ (uint)auStack_474);
  return;
}



/* FUN_10004b20 @ 10004b20 size 739 */

void FUN_10004b20(undefined4 param_1)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined4 *_Dst;
  undefined1 auStack_828 [16];
  char acStack_818 [1024];
  undefined1 local_418 [16];
  char acStack_408 [1028];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_828;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_418);
  if ((iVar2 != 0) && (acStack_408[0] == '{')) {
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_418);
    while (((iVar2 != 0 && (acStack_408[0] != '\0')) && (acStack_408[0] != '}'))) {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x164))(acStack_408);
      if (iVar2 != 0) {
        memset(auStack_828,0,0x410);
        iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(iVar2,auStack_828);
        while ((iVar3 != 0 && (acStack_818[0] != '}'))) {
          iVar6 = 0;
          iVar3 = 99999;
          do {
            iVar4 = (int)acStack_818[iVar6];
            iVar5 = (int)"assetGlobalDef"[iVar6];
            iVar6 = iVar6 + 1;
            if (iVar3 == 0) break;
            if (iVar4 != iVar5) {
              if (iVar4 - 0x61U < 0x1a) {
                iVar4 = iVar4 + -0x20;
              }
              if (iVar5 - 0x61U < 0x1a) {
                iVar5 = iVar5 + -0x20;
              }
              if (iVar4 != iVar5) {
                if ((char)((iVar5 <= iVar4) * '\x02') != '\x01') {
                  iVar6 = FUN_100016c0();
                  iVar3 = DAT_106b40e4;
                  if (iVar6 == 0) {
                    iVar6 = DAT_106b40e4 * 0x1154;
                    _Dst = &DAT_106b4920 + DAT_106b40e4 * 0x455;
                    if (DAT_106b40e4 < 0x80) {
                      memset(_Dst,0,0x1154);
                      iVar4 = DAT_106b40d0;
                      *(undefined4 *)(&DAT_106b4a34 + iVar6) = 0xffffffff;
                      (&DAT_106b4a40)[iVar3 * 0x455] = *(undefined4 *)(iVar4 + 0xf220);
                      (&DAT_106b4a3c)[iVar3 * 0x455] = *(undefined4 *)(iVar4 + 0xf218);
                      (&DAT_106b4a38)[iVar3 * 0x455] = *(undefined4 *)(iVar4 + 0xf21c);
                      memset(_Dst,0,0x100);
                      uVar1 = DAT_10029234;
                      *(undefined4 *)(&DAT_106b4964 + iVar6) = DAT_10029234;
                      *(undefined4 *)(&DAT_106b49a4 + iVar6) = uVar1;
                      *(undefined4 *)(&DAT_106b49a0 + iVar6) = uVar1;
                      *(undefined4 *)(&DAT_106b499c + iVar6) = uVar1;
                      *(undefined4 *)(&DAT_106b4998 + iVar6) = uVar1;
                      (&DAT_106b494c)[iVar3 * 0x455] = 0xffffffff;
                      iVar6 = FUN_10020190(iVar2,_Dst);
                      if (iVar6 != 0) {
                        if ((&DAT_106b4a24)[iVar3 * 0x455] != 0) {
                          *_Dst = 0;
                          (&DAT_106b4924)[iVar3 * 0x455] = 0;
                          (&DAT_106b4928)[iVar3 * 0x455] = DAT_10029398;
                          (&DAT_106b492c)[iVar3 * 0x455] = DAT_10029394;
                        }
                        FUN_100159a0();
                        FUN_100154e0();
                        DAT_106b40e4 = DAT_106b40e4 + 1;
                      }
                    }
                  }
                  goto LAB_10004d7e;
                }
                break;
              }
            }
            iVar3 = iVar3 + -1;
          } while (iVar4 != 0);
          iVar3 = FUN_100045b0(iVar2);
          if (iVar3 == 0) break;
LAB_10004d7e:
          memset(auStack_828,0,0x410);
          iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(iVar2,auStack_828);
        }
        (**(code **)(DAT_106b40a8 + 0x168))(iVar2);
      }
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_418);
    }
  }
  __security_check_cookie(local_4 ^ (uint)auStack_828);
  return;
}



/* FUN_1000db60 @ 1000db60 size 732 */

undefined4 FUN_1000db60(void)

{
  char cVar1;
  char *in_EAX;
  int iVar2;
  char *_Str;
  undefined1 *puVar3;
  undefined1 *puVar4;
  char *pcVar5;
  char *pcVar6;
  char *pcVar7;
  char *unaff_ESI;
  code *pcVar8;
  int iStack_c;
  
  memset(unaff_ESI,0,0xd04);
  _Str = unaff_ESI + 0x840;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x104))();
  if (iVar2 == 0) {
    return 0;
  }
  if (in_EAX == (char *)0x0) {
    FUN_10001e70();
  }
  strncpy(unaff_ESI,in_EAX,0x3f);
  unaff_ESI[0x3f] = '\0';
  unaff_ESI[0xd00] = '\0';
  unaff_ESI[0xd01] = '\0';
  unaff_ESI[0xd02] = '\0';
  unaff_ESI[0xd03] = '\0';
  *(char **)(unaff_ESI + 0x40) = "Address";
  *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x44) = &DAT_100239ab;
  *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x48) = &DAT_100239ab;
  *(char **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x4c) = unaff_ESI;
  *(int *)(unaff_ESI + 0xd00) = *(int *)(unaff_ESI + 0xd00) + 1;
  do {
    pcVar8 = strchr_exref;
    strchr_exref = pcVar8;
    if (((_Str == (char *)0x0) || (*_Str == '\0')) ||
       (_Str = strchr(_Str,0x5c), _Str == (char *)0x0)) break;
    *_Str = '\0';
    _Str = _Str + 1;
    if (*_Str == '\\') break;
    *(char **)(unaff_ESI + (*(int *)(unaff_ESI + 0xd00) + 4) * 0x10) = _Str;
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x44) = &DAT_100239ab;
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x48) = &DAT_100239ab;
    _Str = strchr(_Str,0x5c);
    if (_Str == (char *)0x0) break;
    *_Str = '\0';
    _Str = _Str + 1;
    *(char **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x4c) = _Str;
    *(int *)(unaff_ESI + 0xd00) = *(int *)(unaff_ESI + 0xd00) + 1;
  } while (*(int *)(unaff_ESI + 0xd00) < 0x80);
  if (*(int *)(unaff_ESI + 0xd00) < 0x7d) {
    *(undefined **)(unaff_ESI + (*(int *)(unaff_ESI + 0xd00) + 4) * 0x10) = &DAT_100239ab;
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x44) = &DAT_100239ab;
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x48) = &DAT_100239ab;
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x4c) = &DAT_100239ab;
    *(int *)(unaff_ESI + 0xd00) = *(int *)(unaff_ESI + 0xd00) + 1;
    *(undefined **)(unaff_ESI + (*(int *)(unaff_ESI + 0xd00) + 4) * 0x10) = &DAT_10027c14;
    *(char **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x44) = "score";
    *(undefined **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x48) = &DAT_10027c20;
    pcVar7 = (char *)0x0;
    *(undefined1 **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x4c) = &DAT_10025e84;
    *(int *)(unaff_ESI + 0xd00) = *(int *)(unaff_ESI + 0xd00) + 1;
    iStack_c = 0;
    if (_Str != (char *)0x0) {
      while (*_Str != '\0') {
        if (*_Str == '\\') {
          *_Str = '\0';
          _Str = _Str + 1;
        }
        if ((_Str == (char *)0x0) ||
           (puVar3 = (undefined1 *)(*pcVar8)(_Str,0x20), puVar3 == (undefined1 *)0x0)) break;
        *puVar3 = 0;
        puVar4 = (undefined1 *)(*pcVar8)(puVar3 + 1,0x20);
        if (puVar4 == (undefined1 *)0x0) break;
        *puVar4 = 0;
        pcVar5 = unaff_ESI + (int)(pcVar7 + 0xc40);
        FUN_10001830(pcVar5,0xc0 - (int)pcVar7,&DAT_10025d20,iStack_c);
        *(char **)(unaff_ESI + (*(int *)(unaff_ESI + 0xd00) + 4) * 0x10) = pcVar5;
        pcVar6 = pcVar5 + 1;
        do {
          cVar1 = *pcVar5;
          pcVar5 = pcVar5 + 1;
        } while (cVar1 != '\0');
        pcVar7 = pcVar5 + (int)(pcVar7 + (1 - (int)pcVar6));
        *(char **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x44) = _Str;
        *(undefined1 **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x48) = puVar3 + 1;
        *(undefined1 **)(unaff_ESI + *(int *)(unaff_ESI + 0xd00) * 0x10 + 0x4c) = puVar4 + 1;
        *(int *)(unaff_ESI + 0xd00) = *(int *)(unaff_ESI + 0xd00) + 1;
        if ((0x7f < *(int *)(unaff_ESI + 0xd00)) ||
           (pcVar6 = strchr(puVar4 + 1,0x5c), pcVar6 == (char *)0x0)) break;
        iStack_c = iStack_c + 1;
        _Str = pcVar6 + 1;
        *pcVar6 = '\0';
        pcVar8 = strchr_exref;
        if (_Str == (char *)0x0) break;
      }
    }
  }
  FUN_1000da60();
  return 1;
}



/* FUN_10013ba0 @ 10013ba0 size 718 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void __thiscall FUN_10013ba0(undefined4 param_1,void *param_2)

{
  undefined1 *puVar1;
  int *piVar2;
  undefined1 *puVar3;
  uint uVar4;
  char *pcVar5;
  int iVar6;
  int iVar7;
  double dVar8;
  undefined1 *puStack_4e38;
  float fStack_4e34;
  undefined4 local_4e30;
  int iStack_4e2c;
  undefined4 local_4e28;
  undefined1 auStack_4e24 [20000];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&puStack_4e38;
  local_4e28 = param_1;
  memset(param_2,0,0x2e8);
  uVar4 = (**(code **)(DAT_106b40a8 + 0x38))(param_1,&local_4e30,0);
  if (0 < (int)uVar4) {
    if (uVar4 < 19999) {
      (**(code **)(DAT_106b40a8 + 0x3c))(auStack_4e24,uVar4,local_4e30);
      auStack_4e24[uVar4] = 0;
      (**(code **)(DAT_106b40a8 + 0x44))(local_4e30);
      FUN_10001400(auStack_4e24);
      puVar1 = auStack_4e24;
      iStack_4e2c = 0;
      puStack_4e38 = puVar1;
      pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
      while (puVar3 = puStack_4e38, pcVar5 != (char *)0x0) {
        iVar6 = FUN_100016c0();
        if (iVar6 == 0) {
LAB_10013c9e:
          iVar6 = FUN_10001500(&puStack_4e38,1);
          puVar3 = puStack_4e38;
          if (iVar6 == 0) break;
        }
        else {
          iVar6 = FUN_100016c0();
          if (iVar6 == 0) {
            iVar6 = 0;
            do {
              iVar7 = FUN_10001500(&puStack_4e38,1);
              if (iVar7 == 0) break;
              iVar6 = iVar6 + 1;
            } while (iVar6 < 3);
          }
          else {
            iVar6 = FUN_100016c0();
            if (iVar6 == 0) goto LAB_10013c9e;
            if (('/' < *pcVar5) && (puVar3 = puVar1, *pcVar5 < ':')) break;
            FUN_10001ee0("unknown token \'%s\' is %s\n",pcVar5,param_1);
          }
        }
        puVar1 = puStack_4e38;
        pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
      }
      puStack_4e38 = puVar3;
      iVar6 = 0;
      do {
        pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
        if (pcVar5 == (char *)0x0) break;
        iVar7 = atoi(pcVar5);
        piVar2 = (int *)((int)param_2 + iVar6 * 0x18);
        *piVar2 = iVar7;
        if (iVar6 == 0xd) {
          iStack_4e2c = *(int *)((int)param_2 + 0x138) - *(int *)((int)param_2 + 0x90);
LAB_10013d87:
          *piVar2 = iVar7 - iStack_4e2c;
        }
        else if (0xc < iVar6) goto LAB_10013d87;
        pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
        if (pcVar5 == (char *)0x0) break;
        iVar7 = atoi(pcVar5);
        piVar2[1] = iVar7;
        pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
        if (pcVar5 == (char *)0x0) break;
        iVar7 = atoi(pcVar5);
        piVar2[2] = iVar7;
        pcVar5 = (char *)FUN_10001500(&puStack_4e38,1);
        if (pcVar5 == (char *)0x0) break;
        dVar8 = atof(pcVar5);
        fStack_4e34 = (float)dVar8;
        if (fStack_4e34 == 0.0) {
          fStack_4e34 = DAT_10029234;
        }
        iVar7 = FUN_10021270();
        iVar6 = iVar6 + 1;
        piVar2[3] = iVar7;
        piVar2[4] = iVar7;
      } while (iVar6 < 0x1f);
      if (iVar6 != 0x1f) {
        FUN_10001ee0("Error parsing animation file: %s",local_4e28);
        __security_check_cookie(local_4 ^ (uint)&puStack_4e38);
        return;
      }
      __security_check_cookie(local_4 ^ (uint)&puStack_4e38);
      return;
    }
    FUN_10001ee0("File %s too long\n",param_1);
  }
  __security_check_cookie(local_4 ^ (uint)&puStack_4e38);
  return;
}



/* FUN_10011c50 @ 10011c50 size 700 */

void FUN_10011c50(undefined *param_1)

{
  char cVar1;
  undefined *puVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  char *pcVar6;
  char *pcVar7;
  undefined4 uVar8;
  undefined4 *puVar9;
  int unaff_ESI;
  undefined **ppuVar10;
  char local_44 [10];
  undefined1 auStack_3a [54];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_44;
  *(undefined **)(unaff_ESI + 0x424) = param_1;
  *(undefined **)(unaff_ESI + 0x464) = param_1;
  *(undefined4 *)(unaff_ESI + 0x3f0) = 0;
  *(undefined4 *)(unaff_ESI + 0x3f4) = 0;
  *(undefined4 *)(unaff_ESI + 0x3f8) = 0;
  if (param_1 == (undefined *)0x0) {
LAB_10011efb:
    __security_check_cookie(local_4 ^ (uint)local_44);
    return;
  }
LAB_10011c90:
  ppuVar10 = &PTR_s_item_armor_shard_100241e0;
  puVar2 = PTR_s_item_armor_shard_100241e0;
  while (puVar2 != (undefined *)0x0) {
    if ((ppuVar10[0xd] == (undefined *)0x1) && (ppuVar10[0xe] == param_1)) {
      if (*ppuVar10 != (undefined *)0x0) {
        uVar8 = (**(code **)(DAT_106b40a8 + 0x54))(ppuVar10[2]);
        *(undefined4 *)(unaff_ESI + 0x3f0) = uVar8;
      }
      break;
    }
    ppuVar10 = ppuVar10 + 0x12;
    puVar2 = *ppuVar10;
  }
  if (*(int *)(unaff_ESI + 0x3f0) == 0) goto code_r0x10011cd8;
  if (((param_1 == (undefined *)0x2) || (param_1 == (undefined *)0x1)) ||
     (param_1 == (undefined *)0x9)) {
    pcVar6 = ppuVar10[2];
    iVar3 = -(int)pcVar6;
    do {
      cVar1 = *pcVar6;
      pcVar6[(int)(local_44 + iVar3)] = cVar1;
      pcVar6 = pcVar6 + 1;
    } while (cVar1 != '\0');
    pcVar6 = local_44;
    cVar1 = local_44[0];
    while ((cVar1 != '\0' && (cVar1 != '.'))) {
      *pcVar6 = cVar1;
      pcVar7 = pcVar6 + 1;
      pcVar6 = pcVar6 + 1;
      cVar1 = *pcVar7;
    }
    *pcVar6 = '\0';
    pcVar6 = &stack0xffffffbb;
    do {
      pcVar7 = pcVar6;
      pcVar6 = pcVar7 + 1;
    } while (pcVar7[1] != '\0');
    *(undefined4 *)(pcVar7 + 1) = s__barrel_md3_100281f8._0_4_;
    *(undefined4 *)(pcVar7 + 5) = s__barrel_md3_100281f8._4_4_;
    *(undefined4 *)(pcVar7 + 9) = s__barrel_md3_100281f8._8_4_;
    uVar8 = (**(code **)(DAT_106b40a8 + 0x54))(local_44);
    *(undefined4 *)(unaff_ESI + 0x3f4) = uVar8;
  }
  pcVar6 = ppuVar10[2];
  iVar3 = -(int)pcVar6;
  do {
    cVar1 = *pcVar6;
    pcVar6[(int)(local_44 + iVar3)] = cVar1;
    pcVar6 = pcVar6 + 1;
  } while (cVar1 != '\0');
  pcVar6 = local_44;
  while ((local_44[0] != '\0' && (local_44[0] != '.'))) {
    *pcVar6 = local_44[0];
    pcVar7 = pcVar6 + 1;
    pcVar6 = pcVar6 + 1;
    local_44[0] = *pcVar7;
  }
  *pcVar6 = '\0';
  puVar5 = (undefined4 *)&stack0xffffffbb;
  do {
    puVar9 = puVar5;
    puVar5 = (undefined4 *)((int)puVar9 + 1);
  } while (*(char *)((int)puVar9 + 1) != '\0');
  *(undefined4 *)((int)puVar9 + 1) = DAT_10028204;
  *(undefined4 *)((int)puVar9 + 5) = DAT_10028208;
  *(undefined2 *)((int)puVar9 + 9) = DAT_1002820c;
  *(undefined1 *)((int)puVar9 + 0xb) = DAT_1002820e;
  uVar8 = (**(code **)(DAT_106b40a8 + 0x54))(local_44);
  *(undefined4 *)(unaff_ESI + 0x3f8) = uVar8;
  uVar4 = DAT_10029364;
  uVar8 = DAT_10029234;
  switch(param_1) {
  case (undefined *)0x1:
  case (undefined *)0x6:
  case (undefined *)0x8:
  case (undefined *)0xa:
    *(undefined4 *)(unaff_ESI + 0x3fc) = DAT_10029364;
    *(undefined4 *)(unaff_ESI + 0x400) = uVar4;
    uVar8 = DAT_10029234;
    break;
  case (undefined *)0x2:
  case (undefined *)0x3:
    *(undefined4 *)(unaff_ESI + 0x3fc) = DAT_10029234;
    goto LAB_10011e52;
  case (undefined *)0x4:
    *(undefined4 *)(unaff_ESI + 0x3fc) = DAT_10029234;
    *(undefined4 *)(unaff_ESI + 0x400) = DAT_10029360;
    uVar8 = DAT_10029328;
    break;
  case (undefined *)0x5:
    *(undefined4 *)(unaff_ESI + 0x3fc) = DAT_10029234;
    uVar8 = DAT_1002935c;
    goto LAB_10011e52;
  case (undefined *)0x7:
    *(undefined4 *)(unaff_ESI + 0x3fc) = DAT_10029234;
    uVar8 = DAT_10029328;
LAB_10011e52:
    *(undefined4 *)(unaff_ESI + 0x400) = uVar8;
    uVar8 = 0;
    break;
  case (undefined *)0x9:
    *(undefined4 *)(unaff_ESI + 0x400) = DAT_10029360;
    goto LAB_10011eea;
  default:
    *(undefined4 *)(unaff_ESI + 0x400) = DAT_10029234;
LAB_10011eea:
    *(undefined4 *)(unaff_ESI + 0x3fc) = uVar8;
  }
  *(undefined4 *)(unaff_ESI + 0x404) = uVar8;
  goto LAB_10011efb;
code_r0x10011cd8:
  param_1 = (undefined *)(-(uint)(param_1 != (undefined *)0x2) & 2);
  *(undefined **)(unaff_ESI + 0x464) = param_1;
  *(undefined4 *)(unaff_ESI + 0x3f0) = 0;
  *(undefined4 *)(unaff_ESI + 0x3f4) = 0;
  *(undefined4 *)(unaff_ESI + 0x3f8) = 0;
  if (param_1 == (undefined *)0x0) {
    __security_check_cookie(local_4 ^ (uint)local_44);
    return;
  }
  goto LAB_10011c90;
}



/* FUN_1001d7b0 @ 1001d7b0 size 697 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_1001d7b0(int param_1,undefined4 *param_2)

{
  float fVar1;
  int iVar2;
  float10 fVar3;
  undefined1 auStack_2c [4];
  float fStack_28;
  float fStack_24;
  float fStack_20;
  undefined4 uStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_2c;
  if (param_2 != (undefined4 *)0x0) {
    if (((param_2[0x12] & 4) == 0) && (param_1 == 0)) {
      param_2[0x12] = param_2[0x12] & 0xffefffff;
      FUN_100155a0();
    }
    else if ((((param_2[0xf] == 0) && (param_2[0x10] == 0)) ||
             ((*(code **)(DAT_106b40d0 + 0x4c) == (code *)0x0 ||
              (iVar2 = (**(code **)(DAT_106b40d0 + 0x4c))(param_2[0xf],param_2[0x10]), iVar2 != 0)))
             ) && (fVar3 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))("web_browserActive"),
                  fVar3 == (float10)0)) {
      if (param_1 != 0) {
        param_2[0x12] = param_2[0x12] | 0x100000;
      }
      FUN_100155a0();
      FUN_100156b0();
      if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
        (**(code **)(DAT_106b40d0 + 0xd8))(param_2[0x42]);
      }
      if (param_2[0x41] != 0) {
        fStack_24 = (float)param_2[0x3e];
        if (fStack_24 <= _DAT_10029214) {
          (**(code **)(DAT_106b40d0 + 8))(0,0,DAT_10029398,DAT_10029394,param_2[0x3a]);
        }
        else {
          fStack_20 = (float)*(int *)(DAT_106b40d0 + 0x11f0c);
          fVar1 = ((fStack_24 -
                   (float)*(int *)(DAT_106b40d0 + 0x11f08) * ((float)param_2[0x3f] / fStack_20)) /
                  fStack_24) * (float)_DAT_10029278;
          fStack_28 = 1.0 - fVar1;
          (**(code **)(DAT_106b40d0 + 0xc))
                    (0,0,(float)*(int *)(DAT_106b40d0 + 0x11f08),fStack_20,fVar1,0,fStack_28,
                     0x3f800000,param_2[0x3a]);
        }
      }
      FUN_10014f00(param_2[0x48],param_2[0x47],(float)(int)param_2[0x46]);
      iVar2 = 0;
      if (0 < (int)param_2[0x43]) {
        do {
          if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
            (**(code **)(DAT_106b40d0 + 0xd8))(param_2[0x42]);
          }
          FUN_1001ced0();
          iVar2 = iVar2 + 1;
        } while (iVar2 < (int)param_2[0x43]);
      }
      if (DAT_106b40ec != 0) {
        uStack_10 = DAT_10029234;
        uStack_14 = DAT_10029234;
        uStack_1c = DAT_10029234;
        uStack_18 = 0;
        (**(code **)(DAT_106b40d0 + 0x28))
                  (*param_2,param_2[1],param_2[2],param_2[3],0x3f800000,&uStack_1c);
      }
      if (*(code **)(DAT_106b40d0 + 0xd8) != (code *)0x0) {
        (**(code **)(DAT_106b40d0 + 0xd8))(0);
      }
      __security_check_cookie(local_c ^ (uint)auStack_2c);
      return;
    }
  }
  __security_check_cookie(local_c ^ (uint)auStack_2c);
  return;
}



/* FUN_100093b0 @ 100093b0 size 688 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100093b0(undefined4 param_1,undefined4 param_2)

{
  float fVar1;
  float *unaff_ESI;
  char *pcVar2;
  int iVar3;
  int iVar4;
  float10 extraout_ST0;
  float10 fVar5;
  float local_514;
  float local_510;
  int local_50c;
  float local_508;
  undefined4 auStack_504 [64];
  char local_404 [1023];
  undefined1 local_5;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_514;
  FUN_10001900("VENDOR: %s",&DAT_10755a1c,0,0x1e,param_2);
  local_514 = *unaff_ESI + (float)_DAT_100292f0;
  FUN_10003ec0(local_514,unaff_ESI[1],0,param_1);
  FUN_10001900("VERSION: %s: %s",&DAT_10755e1c,&DAT_1075561c,0,0x1e,param_2);
  local_514 = *unaff_ESI + (float)_DAT_100292f0;
  FUN_10003ec0(local_514,unaff_ESI[1] + (float)_DAT_10029440,0,param_1);
  FUN_10001900("PIXELFORMAT: color(%d-bits) Z(%d-bits) stencil(%d-bits)",DAT_10758224,DAT_10758228,
               DAT_1075822c,0,0x1e,param_2);
  local_514 = *unaff_ESI + (float)_DAT_100292f0;
  FUN_10003ec0(local_514,unaff_ESI[1] + (float)_DAT_10029438,0,param_1);
  strncpy(local_404,&DAT_1075621c,0x3ff);
  local_514 = unaff_ESI[1];
  local_5 = 0;
  pcVar2 = local_404;
  local_50c = FUN_10021270();
  local_510 = (float)local_50c;
  fVar1 = 0.0;
  local_514 = 0.0;
  fVar5 = (float10)local_50c;
  if (fVar5 < (float10)unaff_ESI[3] + extraout_ST0) {
LAB_1000954e:
    if (*pcVar2 != '\0') {
      do {
        if (*pcVar2 != ' ') break;
        *pcVar2 = '\0';
        pcVar2 = pcVar2 + 1;
      } while (*pcVar2 != '\0');
      if (*pcVar2 != '\0') {
        if (*pcVar2 != ' ') {
          auStack_504[(int)fVar1] = pcVar2;
          fVar1 = (float)((int)fVar1 + 1);
          local_514 = fVar1;
        }
        do {
          if (*pcVar2 == ' ') break;
          pcVar2 = pcVar2 + 1;
        } while (*pcVar2 != '\0');
      }
      goto LAB_1000954e;
    }
  }
  iVar3 = 0;
  if (0 < (int)fVar1) {
    do {
      local_508 = *unaff_ESI + (float)_DAT_100292f0;
      FUN_10003ec0(local_508,(float)fVar5,0,param_1);
      iVar4 = iVar3 + 1;
      if (iVar4 < (int)local_514) {
        local_508 = unaff_ESI[2] * (float)_DAT_10029278 + *unaff_ESI;
        FUN_10003ec0(local_508,local_510,0,param_1);
        iVar4 = iVar3 + 2;
      }
      local_50c = local_50c + 10;
      local_510 = (float)local_50c;
      fVar5 = (float10)local_50c;
    } while ((fVar5 <= ((float10)unaff_ESI[3] + (float10)unaff_ESI[1]) - (float10)_DAT_10029428) &&
            (iVar3 = iVar4, iVar4 < (int)local_514));
  }
  __security_check_cookie(local_4 ^ (uint)&local_514);
  return;
}



/* FUN_10005ff0 @ 10005ff0 size 684 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10005ff0(undefined4 *param_1)

{
  char *pcVar1;
  int aiStack_298 [3];
  undefined4 uStack_28c;
  char acStack_288 [64];
  char acStack_248 [63];
  undefined1 uStack_209;
  undefined1 auStack_208 [256];
  char acStack_108 [255];
  undefined1 uStack_9;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)aiStack_298;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceRedTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_248,&DAT_10042f38,0x3f);
  uStack_209 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceRedTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_108,&DAT_10042f38,0xff);
  uStack_9 = 0;
  auStack_208[0] = 0;
  if (acStack_248[0] == '\0') goto LAB_10006283;
  if (DAT_106b40b8 == 0) {
    DAT_106b40b8 = 1;
    DAT_1002af3c = 1;
LAB_100060b0:
    auStack_208[0] = 0;
    memset(&DAT_10045740,0,0x47c);
    aiStack_298[2] = DAT_100294fc;
    aiStack_298[1] = 0;
    uStack_28c = 0;
    FUN_10014250(acStack_108,auStack_208);
    FUN_100142e0();
    DAT_1002af3c = 0;
  }
  else if (DAT_1002af3c != 0) goto LAB_100060b0;
  _DAT_10045ba8 = 1;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamHeadColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_10045bac = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_10045bac = aiStack_298[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamUpperColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_10045bb0 = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_10045bb0 = aiStack_298[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_teamLowerColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_10045bb4 = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_10045bb4 = aiStack_298[0];
  }
  FUN_10012d90(*param_1,param_1[1],param_1[2],param_1[3]);
LAB_10006283:
  __security_check_cookie(local_4 ^ (uint)aiStack_298);
  return;
}



/* FUN_100062a0 @ 100062a0 size 684 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100062a0(undefined4 *param_1)

{
  char *pcVar1;
  int aiStack_298 [3];
  undefined4 uStack_28c;
  char acStack_288 [64];
  char acStack_248 [63];
  undefined1 uStack_209;
  undefined1 auStack_208 [256];
  char acStack_108 [255];
  undefined1 uStack_9;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)aiStack_298;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceBlueTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_248,&DAT_10042f38,0x3f);
  uStack_209 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceBlueTeamModel",&DAT_10042f38,0x400);
  strncpy(acStack_108,&DAT_10042f38,0xff);
  uStack_9 = 0;
  auStack_208[0] = 0;
  if (acStack_248[0] == '\0') goto LAB_10006533;
  if (DAT_106b40bc == 0) {
    DAT_106b40bc = 1;
    DAT_1002af40 = 1;
LAB_10006360:
    auStack_208[0] = 0;
    memset(&DAT_10045bc0,0,0x47c);
    aiStack_298[2] = DAT_100294fc;
    aiStack_298[1] = 0;
    uStack_28c = 0;
    FUN_10014250(acStack_108,auStack_208);
    FUN_100142e0();
    DAT_1002af40 = 0;
  }
  else if (DAT_1002af40 != 0) goto LAB_10006360;
  _DAT_10046028 = 1;
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyHeadColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_1004602c = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_1004602c = aiStack_298[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyUpperColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_10046030 = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_10046030 = aiStack_298[0];
  }
  (**(code **)(DAT_106b40a8 + 0x24))("cg_enemyLowerColor",acStack_288,0x40);
  pcVar1 = strstr(acStack_288,"0x");
  if (pcVar1 == (char *)0x0) {
    _DAT_10046034 = atoi(acStack_288);
  }
  else {
    aiStack_298[0] = 0;
    sscanf(acStack_288,"0x%08x",aiStack_298);
    _DAT_10046034 = aiStack_298[0];
  }
  FUN_10012d90(*param_1,param_1[1],param_1[2],param_1[3]);
LAB_10006533:
  __security_check_cookie(local_4 ^ (uint)aiStack_298);
  return;
}



/* FUN_1000ae50 @ 1000ae50 size 632 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1000ae50(void)

{
  int iVar1;
  int iVar2;
  int unaff_ESI;
  float10 fVar3;
  
  (**(code **)(DAT_106b40a8 + 0x28))();
  iVar1 = FUN_10021270();
  if (unaff_ESI != 0) {
    iVar2 = FUN_100016c0();
    if (iVar2 == 0) {
      (**(code **)(DAT_106b40a8 + 0x24))("ui_Name",&DAT_10042f38,0x400);
      (**(code **)(DAT_106b40a8 + 0x1c))(&DAT_10025e84,&DAT_10042f38);
      return;
    }
    iVar2 = FUN_100016c0();
    if (iVar2 == 0) {
      fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))(&DAT_10027284);
      if (_DAT_10029408 <= (float)fVar3) {
        (**(code **)(DAT_106b40a8 + 0x1c))("cl_maxpackets",&DAT_1002648c);
        (**(code **)(DAT_106b40a8 + 0x1c))("cl_packetdup",&DAT_1002729c);
        return;
      }
      if ((float)_DAT_10029400 <= (float)fVar3) {
        (**(code **)(DAT_106b40a8 + 0x1c))();
        (**(code **)(DAT_106b40a8 + 0x1c))("cl_packetdup",&DAT_100272b0);
        return;
      }
      (**(code **)(DAT_106b40a8 + 0x1c))("cl_maxpackets",&DAT_10026480);
      (**(code **)(DAT_106b40a8 + 0x1c))("cl_packetdup",&DAT_1002729c);
      return;
    }
    iVar2 = FUN_100016c0();
    if (iVar2 == 0) {
      (**(code **)(DAT_106b40a8 + 0x24))(&DAT_10025e84,&DAT_10042f38,0x400);
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_Name",&DAT_10042f38);
      return;
    }
    iVar2 = FUN_100016c0();
    if (iVar2 == 0) {
      if (iVar1 == 0) {
        (**(code **)(DAT_106b40a8 + 0x1c))("r_depthBits",&DAT_100252c0);
        (**(code **)(DAT_106b40a8 + 0x1c))("r_stencilBits",&DAT_100252c0);
        return;
      }
      if (iVar1 == 0x10) {
        (**(code **)(DAT_106b40a8 + 0x1c))("r_depthBits",&DAT_100272e8);
        (**(code **)(DAT_106b40a8 + 0x1c))("r_stencilBits",&DAT_100252c0);
        return;
      }
      if (iVar1 == 0x20) {
        (**(code **)(DAT_106b40a8 + 0x1c))("r_depthBits",&DAT_100272ec);
        return;
      }
    }
    else {
      iVar2 = FUN_100016c0();
      if (iVar2 == 0) {
        if (iVar1 == 0) {
          (**(code **)(DAT_106b40a8 + 0x1c))("m_pitch","0.022");
          return;
        }
        (**(code **)(DAT_106b40a8 + 0x1c))("m_pitch","-0.022");
      }
    }
  }
  return;
}



/* FUN_1001a150 @ 1001a150 size 628 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_1001a150(int param_1,undefined4 *param_2)

{
  int iVar1;
  int iVar2;
  float10 fVar3;
  undefined1 auStack_20 [4];
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  uint local_4;
  
  iVar2 = DAT_106b40d0;
  local_4 = DAT_1002a000 ^ (uint)auStack_20;
  iVar1 = *(int *)(param_1 + 0x134);
  local_1c = *(float *)(iVar1 + 0x11c);
  local_18 = *(float *)(iVar1 + 0x120);
  if (((*(byte *)(param_1 + 0x48) & 0x60) != 0) &&
     (*(int *)(param_1 + 0x74) < *(int *)(DAT_106b40d0 + 0xe8))) {
    *(int *)(param_1 + 0x74) = *(int *)(iVar1 + 0x118) + *(int *)(DAT_106b40d0 + 0xe8);
    if ((*(byte *)(param_1 + 0x48) & 0x20) == 0) {
      local_18 = local_18 + *(float *)(param_1 + 0x84);
      *(float *)(param_1 + 0x84) = local_18;
      if (local_1c <= local_18) {
        *(float *)(param_1 + 0x84) = local_1c;
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xffffffbf;
      }
    }
    else {
      local_18 = *(float *)(param_1 + 0x84) - local_18;
      *(float *)(param_1 + 0x84) = local_18;
      if (local_18 <= 0.0) {
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xffffffdb;
      }
    }
  }
  if ((*(byte *)(param_1 + 0x48) & 2) == 0) {
    if ((*(int *)(param_1 + 300) == 1) && (iVar2 = *(int *)(iVar2 + 0xe8), (iVar2 / 200 & 1U) == 0))
    {
      local_8 = (float)_DAT_10029448;
      local_14 = *(float *)(param_1 + 0x78) * local_8;
      local_10 = *(float *)(param_1 + 0x7c) * local_8;
      local_1c = (float)(iVar2 / 0x4b);
      local_c = *(float *)(param_1 + 0x80) * local_8;
      local_8 = local_8 * *(float *)(param_1 + 0x84);
      fVar3 = (float10)_CIsin();
      local_1c = (float)((float10)_DAT_10029278 + fVar3 * (float10)_DAT_10029278);
      FUN_100147a0(local_1c);
    }
    else {
      *param_2 = *(undefined4 *)(param_1 + 0x78);
      param_2[1] = *(undefined4 *)(param_1 + 0x7c);
      param_2[2] = *(undefined4 *)(param_1 + 0x80);
      param_2[3] = *(undefined4 *)(param_1 + 0x84);
    }
  }
  else {
    local_8 = (float)_DAT_10029448;
    local_14 = *(float *)(iVar1 + 0x134) * local_8;
    local_10 = *(float *)(iVar1 + 0x138) * local_8;
    local_1c = (float)(*(int *)(iVar2 + 0xe8) / 0x4b);
    local_c = *(float *)(iVar1 + 0x13c) * local_8;
    local_8 = local_8 * *(float *)(iVar1 + 0x140);
    fVar3 = (float10)_CIsin();
    local_1c = (float)((float10)_DAT_10029278 + fVar3 * (float10)_DAT_10029278);
    FUN_100147a0(local_1c);
  }
  if (((((int *)(param_1 + 0x16c) != (int *)0x0) && (*(int *)(param_1 + 0x16c) != 0)) &&
      (*(char **)(param_1 + 0x15c) != (char *)0x0)) &&
     ((**(char **)(param_1 + 0x15c) != '\0' && ((*(byte *)(param_1 + 0x17c) & 3) != 0)))) {
    iVar2 = FUN_10016e70(1);
    if (iVar2 == 0) {
      *param_2 = *(undefined4 *)(iVar1 + 0x144);
      param_2[1] = *(undefined4 *)(iVar1 + 0x148);
      param_2[2] = *(undefined4 *)(iVar1 + 0x14c);
      param_2[3] = *(undefined4 *)(iVar1 + 0x150);
    }
  }
  __security_check_cookie(local_4 ^ (uint)auStack_20);
  return;
}



/* FUN_10010660 @ 10010660 size 622 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10010660(float param_1,float param_2,float param_3,float param_4,float param_5,
                 char *param_6)

{
  char *pcVar1;
  char cVar2;
  char *pcVar3;
  char *pcVar4;
  char *pcVar5;
  float local_438;
  int iStack_434;
  int iStack_430;
  float local_42c [2];
  float fStack_424;
  float afStack_418 [2];
  float fStack_410;
  char local_404 [1023];
  undefined1 local_5;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_438;
  if ((param_6 != (char *)0x0) && (*param_6 != '\0')) {
    strncpy(local_404,param_6,0x3ff);
    pcVar4 = local_404;
    local_5 = 0;
    pcVar3 = pcVar4;
    pcVar5 = pcVar4;
LAB_100106b4:
    do {
      pcVar1 = pcVar4 + 1;
      pcVar4 = pcVar4 + 1;
      if (*pcVar1 != ' ') {
        if (*pcVar1 != '\0') goto LAB_100106b4;
      }
      cVar2 = *pcVar4;
      *pcVar4 = '\0';
      if (DAT_106b40a4 == _DAT_10029214) {
        DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
      }
      local_438 = DAT_106b40a4 * param_5;
      if (pcVar5 != (char *)0x0) {
        (**(code **)(DAT_106b40a8 + 0x17c))(pcVar5,0,0,local_438,0xffffffff,local_42c);
        local_438 = (fStack_424 - local_42c[0]) / _DAT_10746420;
        iStack_430 = (int)local_438;
      }
      *pcVar4 = cVar2;
      if (param_3 < (float)iStack_430) {
        if (pcVar5 == pcVar3) {
          pcVar3 = pcVar4;
        }
        *pcVar3 = '\0';
        if (DAT_106b40a4 == _DAT_10029214) {
          DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
        }
        local_438 = DAT_106b40a4 * param_5;
        if (pcVar5 != (char *)0x0) {
          (**(code **)(DAT_106b40a8 + 0x17c))(pcVar5,0,0,local_438,0xffffffff,afStack_418);
          iStack_434 = (int)((fStack_410 - afStack_418[0]) / _DAT_10746420);
        }
        local_438 = param_1 - (float)(iStack_434 / 2);
        FUN_10003ec0(local_438,param_2,0,param_5,&DAT_1002be24,pcVar5,0,0,6);
        param_2 = param_2 + param_4;
        if (cVar2 == '\0') {
          if (pcVar3[1] == '\0') goto LAB_100108ae;
          break;
        }
        pcVar4 = pcVar3 + 1;
        pcVar3 = pcVar4;
        pcVar5 = pcVar4;
        goto LAB_100106b4;
      }
      pcVar3 = pcVar4;
    } while (cVar2 != '\0');
    FUN_100105f0(param_1,param_2,param_5);
  }
LAB_100108ae:
  __security_check_cookie(local_4 ^ (uint)&local_438);
  return;
}



/* FUN_10009080 @ 10009080 size 609 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10009080(undefined4 param_1,undefined4 param_2)

{
  float fVar1;
  float fVar2;
  int iVar3;
  float *unaff_EBX;
  int iVar4;
  float10 fVar5;
  float10 extraout_ST0;
  
  iVar3 = DAT_107644b8;
  if (DAT_107644b8 != 0) {
    if (DAT_107644bc == -1) {
      DAT_107644bc = 0;
      DAT_107644c0 = FUN_10021270();
      DAT_107644c4 = -1;
    }
    iVar4 = DAT_107644c8;
    if (iVar3 < DAT_107644c8) {
      DAT_107644c8 = 0;
      DAT_107644c0 = FUN_10021270();
      DAT_107644c4 = -1;
      iVar4 = 0;
    }
    fVar5 = (float10)_DAT_100292f0;
    if (DAT_107644cc < DAT_10746428) {
      fVar1 = *unaff_EBX;
      DAT_107644cc = DAT_10746428 + 10;
      if ((float10)fVar1 + fVar5 < (float10)DAT_107644c0) {
        DAT_107644c0 = DAT_107644c0 + -2;
        if (-1 < DAT_107644c4) {
          DAT_107644c4 = DAT_107644c4 + -2;
        }
      }
      else if (iVar4 < iVar3) {
        FUN_10003d90(0,param_1);
        fVar5 = (float10)_DAT_100292f0;
        DAT_107644c0 = DAT_107644c0 + -1 + (int)fVar1;
        iVar4 = DAT_107644c8 + 1;
        DAT_107644c8 = iVar4;
      }
      else {
        iVar4 = 0;
        DAT_107644c8 = 0;
        if (DAT_107644c4 < 0) {
          DAT_107644c0 = FUN_10021270();
          DAT_107644c4 = -1;
          fVar5 = extraout_ST0;
        }
        else {
          DAT_107644c0 = DAT_107644c4;
          DAT_107644c4 = -1;
        }
      }
    }
    fVar1 = *unaff_EBX;
    fVar2 = unaff_EBX[2];
    if ((int)&DAT_107644d0 + iVar4 != 0) {
      FUN_10004280((float)DAT_107644c0,(unaff_EBX[3] + unaff_EBX[1]) - (float)_DAT_10029268,param_1,
                   param_2,(int)&DAT_107644d0 + iVar4);
      iVar4 = DAT_107644c8;
    }
    if (-1 < DAT_107644c4) {
      FUN_10004280((float)DAT_107644c4,(unaff_EBX[3] + unaff_EBX[1]) - (float)_DAT_10029268,param_1,
                   param_2,&DAT_107644d0);
      iVar4 = DAT_107644c8;
    }
    if ((iVar4 == 0) || ((float)(((float10)fVar1 + (float10)fVar2) - fVar5) <= _DAT_10029214)) {
      DAT_107644c4 = -1;
    }
    else if (DAT_107644c4 == -1) {
      DAT_107644c4 = FUN_10021270();
      return;
    }
  }
  return;
}



/* FUN_1001a3d0 @ 1001a3d0 size 600 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_1001a3d0(float *param_1)

{
  char cVar1;
  float fVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  int iStack_834;
  int iStack_830;
  int local_82c;
  float fStack_828;
  char *local_824;
  int iStack_820;
  undefined1 local_81c [16];
  char acStack_80c [1024];
  char local_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)&iStack_834;
  pcVar3 = (char *)param_1[0x4c];
  local_82c = 0;
  local_824 = (char *)0x0;
  if (pcVar3 == (char *)0x0) {
    if (param_1[0x56] == 0.0) goto LAB_1001a60f;
    (**(code **)(DAT_106b40d0 + 0x58))(param_1[0x56],local_40c,0x400);
    pcVar3 = local_40c;
  }
  if (*pcVar3 != '\0') {
    FUN_1001a150(local_81c);
    FUN_10019f10(pcVar3);
    fStack_828 = param_1[0x48];
    acStack_80c[0] = '\0';
    iStack_834 = 0;
    iStack_830 = 0;
    iVar4 = 0;
    do {
      cVar1 = *pcVar3;
      if ((((cVar1 == ' ') || (cVar1 == '\t')) || (cVar1 == '\n')) || (cVar1 == '\0')) {
        local_824 = pcVar3 + 1;
        iStack_830 = local_82c;
        iStack_834 = iVar4;
      }
      local_82c = (**(code **)(DAT_106b40d0 + 0x14))(acStack_80c,param_1[0x49],param_1[0x4a],0);
      iVar5 = iStack_834;
      if (((iStack_834 != 0) && (param_1[2] < (float)local_82c)) ||
         ((cVar1 = *pcVar3, cVar1 == '\n' || (cVar1 == '\0')))) {
        if (iVar4 != 0) {
          fVar2 = param_1[0x46];
          if (fVar2 == 0.0) {
            fVar2 = param_1[0x47];
LAB_1001a53d:
            param_1[0x40] = fVar2;
          }
          else {
            if (fVar2 == 2.8026e-45) {
              fVar2 = param_1[0x47] - (float)iStack_830;
              goto LAB_1001a53d;
            }
            if (fVar2 == 1.4013e-45) {
              iStack_834 = iStack_830 / 2;
              fVar2 = param_1[0x47] - (float)iStack_834;
              goto LAB_1001a53d;
            }
          }
          param_1[0x41] = fStack_828;
          if (param_1[0xd] != 0.0) {
            param_1[0x40] = param_1[0x11] + param_1[0x40];
            param_1[0x41] = param_1[0x11] + param_1[0x41];
          }
          fVar2 = param_1[0x40];
          acStack_80c[iVar5] = '\0';
          param_1[0x40] = fVar2 + *param_1;
          param_1[0x41] = param_1[1] + param_1[0x41];
          (**(code **)(DAT_106b40d0 + 0x10))
                    (param_1[0x40],param_1[0x41],param_1[0x49],param_1[0x4a],local_81c,acStack_80c,0
                     ,0,param_1[0x4b]);
        }
        if (*pcVar3 == '\0') break;
        iVar5 = 0;
        iStack_834 = 0;
        iStack_830 = 0;
        fStack_828 = (float)iStack_820 * (float)_DAT_10029508 + fStack_828;
        pcVar3 = local_824;
      }
      else {
        acStack_80c[iVar4] = cVar1;
        iVar5 = iVar4 + 1;
        acStack_80c[iVar4 + 1] = '\0';
        pcVar3 = pcVar3 + 1;
      }
      iVar4 = iVar5;
    } while (pcVar3 != (char *)0x0);
  }
LAB_1001a60f:
  __security_check_cookie(local_8 ^ (uint)&iStack_834);
  return;
}



/* FUN_1001a8e0 @ 1001a8e0 size 587 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001a8e0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int unaff_ESI;
  float10 fVar5;
  float fStack_438;
  undefined4 *puStack_434;
  float local_430;
  undefined4 uStack_42c;
  undefined4 uStack_428;
  undefined4 uStack_424;
  undefined4 uStack_420;
  float local_41c;
  float local_418;
  float fStack_414;
  float fStack_410;
  undefined1 local_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)&fStack_438;
  iVar1 = *(int *)(unaff_ESI + 0x288);
  FUN_1001a7e0();
  local_40c[0] = 0;
  if (*(int *)(unaff_ESI + 0x158) != 0) {
    (**(code **)(DAT_106b40d0 + 0x58))(*(int *)(unaff_ESI + 0x158),local_40c,0x400);
  }
  iVar3 = DAT_106b40d0;
  iVar2 = *(int *)(unaff_ESI + 0x134);
  local_430 = (float)(*(uint *)(unaff_ESI + 0x48) & 2);
  if (local_430 == 0.0) {
    uStack_42c = *(undefined4 *)(unaff_ESI + 0x78);
    uStack_428 = *(undefined4 *)(unaff_ESI + 0x7c);
    uStack_424 = *(undefined4 *)(unaff_ESI + 0x80);
    uStack_420 = *(undefined4 *)(unaff_ESI + 0x84);
  }
  else {
    fStack_410 = (float)_DAT_10029448;
    local_41c = *(float *)(iVar2 + 0x134) * fStack_410;
    local_418 = *(float *)(iVar2 + 0x138) * fStack_410;
    fStack_414 = *(float *)(iVar2 + 0x13c) * fStack_410;
    fStack_410 = fStack_410 * *(float *)(iVar2 + 0x140);
    fStack_438 = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fVar5 = (float10)_CIsin();
    fStack_438 = (float)((float10)_DAT_10029278 + fVar5 * (float10)_DAT_10029278);
    FUN_100147a0(fStack_438);
  }
  if ((*(char **)(unaff_ESI + 0x130) == (char *)0x0) ||
     (fStack_438 = 1.12104e-44, **(char **)(unaff_ESI + 0x130) == '\0')) {
    fStack_438 = 0.0;
  }
  if ((local_430 != 0.0) && (DAT_106b40d8 != 0)) {
    iVar2 = *(int *)(iVar1 + 0x18);
    puStack_434 = (undefined4 *)(iVar3 + 0x68);
    uVar4 = (**(code **)(iVar3 + 0x70))
                      (*(undefined4 *)(iVar1 + 0x14),*(undefined4 *)(unaff_ESI + 300));
    local_430 = *(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) +
                (float)(int)fStack_438;
    (*(code *)*puStack_434)
              (local_430,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
               *(undefined4 *)(unaff_ESI + 0x128),&uStack_42c,local_40c + iVar2,
               *(int *)(unaff_ESI + 0x284) - iVar2,uVar4);
    __security_check_cookie(local_8 ^ (uint)&fStack_438);
    return;
  }
  puStack_434 = (undefined4 *)
                (*(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) +
                (float)(int)fStack_438);
  (**(code **)(iVar3 + 0x10))
            (puStack_434,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
             *(undefined4 *)(unaff_ESI + 0x128),&uStack_42c,local_40c + *(int *)(iVar1 + 0x18),0,
             *(undefined4 *)(iVar1 + 0x14),*(undefined4 *)(unaff_ESI + 300));
  __security_check_cookie(local_8 ^ (uint)&fStack_438);
  return;
}



/* FUN_1001b9e0 @ 1001b9e0 size 583 */

undefined4 __thiscall FUN_1001b9e0(float *param_1,int param_2,int param_3)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int unaff_EBX;
  
  if ((((param_1 == (float *)0x0) || ((float)*(int *)(DAT_106b40d0 + 0xf0) <= *param_1)) ||
      (param_1[2] + *param_1 <= (float)*(int *)(DAT_106b40d0 + 0xf0))) ||
     (((float)*(int *)(DAT_106b40d0 + 0xf4) <= param_1[1] ||
      (param_1[3] + param_1[1] <= (float)*(int *)(DAT_106b40d0 + 0xf4))))) {
    if (DAT_106b40d4 == 0) {
      return 1;
    }
  }
  else if (DAT_106b40d4 == 0) {
    if (param_2 == 0) {
      return 1;
    }
    if ((unaff_EBX != 0xb2) && (unaff_EBX != 0xd)) {
      return 1;
    }
    DAT_106b40d4 = 1;
    DAT_106b40dc = param_1;
    return 1;
  }
  if (DAT_106b40dc == (float *)0x0) {
    return 1;
  }
  if (param_3 != 0) {
    return 1;
  }
  if (unaff_EBX == 0x1b) {
    DAT_106b40d4 = 0;
    return 1;
  }
  if (unaff_EBX == 0x60) {
    return 1;
  }
  if (unaff_EBX == 0x7f) {
    iVar3 = FUN_1001b250();
    if (iVar3 != -1) {
      (&DAT_1002a0e0)[iVar3 * 6] = 0xffffffff;
      (&DAT_1002a0e4)[iVar3 * 6] = 0xffffffff;
    }
    FUN_1001b1e0();
    DAT_106b40d4 = 0;
    DAT_106b40dc = (float *)0x0;
    return 1;
  }
  if (unaff_EBX != -1) {
    piVar2 = &DAT_1002a0e4;
    do {
      if (*piVar2 == unaff_EBX) {
        *piVar2 = -1;
      }
      if (piVar2[-1] == unaff_EBX) {
        piVar2[-1] = *piVar2;
        *piVar2 = -1;
      }
      piVar2 = piVar2 + 6;
    } while ((int)piVar2 < 0x1002a87c);
  }
  iVar3 = FUN_1001b250();
  if (iVar3 == -1) goto LAB_1001bbb8;
  iVar1 = (&DAT_1002a0e0)[iVar3 * 6];
  if (unaff_EBX == -1) {
    if (iVar1 != -1) {
      (**(code **)(DAT_106b40d0 + 0x94))(iVar1,&DAT_100239ab);
      (&DAT_1002a0e0)[iVar3 * 6] = 0xffffffff;
    }
    if ((&DAT_1002a0e4)[iVar3 * 6] == -1) goto LAB_1001bbb8;
    (**(code **)(DAT_106b40d0 + 0x94))((&DAT_1002a0e4)[iVar3 * 6],&DAT_100239ab);
  }
  else {
    if (iVar1 == -1) {
      (&DAT_1002a0e0)[iVar3 * 6] = unaff_EBX;
      goto LAB_1001bbb8;
    }
    if ((iVar1 != unaff_EBX) && ((&DAT_1002a0e4)[iVar3 * 6] == -1)) {
      (&DAT_1002a0e4)[iVar3 * 6] = unaff_EBX;
      goto LAB_1001bbb8;
    }
    (**(code **)(DAT_106b40d0 + 0x94))(iVar1,&DAT_100239ab);
    (**(code **)(DAT_106b40d0 + 0x94))((&DAT_1002a0e4)[iVar3 * 6],&DAT_100239ab);
    (&DAT_1002a0e0)[iVar3 * 6] = unaff_EBX;
  }
  (&DAT_1002a0e4)[iVar3 * 6] = 0xffffffff;
LAB_1001bbb8:
  FUN_1001b1e0();
  DAT_106b40d4 = 0;
  return 1;
}



/* FUN_10002e20 @ 10002e20 size 576 */

void FUN_10002e20(undefined4 param_1,int param_2)

{
  char *pcVar1;
  byte bVar2;
  char cVar3;
  byte *pbVar4;
  int iVar5;
  char *pcVar6;
  char *pcVar7;
  byte *pbVar8;
  undefined *puVar9;
  byte *pbVar10;
  int iVar11;
  bool bVar12;
  undefined4 local_80c;
  int local_808;
  char local_804 [1024];
  char local_404 [1023];
  undefined1 local_5;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_80c;
  local_80c = param_1;
  iVar11 = 0;
  pbVar4 = (byte *)FUN_10001500(&local_80c,1);
  bVar2 = *pbVar4;
  do {
    if (bVar2 == 0) {
LAB_1000304b:
      __security_check_cookie(local_4 ^ (uint)&local_80c);
      return;
    }
    pbVar8 = &DAT_10025cc4;
    do {
      bVar2 = *pbVar4;
      bVar12 = bVar2 < *pbVar8;
      if (bVar2 != *pbVar8) {
LAB_10002e85:
        iVar5 = (1 - (uint)bVar12) - (uint)(bVar12 != 0);
        goto LAB_10002e8a;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar4[1];
      bVar12 = bVar2 < pbVar8[1];
      if (bVar2 != pbVar8[1]) goto LAB_10002e85;
      pbVar4 = pbVar4 + 2;
      pbVar8 = pbVar8 + 2;
    } while (bVar2 != 0);
    iVar5 = 0;
LAB_10002e8a:
    if (iVar5 != 0) {
      pcVar6 = "Missing { in info file\n";
LAB_10003041:
      FUN_10001ee0(pcVar6);
      goto LAB_1000304b;
    }
    if (iVar11 == param_2) {
      pcVar6 = "Max infos exceeded\n";
      goto LAB_10003041;
    }
    local_804[0] = '\0';
    pbVar4 = (byte *)FUN_10001500(&local_80c,1);
    bVar2 = *pbVar4;
    while (bVar2 != 0) {
      pbVar10 = &DAT_10025d14;
      pbVar8 = pbVar4;
      do {
        bVar2 = *pbVar8;
        bVar12 = bVar2 < *pbVar10;
        if (bVar2 != *pbVar10) {
LAB_10002ee7:
          iVar5 = (1 - (uint)bVar12) - (uint)(bVar12 != 0);
          goto LAB_10002eec;
        }
        if (bVar2 == 0) break;
        bVar2 = pbVar8[1];
        bVar12 = bVar2 < pbVar10[1];
        if (bVar2 != pbVar10[1]) goto LAB_10002ee7;
        pbVar8 = pbVar8 + 2;
        pbVar10 = pbVar10 + 2;
      } while (bVar2 != 0);
      iVar5 = 0;
LAB_10002eec:
      if (iVar5 == 0) goto LAB_10002f78;
      strncpy(local_404,(char *)pbVar4,0x3ff);
      local_5 = 0;
      pcVar6 = (char *)FUN_10001500(&local_80c,0);
      if (*pcVar6 == '\0') {
        *(undefined4 *)pcVar6 = DAT_10025d18;
        *(undefined2 *)(pcVar6 + 4) = DAT_10025d1c;
        pcVar6[6] = DAT_10025d1e;
      }
      FUN_10001b80(local_804);
      pbVar4 = (byte *)FUN_10001500(&local_80c,1);
      bVar2 = *pbVar4;
    }
    FUN_10001ee0("Unexpected end of info file\n");
LAB_10002f78:
    pcVar6 = local_804;
    do {
      cVar3 = *pcVar6;
      pcVar6 = pcVar6 + 1;
    } while (cVar3 != '\0');
    pcVar7 = (char *)FUN_10001900(&DAT_10025d20,0x400);
    pcVar1 = pcVar7 + 1;
    do {
      cVar3 = *pcVar7;
      pcVar7 = pcVar7 + 1;
    } while (cVar3 != '\0');
    pcVar6 = pcVar6 + (int)(pcVar7 + ((6 - (int)pcVar1) - (int)(local_804 + 1)));
    if ((int)(pcVar6 + DAT_10050054) < 0x600001) {
      puVar9 = &DAT_10053058 + DAT_10050054;
      DAT_10050054 = DAT_10050054 + ((uint)(pcVar6 + 0xf) & 0xfffffff0);
    }
    else {
      DAT_106b3058 = 1;
      FUN_10001e70(0,"UI_Alloc: Failure. Out of memory! allocpoint: %i, sz: %i, MEM_POOL_SIZE: %i",
                   DAT_10050054,pcVar6,0x600000);
      puVar9 = (undefined *)0x0;
    }
    *(undefined **)(local_808 + iVar11 * 4) = puVar9;
    if (puVar9 != (undefined *)0x0) {
      pcVar6 = local_804;
      iVar5 = (int)puVar9 - (int)pcVar6;
      do {
        cVar3 = *pcVar6;
        pcVar6[iVar5] = cVar3;
        pcVar6 = pcVar6 + 1;
      } while (cVar3 != '\0');
      iVar11 = iVar11 + 1;
    }
    pbVar4 = (byte *)FUN_10001500(&local_80c,1);
    bVar2 = *pbVar4;
  } while( true );
}



/* FUN_10006c60 @ 10006c60 size 562 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_10006c60(float *param_1)

{
  code *pcVar1;
  int iVar2;
  float *unaff_EDI;
  float10 fVar3;
  float fVar4;
  float fStack00000004;
  float fStack_18;
  float fStack_14;
  float fStack_10;
  float fStack_c;
  undefined4 uStack_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&fStack_18;
  if ((-1 < DAT_10766ae8) && (DAT_10766ae8 < 0x1e)) {
    if (DAT_10766ae8 != 0) {
      fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairHealth");
      if (fVar3 == (float10)0) {
        fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairColor");
        if (((float10)0 <= fVar3 - (float10)_DAT_10029228) &&
           (fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairColor"),
           fVar3 - (float10)_DAT_10029228 <= (float10)_DAT_100293f8)) {
          (**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairColor");
        }
        iVar2 = FUN_10021270();
        iVar2 = iVar2 * 0x10;
        fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairBrightness");
        fStack_14 = (float)(fVar3 * (float10)*(float *)(&DAT_1002bbf0 + iVar2));
        fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairBrightness");
        fStack_10 = (float)(fVar3 * (float10)*(float *)(&DAT_1002bbf4 + iVar2));
        fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairBrightness");
        param_1 = &fStack_14;
        fStack_c = (float)(fVar3 * (float10)*(float *)(&DAT_1002bbf8 + iVar2));
        uStack_8 = DAT_10029234;
      }
      else {
        fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairBrightness");
        pcVar1 = *(code **)(DAT_106b40a8 + 0x28);
        *param_1 = (float)(fVar3 * (float10)*param_1);
        fVar3 = (float10)(*pcVar1)("cg_crosshairBrightness");
        pcVar1 = *(code **)(DAT_106b40a8 + 0x28);
        param_1[1] = (float)(fVar3 * (float10)param_1[1]);
        fVar3 = (float10)(*pcVar1)("cg_crosshairBrightness");
        param_1[2] = (float)(fVar3 * (float10)param_1[2]);
      }
      (**(code **)(DAT_106b40a8 + 0x74))(param_1);
      fVar3 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairSize");
      fStack00000004 = (float)fVar3;
      fVar4 = DAT_100293c8;
      if ((DAT_100293c8 < fStack00000004) || (fVar4 = DAT_10029450, fStack00000004 < DAT_10029450))
      {
        fStack00000004 = fVar4;
      }
      fStack_18 = *unaff_EDI - (float)_DAT_100292f0;
      FUN_10002c50(fStack_18,(unaff_EDI[1] - unaff_EDI[3]) + (float)_DAT_100292f0,fStack00000004,
                   fStack00000004,*(undefined4 *)(&DAT_107555a4 + DAT_10766ae8 * 4));
      (**(code **)(DAT_106b40a8 + 0x74))(0);
    }
    __security_check_cookie(local_4 ^ (uint)&fStack_18);
    return;
  }
  DAT_10766ae8 = 0;
  __security_check_cookie(local_4 ^ (uint)&fStack_18);
  return;
}



/* FUN_10019f10 @ 10019f10 size 561 */

void FUN_10019f10(float param_1)

{
  float fVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  int *unaff_EBX;
  float *unaff_ESI;
  int *unaff_EDI;
  float fStack_10c;
  float fStack_108;
  undefined1 auStack_104 [256];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&fStack_10c;
  if (param_1 == 0.0) {
    param_1 = unaff_ESI[0x4c];
  }
  if (param_1 == 0.0) goto LAB_1001a12b;
  *unaff_EDI = (int)unaff_ESI[0x42];
  *unaff_EBX = (int)unaff_ESI[0x43];
  if ((*unaff_EDI != 0) && ((unaff_ESI[0x44] != 1.12104e-44 || (unaff_ESI[0x46] != 1.4013e-45))))
  goto LAB_1001a12b;
  fStack_10c = (float)(**(code **)(DAT_106b40d0 + 0x14))
                                (unaff_ESI[0x4c],unaff_ESI[0x49],unaff_ESI[0x4a],0);
  if ((unaff_ESI[0x44] == 1.12104e-44) &&
     ((unaff_ESI[0x46] == 1.4013e-45 || (unaff_ESI[0x46] == 2.8026e-45)))) {
    iVar3 = (**(code **)(DAT_106b40d0 + 0xa8))(unaff_ESI[0xe],unaff_ESI[0x4a]);
LAB_1001a031:
    fStack_10c = (float)((int)fStack_10c + iVar3);
  }
  else if ((unaff_ESI[0x44] == 5.60519e-45) &&
          ((unaff_ESI[0x46] == 1.4013e-45 && (unaff_ESI[0x56] != 0.0)))) {
    (**(code **)(DAT_106b40d0 + 0x58))(unaff_ESI[0x56],auStack_104,0x100);
    iVar3 = (**(code **)(DAT_106b40d0 + 0x14))(auStack_104,unaff_ESI[0x49],unaff_ESI[0x4a],0);
    goto LAB_1001a031;
  }
  iVar4 = (**(code **)(DAT_106b40d0 + 0x14))(param_1,unaff_ESI[0x49],unaff_ESI[0x4a],0);
  iVar3 = DAT_106b40d0;
  *unaff_EDI = iVar4;
  iVar3 = (**(code **)(iVar3 + 0x18))(param_1,unaff_ESI[0x4a],0);
  *unaff_EBX = iVar3;
  unaff_ESI[0x42] = (float)*unaff_EDI;
  iVar3 = *unaff_EBX;
  unaff_ESI[0x41] = unaff_ESI[0x48];
  unaff_ESI[0x43] = (float)iVar3;
  fVar1 = unaff_ESI[0x47];
  unaff_ESI[0x40] = fVar1;
  fStack_108 = fVar1;
  fVar2 = fStack_10c;
  if (unaff_ESI[0x46] == 2.8026e-45) {
LAB_1001a0e4:
    unaff_ESI[0x40] = fVar1 - (float)(int)fVar2;
  }
  else if (unaff_ESI[0x46] == 1.4013e-45) {
    fStack_108 = (float)((int)fStack_10c / 2);
    fVar2 = (float)((int)fStack_10c / 2);
    goto LAB_1001a0e4;
  }
  if (unaff_ESI[0xd] != 0.0) {
    unaff_ESI[0x40] = unaff_ESI[0x40] + unaff_ESI[0x11];
    unaff_ESI[0x41] = unaff_ESI[0x41] + unaff_ESI[0x11];
  }
  unaff_ESI[0x40] = unaff_ESI[0x40] + *unaff_ESI;
  unaff_ESI[0x41] = unaff_ESI[1] + unaff_ESI[0x41];
LAB_1001a12b:
  __security_check_cookie(local_4 ^ (uint)&fStack_10c);
  return;
}



/* FUN_1000a9d0 @ 1000a9d0 size 543 */

void FUN_1000a9d0(void)

{
  byte bVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  byte *pbVar6;
  undefined *puVar7;
  undefined4 uVar8;
  byte *pbVar9;
  int iVar10;
  byte *pbVar11;
  bool bVar12;
  int iStack_814;
  int iStack_810;
  int iStack_80c;
  int iStack_808;
  byte local_804 [2048];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&iStack_814;
  DAT_107613d8 = 0;
  iStack_80c = (**(code **)(DAT_106b40a8 + 0x4c))("$modlist",&DAT_100239ab,local_804,0x800);
  pbVar11 = local_804;
  iStack_814 = 0;
  if (0 < iStack_80c) {
    do {
      pbVar6 = pbVar11;
      do {
        bVar1 = *pbVar6;
        pbVar6 = pbVar6 + 1;
      } while (bVar1 != 0);
      iStack_810 = (int)pbVar6 - (int)(pbVar11 + 1);
      if (pbVar11 == (byte *)0x0) {
LAB_1000ab33:
        puVar7 = (undefined *)0x0;
      }
      else {
        if (*pbVar11 != 0) {
          iStack_808 = FUN_10014510();
          iVar5 = DAT_10050054;
          puVar2 = (undefined4 *)(&DAT_10051058)[iStack_808];
          for (puVar3 = puVar2; puVar3 != (undefined4 *)0x0; puVar3 = (undefined4 *)*puVar3) {
            pbVar6 = (byte *)puVar3[1];
            pbVar9 = pbVar11;
            do {
              bVar1 = *pbVar9;
              bVar12 = bVar1 < *pbVar6;
              if (bVar1 != *pbVar6) {
LAB_1000aa95:
                iVar10 = (1 - (uint)bVar12) - (uint)(bVar12 != 0);
                goto LAB_1000aa9a;
              }
              if (bVar1 == 0) break;
              bVar1 = pbVar9[1];
              bVar12 = bVar1 < pbVar6[1];
              if (bVar1 != pbVar6[1]) goto LAB_1000aa95;
              pbVar9 = pbVar9 + 2;
              pbVar6 = pbVar6 + 2;
            } while (bVar1 != 0);
            iVar10 = 0;
LAB_1000aa9a:
            if (iVar10 == 0) {
              puVar7 = (undefined *)puVar3[1];
              goto LAB_1000ab35;
            }
          }
          pbVar6 = pbVar11;
          do {
            bVar1 = *pbVar6;
            pbVar6 = pbVar6 + 1;
          } while (bVar1 != 0);
          pbVar6 = pbVar6 + (int)(DAT_106b40f4 + (1 - (int)(pbVar11 + 1)));
          if ((int)pbVar6 < 0x60000) {
            puVar7 = &DAT_10653058 + (int)DAT_106b40f4;
            pbVar9 = pbVar11;
            do {
              bVar1 = *pbVar9;
              pbVar9[(int)puVar7 - (int)pbVar11] = bVar1;
              pbVar9 = pbVar9 + 1;
              puVar3 = puVar2;
            } while (bVar1 != 0);
            do {
              puVar4 = puVar3;
              puVar3 = puVar2;
              if (puVar3 == (undefined4 *)0x0) break;
              puVar2 = (undefined4 *)*puVar3;
            } while ((undefined4 *)*puVar3 != (undefined4 *)0x0);
            DAT_106b40f4 = pbVar6;
            if (DAT_10050054 + 8 < 0x600001) {
              puVar2 = (undefined4 *)(&DAT_10053058 + DAT_10050054);
              DAT_10050054 = DAT_10050054 + 0x10;
              if (puVar2 != (undefined4 *)0x0) {
                *puVar2 = 0;
                *(undefined **)(&DAT_1005305c + iVar5) = puVar7;
                if (puVar4 == (undefined4 *)0x0) {
                  (&DAT_10051058)[iStack_808] = puVar2;
                }
                else {
                  *puVar4 = puVar2;
                }
                goto LAB_1000ab35;
              }
            }
            else {
              DAT_106b3058 = 1;
              FUN_10001e70(0,
                           "UI_Alloc: Failure. Out of memory! allocpoint: %i, sz: %i, MEM_POOL_SIZE: %i"
                           ,DAT_10050054,8,0x600000);
            }
          }
          goto LAB_1000ab33;
        }
        puVar7 = &DAT_100239ab;
      }
LAB_1000ab35:
      iVar5 = iStack_810;
      pbVar9 = pbVar11 + iStack_810 + 1;
      (&DAT_107611d8)[DAT_107613d8 * 2] = puVar7;
      uVar8 = FUN_10014560();
      (&DAT_107611dc)[DAT_107613d8 * 2] = uVar8;
      pbVar6 = pbVar9 + 1;
      do {
        bVar1 = *pbVar9;
        pbVar9 = pbVar9 + 1;
      } while (bVar1 != 0);
      pbVar11 = pbVar11 + (int)(pbVar9 + (iVar5 - (int)pbVar6) + 2);
      DAT_107613d8 = DAT_107613d8 + 1;
    } while ((DAT_107613d8 < 0x40) && (iStack_814 = iStack_814 + 1, iStack_814 < iStack_80c));
  }
  __security_check_cookie(local_4 ^ (uint)&iStack_814);
  return;
}



/* FUN_10011a30 @ 10011a30 size 536 */

void FUN_10011a30(int param_1)

{
  undefined4 *puVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  undefined4 uVar6;
  undefined1 local_28 [4];
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  int iStack_14;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_28;
  (**(code **)(DAT_106b40a8 + 0xc))(local_28);
  iVar3 = DAT_106b40a8;
  uVar4 = FUN_10001900("%s-%i, %i at %i:%i",(&PTR_DAT_1002adf4)[iStack_18],uStack_1c,
                       iStack_14 + 0x76c,uStack_20,uStack_24);
  uVar4 = FUN_10001900("ui_lastServerRefresh_%i",DAT_1074148c,uVar4);
  (**(code **)(iVar3 + 0x1c))(uVar4);
  if (param_1 == 0) {
    (**(code **)(DAT_106b40a8 + 0x100))(DAT_1074148c);
    DAT_10762484 = DAT_10746428 + 1000;
    DAT_10762498 = 1;
    __security_check_cookie(local_4 ^ (uint)local_28);
    return;
  }
  uVar4 = 1;
  DAT_107644a8 = DAT_10746428 + 1000;
  DAT_10762498 = 1;
  DAT_107644a0 = 0;
  DAT_107644a4 = 0;
  (**(code **)(DAT_106b40a8 + 0xec))(DAT_1074148c,0xffffffff,1);
  (**(code **)(DAT_106b40a8 + 0x100))(DAT_1074148c);
  if (DAT_1074148c == 0) {
    (**(code **)(DAT_106b40a8 + 0x50))("localservers\n");
    DAT_10762484 = DAT_10746428 + 1000;
    __security_check_cookie(local_4 ^ (uint)local_28);
    return;
  }
  DAT_10762484 = DAT_10746428 + 5000;
  if (DAT_1074148c == 2) {
    uVar4 = 0;
  }
  else if (DAT_1074148c != 1) goto LAB_10011c37;
  (**(code **)(DAT_106b40a8 + 0x24))("debug_protocol",&DAT_10042f38,0x400);
  iVar3 = DAT_106b40a8;
  pcVar5 = &DAT_10042f38;
  do {
    cVar2 = *pcVar5;
    pcVar5 = pcVar5 + 1;
  } while (cVar2 != '\0');
  if (pcVar5 != &DAT_10042f39) {
    uVar4 = FUN_10001900("globalservers %d %s full empty\n",uVar4,&DAT_10042f38);
    (**(code **)(iVar3 + 0x50))(uVar4);
    __security_check_cookie(local_4 ^ (uint)local_28);
    return;
  }
  puVar1 = (undefined4 *)(DAT_106b40a8 + 0x50);
  (**(code **)(DAT_106b40a8 + 0x28))("protocol");
  uVar6 = FUN_10021270();
  uVar4 = FUN_10001900("globalservers %d %d full empty\n",uVar4,uVar6);
  (*(code *)*puVar1)(uVar4);
LAB_10011c37:
  __security_check_cookie(local_4 ^ (uint)local_28);
  return;
}



/* FUN_1001b7c0 @ 1001b7c0 size 530 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001b7c0(void)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int unaff_ESI;
  float10 fVar4;
  undefined1 auStack_30 [4];
  float fStack_2c;
  float local_28;
  float local_24;
  float local_20;
  float local_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_30;
  uVar3 = 0;
  iVar1 = *(int *)(unaff_ESI + 0x134);
  if (*(int *)(unaff_ESI + 0x288) != 0) {
    uVar3 = *(undefined4 *)(*(int *)(unaff_ESI + 0x288) + 0x14);
  }
  if (*(int *)(unaff_ESI + 0x158) != 0) {
    (**(code **)(DAT_106b40d0 + 0x5c))(*(int *)(unaff_ESI + 0x158));
  }
  iVar2 = DAT_106b40d0;
  if ((*(byte *)(unaff_ESI + 0x48) & 2) == 0) {
    uStack_18 = *(undefined4 *)(unaff_ESI + 0x78);
    uStack_14 = *(undefined4 *)(unaff_ESI + 0x7c);
    uStack_10 = *(undefined4 *)(unaff_ESI + 0x80);
    uStack_c = *(undefined4 *)(unaff_ESI + 0x84);
  }
  else {
    if (DAT_106b40dc == unaff_ESI) {
      local_28 = DAT_10029518;
      local_24 = 0.0;
      local_20 = 0.0;
      local_1c = DAT_10029518;
    }
    else {
      local_1c = (float)_DAT_10029388;
      local_28 = *(float *)(iVar1 + 0x134) * local_1c;
      local_24 = *(float *)(iVar1 + 0x138) * local_1c;
      local_20 = *(float *)(iVar1 + 0x13c) * local_1c;
      local_1c = local_1c * *(float *)(iVar1 + 0x140);
    }
    fStack_2c = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fVar4 = (float10)_CIsin();
    fStack_2c = (float)((float10)_DAT_10029278 + fVar4 * (float10)_DAT_10029278);
    FUN_100147a0(fStack_2c);
  }
  if (*(int *)(unaff_ESI + 0x130) != 0) {
    FUN_1001a7e0();
    FUN_1001b2a0();
    fStack_2c = *(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) + (float)_DAT_10029220
    ;
    (**(code **)(DAT_106b40d0 + 0x10))
              (fStack_2c,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
               *(undefined4 *)(unaff_ESI + 0x128),&uStack_18,&DAT_1073f320,0,uVar3,
               *(undefined4 *)(unaff_ESI + 300));
    __security_check_cookie(local_8 ^ (uint)auStack_30);
    return;
  }
  (**(code **)(iVar2 + 0x10))
            (*(undefined4 *)(unaff_ESI + 0x100),*(undefined4 *)(unaff_ESI + 0x104),
             *(undefined4 *)(unaff_ESI + 0x124),*(undefined4 *)(unaff_ESI + 0x128),&uStack_18,
             "FIXME",0,uVar3,*(undefined4 *)(unaff_ESI + 300));
  __security_check_cookie(local_8 ^ (uint)auStack_30);
  return;
}



/* FUN_1001f7c0 @ 1001f7c0 size 528 */

void FUN_1001f7c0(char *param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  char *pcVar6;
  uint uVar7;
  char acStack_486 [62];
  undefined4 uStack_448;
  char *pcStack_444;
  char *pcStack_440;
  char *pcStack_43c;
  undefined1 auStack_42c [4];
  int *piStack_428;
  undefined4 local_424;
  char local_420 [16];
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_42c;
  pcStack_43c = local_420;
  local_424 = param_2;
  pcStack_440 = param_1;
  pcStack_444 = (char *)0x1001f7fb;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
  if ((iVar2 == 0) || (acStack_410[0] != '{')) {
LAB_1001f9b9:
    __security_check_cookie(local_c ^ (uint)auStack_42c);
    return;
  }
  pcStack_43c = local_420;
  pcStack_440 = param_1;
  pcStack_444 = (char *)0x1001f825;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
  while( true ) {
    if (iVar2 == 0) {
      pcStack_43c = "end of file inside menu item\n";
      pcStack_444 = (char *)0x1001f938;
      pcStack_440 = param_1;
      FUN_10014710();
      __security_check_cookie(local_c ^ (uint)auStack_42c);
      return;
    }
    if (acStack_410[0] == '}') {
      __security_check_cookie(local_c ^ (uint)auStack_42c);
      return;
    }
    uVar7 = 0;
    if (acStack_410[0] != '\0') {
      iVar2 = 0x77;
      cVar1 = acStack_410[0];
      do {
        if ((byte)(cVar1 + 0xbfU) < 0x1a) {
          iVar3 = cVar1 + 0x20;
        }
        else {
          iVar3 = (int)cVar1;
        }
        uVar7 = uVar7 + iVar3 * iVar2;
        cVar1 = acStack_486[iVar2];
        iVar2 = iVar2 + 1;
      } while (cVar1 != '\0');
    }
    piStack_428 = (int *)(&DAT_106b4120)[((int)((int)uVar7 >> 10 ^ uVar7) >> 10 ^ uVar7) & 0x1ff];
    if (piStack_428 != (int *)0x0) break;
LAB_1001f977:
    pcStack_43c = acStack_410;
    pcStack_440 = "unknown menu item keyword %s";
    uStack_448 = 0x1001f987;
    pcStack_444 = param_1;
    FUN_10014710();
LAB_1001f90e:
    pcStack_43c = local_420;
    pcStack_444 = (char *)0x1001f922;
    pcStack_440 = param_1;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
  }
LAB_1001f8a0:
  if (*piStack_428 != 0) {
    pcVar6 = acStack_410;
    iVar3 = *piStack_428 - (int)pcVar6;
    iVar2 = 99999;
    do {
      iVar4 = (int)pcVar6[iVar3];
      iVar5 = (int)*pcVar6;
      pcVar6 = pcVar6 + 1;
      if (iVar2 == 0) goto LAB_1001f8f1;
      if (iVar4 != iVar5) {
        if (iVar4 - 0x61U < 0x1a) {
          iVar4 = iVar4 + -0x20;
        }
        if (iVar5 - 0x61U < 0x1a) {
          iVar5 = iVar5 + -0x20;
        }
        if (iVar4 != iVar5) goto LAB_1001f952;
      }
      iVar2 = iVar2 + -1;
      if (iVar4 == 0) goto LAB_1001f8f1;
    } while( true );
  }
  goto LAB_1001f968;
LAB_1001f952:
  if ((char)((iVar5 <= iVar4) * '\x02') == '\x01') {
LAB_1001f8f1:
    pcStack_43c = param_1;
    pcStack_444 = (char *)0x1001f903;
    pcStack_440 = (char *)local_424;
    iVar2 = (*(code *)piStack_428[1])();
    if (iVar2 != 0) goto LAB_1001f90e;
    pcStack_43c = acStack_410;
    pcStack_440 = "couldn\'t parse menu item keyword %s";
    pcStack_444 = param_1;
    uStack_448 = 0x1001f9b6;
    FUN_10014710();
    goto LAB_1001f9b9;
  }
LAB_1001f968:
  piStack_428 = (int *)piStack_428[2];
  if (piStack_428 == (int *)0x0) goto LAB_1001f977;
  goto LAB_1001f8a0;
}



/* FUN_10012550 @ 10012550 size 526 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_10012550(int *param_1,float param_2,float param_3,float param_4,float param_5)

{
  ushort uVar1;
  uint uVar2;
  float fVar3;
  undefined4 *extraout_ECX;
  undefined4 *extraout_ECX_00;
  float *unaff_ESI;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float in_XMM0_Da;
  
  if (*param_1 == 0) {
    FUN_10001140(*unaff_ESI,param_2);
    if ((in_XMM0_Da <= param_3) && (-param_3 <= in_XMM0_Da)) {
      return;
    }
    *extraout_ECX = 1;
  }
  FUN_10001140(param_2,*unaff_ESI);
  fVar3 = DAT_10029328;
  if (((float)_DAT_10029278 * param_3 <= ABS(in_XMM0_Da)) &&
     (fVar3 = DAT_10029358, ABS(in_XMM0_Da) < param_3)) {
    fVar3 = DAT_10029234;
  }
  if (in_XMM0_Da < 0.0) {
    if (in_XMM0_Da < 0.0) {
      fVar3 = -param_5 * (float)DAT_1074642c * fVar3;
      if (fVar3 <= in_XMM0_Da) {
        *extraout_ECX_00 = 0;
        fVar3 = in_XMM0_Da;
      }
      uVar2 = FUN_10021270(*unaff_ESI + fVar3);
      fVar3 = (float)(uVar2 & 0xffff);
      *unaff_ESI = (float)((float10)(int)fVar3 * extraout_ST0_00);
    }
  }
  else {
    param_5 = (float)DAT_1074642c * fVar3 * param_5;
    if (in_XMM0_Da <= param_5) {
      *extraout_ECX_00 = 0;
      param_5 = in_XMM0_Da;
    }
    uVar2 = FUN_10021270(*unaff_ESI + param_5);
    fVar3 = (float)(uVar2 & 0xffff);
    *unaff_ESI = (float)((float10)(int)fVar3 * extraout_ST0);
  }
  FUN_10001140(param_2,*unaff_ESI);
  if (in_XMM0_Da <= param_4) {
    if (-param_4 <= in_XMM0_Da) {
      return;
    }
    uVar1 = FUN_10021270(fVar3,(param_4 - (float)_DAT_10029228) + param_2);
    *unaff_ESI = (float)uVar1 * (float)_DAT_100292b8;
    return;
  }
  uVar1 = FUN_10021270(fVar3,param_2 - (param_4 - (float)_DAT_10029228));
  *unaff_ESI = (float)uVar1 * (float)_DAT_100292b8;
  return;
}



/* FUN_1001ab30 @ 1001ab30 size 524 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001ab30(void)

{
  int iVar1;
  int iVar2;
  undefined *puVar3;
  int unaff_ESI;
  float10 fVar4;
  float fStack_30;
  float local_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  float local_18;
  float local_14;
  float fStack_10;
  float fStack_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)&fStack_30;
  iVar1 = *(int *)(unaff_ESI + 0x134);
  if (*(int *)(unaff_ESI + 0x158) == 0) {
    local_2c = 0.0;
  }
  else {
    fVar4 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(*(int *)(unaff_ESI + 0x158));
    local_2c = (float)fVar4;
  }
  iVar2 = DAT_106b40d0;
  if ((*(byte *)(unaff_ESI + 0x48) & 2) == 0) {
    uStack_28 = *(undefined4 *)(unaff_ESI + 0x78);
    uStack_24 = *(undefined4 *)(unaff_ESI + 0x7c);
    uStack_20 = *(undefined4 *)(unaff_ESI + 0x80);
    uStack_1c = *(undefined4 *)(unaff_ESI + 0x84);
  }
  else {
    fStack_c = (float)_DAT_10029448;
    local_18 = *(float *)(iVar1 + 0x134) * fStack_c;
    local_14 = *(float *)(iVar1 + 0x138) * fStack_c;
    fStack_30 = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fStack_10 = *(float *)(iVar1 + 0x13c) * fStack_c;
    fStack_c = fStack_c * *(float *)(iVar1 + 0x140);
    fVar4 = (float10)_CIsin();
    fStack_30 = (float)((float10)_DAT_10029278 + fVar4 * (float10)_DAT_10029278);
    FUN_100147a0(fStack_30);
  }
  if (*(int *)(unaff_ESI + 0x130) != 0) {
    FUN_1001a7e0();
    puVar3 = &DAT_1002911c;
    if (local_2c == _DAT_10029214) {
      puVar3 = &DAT_10029120;
    }
    fStack_30 = *(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) + (float)_DAT_10029220
    ;
    (**(code **)(DAT_106b40d0 + 0x10))
              (fStack_30,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
               *(undefined4 *)(unaff_ESI + 0x128),&uStack_28,puVar3,0,0,
               *(undefined4 *)(unaff_ESI + 300));
    __security_check_cookie(local_8 ^ (uint)&fStack_30);
    return;
  }
  puVar3 = &DAT_1002911c;
  if (local_2c == _DAT_10029214) {
    puVar3 = &DAT_10029120;
  }
  (**(code **)(iVar2 + 0x10))
            (*(undefined4 *)(unaff_ESI + 0x100),*(undefined4 *)(unaff_ESI + 0x104),
             *(undefined4 *)(unaff_ESI + 0x124),*(undefined4 *)(unaff_ESI + 0x128),&uStack_28,puVar3
             ,0,0,*(undefined4 *)(unaff_ESI + 300));
  __security_check_cookie(local_8 ^ (uint)&fStack_30);
  return;
}



/* __CRT_INIT@12 @ 10020a46 size 522 */

/* Library Function - Single Match
    __CRT_INIT@12
   
   Library: Visual Studio 2010 Release */

undefined4 __CRT_INIT_12(int *param_1,int *param_2,int *param_3)

{
  bool bVar1;
  BOOL BVar2;
  LONG LVar3;
  int *piVar4;
  int iVar5;
  code *pcVar6;
  int *piVar7;
  int *piVar8;
  
  if (param_2 == (int *)0x0) {
    if (DAT_1002c4c0 < 1) {
      return 0;
    }
    DAT_1002c4c0 = DAT_1002c4c0 + -1;
    iVar5 = *(int *)((int)Self + 4);
    bVar1 = false;
    while (LVar3 = InterlockedCompareExchange((LONG *)&DAT_106b4108,iVar5,0), LVar3 != 0) {
      if (LVar3 == iVar5) {
        bVar1 = true;
        break;
      }
      Sleep(1000);
    }
    if (DAT_106b4104 == 2) {
      param_2 = DecodePointer(DAT_106b4110);
      if (param_2 != (int *)0x0) {
        piVar4 = DecodePointer(DAT_106b410c);
        param_1 = piVar4;
        param_3 = param_2;
        while (piVar4 = piVar4 + -1, param_2 <= piVar4) {
          if ((*piVar4 != 0) && (iVar5 = encoded_null(), *piVar4 != iVar5)) {
            pcVar6 = DecodePointer((PVOID)*piVar4);
            iVar5 = encoded_null();
            *piVar4 = iVar5;
            (*pcVar6)();
            piVar7 = DecodePointer(DAT_106b4110);
            piVar8 = DecodePointer(DAT_106b410c);
            if ((param_3 != piVar7) || (param_1 != piVar8)) {
              piVar4 = piVar8;
              param_1 = piVar8;
              param_2 = piVar7;
              param_3 = piVar7;
            }
          }
        }
        free(param_2);
        DAT_106b410c = (PVOID)encoded_null();
        DAT_106b4110 = DAT_106b410c;
      }
      DAT_106b4104 = 0;
      if (!bVar1) {
        InterlockedExchange((LONG *)&DAT_106b4108,0);
      }
    }
    else {
      _amsg_exit(0x1f);
    }
  }
  else if (param_2 == (int *)0x1) {
    iVar5 = *(int *)((int)Self + 4);
    bVar1 = false;
    while (LVar3 = InterlockedCompareExchange((LONG *)&DAT_106b4108,iVar5,0), LVar3 != 0) {
      if (LVar3 == iVar5) {
        bVar1 = true;
        break;
      }
      Sleep(1000);
    }
    if (DAT_106b4104 == 0) {
      DAT_106b4104 = 1;
      iVar5 = initterm_e(&DAT_100220d8,&DAT_100220e4);
      if (iVar5 != 0) {
        return 0;
      }
      initterm(&DAT_100220d0,&DAT_100220d4);
      DAT_106b4104 = 2;
    }
    else {
      _amsg_exit(0x1f);
    }
    if (!bVar1) {
      InterlockedExchange((LONG *)&DAT_106b4108,0);
    }
    if ((DAT_106b4114 != (code *)0x0) &&
       (BVar2 = __IsNonwritableInCurrentImage((PBYTE)&DAT_106b4114), BVar2 != 0)) {
      (*DAT_106b4114)(param_1,2,param_3);
    }
    DAT_1002c4c0 = DAT_1002c4c0 + 1;
  }
  return 1;
}



/* FUN_10004070 @ 10004070 size 514 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10004070(float param_1,float param_2,undefined4 param_3,float param_4,undefined4 param_5,
                 int param_6,int param_7,int param_8,int param_9)

{
  float fVar1;
  undefined4 uVar2;
  char cVar3;
  float local_38;
  float local_34;
  float local_30;
  float afStack_2c [2];
  float fStack_24;
  undefined1 auStack_18 [20];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_38;
  local_30 = 0.0;
  if (param_6 != 0) {
    if (param_9 == 0) {
      param_9 = -1;
    }
    if (DAT_106b40a4 == 0.0) {
      DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
    }
    local_38 = DAT_106b40a4 * param_4;
    local_34 = _DAT_10746420 * param_1;
    fVar1 = local_34 + DAT_10746424;
    param_2 = _DAT_1074641c * param_2;
    (**(code **)(DAT_106b40a8 + 0x74))(param_5);
    (**(code **)(DAT_106b40a8 + 0x178))
              ((int)fVar1,(int)param_2,param_6,param_3,local_38,param_9,0,0);
    if ((DAT_10746428 & 0x100) != 0) {
      cVar3 = '\0';
      if ((0 < param_7) && (cVar3 = *(char *)(param_7 + -1 + param_6), cVar3 == ' ')) {
        *(undefined1 *)(param_7 + -1 + param_6) = 0x5f;
      }
      (**(code **)(DAT_106b40a8 + 0x17c))
                (param_6,param_7 + param_6,param_3,local_38,param_9,auStack_18);
      if (cVar3 == ' ') {
        *(undefined1 *)(param_7 + param_6 + -1) = 0x20;
      }
      local_34._0_2_ = (ushort)(byte)((-(param_8 != 0) & 0xe3U) + 0x7c);
      if (param_8 == 0) {
        (**(code **)(DAT_106b40a8 + 0x17c))(&local_34,0,param_3,local_38,0xffffffff,afStack_2c);
        local_30 = (fStack_24 - afStack_2c[0]) * (float)_DAT_10029388;
      }
      uVar2 = FUN_10021270((int)param_2,&local_34,param_3,local_38,0xffffffff,0,0);
      (**(code **)(DAT_106b40a8 + 0x178))(uVar2);
    }
    (**(code **)(DAT_106b40a8 + 0x74))(0);
  }
  __security_check_cookie(local_4 ^ (uint)&local_38);
  return;
}



/* FUN_1000f4c0 @ 1000f4c0 size 510 */

undefined4 FUN_1000f4c0(void)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  pcVar2 = (char *)FUN_10001500();
  if (*pcVar2 != '{') {
    return 0;
  }
  iVar5 = 0;
  DAT_1075add0 = iVar5;
  while( true ) {
    do {
      pcVar2 = (char *)FUN_10001500();
      if (pcVar2 == (char *)0x0) {
        return 0;
      }
      iVar3 = FUN_100016c0();
      if (iVar3 == 0) {
        return 1;
      }
      if (*pcVar2 == '\0') {
        return 0;
      }
    } while (*pcVar2 != '{');
    pcVar2 = (char *)FUN_10001500();
    if (pcVar2 == (char *)0x0) {
      return 0;
    }
    if (*pcVar2 == '\0') {
      return 0;
    }
    uVar4 = FUN_10014560();
    (&DAT_1075add4)[iVar5 * 0x19] = uVar4;
    iVar5 = DAT_1075add0 * 0x19;
    pcVar2 = (char *)FUN_10001500();
    if (pcVar2 == (char *)0x0) {
      return 0;
    }
    if (*pcVar2 == '\0') {
      return 0;
    }
    uVar4 = FUN_10014560();
    (&DAT_1075add8)[iVar5] = uVar4;
    iVar5 = DAT_1075add0 * 0x19;
    pcVar2 = (char *)FUN_10001500();
    if (pcVar2 == (char *)0x0) {
      return 0;
    }
    if (*pcVar2 == '\0') break;
    iVar3 = atoi(pcVar2);
    (&DAT_1075ade4)[iVar5] = iVar3;
    iVar5 = DAT_1075add0 * 0x19;
    pcVar2 = (char *)FUN_10001500();
    if (pcVar2 == (char *)0x0) {
      return 0;
    }
    if (*pcVar2 == '\0') {
      return 0;
    }
    uVar4 = FUN_10014560();
    (&DAT_1075ade0)[iVar5] = uVar4;
    (&DAT_1075ade8)[DAT_1075add0 * 0x19] = 0;
    pcVar2 = (char *)FUN_10001500();
    cVar1 = *pcVar2;
    while (('/' < cVar1 && (cVar1 < ':'))) {
      (&DAT_1075ade8)[DAT_1075add0 * 0x19] =
           (&DAT_1075ade8)[DAT_1075add0 * 0x19] | 1 << (cVar1 - 0x30U & 0x1f);
      cVar1 = *pcVar2;
      iVar5 = DAT_1075add0 * 0x19;
      pcVar2 = (char *)FUN_10001500();
      if (pcVar2 == (char *)0x0) {
        return 0;
      }
      if (*pcVar2 == '\0') {
        return 0;
      }
      iVar3 = atoi(pcVar2);
      *(int *)(&DAT_1075ad30 + (iVar5 + cVar1) * 4) = iVar3;
      pcVar2 = (char *)FUN_10001500();
      cVar1 = *pcVar2;
    }
    (&DAT_1075adec)[DAT_1075add0 * 0x19] = 0xffffffff;
    if (DAT_1075add0 < 0x100) {
      iVar5 = DAT_1075add0 + 1;
      DAT_1075add0 = iVar5;
    }
    else {
      FUN_10001ee0("Too many maps, last one replaced!\n");
      iVar5 = DAT_1075add0;
    }
  }
  return 0;
}



/* FUN_10020190 @ 10020190 size 509 */

void FUN_10020190(undefined4 param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  char *pcVar6;
  int *piVar7;
  uint uVar8;
  char acStackY_482 [54];
  undefined4 uStackY_44c;
  undefined4 uStackY_448;
  undefined1 *puStackY_444;
  undefined1 auStack_424 [4];
  undefined4 local_420;
  undefined1 local_41c [16];
  char acStack_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_424;
  local_420 = param_2;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
  if ((iVar2 != 0) && (acStack_40c[0] == '{')) {
    puStackY_444 = (undefined1 *)0x100201f5;
    memset(local_41c,0,0x410);
    puStackY_444 = local_41c;
    uStackY_448 = param_1;
    uStackY_44c = 0x10020208;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
    while (iVar2 != 0) {
      if (acStack_40c[0] == '}') goto LAB_1002037c;
      uVar8 = 0;
      if (acStack_40c[0] != '\0') {
        iVar2 = 0x77;
        cVar1 = acStack_40c[0];
        do {
          if ((byte)(cVar1 + 0xbfU) < 0x1a) {
            iVar3 = cVar1 + 0x20;
          }
          else {
            iVar3 = (int)cVar1;
          }
          uVar8 = uVar8 + iVar3 * iVar2;
          cVar1 = acStackY_482[iVar2];
          iVar2 = iVar2 + 1;
        } while (cVar1 != '\0');
      }
      piVar7 = (int *)(&DAT_1073f360)[((int)((int)uVar8 >> 10 ^ uVar8) >> 10 ^ uVar8) & 0x1ff];
      if (piVar7 != (int *)0x0) {
LAB_10020280:
        if (*piVar7 != 0) {
          pcVar6 = acStack_40c;
          iVar3 = *piVar7 - (int)pcVar6;
          iVar2 = 99999;
          do {
            iVar4 = (int)pcVar6[iVar3];
            iVar5 = (int)*pcVar6;
            pcVar6 = pcVar6 + 1;
            if (iVar2 == 0) goto LAB_100202d1;
            if (iVar4 != iVar5) {
              if (iVar4 - 0x61U < 0x1a) {
                iVar4 = iVar4 + -0x20;
              }
              if (iVar5 - 0x61U < 0x1a) {
                iVar5 = iVar5 + -0x20;
              }
              if (iVar4 != iVar5) goto LAB_1002032a;
            }
            iVar2 = iVar2 + -1;
            if (iVar4 == 0) goto LAB_100202d1;
          } while( true );
        }
        goto LAB_10020340;
      }
LAB_1002034b:
      puStackY_444 = (undefined1 *)0x1002035b;
      FUN_10014710();
LAB_100202ea:
      puStackY_444 = (undefined1 *)0x100202fb;
      memset(local_41c,0,0x410);
      puStackY_444 = local_41c;
      uStackY_44c = 0x1002030f;
      uStackY_448 = param_1;
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
    }
    FUN_10014710();
  }
LAB_1002037c:
  __security_check_cookie(local_8 ^ (uint)auStack_424);
  return;
LAB_1002032a:
  if ((char)((iVar5 <= iVar4) * '\x02') == '\x01') {
LAB_100202d1:
    iVar2 = (*(code *)piVar7[1])();
    if (iVar2 != 0) goto LAB_100202ea;
    puStackY_444 = (undefined1 *)0x10020377;
    FUN_10014710();
    goto LAB_1002037c;
  }
LAB_10020340:
  piVar7 = (int *)piVar7[2];
  if (piVar7 == (int *)0x0) goto LAB_1002034b;
  goto LAB_10020280;
}



/* FUN_100139a0 @ 100139a0 size 503 */

void __fastcall FUN_100139a0(undefined4 param_1,char *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_8c;
  undefined4 local_88;
  undefined1 local_84 [128];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_8c;
  local_8c = param_4;
  if ((param_2 == (char *)0x0) || (*param_2 == '\0')) {
    FUN_10001830(local_84,0x80,"models/players/%s/lower_%s.skin");
  }
  else {
    FUN_10001830(local_84,0x80,"models/players/%s/%s/lower_%s.skin");
  }
  iVar1 = (**(code **)(DAT_106b40a8 + 0x58))(local_84);
  *(int *)(param_3 + 4) = iVar1;
  if (iVar1 == 0) {
    if ((param_2 == (char *)0x0) || (*param_2 == '\0')) {
      FUN_10001830(local_84,0x80,"models/players/characters/%s/lower_%s.skin");
    }
    else {
      FUN_10001830(local_84,0x80,"models/players/characters/%s/%s/lower_%s.skin");
    }
    uVar2 = (**(code **)(DAT_106b40a8 + 0x58))(local_84);
    *(undefined4 *)(param_3 + 4) = uVar2;
  }
  if ((param_2 == (char *)0x0) || (*param_2 == '\0')) {
    FUN_10001830(local_84,0x80,"models/players/%s/upper_%s.skin");
  }
  else {
    FUN_10001830(local_84,0x80,"models/players/%s/%s/upper_%s.skin");
  }
  iVar1 = (**(code **)(DAT_106b40a8 + 0x58))(local_84);
  *(int *)(param_3 + 0x3c) = iVar1;
  if (iVar1 == 0) {
    if ((param_2 == (char *)0x0) || (*param_2 == '\0')) {
      FUN_10001830(local_84,0x80,"models/players/characters/%s/upper_%s.skin");
    }
    else {
      FUN_10001830(local_84,0x80,"models/players/characters/%s/%s/upper_%s.skin");
    }
    uVar2 = (**(code **)(DAT_106b40a8 + 0x58))(local_84);
    *(undefined4 *)(param_3 + 0x3c) = uVar2;
  }
  iVar1 = FUN_10013850(param_2,local_88);
  if (iVar1 != 0) {
    uVar2 = (**(code **)(DAT_106b40a8 + 0x58))(local_84);
    *(undefined4 *)(param_3 + 0x74) = uVar2;
  }
  if (((*(int *)(param_3 + 4) != 0) && (*(int *)(param_3 + 0x3c) != 0)) &&
     (*(int *)(param_3 + 0x74) != 0)) {
    __security_check_cookie(local_4 ^ (uint)&local_8c);
    return;
  }
  __security_check_cookie(local_4 ^ (uint)&local_8c);
  return;
}



/* FUN_1001b5c0 @ 1001b5c0 size 502 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001b5c0(void)

{
  float fVar1;
  float *unaff_ESI;
  float10 fVar2;
  undefined1 auStack_34 [4];
  float fStack_30;
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  float local_18;
  float local_14;
  float fStack_10;
  float fStack_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_34;
  fVar1 = unaff_ESI[0x4d];
  if (unaff_ESI[0x56] != 0.0) {
    (**(code **)(DAT_106b40d0 + 0x5c))(unaff_ESI[0x56]);
  }
  if (((uint)unaff_ESI[0x12] & 2) == 0) {
    fStack_28 = unaff_ESI[0x1e];
    fStack_24 = unaff_ESI[0x1f];
    fStack_20 = unaff_ESI[0x20];
    fStack_1c = unaff_ESI[0x21];
  }
  else {
    fStack_c = (float)_DAT_10029448;
    local_18 = *(float *)((int)fVar1 + 0x134) * fStack_c;
    local_14 = *(float *)((int)fVar1 + 0x138) * fStack_c;
    fStack_30 = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fStack_10 = *(float *)((int)fVar1 + 0x13c) * fStack_c;
    fStack_c = fStack_c * *(float *)((int)fVar1 + 0x140);
    fVar2 = (float10)_CIsin();
    fStack_30 = (float)((float10)_DAT_10029278 + fVar2 * (float10)_DAT_10029278);
    FUN_100147a0(fStack_30);
  }
  fStack_30 = unaff_ESI[1];
  if (unaff_ESI[0x4c] == 0.0) {
    fStack_2c = *unaff_ESI;
  }
  else {
    FUN_1001a7e0();
    fStack_2c = unaff_ESI[0x42] + unaff_ESI[0x40] + (float)_DAT_10029220;
  }
  (**(code **)(DAT_106b40d0 + 4))(0);
  (**(code **)(DAT_106b40d0 + 8))
            (fStack_2c,fStack_30,_DAT_10029520,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf244));
  fVar2 = (float10)FUN_10017410();
  fStack_2c = (float)fVar2;
  (**(code **)(DAT_106b40d0 + 4))(&fStack_28);
  fVar1 = fStack_30 - (float)_DAT_100292f0;
  fStack_30 = fStack_2c - (float)_DAT_10029300;
  (**(code **)(DAT_106b40d0 + 8))
            (fStack_30,fVar1,_DAT_10029370,_DAT_1002951c,*(undefined4 *)(DAT_106b40d0 + 0xf204));
  __security_check_cookie(local_8 ^ (uint)auStack_34);
  return;
}



/* FUN_10018680 @ 10018680 size 492 */

undefined4 __thiscall FUN_10018680(int param_1,float *param_2)

{
  char cVar1;
  float fVar2;
  char *pcVar3;
  int iVar4;
  int iVar5;
  char *pcVar6;
  int iVar7;
  undefined4 uVar8;
  undefined4 *puVar9;
  int iVar10;
  int local_10;
  
  fVar2 = param_2[0xa2];
  iVar10 = 0;
  if (fVar2 != 0.0) {
    if ((((((*param_2 < (float)*(int *)(DAT_106b40d0 + 0xf0)) &&
           ((float)*(int *)(DAT_106b40d0 + 0xf0) < param_2[2] + *param_2)) &&
          (param_2[1] < (float)*(int *)(DAT_106b40d0 + 0xf4))) &&
         (((float)*(int *)(DAT_106b40d0 + 0xf4) < param_2[3] + param_2[1] &&
          (((uint)param_2[0x12] & 2) != 0)))) && (param_2[0x56] != 0.0)) &&
       (((param_1 == 0xb2 || (param_1 == 0xd)) || ((param_1 == 0xb3 || (param_1 == 0xb4)))))) {
      local_10 = FUN_100185d0();
      local_10 = local_10 + 1;
      if (param_2[0xa2] == 0.0) {
        iVar5 = 0;
      }
      else {
        iVar5 = *(int *)((int)param_2[0xa2] + 0x180);
      }
      if ((local_10 < 0) || (iVar5 <= local_10)) {
        local_10 = 0;
      }
      iVar5 = FUN_10015ea0(param_2[0x4d],*(undefined4 *)((int)fVar2 + 0x80 + local_10 * 4));
      if ((iVar5 != 0) && (iVar5 = *(int *)(iVar5 + 0x288), 0 < *(int *)(iVar5 + 0x180))) {
        puVar9 = (undefined4 *)(iVar5 + 0x80);
        do {
          pcVar3 = (char *)*puVar9;
          pcVar6 = pcVar3;
          do {
            cVar1 = *pcVar6;
            pcVar6 = pcVar6 + 1;
          } while (cVar1 != '\0');
          iVar7 = FUN_10001670();
          iVar4 = DAT_106b40d0;
          if (iVar7 == 0) {
            uVar8 = FUN_10001900(&DAT_100256f8,pcVar3);
            (**(code **)(iVar4 + 0x60))(puVar9[-0x20],uVar8);
          }
          else {
            uVar8 = FUN_10001900(&DAT_100290e8,(double)(float)puVar9[0x20]);
            (**(code **)(iVar4 + 0x60))(puVar9[-0x20],uVar8);
          }
          iVar10 = iVar10 + 1;
          puVar9 = puVar9 + 1;
        } while (iVar10 < *(int *)(iVar5 + 0x180));
      }
      (**(code **)(DAT_106b40d0 + 0x60))(param_2[0x56],*(undefined4 *)((int)fVar2 + local_10 * 4));
      return 1;
    }
  }
  return 0;
}



/* FUN_1001b3d0 @ 1001b3d0 size 485 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001b3d0(void)

{
  float fVar1;
  float *unaff_ESI;
  float10 fVar2;
  undefined1 auStack_34 [4];
  float fStack_30;
  float fStack_2c;
  float fStack_28;
  float fStack_24;
  float fStack_20;
  float fStack_1c;
  float local_18;
  float local_14;
  float fStack_10;
  float fStack_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_34;
  fVar1 = unaff_ESI[0x4d];
  if (unaff_ESI[0x56] != 0.0) {
    (**(code **)(DAT_106b40d0 + 0x5c))(unaff_ESI[0x56]);
  }
  if (((uint)unaff_ESI[0x12] & 2) == 0) {
    fStack_28 = unaff_ESI[0x1e];
    fStack_24 = unaff_ESI[0x1f];
    fStack_20 = unaff_ESI[0x20];
    fStack_1c = unaff_ESI[0x21];
  }
  else {
    fStack_c = (float)_DAT_10029448;
    local_18 = *(float *)((int)fVar1 + 0x134) * fStack_c;
    local_14 = *(float *)((int)fVar1 + 0x138) * fStack_c;
    fStack_30 = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fStack_10 = *(float *)((int)fVar1 + 0x13c) * fStack_c;
    fStack_c = fStack_c * *(float *)((int)fVar1 + 0x140);
    fVar2 = (float10)_CIsin();
    fStack_30 = (float)((float10)_DAT_10029278 + fVar2 * (float10)_DAT_10029278);
    FUN_100147a0(fStack_30);
  }
  fStack_30 = unaff_ESI[1];
  if (unaff_ESI[0x4c] == 0.0) {
    fStack_2c = *unaff_ESI;
  }
  else {
    FUN_1001a7e0();
    fStack_2c = unaff_ESI[0x42] + unaff_ESI[0x40] + (float)_DAT_10029220;
  }
  (**(code **)(DAT_106b40d0 + 4))(&fStack_28);
  (**(code **)(DAT_106b40d0 + 8))
            (fStack_2c,fStack_30,_DAT_10029520,DAT_10029390,*(undefined4 *)(DAT_106b40d0 + 0xf200));
  fVar2 = (float10)FUN_10017410();
  fStack_2c = (float)fVar2;
  fVar1 = fStack_30 - (float)_DAT_100292f0;
  fStack_30 = fStack_2c - (float)_DAT_10029300;
  (**(code **)(DAT_106b40d0 + 8))
            (fStack_30,fVar1,_DAT_10029370,_DAT_1002951c,*(undefined4 *)(DAT_106b40d0 + 0xf204));
  __security_check_cookie(local_8 ^ (uint)auStack_34);
  return;
}



/* FUN_10001b80 @ 10001b80 size 476 */

void __thiscall FUN_10001b80(char *param_1,char *param_2)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  uint uVar4;
  char *pcVar5;
  uint uVar6;
  int iVar7;
  char *unaff_EBX;
  undefined1 auStack_408 [3];
  char acStack_405 [1025];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_408;
  acStack_405[1] = 0;
  memset(acStack_405 + 2,0,0x3ff);
  pcVar2 = param_2;
  do {
    cVar1 = *pcVar2;
    pcVar2 = pcVar2 + 1;
  } while (cVar1 != '\0');
  if (0x3ff < (uint)((int)pcVar2 - (int)(param_2 + 1))) {
    FUN_10001ee0("Info_SetValueForKey: oversize infostring\n");
    __security_check_cookie(local_4 ^ (uint)auStack_408);
    return;
  }
  pcVar2 = strchr(param_1,0x5c);
  if ((pcVar2 == (char *)0x0) && (pcVar2 = strchr(unaff_EBX,0x5c), pcVar2 == (char *)0x0)) {
    pcVar2 = strchr(param_1,0x3b);
    if ((pcVar2 == (char *)0x0) && (pcVar2 = strchr(unaff_EBX,0x3b), pcVar2 == (char *)0x0)) {
      pcVar2 = strchr(param_1,0x22);
      if ((pcVar2 == (char *)0x0) && (pcVar2 = strchr(unaff_EBX,0x22), pcVar2 == (char *)0x0)) {
        FUN_10001a60();
        if (unaff_EBX != (char *)0x0) {
          pcVar2 = unaff_EBX + 1;
          do {
            cVar1 = *unaff_EBX;
            unaff_EBX = unaff_EBX + 1;
          } while (cVar1 != '\0');
          if (unaff_EBX != pcVar2) {
            FUN_10001830(acStack_405 + 1,0x400,"\\%s\\%s",param_1);
            pcVar2 = acStack_405 + 1;
            do {
              cVar1 = *pcVar2;
              pcVar2 = pcVar2 + 1;
            } while (cVar1 != '\0');
            pcVar5 = param_2;
            do {
              cVar1 = *pcVar5;
              pcVar5 = pcVar5 + 1;
            } while (cVar1 != '\0');
            pcVar3 = param_2;
            if ((char *)0x3ff <
                pcVar2 + (int)(pcVar5 + (-(int)(param_2 + 1) - (int)(acStack_405 + 2)))) {
              pcVar2 = "Info_SetValueForKey: Info string length exceeded\n";
              goto LAB_10001d3a;
            }
            do {
              cVar1 = *pcVar3;
              pcVar3 = pcVar3 + 1;
            } while (cVar1 != '\0');
            uVar4 = (int)pcVar3 - (int)param_2;
            pcVar2 = acStack_405;
            do {
              pcVar5 = pcVar2 + 1;
              pcVar2 = pcVar2 + 1;
            } while (*pcVar5 != '\0');
            pcVar5 = param_2;
            for (uVar6 = uVar4 >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
              *(undefined4 *)pcVar2 = *(undefined4 *)pcVar5;
              pcVar5 = pcVar5 + 4;
              pcVar2 = pcVar2 + 4;
            }
            pcVar3 = acStack_405 + 1;
            for (uVar4 = uVar4 & 3; uVar4 != 0; uVar4 = uVar4 - 1) {
              *pcVar2 = *pcVar5;
              pcVar5 = pcVar5 + 1;
              pcVar2 = pcVar2 + 1;
            }
            iVar7 = (int)param_2 - (int)pcVar3;
            do {
              cVar1 = *pcVar3;
              pcVar3[iVar7] = cVar1;
              pcVar3 = pcVar3 + 1;
            } while (cVar1 != '\0');
          }
        }
        __security_check_cookie(local_4 ^ (uint)auStack_408);
        return;
      }
      pcVar2 = "Info_SetValueForKey: Can\'t use keys or values with a \"\n";
    }
    else {
      pcVar2 = "Info_SetValueForKey: Can\'t use keys or values with a semicolon\n";
    }
  }
  else {
    pcVar2 = "Info_SetValueForKey: Can\'t use keys or values with a \\\n";
  }
LAB_10001d3a:
  FUN_10001ee0(pcVar2);
  __security_check_cookie(local_4 ^ (uint)auStack_408);
  return;
}



/* FUN_10019790 @ 10019790 size 475 */

void FUN_10019790(undefined4 param_1,int param_2,undefined4 param_3)

{
  undefined4 *puVar1;
  char *pcVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  undefined4 *puVar6;
  int unaff_EDI;
  undefined1 auStack_7ec [4];
  undefined1 local_7e8 [308];
  undefined1 local_548 [308];
  undefined1 local_2a8 [308];
  undefined4 *local_174;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_7ec;
  if (unaff_EDI == 0) goto LAB_10019953;
  if ((param_2 != 0) && ((*(uint *)(unaff_EDI + 0x48) & 0x20000) != 0)) {
    if (((*(uint *)(unaff_EDI + 0x48) & 4) != 0) && (*(int *)(unaff_EDI + 0x128) != 0)) {
      FUN_10016d70(local_548);
    }
    *(uint *)(unaff_EDI + 0x48) = *(uint *)(unaff_EDI + 0x48) & 0xfffffff9;
  }
  iVar5 = 0;
  if (0 < DAT_106b40e4) {
    puVar6 = &DAT_106b4a50;
    do {
      puVar1 = puVar6 + -0x4c;
      iVar3 = FUN_100208f0(puVar1,(float)*(int *)(DAT_106b40d0 + 0xf0),
                           (float)*(int *)(DAT_106b40d0 + 0xf4));
      if (iVar3 != 0) {
        if (((*(byte *)(unaff_EDI + 0x48) & 4) != 0) && (*(int *)(unaff_EDI + 0x128) != 0)) {
          FUN_10016d70(local_7e8);
        }
        *(uint *)(unaff_EDI + 0x48) = *(uint *)(unaff_EDI + 0x48) & 0xfffffff9;
        puVar6[-0x3a] = puVar6[-0x3a] | 6;
        if (puVar6[-3] != 0) {
          local_174 = puVar1;
          FUN_10016d70(local_2a8);
        }
        pcVar2 = (char *)*puVar6;
        if ((pcVar2 != (char *)0x0) && (*pcVar2 != '\0')) {
          (**(code **)(DAT_106b40d0 + 0xb0))(pcVar2,pcVar2);
        }
        FUN_100196b0();
        FUN_1001d600(puVar1,(float)*(int *)(DAT_106b40d0 + 0xf0),
                     (float)*(int *)(DAT_106b40d0 + 0xf4));
        FUN_10019a10(puVar1,param_1,param_2,param_3);
      }
      iVar5 = iVar5 + 1;
      puVar6 = puVar6 + 0x455;
    } while (iVar5 < DAT_106b40e4);
  }
  iVar5 = 0;
  if (DAT_106b40e4 < 1) {
LAB_10019938:
    if (*(code **)(DAT_106b40d0 + 0xa4) != (code *)0x0) {
      (**(code **)(DAT_106b40d0 + 0xa4))(0);
    }
  }
  else {
    puVar4 = &DAT_106b4968;
    iVar3 = DAT_106b40e4;
    do {
      if ((*puVar4 & 0x100004) != 0) {
        iVar5 = iVar5 + 1;
      }
      puVar4 = puVar4 + 0x455;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
    if (iVar5 == 0) goto LAB_10019938;
  }
  FUN_100196b0();
LAB_10019953:
  __security_check_cookie(local_4 ^ (uint)auStack_7ec);
  return;
}



/* FUN_100142e0 @ 100142e0 size 465 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_100142e0(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int in_EAX;
  uint uVar4;
  uint uVar5;
  
  uVar1 = param_1[1];
  *(undefined4 *)(param_2 + 0x40c) = *param_1;
  uVar2 = param_1[2];
  *(undefined4 *)(param_2 + 0x450) = 0;
  *(undefined4 *)(param_2 + 0x414) = uVar2;
  *(undefined4 *)(param_2 + 0x410) = uVar1;
  *(undefined4 *)(param_2 + 0x418) = DAT_106b4090;
  *(undefined4 *)(param_2 + 0x41c) = DAT_106b4094;
  *(undefined4 *)(param_2 + 0x420) = DAT_106b4098;
  if (*(int *)(param_2 + 0x454) != 0) {
    *(undefined4 *)(param_2 + 0x454) = 0;
    _DAT_1004f9dc = 0;
    *(undefined4 *)(param_2 + 0x440) = 0;
    *(uint *)(param_2 + 0x428) = ~*(uint *)(param_2 + 0x428) & 0x80 | 0x16;
    *(undefined4 *)(param_2 + 0x1c) = uVar1;
    *(undefined4 *)(param_2 + 0x20) = 0;
    *(undefined4 *)(param_2 + 0x448) = 0;
    *(uint *)(param_2 + 0x42c) = ~*(uint *)(param_2 + 0x42c) & 0x80 | 0xb;
    *(undefined4 *)(param_2 + 0x54) = uVar1;
    *(undefined4 *)(param_2 + 0x58) = 0;
    if (in_EAX == -1) {
      return;
    }
    *(int *)(param_2 + 0x430) = in_EAX;
    *(int *)(param_2 + 0x424) = in_EAX;
    *(int *)(param_2 + 0x434) = in_EAX;
    *(undefined4 *)(param_2 + 0x438) = 0xffffffff;
    *(undefined4 *)(param_2 + 0x43c) = 0;
    FUN_10011c50();
    return;
  }
  if (in_EAX == -1) {
    *(undefined4 *)(param_2 + 0x438) = 0xffffffff;
    *(undefined4 *)(param_2 + 0x43c) = 0;
  }
  else if (in_EAX != 0) {
    *(int *)(param_2 + 0x438) = in_EAX;
    *(int *)(param_2 + 0x43c) = DAT_1004fe5c + 0xfa;
  }
  iVar3 = *(int *)(param_2 + 0x434);
  uVar4 = *(uint *)(param_2 + 0x428) & 0xffffff7f;
  *(int *)(param_2 + 0x430) = iVar3;
  if ((uVar4 == 0x12) || (uVar4 == 0x13)) {
    *(undefined4 *)(param_2 + 0x440) = 0x16;
  }
  else if (uVar4 != 0x16) {
    _DAT_1004f9dc = 0;
    *(undefined4 *)(param_2 + 0x440) = 0;
    FUN_10011f40();
  }
  if ((iVar3 == 0) || (uVar4 = 0xb, iVar3 == 1)) {
    uVar4 = 0xc;
  }
  uVar5 = *(uint *)(param_2 + 0x42c) & 0xffffff7f;
  if (((iVar3 == *(int *)(param_2 + 0x424)) && (uVar5 != 10)) && (uVar5 != 9)) {
    if ((uVar5 != 6) && (uVar5 != 7)) {
      if (uVar4 == uVar5) {
        return;
      }
      *(undefined4 *)(param_2 + 0x448) = 0;
      FUN_10011fc0();
      return;
    }
    if (uVar4 == uVar5) {
      return;
    }
  }
  *(uint *)(param_2 + 0x448) = uVar4;
  return;
}



/* FUN_10019180 @ 10019180 size 463 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 __fastcall FUN_10019180(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  float *pfVar3;
  float *unaff_ESI;
  float fVar4;
  float fVar5;
  undefined8 uVar6;
  float local_28;
  
  iVar1 = DAT_106b40d0;
  if (unaff_ESI[0x56] != 0.0) {
    local_28 = *unaff_ESI;
    fVar4 = (float)*(int *)(DAT_106b40d0 + 0xf0);
    fVar5 = (float)*(int *)(DAT_106b40d0 + 0xf4);
    if ((((local_28 < fVar4) && (fVar4 < unaff_ESI[2] + local_28)) && (unaff_ESI[1] < fVar5)) &&
       ((fVar5 < unaff_ESI[3] + unaff_ESI[1] &&
        ((((param_1 == 0xb2 || (param_1 == 0xd)) || ((param_1 == 0xb3 || (param_1 == 0xb4)))) &&
         (unaff_ESI[0xa2] != 0.0)))))) {
      if (unaff_ESI[0x4c] != 0.0) {
        local_28 = unaff_ESI[0x42] + unaff_ESI[0x40] + (float)_DAT_10029220;
      }
      uVar6 = FUN_10015c00(fVar4,fVar5);
      pfVar3 = (float *)((ulonglong)uVar6 >> 0x20);
      if ((int)uVar6 != 0) {
        fVar5 = *pfVar3;
        uVar2 = FUN_10001900(&DAT_100290e8,
                             (double)(fVar5 + (pfVar3[1] - fVar5) *
                                              ((fVar4 - local_28) / (float)_DAT_10029218)));
        (**(code **)(iVar1 + 0x60))(unaff_ESI[0x56],uVar2);
        return 1;
      }
    }
  }
  (**(code **)(iVar1 + 0xa0))();
  return 0;
}



/* FUN_10016fc0 @ 10016fc0 size 461 */

void __thiscall FUN_10016fc0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  undefined4 *puVar5;
  undefined1 auStack_1c [4];
  undefined4 local_18;
  float local_14;
  undefined4 local_10;
  float local_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_1c;
  puVar5 = (undefined4 *)(DAT_106b40d0 + 0xf214);
  if (((param_1 == 0) || ((*(uint *)(param_1 + 0x48) & 0x12) != 0)) ||
     ((*(uint *)(param_1 + 0x48) & 4) == 0)) {
LAB_10017178:
    __security_check_cookie(local_8 ^ (uint)auStack_1c);
    return;
  }
  iVar1 = *(int *)(param_1 + 0x134);
  if ((*(byte *)(param_1 + 0x17c) & 3) != 0) {
    iVar2 = FUN_10016e70(1);
    if (iVar2 == 0) goto LAB_10017178;
  }
  if ((*(byte *)(param_1 + 0x17c) & 0xc) != 0) {
    iVar2 = FUN_10016e70(4);
    if (iVar2 == 0) goto LAB_10017178;
  }
  iVar2 = FUN_10015a80();
  if (*(int *)(param_1 + 0x110) == 0) {
    local_14 = *(float *)(param_1 + 0x104);
    local_10 = *(undefined4 *)(param_1 + 0x108);
    local_18 = *(undefined4 *)(param_1 + 0x100);
    local_c = *(float *)(param_1 + 0x10c);
    (**(code **)(DAT_106b40d0 + 0xd4))(0,0,&local_10,&local_c);
    local_14 = local_14 - local_c;
    iVar3 = FUN_10015c00(param_2,param_3);
    if (iVar3 == 0) {
      if ((iVar2 != 0) &&
         (*(uint *)(iVar2 + 0x48) = *(uint *)(iVar2 + 0x48) | 2, *(int *)(iVar2 + 0x150) != 0)) {
        FUN_10016d70(iVar2);
      }
      goto LAB_10017122;
    }
    *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 2;
  }
  else {
    *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 2;
    if (*(int *)(param_1 + 0x150) != 0) {
      FUN_10016d70(param_1);
    }
  }
  if (*(int *)(param_1 + 0x188) != 0) {
    puVar5 = (undefined4 *)(param_1 + 0x188);
  }
  if (puVar5 != (undefined4 *)0x0) {
    (**(code **)(DAT_106b40d0 + 0x74))(*puVar5,6);
  }
LAB_10017122:
  iVar2 = 0;
  if (0 < *(int *)(iVar1 + 0x10c)) {
    piVar4 = (int *)(iVar1 + 0x154);
    while (*piVar4 != param_1) {
      iVar2 = iVar2 + 1;
      piVar4 = piVar4 + 1;
      if (*(int *)(iVar1 + 0x10c) <= iVar2) {
        __security_check_cookie(local_8 ^ (uint)auStack_1c);
        return;
      }
    }
    *(int *)(iVar1 + 0x114) = iVar2;
  }
  __security_check_cookie(local_8 ^ (uint)auStack_1c);
  return;
}



/* FUN_100165e0 @ 100165e0 size 452 */

void FUN_100165e0(undefined4 param_1,float param_2,float param_3,float param_4,float param_5,
                 float param_6,float param_7,float param_8,float param_9,float param_10)

{
  float *pfVar1;
  int iVar2;
  float *pfVar3;
  uint uVar4;
  int iVar5;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST0_01;
  float10 extraout_ST0_02;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  
  iVar2 = FUN_10015c50();
  iVar5 = 0;
  if (0 < iVar2) {
    do {
      pfVar3 = (float *)FUN_10015cc0(param_1,iVar5);
      if (pfVar3 != (float *)0x0) {
        pfVar3[0x12] = (float)((uint)pfVar3[0x12] | 0x104);
        pfVar3[0x1c] = param_10;
        pfVar3[4] = param_2;
        pfVar3[5] = param_3;
        pfVar3[6] = param_4;
        pfVar3[7] = param_5;
        pfVar3[0x14] = param_6;
        pfVar3[0x15] = param_7;
        pfVar3[0x16] = param_8;
        pfVar3[0x17] = param_9;
        uVar4 = FUN_10021270();
        pfVar3[0x18] = (float)((float10)(int)((uVar4 ^ (int)uVar4 >> 0x1f) - ((int)uVar4 >> 0x1f)) /
                              extraout_ST0);
        uVar4 = FUN_10021270();
        pfVar3[0x19] = (float)((float10)(int)((uVar4 ^ (int)uVar4 >> 0x1f) - ((int)uVar4 >> 0x1f)) /
                              extraout_ST0_00);
        uVar4 = FUN_10021270();
        pfVar3[0x1a] = (float)((float10)(int)((uVar4 ^ (int)uVar4 >> 0x1f) - ((int)uVar4 >> 0x1f)) /
                              extraout_ST0_01);
        uVar4 = FUN_10021270();
        pfVar1 = (float *)pfVar3[0x4d];
        pfVar3[0x1b] = (float)((float10)(int)((uVar4 ^ (int)uVar4 >> 0x1f) - ((int)uVar4 >> 0x1f)) /
                              extraout_ST0_02);
        if (pfVar1 != (float *)0x0) {
          local_18 = *pfVar1;
          local_14 = pfVar1[1];
          if (pfVar1[0xd] != 0.0) {
            local_18 = pfVar1[0x11] + local_18;
            local_14 = pfVar1[0x11] + local_14;
          }
          local_10 = local_18;
          local_c = local_14;
          if (pfVar3[0xd] != 0.0) {
            local_10 = pfVar3[0x11] + local_18;
            local_c = pfVar3[0x11] + local_14;
          }
          pfVar3[0x42] = 0.0;
          pfVar3[0x43] = 0.0;
          *pfVar3 = local_10 + pfVar3[4];
          pfVar3[1] = pfVar3[5] + local_c;
          pfVar3[2] = pfVar3[6];
          pfVar3[3] = pfVar3[7];
        }
      }
      iVar5 = iVar5 + 1;
    } while (iVar5 < iVar2);
  }
  return;
}



/* FUN_10005690 @ 10005690 size 437 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10005690(undefined4 *param_1)

{
  float10 fVar1;
  undefined1 auStack_258 [4];
  undefined4 uStack_254;
  undefined4 uStack_250;
  undefined4 uStack_24c;
  char acStack_248 [63];
  undefined1 uStack_209;
  char acStack_208 [255];
  undefined1 uStack_109;
  undefined1 auStack_108 [260];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_258;
  (**(code **)(DAT_106b40a8 + 0x24))("model",&DAT_10042f38,0x400);
  strncpy(acStack_248,&DAT_10042f38,0x3f);
  uStack_209 = 0;
  (**(code **)(DAT_106b40a8 + 0x24))("headmodel",&DAT_10042f38,0x400);
  strncpy(acStack_208,&DAT_10042f38,0xff);
  uStack_109 = 0;
  auStack_108[0] = 0;
  fVar1 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_loadout");
  if (fVar1 != (float10)0) {
    (**(code **)(DAT_106b40a8 + 0x28))("cg_weaponPrimary");
    FUN_10021270();
  }
  if (DAT_1002aedc != 0) {
    memset(&DAT_1004f560,0,0x47c);
    uStack_250 = DAT_10029500;
    uStack_254 = DAT_10029380;
    uStack_24c = 0;
    FUN_10014250(acStack_208,auStack_108);
    FUN_100142e0();
    DAT_1002aedc = 0;
  }
  _DAT_1004f9c8 = 0;
  FUN_10012d90(*param_1,param_1[1],param_1[2],param_1[3]);
  __security_check_cookie(local_4 ^ (uint)auStack_258);
  return;
}



/* FUN_1001ad40 @ 1001ad40 size 434 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001ad40(void)

{
  int iVar1;
  undefined4 uVar2;
  int unaff_ESI;
  float10 fVar3;
  undefined1 auStack_30 [4];
  float local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_30;
  iVar1 = *(int *)(unaff_ESI + 0x134);
  if ((*(byte *)(unaff_ESI + 0x48) & 2) == 0) {
    local_28 = *(undefined4 *)(unaff_ESI + 0x78);
    local_24 = *(undefined4 *)(unaff_ESI + 0x7c);
    local_20 = *(undefined4 *)(unaff_ESI + 0x80);
    local_1c = *(undefined4 *)(unaff_ESI + 0x84);
  }
  else {
    local_c = (float)_DAT_10029448;
    local_18 = *(float *)(iVar1 + 0x134) * local_c;
    local_14 = *(float *)(iVar1 + 0x138) * local_c;
    local_10 = *(float *)(iVar1 + 0x13c) * local_c;
    local_c = local_c * *(float *)(iVar1 + 0x140);
    local_2c = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fVar3 = (float10)_CIsin();
    local_2c = (float)((float10)_DAT_10029278 + fVar3 * (float10)_DAT_10029278);
    FUN_100147a0(local_2c);
  }
  uVar2 = FUN_10018280();
  if (*(int *)(unaff_ESI + 0x130) != 0) {
    FUN_1001a7e0();
    local_2c = *(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) + (float)_DAT_10029220;
    (**(code **)(DAT_106b40d0 + 0x10))
              (local_2c,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
               *(undefined4 *)(unaff_ESI + 0x128),&local_28,uVar2,0,0,
               *(undefined4 *)(unaff_ESI + 300));
    __security_check_cookie(local_8 ^ (uint)auStack_30);
    return;
  }
  (**(code **)(DAT_106b40d0 + 0x10))
            (*(undefined4 *)(unaff_ESI + 0x100),*(undefined4 *)(unaff_ESI + 0x104),
             *(undefined4 *)(unaff_ESI + 0x124),*(undefined4 *)(unaff_ESI + 0x128),&local_28,uVar2,0
             ,0,*(undefined4 *)(unaff_ESI + 300));
  __security_check_cookie(local_8 ^ (uint)auStack_30);
  return;
}



/* FUN_1001af00 @ 1001af00 size 434 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_1001af00(void)

{
  int iVar1;
  undefined4 uVar2;
  int unaff_ESI;
  float10 fVar3;
  undefined1 auStack_30 [4];
  float local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  float local_18;
  float local_14;
  float local_10;
  float local_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_30;
  iVar1 = *(int *)(unaff_ESI + 0x134);
  if ((*(byte *)(unaff_ESI + 0x48) & 2) == 0) {
    local_28 = *(undefined4 *)(unaff_ESI + 0x78);
    local_24 = *(undefined4 *)(unaff_ESI + 0x7c);
    local_20 = *(undefined4 *)(unaff_ESI + 0x80);
    local_1c = *(undefined4 *)(unaff_ESI + 0x84);
  }
  else {
    local_c = (float)_DAT_10029448;
    local_18 = *(float *)(iVar1 + 0x134) * local_c;
    local_14 = *(float *)(iVar1 + 0x138) * local_c;
    local_10 = *(float *)(iVar1 + 0x13c) * local_c;
    local_c = local_c * *(float *)(iVar1 + 0x140);
    local_2c = (float)(*(int *)(DAT_106b40d0 + 0xe8) / 0x4b);
    fVar3 = (float10)_CIsin();
    local_2c = (float)((float10)_DAT_10029278 + fVar3 * (float10)_DAT_10029278);
    FUN_100147a0(local_2c);
  }
  uVar2 = FUN_10018510();
  if (*(int *)(unaff_ESI + 0x130) != 0) {
    FUN_1001a7e0();
    local_2c = *(float *)(unaff_ESI + 0x108) + *(float *)(unaff_ESI + 0x100) + (float)_DAT_10029220;
    (**(code **)(DAT_106b40d0 + 0x10))
              (local_2c,*(undefined4 *)(unaff_ESI + 0x104),*(undefined4 *)(unaff_ESI + 0x124),
               *(undefined4 *)(unaff_ESI + 0x128),&local_28,uVar2,0,0,
               *(undefined4 *)(unaff_ESI + 300));
    __security_check_cookie(local_8 ^ (uint)auStack_30);
    return;
  }
  (**(code **)(DAT_106b40d0 + 0x10))
            (*(undefined4 *)(unaff_ESI + 0x100),*(undefined4 *)(unaff_ESI + 0x104),
             *(undefined4 *)(unaff_ESI + 0x124),*(undefined4 *)(unaff_ESI + 0x128),&local_28,uVar2,0
             ,0,*(undefined4 *)(unaff_ESI + 300));
  __security_check_cookie(local_8 ^ (uint)auStack_30);
  return;
}



/* FUN_1001a630 @ 1001a630 size 431 */

void __fastcall FUN_1001a630(int param_1)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  char *pcVar4;
  char *_Str;
  float fStack_82c;
  int iStack_828;
  undefined4 uStack_824;
  int iStack_820;
  undefined1 local_81c [16];
  char acStack_80c [1024];
  char local_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)&fStack_82c;
  _Str = *(char **)(param_1 + 0x130);
  if (_Str == (char *)0x0) {
    if (*(int *)(param_1 + 0x158) == 0) goto LAB_1001a7c6;
    (**(code **)(DAT_106b40d0 + 0x58))(*(int *)(param_1 + 0x158),local_40c,0x400);
    _Str = local_40c;
  }
  if (*_Str != '\0') {
    FUN_1001a150(local_81c);
    FUN_10019f10(_Str);
    uStack_824 = *(undefined4 *)(param_1 + 0x100);
    fStack_82c = *(float *)(param_1 + 0x104);
    pcVar4 = strchr(_Str,0xd);
    while ((pcVar4 != (char *)0x0 && (*pcVar4 != '\0'))) {
      strncpy(acStack_80c,_Str,(size_t)(pcVar4 + (1 - (int)_Str)));
      uVar2 = *(undefined4 *)(param_1 + 300);
      uVar1 = *(undefined4 *)(param_1 + 0x128);
      uVar3 = *(undefined4 *)(param_1 + 0x124);
      pcVar4[(int)(acStack_80c + -(int)_Str)] = '\0';
      (**(code **)(DAT_106b40d0 + 0x10))
                (uStack_824,fStack_82c,uVar3,uVar1,local_81c,acStack_80c,0,0,uVar2);
      iStack_828 = iStack_820 + 5;
      _Str = pcVar4 + 1;
      fStack_82c = (float)iStack_828 + fStack_82c;
      pcVar4 = strchr(_Str,0xd);
    }
    (**(code **)(DAT_106b40d0 + 0x10))
              (uStack_824,fStack_82c,*(undefined4 *)(param_1 + 0x124),
               *(undefined4 *)(param_1 + 0x128),local_81c,_Str,0,0,*(undefined4 *)(param_1 + 300));
  }
LAB_1001a7c6:
  __security_check_cookie(local_8 ^ (uint)&fStack_82c);
  return;
}



/* FUN_1001d600 @ 1001d600 size 426 */

void FUN_1001d600(int param_1,undefined4 param_2,undefined4 param_3)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int local_8;
  int local_4;
  
  local_4 = 0;
  if ((((param_1 != 0) && ((*(uint *)(param_1 + 0x48) & 0x100004) != 0)) && (DAT_106b40cc == 0)) &&
     ((DAT_106b40d4 == 0 && (DAT_106b40d8 == 0)))) {
    local_8 = 0;
    do {
      iVar4 = 0;
      if (0 < *(int *)(param_1 + 0x10c)) {
        piVar5 = (int *)(param_1 + 0x154);
        do {
          if ((*(uint *)(*piVar5 + 0x48) & 0x100004) != 0) {
            if ((*(byte *)(*piVar5 + 0x17c) & 3) != 0) {
              iVar2 = FUN_10016e70(1);
              if (iVar2 == 0) goto LAB_1001d77c;
            }
            if ((*(byte *)(*piVar5 + 0x17c) & 0xc) != 0) {
              iVar2 = FUN_10016e70(4);
              if (iVar2 == 0) goto LAB_1001d77c;
            }
            iVar2 = *piVar5;
            iVar3 = FUN_10015c00(param_2,param_3);
            if (iVar3 == 0) {
              if ((*(byte *)(iVar2 + 0x48) & 1) != 0) {
                FUN_10017b50();
                if (*piVar5 != 0) {
                  puVar1 = (uint *)(*piVar5 + 0x48);
                  *puVar1 = *puVar1 & 0xfffffffe;
                }
              }
            }
            else if (local_8 == 1) {
              if ((*(int *)(iVar2 + 0x110) == 0) && (*(int *)(iVar2 + 0x130) != 0)) {
                FUN_10019970(param_2,param_3);
                iVar3 = FUN_10015c00();
                if (iVar3 == 0) goto LAB_1001d77c;
              }
              if (((*(uint *)(iVar2 + 0x48) & 4) != 0) && ((*(uint *)(iVar2 + 0x48) & 0x20) == 0)) {
                FUN_100179d0(param_2,param_3);
                if (local_4 == 0) {
                  local_4 = FUN_10016fc0(param_2,param_3);
                }
              }
            }
          }
LAB_1001d77c:
          iVar4 = iVar4 + 1;
          piVar5 = piVar5 + 1;
        } while (iVar4 < *(int *)(param_1 + 0x10c));
      }
      local_8 = local_8 + 1;
    } while (local_8 < 2);
  }
  return;
}



/* FUN_10003ec0 @ 10003ec0 size 424 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10003ec0(float param_1,float param_2,undefined4 param_3,float param_4,undefined4 param_5,
                 int param_6,undefined4 param_7,int param_8,int param_9)

{
  float fVar1;
  float fVar2;
  float fVar3;
  
  if (param_6 != 0) {
    if (param_8 == 0) {
      param_8 = -1;
    }
    if (DAT_106b40a4 == _DAT_10029214) {
      DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
    }
    fVar2 = DAT_106b40a4;
    fVar3 = DAT_10029234;
    if ((param_9 == 3) || (fVar3 = DAT_10029358, param_9 == 6)) {
      fVar1 = _DAT_10746420 * (fVar3 + param_1) + DAT_10746424;
      fVar3 = _DAT_1074641c * (fVar3 + param_2);
      (**(code **)(DAT_106b40a8 + 0x74))(&DAT_1002bdb4);
      (**(code **)(DAT_106b40a8 + 0x178))
                ((int)fVar1,(int)fVar3,param_6,param_3,fVar2 * param_4,param_8,0,1);
    }
    fVar3 = _DAT_10746420 * param_1 + DAT_10746424;
    param_2 = _DAT_1074641c * param_2;
    (**(code **)(DAT_106b40a8 + 0x74))(param_5);
    (**(code **)(DAT_106b40a8 + 0x178))
              ((int)fVar3,(int)param_2,param_6,param_3,fVar2 * param_4,param_8,0,0);
    (**(code **)(DAT_106b40a8 + 0x74))(0);
  }
  return;
}



/* FUN_10018cb0 @ 10018cb0 size 421 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10018cb0(int *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  
  piVar3 = *(int **)(param_1[6] + 0x288);
  if ((*(uint *)(param_1[6] + 0x48) & 0x400) == 0) {
    iVar4 = DAT_106b40d0;
    if ((float)*(int *)(DAT_106b40d0 + 0xf4) != (float)param_1[5]) {
      iVar1 = FUN_10017190();
      iVar4 = DAT_106b40d0;
      iVar2 = FUN_10021270();
      if (iVar2 < 0) {
        iVar2 = 0;
      }
      else if (iVar1 < iVar2) {
        iVar2 = iVar1;
      }
      *piVar3 = iVar2;
      param_1[5] = (int)(float)*(int *)(iVar4 + 0xf4);
    }
  }
  else {
    if ((float)*(int *)(DAT_106b40d0 + 0xf0) == (float)param_1[4]) {
      return;
    }
    iVar1 = FUN_10017190();
    iVar4 = DAT_106b40d0;
    iVar2 = FUN_10021270();
    if (iVar2 < 0) {
      iVar2 = 0;
    }
    else if (iVar1 < iVar2) {
      iVar2 = iVar1;
    }
    *piVar3 = iVar2;
    param_1[4] = (int)(float)*(int *)(iVar4 + 0xf0);
  }
  piVar3 = (int *)(iVar4 + 0xe8);
  if (*param_1 < *(int *)(iVar4 + 0xe8)) {
    FUN_10017b90();
    piVar3 = (int *)(DAT_106b40d0 + 0xe8);
    *param_1 = param_1[2] + *piVar3;
  }
  if (param_1[1] < *piVar3) {
    param_1[1] = *piVar3 + 0x96;
    if (0x14 < param_1[2]) {
      param_1[2] = param_1[2] + -0x28;
    }
  }
  return;
}



/* FUN_10012760 @ 10012760 size 412 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10012760(void)

{
  float10 fVar1;
  float fVar2;
  float fVar3;
  
  fVar1 = (float10)_CIsin();
  _DAT_1002c928 = (float)fVar1;
  fVar1 = (float10)_CIcos();
  _DAT_1002c920 = (float)fVar1;
  fVar1 = (float10)_CIsin();
  DAT_1002c924 = (float)fVar1;
  fVar1 = (float10)_CIcos();
  _DAT_1002c92c = (float)fVar1;
  fVar1 = (float10)_CIsin();
  _DAT_1002c930 = (float)fVar1;
  fVar1 = (float10)_CIcos();
  _DAT_1002c8f8 = (float)fVar1;
  fVar2 = _DAT_1002c92c * _DAT_1002c920;
  fVar3 = _DAT_1002c92c * _DAT_1002c928;
  if (ABS(fVar2) < (float)_DAT_10029350) {
    fVar2 = 0.0;
  }
  if ((float)_DAT_10029350 <= ABS(fVar3)) {
    if (fVar3 != 0.0) goto LAB_10012893;
  }
  else {
    fVar3 = 0.0;
  }
  if (0.0 < fVar2) {
    return;
  }
LAB_10012893:
  if (fVar3 < 0.0) {
    if (0.0 < fVar2) {
      return;
    }
    if (fVar2 == 0.0) {
      return;
    }
    if (fVar2 < 0.0) {
      return;
    }
  }
  if (((fVar3 != 0.0) || (0.0 <= fVar2)) && (0.0 < fVar3)) {
    if (fVar2 < 0.0) {
      return;
    }
    if (fVar2 == 0.0) {
      return;
    }
  }
  return;
}



/* FUN_10018370 @ 10018370 size 412 */

undefined4 __fastcall FUN_10018370(int param_1)

{
  float fVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  float *unaff_ESI;
  
  fVar1 = unaff_ESI[0xa2];
  if (fVar1 != 0.0) {
    if ((((((*unaff_ESI < (float)*(int *)(DAT_106b40d0 + 0xf0)) &&
           ((float)*(int *)(DAT_106b40d0 + 0xf0) < unaff_ESI[2] + *unaff_ESI)) &&
          (unaff_ESI[1] < (float)*(int *)(DAT_106b40d0 + 0xf4))) &&
         (((float)*(int *)(DAT_106b40d0 + 0xf4) < unaff_ESI[3] + unaff_ESI[1] &&
          (((uint)unaff_ESI[0x12] & 2) != 0)))) && (unaff_ESI[0x56] != 0.0)) &&
       (((param_1 == 0xb2 || (param_1 == 0xd)) || ((param_1 == 0xb3 || (param_1 == 0xb4)))))) {
      iVar3 = FUN_100181a0();
      iVar2 = DAT_106b40d0;
      iVar3 = iVar3 + 1;
      iVar5 = 0;
      if (unaff_ESI[0xa2] != 0.0) {
        iVar5 = *(int *)((int)unaff_ESI[0xa2] + 0x180);
      }
      if ((iVar3 < 0) || (iVar5 <= iVar3)) {
        iVar3 = 0;
      }
      if (*(int *)((int)fVar1 + 0x184) == 0) {
        fVar1 = *(float *)((int)fVar1 + 0x100 + iVar3 * 4);
        if ((float)(int)fVar1 != fVar1) {
          uVar4 = FUN_10001900(&DAT_100290e8,(double)fVar1);
          (**(code **)(iVar2 + 0x60))(unaff_ESI[0x56],uVar4);
          return 1;
        }
        uVar4 = FUN_10001900(&DAT_10025920,(int)fVar1);
        (**(code **)(iVar2 + 0x60))(unaff_ESI[0x56],uVar4);
        return 1;
      }
      (**(code **)(DAT_106b40d0 + 0x60))
                (unaff_ESI[0x56],*(undefined4 *)((int)fVar1 + 0x80 + iVar3 * 4));
      return 1;
    }
  }
  return 0;
}



/* FUN_10018e60 @ 10018e60 size 411 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10018e60(int param_1)

{
  undefined4 *puVar1;
  float fVar2;
  float *pfVar3;
  int iVar4;
  undefined4 uVar5;
  code *pcVar6;
  undefined1 auStack_78 [36];
  float local_54;
  float local_50;
  float local_4c [2];
  uint local_44;
  
  local_44 = DAT_1002a000 ^ (uint)auStack_78;
  pfVar3 = *(float **)(param_1 + 0x18);
  if (pfVar3[0x4c] == 0.0) {
    local_54 = *pfVar3;
  }
  else {
    local_54 = pfVar3[0x42] + pfVar3[0x40] + (float)_DAT_10029220;
  }
  fVar2 = (float)*(int *)(DAT_106b40d0 + 0xf0);
  if (local_54 <= fVar2) {
    local_50 = local_54 + (float)_DAT_10029218;
    if (local_50 < fVar2) goto LAB_10018ee1;
  }
  else {
    local_50 = local_54;
    fVar2 = local_50;
  }
  local_50 = fVar2;
LAB_10018ee1:
  fVar2 = *(float *)pfVar3[0xa2];
  iVar4 = *(int *)(param_1 + 0x18);
  local_4c[0] = (((float *)pfVar3[0xa2])[1] - fVar2) *
                ((local_50 - local_54) / (float)_DAT_10029218);
  local_54 = fVar2 + local_4c[0];
  if (*(int *)(iVar4 + 0x184) == 0) {
    if (*(int *)(iVar4 + 0x180) == 0) {
      puVar1 = (undefined4 *)(DAT_106b40d0 + 0x60);
      uVar5 = FUN_10001900(&DAT_100290e8,(double)local_54);
      pcVar6 = (code *)*puVar1;
    }
    else {
      FUN_10001830(local_4c,6,"%%.%df",*(undefined4 *)(iVar4 + 0x180));
      iVar4 = DAT_106b40d0;
      uVar5 = FUN_10001900(local_4c,(double)local_54);
      pcVar6 = *(code **)(iVar4 + 0x60);
    }
    (*pcVar6)(*(undefined4 *)(*(int *)(param_1 + 0x18) + 0x158),uVar5);
    __security_check_cookie(local_44 ^ (uint)auStack_78);
    return;
  }
  puVar1 = (undefined4 *)(DAT_106b40d0 + 0x60);
  ceil((double)local_54);
  uVar5 = FUN_10021270();
  uVar5 = FUN_10001900(&DAT_10025d20,uVar5);
  (*(code *)*puVar1)(*(undefined4 *)(*(int *)(param_1 + 0x18) + 0x158),uVar5);
  __security_check_cookie(local_44 ^ (uint)auStack_78);
  return;
}



/* FUN_10003990 @ 10003990 size 410 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10003990(void)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  _DAT_10755518 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/gradientbar2.tga");
  DAT_10755584 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_base");
  DAT_10755588 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_red");
  _DAT_1075558c = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_yel");
  _DAT_10755590 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_grn");
  _DAT_10755594 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_teal");
  _DAT_10755598 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_blue");
  _DAT_1075559c = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_cyan");
  _DAT_107555a0 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/fx_white");
  _DAT_1075552c = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar.tga");
  _DAT_10755520 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar_arrow_dwn_a.tga");
  _DAT_1075551c = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar_arrow_up_a.tga");
  _DAT_10755524 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar_arrow_left.tga");
  _DAT_10755528 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar_arrow_right.tga");
  _DAT_10755530 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/scrollbar_thumb.tga");
  _DAT_10755540 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/slider2.tga");
  _DAT_10755544 = (**(code **)(DAT_106b40a8 + 0x5c))("ui/assets/sliderbutt_1.tga");
  iVar3 = 1;
  do {
    iVar1 = DAT_106b40a8;
    uVar2 = FUN_10001900("gfx/2d/crosshair%d",iVar3);
    uVar2 = (**(code **)(iVar1 + 0x5c))(uVar2);
    *(undefined4 *)(&DAT_107555a4 + iVar3 * 4) = uVar2;
    iVar3 = iVar3 + 1;
  } while (iVar3 < 0x1e);
  return;
}



/* FUN_10004e10 @ 10004e10 size 403 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall FUN_10004e10(undefined4 param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iStack_424;
  undefined1 auStack_420 [16];
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)&iStack_424;
  iStack_424 = (**(code **)(DAT_106b40a8 + 8))();
  iVar1 = (**(code **)(DAT_106b40a8 + 0x164))(param_1);
  iVar3 = DAT_106b40a8;
  if (iVar1 == 0) {
    uVar2 = FUN_10001900("^3menu file not found: %s, using default\n",param_1);
    (**(code **)(iVar3 + 4))(uVar2);
    iVar1 = (**(code **)(DAT_106b40a8 + 0x164))("ui/menus.txt");
    iVar3 = DAT_106b40a8;
    if (iVar1 == 0) {
      uVar2 = FUN_10001900("^1default menu file not found: ui/menus.txt, unable to continue!\n",
                           param_1);
      (**(code **)(iVar3 + 4))(uVar2);
    }
  }
  _DAT_1076886c = 1;
  if (param_2 != 0) {
    DAT_106b40e4 = 0;
  }
  iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(iVar1,auStack_420);
  while (((iVar3 != 0 && (acStack_410[0] != '\0')) && (acStack_410[0] != '}'))) {
    iVar6 = 0;
    iVar3 = 99999;
    do {
      iVar4 = (int)acStack_410[iVar6];
      iVar5 = (int)"loadmenu"[iVar6];
      iVar6 = iVar6 + 1;
      if (iVar3 == 0) break;
      if (iVar4 != iVar5) {
        if (iVar4 - 0x61U < 0x1a) {
          iVar4 = iVar4 + -0x20;
        }
        if (iVar5 - 0x61U < 0x1a) {
          iVar5 = iVar5 + -0x20;
        }
        if (iVar4 != iVar5) {
          if ((char)((iVar5 <= iVar4) * '\x02') != '\x01') goto LAB_10004f44;
          break;
        }
      }
      iVar3 = iVar3 + -1;
    } while (iVar4 != 0);
    iVar3 = FUN_10004b20(iVar1);
    if (iVar3 == 0) break;
LAB_10004f44:
    iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(iVar1,auStack_420);
  }
  iVar3 = (**(code **)(DAT_106b40a8 + 8))();
  FUN_10001ee0("UI menu load time = %d milli seconds\n",iVar3 - iStack_424);
  (**(code **)(DAT_106b40a8 + 0x168))(iVar1);
  __security_check_cookie(local_c ^ (uint)&iStack_424);
  return;
}



/* FUN_1001f1d0 @ 1001f1d0 size 402 */

void FUN_1001f1d0(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  double dVar4;
  float fStack_424;
  undefined1 local_420 [16];
  char cStack_410;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)&fStack_424;
  FUN_1001da70();
  iVar2 = DAT_106b40a8;
  iVar1 = *(int *)(param_1 + 0x288);
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x180) = 0;
    *(undefined4 *)(iVar1 + 0x184) = 0;
    iVar2 = (**(code **)(iVar2 + 0x16c))(param_2,local_420);
    if ((iVar2 != 0) && (cStack_410 == '{')) {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      do {
        if (iVar2 == 0) {
          FUN_10014710(param_2,"end of file inside menu item\n");
          __security_check_cookie(local_c ^ (uint)&fStack_424);
          return;
        }
        if (cStack_410 == '}') {
          __security_check_cookie(local_c ^ (uint)&fStack_424);
          return;
        }
        if ((cStack_410 != ',') && (cStack_410 != ';')) {
          uVar3 = FUN_10014560();
          *(undefined4 *)(iVar1 + *(int *)(iVar1 + 0x180) * 4) = uVar3;
          iVar2 = FUN_10014c60();
          if (iVar2 == 0) {
            *(undefined4 *)(iVar1 + 0x100 + *(int *)(iVar1 + 0x180) * 4) = 0;
            break;
          }
          dVar4 = atof(*(char **)(iVar1 + 0x80 + *(int *)(iVar1 + 0x180) * 4));
          fStack_424 = (float)dVar4;
          *(float *)(iVar1 + 0x100 + *(int *)(iVar1 + 0x180) * 4) = fStack_424;
          *(int *)(iVar1 + 0x180) = *(int *)(iVar1 + 0x180) + 1;
          if (0x1f < *(int *)(iVar1 + 0x180)) break;
        }
        iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      } while( true );
    }
  }
  __security_check_cookie(local_c ^ (uint)&fStack_424);
  return;
}



/* FUN_1000f340 @ 1000f340 size 383 */

undefined4 FUN_1000f340(int param_1)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  pcVar1 = (char *)FUN_10001500();
  if (*pcVar1 != '{') {
    return 0;
  }
  if (param_1 == 0) {
    DAT_107596a4 = 0;
  }
  else {
    DAT_10759728 = 0;
  }
  do {
    do {
      pcVar1 = (char *)FUN_10001500();
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      iVar2 = FUN_100016c0();
      if (iVar2 == 0) {
        return 1;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
    } while (*pcVar1 != '{');
    if (param_1 == 0) {
      iVar2 = DAT_107596a4 * 8;
      pcVar1 = (char *)FUN_10001500();
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
      uVar3 = FUN_10014560();
      *(undefined4 *)(&DAT_107596a8 + iVar2) = uVar3;
      iVar2 = DAT_107596a4 * 2;
      pcVar1 = (char *)FUN_10001500();
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
      iVar4 = atoi(pcVar1);
      (&DAT_107596ac)[iVar2] = iVar4;
      if (0xf < DAT_107596a4) {
        pcVar1 = "Too many game types, last one replace!\n";
        goto LAB_1000f494;
      }
      DAT_107596a4 = DAT_107596a4 + 1;
    }
    else {
      iVar2 = DAT_10759728 * 2;
      pcVar1 = (char *)FUN_10001500();
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
      uVar3 = FUN_10014560();
      (&DAT_1075972c)[iVar2] = uVar3;
      iVar2 = DAT_10759728 * 2;
      pcVar1 = (char *)FUN_10001500();
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
      iVar4 = atoi(pcVar1);
      (&DAT_10759730)[iVar2] = iVar4;
      if (DAT_10759728 < 0x10) {
        DAT_10759728 = DAT_10759728 + 1;
      }
      else {
        pcVar1 = "Too many net game types, last one replace!\n";
LAB_1000f494:
        FUN_10001ee0(pcVar1);
      }
    }
    pcVar1 = (char *)FUN_10001500();
    if (*pcVar1 != '}') {
      return 0;
    }
  } while( true );
}



/* FUN_10015a80 @ 10015a80 size 378 */

void __fastcall FUN_10015a80(int param_1)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  undefined1 *local_818;
  int *local_814;
  int local_810;
  int local_80c;
  int local_808;
  undefined1 local_804 [2048];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_818;
  local_810 = 0;
  local_808 = param_1;
  if (param_1 == 0) {
    __security_check_cookie(local_4 ^ (uint)&local_818);
    return;
  }
  local_80c = 0;
  if (0 < *(int *)(param_1 + 0x10c)) {
    piVar5 = (int *)(param_1 + 0x154);
    do {
      iVar1 = *piVar5;
      if ((*(byte *)(iVar1 + 0x48) & 2) != 0) {
        local_810 = iVar1;
      }
      *(uint *)(iVar1 + 0x48) = *(uint *)(iVar1 + 0x48) & 0xfffffffd;
      iVar1 = *piVar5;
      if (*(int *)(iVar1 + 0x154) != 0) {
        pcVar2 = *(char **)(iVar1 + 0x154);
        local_814 = piVar5;
        memset(local_804,0,0x800);
        if (((iVar1 != 0) && (pcVar2 != (char *)0x0)) && (*pcVar2 != '\0')) {
          FUN_10001750(pcVar2);
          local_818 = local_804;
LAB_10015b44:
          do {
            pcVar2 = (char *)FUN_10001500(&local_818,0);
            param_1 = local_808;
            piVar5 = local_814;
            if ((pcVar2 == (char *)0x0) || (*pcVar2 == '\0')) break;
            pcVar2 = (char *)FUN_10014560();
            if ((*pcVar2 != ';') || (pcVar2[1] != '\0')) {
              iVar4 = 0;
              do {
                if (((&PTR_s_fadein_1002a018)[iVar4 * 2] != (undefined *)0x0) &&
                   (iVar3 = FUN_100016c0(), iVar3 == 0)) {
                  (*(code *)(&PTR_FUN_1002a01c)[iVar4 * 2])(iVar1,&local_818);
                  goto LAB_10015b44;
                }
                iVar4 = iVar4 + 1;
              } while (iVar4 < 0x17);
              (**(code **)(DAT_106b40d0 + 0x50))(&local_818);
            }
          } while( true );
        }
      }
      local_80c = local_80c + 1;
      piVar5 = piVar5 + 1;
      local_814 = piVar5;
    } while (local_80c < *(int *)(param_1 + 0x10c));
  }
  __security_check_cookie(local_4 ^ (uint)&local_818);
  return;
}



/* FUN_100179d0 @ 100179d0 size 376 */

void __thiscall FUN_100179d0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 local_18;
  float local_14;
  undefined4 local_10;
  float local_c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)&local_18;
  if (param_1 != 0) {
    local_14 = *(float *)(param_1 + 0x104);
    local_10 = *(undefined4 *)(param_1 + 0x108);
    local_18 = *(undefined4 *)(param_1 + 0x100);
    local_c = *(float *)(param_1 + 0x10c);
    (**(code **)(DAT_106b40d0 + 0xd4))(0,0,&local_10,&local_c);
    local_14 = local_14 - local_c;
    if ((*(byte *)(param_1 + 0x17c) & 3) != 0) {
      iVar1 = FUN_10016e70(1);
      if (iVar1 == 0) goto LAB_10017b36;
    }
    if ((*(byte *)(param_1 + 0x17c) & 0xc) != 0) {
      iVar1 = FUN_10016e70(4);
      if (iVar1 == 0) goto LAB_10017b36;
    }
    iVar1 = FUN_10015c00(param_2,param_3);
    if (iVar1 == 0) {
      if ((*(byte *)(param_1 + 0x48) & 0x80) != 0) {
        FUN_10016d70(param_1);
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) & 0xffffff7f;
      }
      if ((*(byte *)(param_1 + 0x48) & 1) == 0) {
        FUN_10016d70(param_1);
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 1;
      }
      if (*(int *)(param_1 + 0x110) == 6) {
        FUN_10017880(param_2,param_3);
      }
    }
    else {
      if ((*(byte *)(param_1 + 0x48) & 0x80) == 0) {
        FUN_10016d70(param_1);
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 0x80;
      }
      if ((*(byte *)(param_1 + 0x48) & 1) == 0) {
        FUN_10016d70(param_1);
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 1;
        __security_check_cookie(local_8 ^ (uint)&local_18);
        return;
      }
    }
  }
LAB_10017b36:
  __security_check_cookie(local_8 ^ (uint)&local_18);
  return;
}



/* FUN_10001500 @ 10001500 size 359 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined1 * FUN_10001500(undefined4 *param_1,int param_2)

{
  char *pcVar1;
  bool bVar2;
  char *pcVar3;
  char cVar4;
  int iVar5;
  
  pcVar3 = (char *)*param_1;
  bVar2 = false;
  iVar5 = 0;
  DAT_10030938 = 0;
  if (pcVar3 == (char *)0x0) {
    *param_1 = 0;
    return &DAT_10030938;
  }
LAB_10001530:
  do {
    cVar4 = *pcVar3;
    while (cVar4 < '!') {
      if (cVar4 == '\0') {
        *param_1 = 0;
        return &DAT_10030938;
      }
      if (cVar4 == '\n') {
        bVar2 = true;
        _DAT_1002c934 = _DAT_1002c934 + 1;
      }
      pcVar1 = pcVar3 + 1;
      pcVar3 = pcVar3 + 1;
      cVar4 = *pcVar1;
    }
    if ((bVar2) && (param_2 == 0)) {
LAB_1000165a:
      *param_1 = pcVar3;
      return &DAT_10030938;
    }
    cVar4 = *pcVar3;
    if (cVar4 != '/') {
      if (cVar4 != '\"') goto LAB_10001623;
      cVar4 = pcVar3[1];
      pcVar3 = pcVar3 + 2;
      while ((cVar4 != '\"' && (cVar4 != '\0'))) {
        if (iVar5 < 0x400) {
          (&DAT_10030938)[iVar5] = cVar4;
          iVar5 = iVar5 + 1;
        }
        cVar4 = *pcVar3;
        pcVar3 = pcVar3 + 1;
      }
      (&DAT_10030938)[iVar5] = 0;
      *param_1 = pcVar3;
      return &DAT_10030938;
    }
    if (pcVar3[1] == '/') {
      pcVar1 = pcVar3 + 2;
      pcVar3 = pcVar3 + 2;
      cVar4 = *pcVar1;
      while ((cVar4 != '\0' && (cVar4 != '\n'))) {
        pcVar1 = pcVar3 + 1;
        pcVar3 = pcVar3 + 1;
        cVar4 = *pcVar1;
      }
      goto LAB_10001530;
    }
    if (pcVar3[1] != '*') {
      do {
        (&DAT_10030938)[iVar5] = cVar4;
        iVar5 = iVar5 + 1;
        do {
          cVar4 = pcVar3[1];
          pcVar3 = pcVar3 + 1;
          if (cVar4 == '\n') {
            _DAT_1002c934 = _DAT_1002c934 + 1;
LAB_10001649:
            if (iVar5 == 0x400) {
              iVar5 = 0;
            }
            (&DAT_10030938)[iVar5] = 0;
            goto LAB_1000165a;
          }
          if (cVar4 < '!') goto LAB_10001649;
LAB_10001623:
        } while (0x3ff < iVar5);
      } while( true );
    }
    pcVar1 = pcVar3 + 2;
    pcVar3 = pcVar3 + 2;
    cVar4 = *pcVar1;
    while (cVar4 != '\0') {
      if ((cVar4 == '*') && (pcVar3[1] == '/')) {
        if (*pcVar3 != '\0') {
          pcVar3 = pcVar3 + 2;
        }
        break;
      }
      pcVar1 = pcVar3 + 1;
      pcVar3 = pcVar3 + 1;
      cVar4 = *pcVar1;
    }
  } while( true );
}



/* FUN_10019000 @ 10019000 size 358 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10019000(void)

{
  int in_EAX;
  uint uVar1;
  undefined4 unaff_EDI;
  
  switch(*(undefined4 *)(in_EAX + 0x110)) {
  case 4:
  case 6:
  case 9:
    uVar1 = FUN_10017570((float)*(int *)(DAT_106b40d0 + 0xf0),(float)*(int *)(DAT_106b40d0 + 0xf4));
    if ((uVar1 & 0x1800) != 0) {
      _DAT_106b306c = *(int *)(DAT_106b40d0 + 0xe8) + 500;
      _DAT_106b3070 = *(int *)(DAT_106b40d0 + 0xe8) + 0x96;
      _DAT_106b3074 = 500;
      _DAT_106b3078 = unaff_EDI;
      _DAT_106b3088 = uVar1 >> 0xb & 1;
      _DAT_106b3084 = in_EAX;
      DAT_106b40c4 = (code *)&LAB_10018c50;
      DAT_106b40c8 = &DAT_106b306c;
      DAT_106b40cc = in_EAX;
      return;
    }
    if ((uVar1 & 0x2000) == 0) {
      return;
    }
    DAT_106b40c4 = FUN_10018cb0;
    break;
  default:
    goto switchD_1001901c_caseD_5;
  case 10:
  case 0xe:
    uVar1 = FUN_10017500((float)*(int *)(DAT_106b40d0 + 0xf0),(float)*(int *)(DAT_106b40d0 + 0xf4));
    if ((uVar1 & 0x2000) == 0) {
      return;
    }
    DAT_106b40c4 = FUN_10018e60;
  }
  _DAT_106b307c = (float)*(int *)(DAT_106b40d0 + 0xf0);
  _DAT_106b3080 = (float)*(int *)(DAT_106b40d0 + 0xf4);
  DAT_106b40c8 = &DAT_106b306c;
  _DAT_106b3078 = unaff_EDI;
  _DAT_106b3084 = in_EAX;
  DAT_106b40cc = in_EAX;
switchD_1001901c_caseD_5:
  return;
}



/* FUN_1000f140 @ 1000f140 size 355 */

undefined4 FUN_1000f140(undefined4 param_1)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  
  pcVar1 = (char *)FUN_10001500(param_1,1);
  iVar4 = DAT_1075829c;
  if (*pcVar1 != '{') {
    return 0;
  }
  while( true ) {
    do {
      pcVar1 = (char *)FUN_10001500(param_1,1);
      if (pcVar1 == (char *)0x0) {
        return 0;
      }
      iVar2 = FUN_100016c0();
      if (iVar2 == 0) {
        return 1;
      }
      if (*pcVar1 == '\0') {
        return 0;
      }
    } while (*pcVar1 != '{');
    pcVar1 = (char *)FUN_10001500(param_1,0);
    if (pcVar1 == (char *)0x0) {
      return 0;
    }
    if (*pcVar1 == '\0') break;
    uVar3 = FUN_10014560();
    (&DAT_107582b0)[iVar4 * 5] = uVar3;
    iVar4 = DAT_1075829c * 5;
    pcVar1 = (char *)FUN_10001500(param_1,0);
    if (pcVar1 == (char *)0x0) {
      return 0;
    }
    if (*pcVar1 == '\0') {
      return 0;
    }
    uVar3 = FUN_10014560();
    (&DAT_107582a4)[iVar4] = uVar3;
    (&DAT_107582ac)[DAT_1075829c * 5] = 0xffffffff;
    FUN_10001900("models/players/%s/icon_%s.tga",(&DAT_107582b0)[DAT_1075829c * 5],
                 (&DAT_107582a4)[DAT_1075829c * 5]);
    uVar3 = FUN_10014560();
    (&DAT_107582a8)[DAT_1075829c * 5] = uVar3;
    if (DAT_1075829c < 0x100) {
      DAT_1075829c = DAT_1075829c + 1;
    }
    else {
      FUN_10001ee0("Too many characters, last character replaced!\n");
    }
    iVar4 = DAT_1075829c;
    pcVar1 = (char *)FUN_10001500(param_1,1);
    if (*pcVar1 != '}') {
      return 0;
    }
  }
  return 0;
}



/* FUN_10015f90 @ 10015f90 size 352 */

void FUN_10015f90(int param_1,undefined4 param_2)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  int local_20;
  int local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_20;
  local_1c = param_1;
  pcVar1 = (char *)FUN_10001500(param_2,0);
  if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
    local_18 = FUN_10014560();
    pcVar1 = (char *)FUN_10001500(param_2,0);
    if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
      iVar2 = FUN_10014560();
      local_20 = FUN_10015c50();
      iVar3 = FUN_10014990();
      if ((iVar3 != 0) && (iVar3 = 0, 0 < local_20)) {
        do {
          iVar4 = FUN_10015cc0(*(undefined4 *)(local_1c + 0x134),iVar3);
          if ((iVar4 != 0) && (iVar2 != 0)) {
            iVar5 = FUN_100016c0();
            if (iVar5 == 0) {
              puVar6 = (undefined4 *)(iVar4 + 0x88);
            }
            else {
              iVar5 = FUN_100016c0();
              if (iVar5 == 0) {
                *(uint *)(iVar4 + 0x48) = *(uint *)(iVar4 + 0x48) | 0x200;
                puVar6 = (undefined4 *)(iVar4 + 0x78);
              }
              else {
                iVar5 = FUN_100016c0();
                if (iVar5 != 0) goto LAB_100160d2;
                puVar6 = (undefined4 *)(iVar4 + 0x98);
              }
            }
            if (puVar6 != (undefined4 *)0x0) {
              *puVar6 = local_14;
              puVar6[1] = local_10;
              puVar6[2] = local_c;
              puVar6[3] = local_8;
            }
          }
LAB_100160d2:
          iVar3 = iVar3 + 1;
        } while (iVar3 < local_20);
      }
    }
  }
  __security_check_cookie(local_4 ^ (uint)&local_20);
  return;
}



/* FUN_100012a0 @ 100012a0 size 346 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100012a0(float *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float *unaff_EBX;
  float *unaff_EDI;
  float10 fVar7;
  
  fVar7 = (float10)_CIsin();
  _DAT_1002c928 = (float)fVar7;
  fVar7 = (float10)_CIcos();
  _DAT_1002c920 = (float)fVar7;
  fVar7 = (float10)_CIsin();
  DAT_1002c924 = (float)fVar7;
  fVar7 = (float10)_CIcos();
  _DAT_1002c92c = (float)fVar7;
  fVar7 = (float10)_CIsin();
  _DAT_1002c930 = (float)fVar7;
  fVar7 = (float10)_CIcos();
  fVar1 = _DAT_1002c92c;
  fVar5 = _DAT_1002c928;
  fVar3 = DAT_1002c924;
  fVar4 = _DAT_1002c920;
  _DAT_1002c8f8 = (float)fVar7;
  if (unaff_EDI != (float *)0x0) {
    *unaff_EDI = _DAT_1002c92c * _DAT_1002c920;
    unaff_EDI[1] = fVar1 * fVar5;
    unaff_EDI[2] = (float)((uint)fVar3 ^ DAT_100292a0);
  }
  fVar6 = _DAT_1002c930;
  fVar3 = _DAT_1002c8f8;
  if (unaff_EBX != (float *)0x0) {
    fVar1 = _DAT_1002c8f8 * (float)_DAT_10029290;
    fVar2 = _DAT_1002c930 * DAT_1002c924;
    *unaff_EBX = -fVar5 * fVar1 - fVar4 * fVar2;
    unaff_EBX[1] = fVar4 * fVar1 - fVar2 * fVar5;
    fVar1 = _DAT_1002c92c;
    unaff_EBX[2] = _DAT_1002c92c * (float)_DAT_10029290 * fVar6;
  }
  if (param_1 != (float *)0x0) {
    fVar2 = fVar3 * DAT_1002c924;
    *param_1 = fVar2 * fVar4 - -fVar5 * fVar6;
    param_1[1] = fVar5 * fVar2 - fVar6 * fVar4;
    param_1[2] = fVar1 * fVar3;
    return;
  }
  return;
}



/* FUN_10011730 @ 10011730 size 345 */

void FUN_10011730(void)

{
  int iVar1;
  char *pcVar2;
  undefined **ppuVar3;
  int iVar4;
  char acStack_804 [1024];
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)acStack_804;
  ppuVar3 = &PTR_DAT_1002afe0;
  iVar4 = 0x82;
  do {
    (**(code **)(DAT_106b40a8 + 0x10))(ppuVar3[-2],ppuVar3[-1],*ppuVar3,ppuVar3[2]);
    ppuVar3 = ppuVar3 + 5;
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceTeamModel",acStack_404,0x400);
  (**(code **)(DAT_106b40a8 + 0x24))("cg_forceTeamSkin",acStack_804,0x400);
  iVar4 = 0;
  do {
    if (acStack_404[iVar4] == '\0') break;
    iVar1 = tolower((int)acStack_404[iVar4]);
    acStack_404[iVar4] = (char)iVar1;
    iVar4 = iVar4 + 1;
  } while (iVar4 < 0x40);
  iVar4 = 0;
  do {
    if (acStack_804[iVar4] == '\0') break;
    iVar1 = tolower((int)acStack_804[iVar4]);
    acStack_804[iVar4] = (char)iVar1;
    iVar4 = iVar4 + 1;
  } while (iVar4 < 0x40);
  pcVar2 = strstr(acStack_804,"bright");
  if (pcVar2 == (char *)0x0) {
    pcVar2 = strstr(acStack_404,"bright");
    if ((pcVar2 == (char *)0x0) || (acStack_804[0] != '\0')) {
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_forceTeamModelBright",&DAT_100252c0);
      goto LAB_1001185f;
    }
  }
  (**(code **)(DAT_106b40a8 + 0x1c))("ui_forceTeamModelBright",&DAT_1002729c);
LAB_1001185f:
  FUN_10011510("cg_forceEnemyModel");
  __security_check_cookie(local_4 ^ (uint)acStack_804);
  return;
}



/* FUN_10014cf0 @ 10014cf0 size 345 */

void FUN_10014cf0(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *unaff_EDI;
  undefined1 auStack_c24 [20];
  undefined1 uStack_c10;
  char cStack_c0f;
  undefined1 local_810 [2052];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_c24;
  memset(local_810,0,0x800);
  iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))();
  if ((iVar1 != 0) && (iVar1 = FUN_100016c0(), iVar1 == 0)) {
    iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))();
    while (iVar1 != 0) {
      iVar1 = FUN_100016c0();
      if (iVar1 == 0) {
        uVar2 = FUN_10014560();
        *unaff_EDI = uVar2;
        __security_check_cookie(local_c ^ (uint)auStack_c24);
        return;
      }
      if (cStack_c0f == '\0') {
        FUN_10001750(&uStack_c10);
      }
      else {
        uVar2 = FUN_10001900(&DAT_100290ac,&uStack_c10);
        FUN_10001750(uVar2);
      }
      FUN_10001750(&DAT_100277a8);
      iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))();
    }
  }
  __security_check_cookie(local_c ^ (uint)auStack_c24);
  return;
}



/* FUN_10008f20 @ 10008f20 size 343 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10008f20(undefined4 param_1)

{
  undefined4 uVar1;
  float *unaff_ESI;
  undefined4 *unaff_EDI;
  float10 fVar2;
  undefined1 auStack_70 [4];
  float local_6c;
  float local_68;
  float local_64;
  float local_60;
  float local_5c;
  char acStack_48 [63];
  undefined1 uStack_9;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_70;
  if (DAT_10762498 == 0) {
    uVar1 = FUN_10001900("ui_lastServerRefresh_%i",DAT_1074148c);
    (**(code **)(DAT_106b40a8 + 0x24))(uVar1,&DAT_10042f38,0x400);
    strncpy(acStack_48,&DAT_10042f38,0x3f);
    uStack_9 = 0;
    FUN_10001900("Refresh Time: %s",acStack_48,0,0);
  }
  else {
    local_5c = (float)_DAT_10029448;
    local_68 = *unaff_ESI * local_5c;
    local_64 = unaff_ESI[1] * local_5c;
    local_6c = (float)(DAT_10746428 / 0x4b);
    local_60 = unaff_ESI[2] * local_5c;
    local_5c = local_5c * unaff_ESI[3];
    fVar2 = (float10)_CIsin();
    local_6c = (float)((float10)_DAT_10029278 + fVar2 * (float10)_DAT_10029278);
    FUN_100147a0(local_6c);
    uVar1 = (**(code **)(DAT_106b40a8 + 0xc4))(DAT_1074148c,0,0);
    FUN_10001900("Getting info for %d servers (ESC to cancel)",uVar1);
  }
  FUN_10003ec0(*unaff_EDI,unaff_EDI[1],0,param_1);
  __security_check_cookie(local_4 ^ (uint)auStack_70);
  return;
}



/* FUN_10006730 @ 10006730 size 341 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10006730(void)

{
  char cVar1;
  int iVar2;
  undefined4 *unaff_ESI;
  undefined1 auStack_19c [4];
  undefined4 uStack_198;
  undefined4 uStack_194;
  undefined4 uStack_190;
  char acStack_18c [64];
  char acStack_14c [64];
  undefined1 uStack_10c;
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)auStack_19c;
  if (DAT_1002af44 != 0) {
    (**(code **)(DAT_106b40a8 + 0x24))("ui_opponentModel",&DAT_10042f38,0x400);
    iVar2 = 0;
    do {
      cVar1 = (&DAT_10042f38)[iVar2];
      acStack_18c[iVar2] = cVar1;
      iVar2 = iVar2 + 1;
    } while (cVar1 != '\0');
    (**(code **)(DAT_106b40a8 + 0x24))("ui_opponentModel",&DAT_10042f38,0x400);
    iVar2 = 0;
    do {
      cVar1 = (&DAT_10042f38)[iVar2];
      acStack_14c[iVar2] = cVar1;
      iVar2 = iVar2 + 1;
    } while (cVar1 != '\0');
    uStack_10c = 0;
    memset(&DAT_10046440,0,0x47c);
    uStack_194 = DAT_100294fc;
    uStack_198 = 0;
    uStack_190 = 0;
    FUN_10014250(acStack_14c,&DAT_100239ab);
    FUN_100142e0();
    FUN_10013e70(&DAT_10046440,acStack_18c);
    DAT_1002af44 = 0;
  }
  _DAT_100468a8 = 0;
  FUN_10012d90(*unaff_ESI,unaff_ESI[1],unaff_ESI[2],unaff_ESI[3]);
  __security_check_cookie(local_8 ^ (uint)auStack_19c);
  return;
}



/* FUN_1001d4a0 @ 1001d4a0 size 340 */

void FUN_1001d4a0(int param_1)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  int iVar5;
  undefined4 *puVar6;
  undefined4 *puVar7;
  undefined4 *local_2a8;
  int local_2a4;
  undefined1 local_2a0 [308];
  undefined4 *local_16c;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_2a8;
  iVar5 = 0;
  local_2a4 = param_1;
  iVar2 = 0;
  local_2a8 = (undefined4 *)0x0;
  if (0 < DAT_106b40e4) {
    puVar4 = &DAT_106b4968;
    do {
      if (((*puVar4 & 2) != 0) && ((*puVar4 & 4) != 0)) {
        puVar6 = &DAT_106b4920 + iVar2 * 0x455;
        goto LAB_1001d4fd;
      }
      iVar2 = iVar2 + 1;
      puVar4 = puVar4 + 0x455;
    } while (iVar2 < DAT_106b40e4);
  }
  puVar6 = (undefined4 *)0x0;
LAB_1001d4fd:
  if (0 < DAT_106b40e4) {
    puVar7 = &DAT_106b4a50;
    iVar2 = DAT_106b40e4;
    do {
      if (((puVar7[-0x44] == 0) || (local_2a4 == 0)) || (iVar3 = FUN_100016c0(), iVar3 != 0)) {
        puVar7[-0x3a] = puVar7[-0x3a] & 0xfffffffd;
      }
      else {
        puVar7[-0x3a] = puVar7[-0x3a] | 6;
        local_2a8 = puVar7 + -0x4c;
        if (puVar7[-3] != 0) {
          local_16c = local_2a8;
          FUN_10016d70(local_2a0);
        }
        pcVar1 = (char *)*puVar7;
        if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
          (**(code **)(DAT_106b40d0 + 0xb0))(pcVar1,pcVar1);
        }
        FUN_100196b0();
        iVar2 = DAT_106b40e4;
        if ((DAT_106b40e8 < 0x10) && (puVar6 != (undefined4 *)0x0)) {
          *(undefined4 **)(&DAT_1073fb60 + DAT_106b40e8 * 4) = puVar6;
          DAT_106b40e8 = DAT_106b40e8 + 1;
          iVar2 = DAT_106b40e4;
        }
      }
      iVar5 = iVar5 + 1;
      puVar7 = puVar7 + 0x455;
    } while (iVar5 < iVar2);
  }
  FUN_100196b0();
  __security_check_cookie(local_4 ^ (uint)&local_2a8);
  return;
}



/* FUN_10013850 @ 10013850 size 336 */

undefined4 FUN_10013850(char *param_1)

{
  char *in_EAX;
  int iVar1;
  char *pcVar2;
  int local_4;
  
  if (*in_EAX == '*') {
    pcVar2 = "heads/";
  }
  else {
    pcVar2 = "";
  }
  do {
    local_4 = 0;
    do {
      if (((local_4 == 0) && (param_1 != (char *)0x0)) && (*param_1 != '\0')) {
        FUN_10001830();
      }
      else {
        FUN_10001830();
      }
      iVar1 = (**(code **)(DAT_106b40a8 + 0x38))();
      if (0 < iVar1) {
        return 1;
      }
      if (((local_4 == 0) && (param_1 != (char *)0x0)) && (*param_1 != '\0')) {
        FUN_10001830();
      }
      else {
        FUN_10001830();
      }
      iVar1 = (**(code **)(DAT_106b40a8 + 0x38))();
      if (0 < iVar1) {
        return 1;
      }
    } while (((param_1 != (char *)0x0) && (*param_1 != '\0')) &&
            (local_4 = local_4 + 1, local_4 < 2));
    if (*pcVar2 != '\0') {
      return 0;
    }
    pcVar2 = "heads/";
  } while( true );
}



/* FUN_10009660 @ 10009660 size 335 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10009660(undefined4 param_1)

{
  int iVar1;
  uint uVar2;
  float *unaff_EDI;
  float fStack_18;
  undefined4 uStack_14;
  undefined4 uStack_10;
  undefined4 uStack_c;
  undefined4 uStack_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&fStack_18;
  (**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairHealth");
  iVar1 = FUN_10021270();
  (**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairColor");
  uVar2 = FUN_10021270();
  if (0x19 < uVar2) {
    uVar2 = 0;
  }
  if (iVar1 != 0) {
    uStack_c = DAT_10029420;
    uStack_10 = DAT_10029420;
    uStack_14 = DAT_10029420;
    uStack_8 = DAT_10029234;
    (**(code **)(DAT_106b40a8 + 0x74))(&uStack_14);
  }
  fStack_18 = unaff_EDI[1] - (float)_DAT_10029410;
  FUN_10002c50(*unaff_EDI,fStack_18,_DAT_10029418,_DAT_1002941c,DAT_10755584);
  fStack_18 = (float)(int)(uVar2 << 4) + *unaff_EDI + (float)_DAT_10029220;
  FUN_10002c50(fStack_18,unaff_EDI[1] - (float)_DAT_10029320,DAT_10029390,_DAT_10029370,
               (&DAT_10755588)[uVar2]);
  if (iVar1 != 0) {
    (**(code **)(DAT_106b40a8 + 0x74))(param_1);
  }
  __security_check_cookie(local_4 ^ (uint)&fStack_18);
  return;
}



/* FUN_10017880 @ 10017880 size 332 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10017880(undefined4 param_1,undefined4 param_2)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  int unaff_ESI;
  
  *(uint *)(unaff_ESI + 0x48) = *(uint *)(unaff_ESI + 0x48) & 0xffff07ff;
  piVar1 = *(int **)(unaff_ESI + 0x288);
  uVar2 = FUN_10017570(param_1,param_2);
  *(uint *)(unaff_ESI + 0x48) = *(uint *)(unaff_ESI + 0x48) | uVar2;
  uVar2 = *(uint *)(unaff_ESI + 0x48);
  if ((uVar2 & 0x400) == 0) {
    if ((uVar2 & 0xf800) == 0) {
      iVar3 = FUN_10015c00(param_1,param_2);
      if (iVar3 != 0) {
        iVar3 = FUN_10021270();
        piVar1[3] = iVar3 + *piVar1;
        if (piVar1[1] < iVar3 + *piVar1) {
          piVar1[3] = piVar1[1];
        }
      }
    }
  }
  else if (((uVar2 & 0xf800) == 0) && (piVar1[6] == 1)) {
    iVar3 = FUN_10015c00(param_1,param_2);
    if (iVar3 != 0) {
      iVar3 = FUN_10021270();
      piVar1[3] = iVar3 + *piVar1;
      if (piVar1[1] <= iVar3 + *piVar1) {
        piVar1[3] = piVar1[1];
        return;
      }
    }
  }
  return;
}



/* FUN_1000acf0 @ 1000acf0 size 327 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_1000acf0(void)

{
  char cVar1;
  undefined4 uVar2;
  char *pcVar3;
  char *pcVar4;
  int iVar5;
  char *pcVar6;
  int iVar7;
  char acStack_1024 [32];
  char acStack_1004 [4096];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)acStack_1024;
  (**(code **)(DAT_106b40a8 + 0x28))("protocol");
  uVar2 = FUN_10021270();
  FUN_10001830(acStack_1024,0x20,"dm_%d",uVar2);
  DAT_107617e0 = (**(code **)(DAT_106b40a8 + 0x4c))("demos",acStack_1024,acStack_1004,0x1000);
  (**(code **)(DAT_106b40a8 + 0x28))("protocol");
  uVar2 = FUN_10021270();
  FUN_10001830(acStack_1024,0x20,".dm_%d",uVar2);
  if (DAT_107617e0 != 0) {
    if (0x100 < DAT_107617e0) {
      DAT_107617e0 = 0x100;
    }
    iVar7 = 0;
    pcVar6 = acStack_1004;
    if (0 < DAT_107617e0) {
      do {
        pcVar3 = pcVar6;
        do {
          cVar1 = *pcVar3;
          pcVar3 = pcVar3 + 1;
        } while (cVar1 != '\0');
        pcVar4 = acStack_1024;
        do {
          cVar1 = *pcVar4;
          pcVar4 = pcVar4 + 1;
        } while (cVar1 != '\0');
        if ((pcVar6 + (int)(pcVar3 + (-((int)pcVar4 - (int)(acStack_1024 + 1)) - (int)(pcVar6 + 1)))
             != (char *)0x0) && (iVar5 = FUN_100016c0(), iVar5 == 0)) {
          pcVar6[(int)(pcVar3 + (-((int)pcVar4 - (int)(acStack_1024 + 1)) - (int)(pcVar6 + 1)))] =
               '\0';
        }
        cVar1 = *pcVar6;
        pcVar4 = pcVar6;
        while (cVar1 != '\0') {
          iVar5 = toupper((int)*pcVar4);
          *pcVar4 = (char)iVar5;
          pcVar4 = pcVar4 + 1;
          cVar1 = *pcVar4;
        }
        uVar2 = FUN_10014560();
        (&DAT_107613e0)[iVar7] = uVar2;
        iVar7 = iVar7 + 1;
        pcVar6 = pcVar6 + (int)(pcVar3 + (1 - (int)(pcVar6 + 1)));
      } while (iVar7 < DAT_107617e0);
    }
  }
  __security_check_cookie(local_4 ^ (uint)acStack_1024);
  return;
}



/* FUN_10003770 @ 10003770 size 326 */

void FUN_10003770(void)

{
  char cVar1;
  int iVar2;
  char *pcVar3;
  char *pcVar4;
  undefined4 uVar5;
  uint uVar6;
  char *pcVar7;
  char *pcVar8;
  char *pcVar9;
  int iStack_59c;
  undefined1 local_598 [275];
  char cStack_485;
  char acStack_484 [4];
  char acStack_480 [4];
  char cStack_47c;
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&iStack_59c;
  DAT_10769814 = 0;
  (*(code *)DAT_106b40a8[4])(local_598,"g_botsFile",&DAT_100239ab,0x50);
  FUN_10003640();
  iVar2 = (*(code *)DAT_106b40a8[0x13])("scripts",&DAT_10025e50,acStack_404,0x400);
  pcVar3 = acStack_404;
  pcVar7 = pcVar3;
  if (0 < iVar2) {
    do {
      do {
        iStack_59c = iVar2;
        cVar1 = *pcVar3;
        pcVar3 = pcVar3 + 1;
        iVar2 = iStack_59c;
      } while (cVar1 != '\0');
      acStack_484[0] = s_scripts__10025da0[0];
      acStack_484[1] = s_scripts__10025da0[1];
      acStack_484[2] = s_scripts__10025da0[2];
      acStack_484[3] = s_scripts__10025da0[3];
      acStack_480[0] = s_scripts__10025da0[4];
      acStack_480[1] = s_scripts__10025da0[5];
      acStack_480[2] = s_scripts__10025da0[6];
      acStack_480[3] = s_scripts__10025da0[7];
      cStack_47c = s_scripts__10025da0[8];
      pcVar4 = pcVar7;
      do {
        cVar1 = *pcVar4;
        pcVar4 = pcVar4 + 1;
      } while (cVar1 != '\0');
      pcVar9 = &cStack_485;
      do {
        pcVar8 = pcVar9 + 1;
        pcVar9 = pcVar9 + 1;
      } while (*pcVar8 != '\0');
      pcVar8 = pcVar7;
      for (uVar6 = (uint)((int)pcVar4 - (int)pcVar7) >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
        *(undefined4 *)pcVar9 = *(undefined4 *)pcVar8;
        pcVar8 = pcVar8 + 4;
        pcVar9 = pcVar9 + 4;
      }
      for (uVar6 = (int)pcVar4 - (int)pcVar7 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *pcVar9 = *pcVar8;
        pcVar8 = pcVar8 + 1;
        pcVar9 = pcVar9 + 1;
      }
      FUN_10003640();
      iVar2 = iStack_59c + -1;
      pcVar7 = pcVar3;
    } while (iStack_59c + -1 != 0);
    iStack_59c = 0;
  }
  uVar5 = FUN_10001900("%i bots parsed\n",DAT_10769814);
  (*(code *)*DAT_106b40a8)(uVar5);
  __security_check_cookie(local_4 ^ (uint)&iStack_59c);
  return;
}



/* FUN_10016e70 @ 10016e70 size 323 */

void FUN_10016e70(uint param_1)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  int unaff_EDI;
  undefined1 *puStack_c08;
  undefined1 local_c04 [1024];
  undefined1 local_804 [2048];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&puStack_c08;
  iVar3 = 0;
  puVar4 = (undefined4 *)(unaff_EDI + 0x16c);
  do {
    memset(local_804,0,0x800);
    if ((((unaff_EDI != 0) && ((char *)*puVar4 != (char *)0x0)) && (*(char *)*puVar4 != '\0')) &&
       ((pcVar1 = (char *)puVar4[-4], pcVar1 != (char *)0x0 && (*pcVar1 != '\0')))) {
      (**(code **)(DAT_106b40d0 + 0x58))(pcVar1,local_c04,0x400);
      FUN_10001750(*puVar4);
      puStack_c08 = local_804;
LAB_10016f05:
      do {
        do {
          pcVar1 = (char *)FUN_10001500(&puStack_c08,0);
          if ((pcVar1 == (char *)0x0) || (*pcVar1 == '\0')) {
            if ((*(uint *)(unaff_EDI + 0x17c) & param_1) != 0) {
LAB_10016f60:
              __security_check_cookie(local_4 ^ (uint)&puStack_c08);
              return;
            }
            goto LAB_10016f8e;
          }
          pcVar1 = (char *)FUN_10014560();
        } while ((*pcVar1 == ';') && (pcVar1[1] == '\0'));
        if ((*(uint *)(unaff_EDI + 0x17c) & param_1) == 0) {
          iVar2 = FUN_100016c0();
          if (iVar2 == 0) goto LAB_10016f60;
          goto LAB_10016f05;
        }
        iVar2 = FUN_100016c0();
      } while (iVar2 != 0);
    }
LAB_10016f8e:
    iVar3 = iVar3 + 1;
    puVar4 = puVar4 + 1;
    if (3 < iVar3) {
      __security_check_cookie(local_4 ^ (uint)&puStack_c08);
      return;
    }
  } while( true );
}



/* FUN_100103f0 @ 100103f0 size 322 */

void FUN_100103f0(void)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  int iVar4;
  char *pcVar5;
  uint uVar6;
  char *unaff_ESI;
  uint unaff_EDI;
  
  if (0x40000000 < (int)unaff_EDI) {
    FUN_10001830();
    pcVar3 = unaff_ESI;
    do {
      cVar1 = *pcVar3;
      pcVar3 = pcVar3 + 1;
    } while (cVar1 != '\0');
    pcVar2 = unaff_ESI;
    do {
      pcVar5 = pcVar2;
      pcVar2 = pcVar5 + 1;
    } while (*pcVar5 != '\0');
    iVar4 = (unaff_EDI & 0xbfffffff) * 100;
    FUN_10001830(pcVar5,0x40 - ((int)pcVar3 - (int)(unaff_ESI + 1)),".%02d GB",
                 (int)(iVar4 + (iVar4 >> 0x1f & 0x3fffffffU)) >> 0x1e);
    return;
  }
  if (0x100000 < (int)unaff_EDI) {
    FUN_10001830();
    pcVar3 = unaff_ESI;
    do {
      cVar1 = *pcVar3;
      pcVar3 = pcVar3 + 1;
    } while (cVar1 != '\0');
    pcVar2 = unaff_ESI;
    do {
      pcVar5 = pcVar2;
      pcVar2 = pcVar5 + 1;
    } while (*pcVar5 != '\0');
    uVar6 = unaff_EDI & 0x800fffff;
    if ((int)uVar6 < 0) {
      uVar6 = (uVar6 - 1 | 0xfff00000) + 1;
    }
    FUN_10001830(pcVar5,0x40 - ((int)pcVar3 - (int)(unaff_ESI + 1)),".%02d MB",
                 (int)(uVar6 * 100 + ((int)(uVar6 * 100) >> 0x1f & 0xfffffU)) >> 0x14);
    return;
  }
  if (0x400 < (int)unaff_EDI) {
    FUN_10001830();
    return;
  }
  FUN_10001830();
  return;
}



/* FUN_1001f370 @ 1001f370 size 322 */

void FUN_1001f370(int param_1,undefined4 param_2)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  undefined4 uVar4;
  undefined1 local_420 [16];
  char cStack_410;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)local_420;
  FUN_1001da70();
  iVar3 = DAT_106b40a8;
  iVar1 = *(int *)(param_1 + 0x288);
  bVar2 = false;
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x180) = 0;
    *(undefined4 *)(iVar1 + 0x184) = 1;
    iVar3 = (**(code **)(iVar3 + 0x16c))(param_2,local_420);
    if ((iVar3 != 0) && (cStack_410 == '{')) {
      iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      while (iVar3 != 0) {
        if (cStack_410 == '}') {
          __security_check_cookie(local_c ^ (uint)local_420);
          return;
        }
        if ((cStack_410 != ',') && (cStack_410 != ';')) {
          if (bVar2) {
            uVar4 = FUN_10014560();
            *(undefined4 *)(iVar1 + 0x80 + *(int *)(iVar1 + 0x180) * 4) = uVar4;
            *(int *)(iVar1 + 0x180) = *(int *)(iVar1 + 0x180) + 1;
            bVar2 = false;
            if (0x1f < *(int *)(iVar1 + 0x180)) goto LAB_1001f483;
          }
          else {
            uVar4 = FUN_10014560();
            *(undefined4 *)(iVar1 + *(int *)(iVar1 + 0x180) * 4) = uVar4;
            bVar2 = true;
          }
        }
        iVar3 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      }
      FUN_10014710(param_2,"end of file inside menu item\n");
    }
  }
LAB_1001f483:
  __security_check_cookie(local_c ^ (uint)local_420);
  return;
}



/* FUN_10002350 @ 10002350 size 314 */

void FUN_10002350(void)

{
  int iVar1;
  undefined1 auStack_9c [4];
  undefined4 local_98;
  int iStack_94;
  undefined1 local_90 [64];
  undefined1 local_50 [68];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_9c;
  memset(local_90,0,0x40);
  FUN_10001830(local_50,0x40,"games/%s_%i.game");
  iVar1 = (**(code **)(DAT_106b40a8 + 0x38))(local_50,&local_98,0);
  if (-1 < iVar1) {
    iStack_94 = 0;
    (**(code **)(DAT_106b40a8 + 0x3c))(&iStack_94,4,local_98);
    if (iStack_94 == 0x40) {
      (**(code **)(DAT_106b40a8 + 0x3c))(local_90,0x40,local_98);
    }
    (**(code **)(DAT_106b40a8 + 0x44))(local_98);
  }
  FUN_10001f70(0);
  (**(code **)(DAT_106b40a8 + 0x28))("protocol");
  FUN_10021270();
  FUN_10001830(local_50,0x40,"demos/%s_%d.dm_%d");
  DAT_10758294 = 0;
  iVar1 = (**(code **)(DAT_106b40a8 + 0x38))(local_50,&local_98,0);
  if (-1 < iVar1) {
    DAT_10758294 = 1;
    (**(code **)(DAT_106b40a8 + 0x44))(local_98);
  }
  __security_check_cookie(local_c ^ (uint)auStack_9c);
  return;
}



/* FUN_10004fc0 @ 10004fc0 size 314 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10004fc0(void)

{
  char cVar1;
  int iVar2;
  char *pcVar3;
  uint *puVar4;
  undefined4 *puVar5;
  char acStack_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)acStack_404;
  iVar2 = 0;
  if (0 < DAT_106b40e4) {
    puVar4 = &DAT_106b4968;
    do {
      if (((*puVar4 & 2) != 0) && ((*puVar4 & 4) != 0)) {
        puVar5 = &DAT_106b4920 + iVar2 * 0x455;
        goto LAB_1000500d;
      }
      iVar2 = iVar2 + 1;
      puVar4 = puVar4 + 0x455;
    } while (iVar2 < DAT_106b40e4);
  }
  puVar5 = (undefined4 *)0x0;
LAB_1000500d:
  (**(code **)(DAT_106b40a8 + 0x24))("ui_menuFiles",&DAT_10042f38,0x400);
  if ((puVar5 != (undefined4 *)0x0) && (pcVar3 = (char *)puVar5[8], pcVar3 != (char *)0x0)) {
    iVar2 = -(int)pcVar3;
    do {
      cVar1 = *pcVar3;
      pcVar3[(int)(acStack_404 + iVar2)] = cVar1;
      pcVar3 = pcVar3 + 1;
    } while (cVar1 != '\0');
  }
  puVar5 = &DAT_10051058;
  for (iVar2 = 0x800; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar5 = 0;
    puVar5 = puVar5 + 1;
  }
  _DAT_106b40f8 = 0;
  DAT_106b40f4 = 0;
  DAT_106b40e4 = 0;
  DAT_106b40e8 = 0;
  DAT_10050054 = 0;
  DAT_106b3058 = 0;
  FUN_1001f730();
  FUN_10020100();
  if ((DAT_106b40d0 != 0) && (*(int *)(DAT_106b40d0 + 0x90) != 0)) {
    FUN_1001b0c0();
  }
  FUN_1000f6d0();
  FUN_10003190();
  FUN_10004e10(1);
  FUN_10016220();
  FUN_1001d4a0(acStack_404);
  __security_check_cookie(local_4 ^ (uint)acStack_404);
  return;
}



/* FUN_1001f010 @ 1001f010 size 302 */

void FUN_1001f010(int param_1,undefined4 param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_424 [4];
  undefined1 local_420 [16];
  char cStack_410;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  FUN_1001da70();
  iVar2 = DAT_106b40a8;
  iVar1 = *(int *)(param_1 + 0x288);
  if (iVar1 != 0) {
    *(undefined4 *)(iVar1 + 0x180) = 0;
    *(undefined4 *)(iVar1 + 0x184) = 0;
    iVar2 = (**(code **)(iVar2 + 0x16c))(param_2,local_420);
    if ((iVar2 != 0) && (cStack_410 == '{')) {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      while (iVar2 != 0) {
        if (cStack_410 == '}') {
          __security_check_cookie(local_c ^ (uint)auStack_424);
          return;
        }
        if ((cStack_410 != ',') && (cStack_410 != ';')) {
          uVar3 = FUN_10014560();
          *(undefined4 *)(iVar1 + *(int *)(iVar1 + 0x180) * 4) = uVar3;
          iVar2 = FUN_100148d0();
          if ((iVar2 == 0) ||
             (*(int *)(iVar1 + 0x180) = *(int *)(iVar1 + 0x180) + 1, 0x1f < *(int *)(iVar1 + 0x180))
             ) goto LAB_1001f110;
        }
        iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      }
      FUN_10014710(param_2,"end of file inside menu item\n");
    }
  }
LAB_1001f110:
  __security_check_cookie(local_c ^ (uint)auStack_424);
  return;
}



/* FUN_1001b2a0 @ 1001b2a0 size 299 */

void FUN_1001b2a0(void)

{
  char cVar1;
  undefined1 uVar2;
  undefined4 *puVar3;
  int in_EAX;
  int iVar4;
  undefined4 *puVar5;
  char *pcVar6;
  uint uVar7;
  undefined **ppuVar8;
  char *pcVar9;
  char *pcVar10;
  int iVar11;
  
  iVar11 = 0;
  ppuVar8 = &PTR_s__scores_1002a0d0;
  while (((in_EAX == 0 || (*ppuVar8 == (undefined *)0x0)) || (iVar4 = FUN_100016c0(), iVar4 != 0)))
  {
    ppuVar8 = ppuVar8 + 6;
    iVar11 = iVar11 + 1;
    if (0x1002a867 < (int)ppuVar8) {
      DAT_1073f320 = DAT_100264c8;
      return;
    }
  }
  if ((&DAT_1002a0e0)[iVar11 * 6] == -1) {
    DAT_1073f320 = DAT_100264c8;
    return;
  }
  (**(code **)(DAT_106b40d0 + 0x8c))((&DAT_1002a0e0)[iVar11 * 6],&DAT_1073f320,0x20);
  pcVar9 = (char *)&DAT_1073f320;
  cVar1 = (char)DAT_1073f320;
  while (cVar1 != '\0') {
    iVar4 = toupper((int)*pcVar9);
    *pcVar9 = (char)iVar4;
    pcVar9 = pcVar9 + 1;
    cVar1 = *pcVar9;
  }
  if ((&DAT_1002a0e4)[iVar11 * 6] != -1) {
    (**(code **)(DAT_106b40d0 + 0x8c))((&DAT_1002a0e4)[iVar11 * 6],&DAT_1073f340,0x20);
    pcVar9 = &DAT_1073f340;
    uVar2 = DAT_10029134;
    cVar1 = DAT_1073f340;
    while (DAT_10029134 = uVar2, cVar1 != '\0') {
      iVar11 = toupper((int)*pcVar9);
      *pcVar9 = (char)iVar11;
      pcVar9 = pcVar9 + 1;
      uVar2 = DAT_10029134;
      cVar1 = *pcVar9;
    }
    puVar3 = (undefined4 *)0x1073f31f;
    do {
      puVar5 = puVar3;
      puVar3 = (undefined4 *)((int)puVar5 + 1);
    } while (*(char *)((int)puVar5 + 1) != '\0');
    *(undefined4 *)((int)puVar5 + 1) = DAT_10029130;
    *(undefined1 *)((int)puVar5 + 5) = uVar2;
    pcVar9 = &DAT_1073f340;
    do {
      pcVar6 = pcVar9;
      pcVar9 = pcVar6 + 1;
    } while (*pcVar6 != '\0');
    pcVar9 = (char *)0x1073f31f;
    do {
      pcVar10 = pcVar9 + 1;
      pcVar9 = pcVar9 + 1;
    } while (*pcVar10 != '\0');
    pcVar10 = &DAT_1073f340;
    for (uVar7 = (uint)(pcVar6 + -0x1073f33f) >> 2; uVar7 != 0; uVar7 = uVar7 - 1) {
      *(undefined4 *)pcVar9 = *(undefined4 *)pcVar10;
      pcVar10 = pcVar10 + 4;
      pcVar9 = pcVar9 + 4;
    }
    for (uVar7 = (uint)(pcVar6 + -0x1073f33f) & 3; uVar7 != 0; uVar7 = uVar7 - 1) {
      *pcVar9 = *pcVar10;
      pcVar10 = pcVar10 + 1;
      pcVar9 = pcVar9 + 1;
    }
    return;
  }
  return;
}



/* FUN_10005560 @ 10005560 size 297 */

void __fastcall FUN_10005560(float *param_1)

{
  int iVar1;
  int in_EAX;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = DAT_10742f8c;
  if (in_EAX == 0) {
    iVar3 = DAT_10744ccc;
  }
  if ((iVar3 < 0) || (DAT_1075add0 < iVar3)) {
    if (in_EAX == 0) {
      DAT_10744ccc = 0;
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentMap",&DAT_100252c0);
    }
    else {
      DAT_10742f8c = 0;
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentNetMap");
    }
    iVar3 = 0;
  }
  iVar1 = DAT_106b40a8;
  if (-2 < (int)(&DAT_1075adec)[iVar3 * 0x19]) {
    if ((&DAT_1075adec)[iVar3 * 0x19] == -1) {
      uVar2 = FUN_10001900("%s.roq",(&DAT_1075add8)[iVar3 * 0x19],0,0,0,0,10);
      uVar2 = (**(code **)(iVar1 + 0x124))(uVar2);
      (&DAT_1075adec)[iVar3 * 0x19] = uVar2;
    }
    if (-1 < (int)(&DAT_1075adec)[iVar3 * 0x19]) {
      (**(code **)(DAT_106b40a8 + 300))((&DAT_1075adec)[iVar3 * 0x19]);
      (**(code **)(DAT_106b40a8 + 0x134))
                ((&DAT_1075adec)[iVar3 * 0x19],(int)*param_1,(int)param_1[1],(int)param_1[2],
                 (int)param_1[3]);
      (**(code **)(DAT_106b40a8 + 0x130))((&DAT_1075adec)[iVar3 * 0x19]);
      return;
    }
    (&DAT_1075adec)[iVar3 * 0x19] = 0xfffffffe;
    return;
  }
  FUN_100053c0();
  return;
}



/* FUN_100168a0 @ 100168a0 size 296 */

void FUN_100168a0(float param_1,float param_2,float param_3)

{
  float *pfVar1;
  int iVar2;
  float *pfVar3;
  int iVar4;
  float10 extraout_ST0;
  float10 extraout_ST1;
  float in_XMM0_Da;
  float in_XMM1_Da;
  float fVar5;
  float local_14;
  float local_10;
  float local_c;
  float local_8;
  
  iVar2 = FUN_10015c50();
  iVar4 = 0;
  if (0 < iVar2) {
    fVar5 = 0.0;
    do {
      pfVar3 = (float *)FUN_10015cc0();
      if (pfVar3 != (float *)0x0) {
        pfVar3[0x12] = (float)((uint)pfVar3[0x12] | 0x10004);
        pfVar3[0x1c] = param_3;
        pfVar1 = (float *)pfVar3[0x4d];
        pfVar3[0x14] = in_XMM1_Da;
        pfVar3[0x15] = in_XMM0_Da;
        pfVar3[4] = param_1;
        pfVar3[5] = param_2;
        if (pfVar1 != (float *)0x0) {
          local_14 = *pfVar1;
          local_10 = pfVar1[1];
          if (pfVar1[0xd] != 0.0) {
            local_14 = pfVar1[0x11] + local_14;
            local_10 = pfVar1[0x11] + local_10;
          }
          local_c = local_14;
          local_8 = local_10;
          if (pfVar3[0xd] != 0.0) {
            local_c = pfVar3[0x11] + local_14;
            local_8 = pfVar3[0x11] + local_10;
          }
          pfVar3[0x42] = fVar5;
          pfVar3[0x43] = fVar5;
          *pfVar3 = (float)((float10)local_c + extraout_ST0);
          pfVar3[1] = (float)((float10)local_8 + extraout_ST1);
          pfVar3[2] = pfVar3[6];
          pfVar3[3] = pfVar3[7];
        }
      }
      iVar4 = iVar4 + 1;
    } while (iVar4 < iVar2);
  }
  return;
}



/* FUN_10003640 @ 10003640 size 290 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_10003640(void)

{
  int iVar1;
  undefined4 uVar2;
  int local_2008;
  undefined1 auStack_2004 [8192];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_2008;
  iVar1 = (*(code *)DAT_106b40a8[0xe])();
  if (local_2008 == 0) {
    uVar2 = FUN_10001900("^1file not found: %s\n");
    (*(code *)*DAT_106b40a8)(uVar2);
    __security_check_cookie(local_4 ^ (uint)&local_2008);
    return;
  }
  if (0x1fff < iVar1) {
    uVar2 = FUN_10001900("^1file too large: %s is %i, max allowed is %i");
    (*(code *)*DAT_106b40a8)(uVar2);
    (*(code *)DAT_106b40a8[0x11])(local_2008);
    __security_check_cookie(local_4 ^ (uint)&local_2008);
    return;
  }
  (*(code *)DAT_106b40a8[0xf])(auStack_2004,iVar1,local_2008);
  auStack_2004[iVar1] = 0;
  (*(code *)DAT_106b40a8[0x11])(local_2008);
  FUN_10001400(auStack_2004);
  iVar1 = FUN_10002e20(auStack_2004,0x400 - DAT_10769814);
  DAT_10769814 = DAT_10769814 + iVar1;
  __security_check_cookie(local_4 ^ (uint)&local_2008);
  return;
}



/* FUN_10001a60 @ 10001a60 size 285 */

void __fastcall FUN_10001a60(byte *param_1)

{
  byte bVar1;
  byte *pbVar2;
  char *pcVar3;
  byte *pbVar4;
  int iVar5;
  byte *pbVar6;
  undefined1 *puVar7;
  byte *unaff_EDI;
  bool bVar8;
  byte local_804 [1024];
  undefined1 local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_804;
  pbVar2 = param_1;
  do {
    bVar1 = *pbVar2;
    pbVar2 = pbVar2 + 1;
  } while (bVar1 != 0);
  if (0x3ff < (uint)((int)pbVar2 - (int)(param_1 + 1))) {
    FUN_10001e70(1,"Info_RemoveKey: oversize infostring");
  }
  pcVar3 = strchr((char *)unaff_EDI,0x5c);
  if (pcVar3 != (char *)0x0) {
LAB_10001b67:
    __security_check_cookie(local_4 ^ (uint)local_804);
    return;
  }
  do {
    pbVar2 = param_1;
    if (*param_1 == 0x5c) {
      pbVar2 = param_1 + 1;
    }
    pbVar6 = local_804;
    bVar1 = *pbVar2;
    while (bVar1 != 0x5c) {
      if (bVar1 == 0) goto LAB_10001b67;
      pbVar2 = pbVar2 + 1;
      *pbVar6 = bVar1;
      pbVar6 = pbVar6 + 1;
      bVar1 = *pbVar2;
    }
    bVar1 = pbVar2[1];
    *pbVar6 = 0;
    puVar7 = local_404;
    while ((pbVar2 = pbVar2 + 1, bVar1 != 0x5c && (bVar1 != 0))) {
      puVar7 = puVar7 + 1;
      bVar1 = pbVar2[1];
    }
    *puVar7 = 0;
    pbVar6 = local_804;
    pbVar4 = unaff_EDI;
    do {
      bVar1 = *pbVar4;
      bVar8 = bVar1 < *pbVar6;
      if (bVar1 != *pbVar6) {
LAB_10001b26:
        iVar5 = (1 - (uint)bVar8) - (uint)(bVar8 != 0);
        goto LAB_10001b2b;
      }
      if (bVar1 == 0) break;
      bVar1 = pbVar4[1];
      bVar8 = bVar1 < pbVar6[1];
      if (bVar1 != pbVar6[1]) goto LAB_10001b26;
      pbVar4 = pbVar4 + 2;
      pbVar6 = pbVar6 + 2;
    } while (bVar1 != 0);
    iVar5 = 0;
LAB_10001b2b:
    if (iVar5 == 0) {
      pbVar6 = pbVar2;
      do {
        bVar1 = *pbVar6;
        pbVar6 = pbVar6 + 1;
      } while (bVar1 != 0);
      memmove(param_1,pbVar2,(size_t)(pbVar6 + (1 - (int)(pbVar2 + 1))));
      goto LAB_10001b67;
    }
    param_1 = pbVar2;
    if (*pbVar2 == 0) {
      __security_check_cookie(local_4 ^ (uint)local_804);
      return;
    }
  } while( true );
}



/* FUN_10019350 @ 10019350 size 282 */

undefined4 __thiscall FUN_10019350(int param_1,int param_2,undefined4 param_3)

{
  int in_EAX;
  undefined4 uVar1;
  
  if (DAT_106b40cc == 0) {
    if (param_2 == 0) {
      return 0;
    }
    if (((in_EAX == 0xb2) || (in_EAX == 0xb3)) || (in_EAX == 0xb4)) {
      FUN_10019000();
    }
  }
  else {
    DAT_106b40cc = 0;
    DAT_106b40c4 = 0;
    DAT_106b40c8 = 0;
  }
  if (param_2 != 0) {
    switch(*(undefined4 *)(param_1 + 0x110)) {
    case 6:
      uVar1 = FUN_10017b90();
      return uVar1;
    case 8:
      if (*(code **)(DAT_106b40d0 + 0x78) != (code *)0x0) {
        uVar1 = (**(code **)(DAT_106b40d0 + 0x78))
                          (*(undefined4 *)(param_1 + 0x38),*(undefined4 *)(param_1 + 0x3c),
                           param_1 + 0x280);
        return uVar1;
      }
      break;
    case 10:
    case 0xe:
      if ((*(byte *)(param_1 + 0x48) & 2) != 0) {
        uVar1 = FUN_10019180();
        return uVar1;
      }
      (**(code **)(DAT_106b40d0 + 0xa0))("slider handle key exit\n");
      break;
    case 0xb:
      uVar1 = FUN_100180a0();
      return uVar1;
    case 0xc:
      uVar1 = FUN_10018370();
      return uVar1;
    case 0xd:
      uVar1 = FUN_1001b9e0(param_2,param_3);
      return uVar1;
    case 0x10:
      uVar1 = FUN_10018680(param_1);
      return uVar1;
    }
  }
  return 0;
}



/* FUN_10003070 @ 10003070 size 280 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_10003070(void)

{
  int iVar1;
  undefined4 uVar2;
  int local_4008;
  undefined1 auStack_4004 [16384];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_4008;
  iVar1 = (*(code *)DAT_106b40a8[0xe])();
  if (local_4008 == 0) {
    uVar2 = FUN_10001900("^1file not found: %s\n");
    (*(code *)*DAT_106b40a8)(uVar2);
    __security_check_cookie(local_4 ^ (uint)&local_4008);
    return;
  }
  if (0x3fff < iVar1) {
    uVar2 = FUN_10001900("^1file too large: %s is %i, max allowed is %i");
    (*(code *)*DAT_106b40a8)(uVar2);
    (*(code *)DAT_106b40a8[0x11])(local_4008);
    __security_check_cookie(local_4 ^ (uint)&local_4008);
    return;
  }
  (*(code *)DAT_106b40a8[0xf])(auStack_4004,iVar1,local_4008);
  auStack_4004[iVar1] = 0;
  (*(code *)DAT_106b40a8[0x11])(local_4008);
  iVar1 = FUN_10002e20(auStack_4004,0x400 - DAT_10044338);
  DAT_10044338 = DAT_10044338 + iVar1;
  __security_check_cookie(local_4 ^ (uint)&local_4008);
  return;
}



/* FUN_10001940 @ 10001940 size 278 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void __fastcall FUN_10001940(char *param_1)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  int unaff_EBX;
  uint uVar4;
  char local_2004 [8192];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_2004;
  if ((param_1 == (char *)0x0) || (unaff_EBX == 0)) {
    __security_check_cookie(local_4 ^ (uint)local_2004);
    return;
  }
  pcVar2 = param_1;
  do {
    cVar1 = *pcVar2;
    pcVar2 = pcVar2 + 1;
  } while (cVar1 != '\0');
  if (0x1fff < (uint)((int)pcVar2 - (int)(param_1 + 1))) {
    FUN_10001e70(1,"Info_ValueForKey: oversize infostring");
  }
  uVar4 = DAT_106b40a0 ^ 1;
  DAT_106b40a0 = uVar4;
  if (*param_1 != '\\') goto LAB_100019a5;
  do {
    param_1 = param_1 + 1;
LAB_100019a5:
    cVar1 = *param_1;
    pcVar2 = local_2004;
    while (cVar1 != '\\') {
      if (cVar1 == '\0') goto LAB_100019fe;
      param_1 = param_1 + 1;
      *pcVar2 = cVar1;
      pcVar2 = pcVar2 + 1;
      cVar1 = *param_1;
    }
    param_1 = param_1 + 1;
    *pcVar2 = '\0';
    pcVar2 = &DAT_1002c938 + uVar4 * 0x2000;
    cVar1 = *param_1;
    while ((cVar1 != '\\' && (cVar1 != '\0'))) {
      param_1 = param_1 + 1;
      *pcVar2 = cVar1;
      pcVar2 = pcVar2 + 1;
      cVar1 = *param_1;
    }
    *pcVar2 = '\0';
    iVar3 = FUN_100016c0();
    if (iVar3 == 0) {
      __security_check_cookie(local_4 ^ (uint)local_2004);
      return;
    }
  } while (*param_1 != '\0');
LAB_100019fe:
  __security_check_cookie(local_4 ^ (uint)local_2004);
  return;
}



/* FUN_1001b0c0 @ 1001b0c0 size 277 */

void FUN_1001b0c0(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;
  int iVar5;
  int iVar6;
  int *local_118;
  int local_114;
  char *local_110;
  int local_10c [2];
  char local_104 [256];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_118;
  local_118 = &DAT_1002a0e0;
  do {
    pcVar4 = (char *)local_118[-4];
    iVar5 = 0;
    local_10c[1] = -1;
    local_10c[0] = -1;
    local_114 = 0;
    local_110 = pcVar4;
    do {
      (**(code **)(DAT_106b40d0 + 0x90))(iVar5,local_104,0x100);
      if ((local_104[0] != '\0') && (pcVar4 != (char *)0x0)) {
        iVar1 = -(int)pcVar4;
        iVar6 = 99999;
        do {
          iVar2 = (int)pcVar4[(int)(local_104 + iVar1)];
          iVar3 = (int)*pcVar4;
          pcVar4 = pcVar4 + 1;
          if (iVar6 == 0) break;
          if (iVar2 != iVar3) {
            if (iVar2 - 0x61U < 0x1a) {
              iVar2 = iVar2 + -0x20;
            }
            if (iVar3 - 0x61U < 0x1a) {
              iVar3 = iVar3 + -0x20;
            }
            if (iVar2 != iVar3) {
              pcVar4 = local_110;
              if ((char)((iVar3 <= iVar2) * '\x02') != '\x01') goto LAB_1001b18c;
              break;
            }
          }
          iVar6 = iVar6 + -1;
        } while (iVar2 != 0);
        local_10c[local_114] = iVar5;
        local_114 = local_114 + 1;
        pcVar4 = local_110;
        if (local_114 == 2) break;
      }
LAB_1001b18c:
      iVar5 = iVar5 + 1;
    } while (iVar5 < 0x100);
    *local_118 = local_10c[0];
    local_118[1] = local_10c[1];
    local_118 = local_118 + 6;
    if (0x1002a877 < (int)local_118) {
      __security_check_cookie(local_4 ^ (uint)&local_118);
      return;
    }
  } while( true );
}



/* FUN_100171f0 @ 100171f0 size 275 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_100171f0(void)

{
  uint uVar1;
  int unaff_ESI;
  
  (**(code **)(DAT_106b40d0 + 0x7c))(*(undefined4 *)(unaff_ESI + 0x280));
  uVar1 = *(uint *)(unaff_ESI + 0x48);
  FUN_10021270();
  if ((uVar1 & 0x400) != 0) {
    FUN_10021270();
    return;
  }
  FUN_10021270();
  return;
}



/* FUN_10011510 @ 10011510 size 273 */

void __thiscall FUN_10011510(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  char *pcVar2;
  int iVar3;
  char acStack_804 [1024];
  char local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)acStack_804;
  (**(code **)(DAT_106b40a8 + 0x24))(param_2,local_404,0x400);
  (**(code **)(DAT_106b40a8 + 0x24))(param_1,acStack_804,0x400);
  iVar3 = 0;
  do {
    if (local_404[iVar3] == '\0') break;
    iVar1 = tolower((int)local_404[iVar3]);
    local_404[iVar3] = (char)iVar1;
    iVar3 = iVar3 + 1;
  } while (iVar3 < 0x40);
  iVar3 = 0;
  do {
    if (acStack_804[iVar3] == '\0') break;
    iVar1 = tolower((int)acStack_804[iVar3]);
    acStack_804[iVar3] = (char)iVar1;
    iVar3 = iVar3 + 1;
  } while (iVar3 < 0x40);
  pcVar2 = strstr(acStack_804,"bright");
  if (pcVar2 == (char *)0x0) {
    pcVar2 = strstr(local_404,"bright");
    if ((pcVar2 == (char *)0x0) || (acStack_804[0] != '\0')) {
      (**(code **)(DAT_106b40a8 + 0x1c))();
      goto LAB_10011607;
    }
  }
  (**(code **)(DAT_106b40a8 + 0x1c))();
LAB_10011607:
  __security_check_cookie(local_4 ^ (uint)acStack_804);
  return;
}



/* FUN_10004280 @ 10004280 size 268 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
FUN_10004280(float param_1,float param_2,float *param_3,float param_4,undefined4 param_5,
            undefined4 param_6)

{
  float fVar1;
  float fVar2;
  float *in_EAX;
  float *pfVar3;
  float fVar4;
  float local_4;
  
  fVar4 = param_1;
  if (param_1 == 0.0) {
    fVar4 = -NAN;
  }
  pfVar3 = param_3;
  local_4 = param_1;
  if (in_EAX != (float *)0x0) {
    local_4 = _DAT_10746420 * *in_EAX + DAT_10746424;
    pfVar3 = &local_4;
  }
  fVar1 = DAT_10746424 + _DAT_10746420 * param_2;
  fVar2 = _DAT_1074641c * (float)param_3;
  (**(code **)(DAT_106b40a8 + 0x74))(param_5);
  if (DAT_106b40a4 == _DAT_10029214) {
    DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
  }
  (**(code **)(DAT_106b40a8 + 0x178))
            ((int)fVar1,(int)fVar2,param_6,0,DAT_106b40a4 * param_4,fVar4,pfVar3,0);
  (**(code **)(DAT_106b40a8 + 0x74))(0);
  if (pfVar3 != (float *)0x0) {
    fVar4 = *pfVar3;
    *pfVar3 = fVar4 - DAT_10746424;
    *pfVar3 = (fVar4 - DAT_10746424) / _DAT_10746420;
  }
  return;
}



/* FUN_100155a0 @ 100155a0 size 267 */

void FUN_100155a0(void)

{
  float *pfVar1;
  undefined4 uVar2;
  int iVar3;
  int *piVar4;
  int unaff_EDI;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_24;
  iVar3 = 0;
  if (0 < *(int *)(unaff_EDI + 0x10c)) {
    piVar4 = (int *)(unaff_EDI + 0x154);
    uVar2 = DAT_10029230;
    do {
      pfVar1 = (float *)*piVar4;
      if (pfVar1[0xe] == 7.69313e-43) {
        local_24 = *pfVar1;
        local_20 = pfVar1[1];
        local_1c = pfVar1[2] + local_24;
        local_18 = pfVar1[3] + local_20;
        if (((*(uint *)(unaff_EDI + 0x48) & 4) == 0) &&
           ((*(uint *)(unaff_EDI + 0x48) & 0x100000) == 0)) {
          local_14 = uVar2;
          local_10 = uVar2;
          local_c = uVar2;
          local_8 = uVar2;
          uVar2 = (**(code **)(DAT_106b40d0 + 0xcc))
                            (*(undefined4 *)(*piVar4 + 0x290),&local_14,
                             *(undefined4 *)(*piVar4 + 0x28c));
          *(undefined4 *)(*piVar4 + 0xe8) = uVar2;
          uVar2 = DAT_10029230;
        }
        else {
          uVar2 = (**(code **)(DAT_106b40d0 + 0xcc))
                            (*(undefined4 *)(*piVar4 + 0x290),&local_24,
                             *(undefined4 *)(*piVar4 + 0x28c));
          *(undefined4 *)(*piVar4 + 0xe8) = uVar2;
          uVar2 = DAT_10029230;
        }
      }
      iVar3 = iVar3 + 1;
      piVar4 = piVar4 + 1;
    } while (iVar3 < *(int *)(unaff_EDI + 0x10c));
  }
  __security_check_cookie(local_4 ^ (uint)&local_24);
  return;
}



/* FUN_10002c50 @ 10002c50 size 264 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10002c50(float param_1,float param_2,float param_3,float param_4,undefined4 param_5)

{
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  
  if (0.0 <= param_3) {
    local_8 = 0;
    local_10 = DAT_10029234;
  }
  else {
    param_3 = (float)((uint)param_3 ^ DAT_100292a0);
    local_8 = DAT_10029234;
    local_10 = 0;
  }
  if (0.0 <= param_4) {
    local_c = 0;
    local_14 = DAT_10029234;
  }
  else {
    param_4 = (float)((uint)param_4 ^ DAT_100292a0);
    local_c = DAT_10029234;
    local_14 = 0;
  }
  (**(code **)(DAT_106b40a8 + 0x78))
            (_DAT_10746420 * param_1 + DAT_10746424,_DAT_1074641c * param_2,param_3 * _DAT_10746420,
             _DAT_1074641c * param_4,local_8,local_c,local_10,local_14,param_5);
  return;
}



/* FUN_10014560 @ 10014560 size 262 */

undefined * FUN_10014560(void)

{
  undefined *puVar1;
  byte bVar2;
  undefined4 *puVar3;
  undefined4 *puVar4;
  int iVar5;
  byte *pbVar6;
  int iVar7;
  undefined4 *puVar8;
  byte *pbVar9;
  byte *unaff_EBX;
  bool bVar10;
  
  if (unaff_EBX == (byte *)0x0) {
    return (undefined *)0x0;
  }
  if (*unaff_EBX == 0) {
    return &DAT_100239ab;
  }
  iVar5 = FUN_10014510();
  puVar8 = (undefined4 *)(&DAT_10051058)[iVar5];
  for (puVar3 = puVar8; puVar3 != (undefined4 *)0x0; puVar3 = (undefined4 *)*puVar3) {
    pbVar9 = (byte *)puVar3[1];
    pbVar6 = unaff_EBX;
    do {
      bVar2 = *pbVar6;
      bVar10 = bVar2 < *pbVar9;
      if (bVar2 != *pbVar9) {
LAB_100145b5:
        iVar7 = (1 - (uint)bVar10) - (uint)(bVar10 != 0);
        goto LAB_100145ba;
      }
      if (bVar2 == 0) break;
      bVar2 = pbVar6[1];
      bVar10 = bVar2 < pbVar9[1];
      if (bVar2 != pbVar9[1]) goto LAB_100145b5;
      pbVar6 = pbVar6 + 2;
      pbVar9 = pbVar9 + 2;
    } while (bVar2 != 0);
    iVar7 = 0;
LAB_100145ba:
    if (iVar7 == 0) {
      return (undefined *)puVar3[1];
    }
  }
  pbVar9 = unaff_EBX + 1;
  pbVar6 = unaff_EBX;
  do {
    bVar2 = *pbVar6;
    pbVar6 = pbVar6 + 1;
  } while (bVar2 != 0);
  if (0x5ffff < (int)(pbVar6 + (((int)DAT_106b40f4 + 1) - (int)pbVar9))) {
    return (undefined *)0x0;
  }
  puVar1 = &DAT_10653058 + (int)DAT_106b40f4;
  iVar7 = (int)puVar1 - (int)unaff_EBX;
  do {
    bVar2 = *unaff_EBX;
    unaff_EBX[iVar7] = bVar2;
    unaff_EBX = unaff_EBX + 1;
    puVar3 = puVar8;
  } while (bVar2 != 0);
  do {
    puVar4 = puVar3;
    puVar3 = puVar8;
    if (puVar3 == (undefined4 *)0x0) break;
    puVar8 = (undefined4 *)*puVar3;
  } while ((undefined4 *)*puVar3 != (undefined4 *)0x0);
  DAT_106b40f4 = pbVar6 + (((int)DAT_106b40f4 + 1) - (int)pbVar9);
  puVar8 = (undefined4 *)FUN_100144c0();
  if (puVar8 == (undefined4 *)0x0) {
    return (undefined *)0x0;
  }
  *puVar8 = 0;
  puVar8[1] = puVar1;
  if (puVar4 != (undefined4 *)0x0) {
    *puVar4 = puVar8;
    return puVar1;
  }
  (&DAT_10051058)[iVar5] = puVar8;
  return puVar1;
}



/* ___report_gsfailure @ 10020d89 size 262 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Library Function - Single Match
    ___report_gsfailure
   
   Libraries: Visual Studio 2005 Release, Visual Studio 2008 Release, Visual Studio 2010 Release */

void __cdecl ___report_gsfailure(void)

{
  undefined4 in_EAX;
  HANDLE hProcess;
  undefined4 in_ECX;
  undefined4 in_EDX;
  undefined4 unaff_EBX;
  undefined4 unaff_EBP;
  undefined4 unaff_ESI;
  undefined4 unaff_EDI;
  undefined2 in_ES;
  undefined2 in_CS;
  undefined2 in_SS;
  undefined2 in_DS;
  undefined2 in_FS;
  undefined2 in_GS;
  byte in_AF;
  byte in_TF;
  byte in_IF;
  byte in_NT;
  byte in_AC;
  byte in_VIF;
  byte in_VIP;
  byte in_ID;
  undefined4 unaff_retaddr;
  UINT uExitCode;
  undefined4 local_32c;
  undefined4 local_328;
  
  _DAT_1002c5e0 =
       (uint)(in_NT & 1) * 0x4000 | (uint)SBORROW4((int)&stack0xfffffffc,0x328) * 0x800 |
       (uint)(in_IF & 1) * 0x200 | (uint)(in_TF & 1) * 0x100 | (uint)((int)&local_32c < 0) * 0x80 |
       (uint)(&stack0x00000000 == (undefined1 *)0x32c) * 0x40 | (uint)(in_AF & 1) * 0x10 |
       (uint)((POPCOUNT((uint)&local_32c & 0xff) & 1U) == 0) * 4 |
       (uint)(&stack0xfffffffc < (undefined1 *)0x328) | (uint)(in_ID & 1) * 0x200000 |
       (uint)(in_VIP & 1) * 0x100000 | (uint)(in_VIF & 1) * 0x80000 | (uint)(in_AC & 1) * 0x40000;
  _DAT_1002c5e4 = &stack0x00000004;
  _DAT_1002c520 = 0x10001;
  _DAT_1002c4c8 = 0xc0000409;
  _DAT_1002c4cc = 1;
  local_32c = DAT_1002a000;
  local_328 = DAT_1002a004;
  _DAT_1002c4d4 = unaff_retaddr;
  _DAT_1002c5ac = in_GS;
  _DAT_1002c5b0 = in_FS;
  _DAT_1002c5b4 = in_ES;
  _DAT_1002c5b8 = in_DS;
  _DAT_1002c5bc = unaff_EDI;
  _DAT_1002c5c0 = unaff_ESI;
  _DAT_1002c5c4 = unaff_EBX;
  _DAT_1002c5c8 = in_EDX;
  _DAT_1002c5cc = in_ECX;
  _DAT_1002c5d0 = in_EAX;
  _DAT_1002c5d4 = unaff_EBP;
  DAT_1002c5d8 = unaff_retaddr;
  _DAT_1002c5dc = in_CS;
  _DAT_1002c5e8 = in_SS;
  DAT_1002c518 = IsDebuggerPresent();
  _crt_debugger_hook(1);
  SetUnhandledExceptionFilter((LPTOP_LEVEL_EXCEPTION_FILTER)0x0);
  UnhandledExceptionFilter((_EXCEPTION_POINTERS *)&PTR_DAT_10022110);
  if (DAT_1002c518 == 0) {
    _crt_debugger_hook(1);
  }
  uExitCode = 0xc0000409;
  hProcess = GetCurrentProcess();
  TerminateProcess(hProcess,uExitCode);
  return;
}



/* FUN_100169d0 @ 100169d0 size 256 */

void FUN_100169d0(undefined4 param_1,undefined4 param_2)

{
  char *pcVar1;
  int iVar2;
  double dVar3;
  undefined4 local_14;
  float local_10;
  float local_c;
  undefined1 local_8 [4];
  float local_4;
  
  pcVar1 = (char *)FUN_10001500(param_2,0);
  if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
    FUN_10014560();
    pcVar1 = (char *)FUN_10001500(param_2,0);
    if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
      dVar3 = atof(pcVar1);
      local_c = (float)dVar3;
      pcVar1 = (char *)FUN_10001500(param_2,0);
      if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
        dVar3 = atof(pcVar1);
        local_10 = (float)dVar3;
        pcVar1 = (char *)FUN_10001500(param_2,0);
        if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
          dVar3 = atof(pcVar1);
          local_4 = (float)dVar3;
          iVar2 = FUN_100148a0(local_8);
          if ((iVar2 != 0) && (iVar2 = FUN_10014ab0(&local_14), iVar2 != 0)) {
            FUN_100168a0(local_c,local_10,local_14);
          }
        }
      }
    }
  }
  return;
}



/* FUN_100180a0 @ 100180a0 size 255 */

undefined4 __fastcall FUN_100180a0(undefined4 param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  float *unaff_ESI;
  float10 fVar3;
  
  if ((((((unaff_ESI != (float *)0x0) && (*unaff_ESI < (float)*(int *)(DAT_106b40d0 + 0xf0))) &&
        ((float)*(int *)(DAT_106b40d0 + 0xf0) < unaff_ESI[2] + *unaff_ESI)) &&
       ((unaff_ESI[1] < (float)*(int *)(DAT_106b40d0 + 0xf4) &&
        ((float)*(int *)(DAT_106b40d0 + 0xf4) < unaff_ESI[3] + unaff_ESI[1])))) &&
      ((((uint)unaff_ESI[0x12] & 2) != 0 && (unaff_ESI[0x56] != 0.0)))) &&
     ((((param_2 == 0xb2 || (param_2 == 0xd)) || (param_2 == 0xb3)) || (param_2 == 0xb4)))) {
    fVar3 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(unaff_ESI[0x56]);
    iVar1 = DAT_106b40d0;
    uVar2 = FUN_10001900(&DAT_10025920,fVar3 == (float10)0);
    (**(code **)(iVar1 + 0x60))(unaff_ESI[0x56],uVar2);
    return 1;
  }
  return 0;
}



/* FUN_10012390 @ 10012390 size 254 */

void FUN_10012390(int param_1)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  uint in_EAX;
  undefined4 uVar4;
  int iVar5;
  undefined4 *unaff_ESI;
  uint uVar6;
  
  if ((in_EAX != unaff_ESI[9]) || (unaff_ESI[10] == 0)) {
    unaff_ESI[9] = in_EAX;
    iVar5 = DAT_106b40a8;
    uVar6 = in_EAX & 0xffffff7f;
    if (((int)uVar6 < 0) || (0x1e < (int)uVar6)) {
      uVar4 = FUN_10001900("Bad animation number: %i",uVar6);
      (**(code **)(iVar5 + 4))(uVar4);
    }
    param_1 = param_1 + (uVar6 * 3 + 0xf) * 8;
    unaff_ESI[10] = param_1;
    unaff_ESI[0xb] = *(int *)(param_1 + 0x10) + unaff_ESI[3];
  }
  iVar3 = DAT_1004fe5c;
  iVar5 = unaff_ESI[3];
  if (iVar5 <= DAT_1004fe5c) {
    piVar1 = (int *)unaff_ESI[10];
    *unaff_ESI = unaff_ESI[2];
    iVar2 = unaff_ESI[0xb];
    unaff_ESI[1] = iVar5;
    if (iVar3 < iVar2) {
      unaff_ESI[3] = iVar2;
    }
    else {
      unaff_ESI[3] = piVar1[3] + iVar5;
    }
    iVar5 = (unaff_ESI[3] - iVar2) / piVar1[3];
    iVar2 = piVar1[1];
    if (iVar2 <= iVar5) {
      if (piVar1[2] == 0) {
        iVar5 = iVar2 + -1;
        unaff_ESI[3] = iVar3;
      }
      else {
        iVar5 = iVar2 + ((iVar5 - iVar2) % piVar1[2] - piVar1[2]);
      }
    }
    unaff_ESI[2] = *piVar1 + iVar5;
    if ((int)unaff_ESI[3] < iVar3) {
      unaff_ESI[3] = iVar3;
    }
  }
  if (iVar3 + 200 < (int)unaff_ESI[3]) {
    unaff_ESI[3] = iVar3;
  }
  if (iVar3 < (int)unaff_ESI[1]) {
    unaff_ESI[1] = iVar3;
  }
  iVar5 = unaff_ESI[1];
  if (unaff_ESI[3] == iVar5) {
    unaff_ESI[4] = 0;
    return;
  }
  unaff_ESI[4] = 1.0 - (float)(iVar3 - iVar5) / (float)(unaff_ESI[3] - iVar5);
  return;
}



/* FUN_1000a110 @ 1000a110 size 253 */

undefined4 FUN_1000a110(void)

{
  int in_EAX;
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if ((((in_EAX != 0xb2) && (in_EAX != 0xb3)) && (in_EAX != 0xd)) && (in_EAX != 0xa9)) {
    return 0;
  }
  iVar1 = FUN_1000d3c0(1);
  iVar3 = DAT_106b40a8;
  if (in_EAX == 0xb3) {
    DAT_1074220c = DAT_1074220c + -1;
    if (DAT_1074220c == 2) {
      DAT_1074220c = 1;
    }
    else if (DAT_1074220c < 2) {
      DAT_1074220c = DAT_107596a4 + -1;
    }
  }
  else {
    DAT_1074220c = DAT_1074220c + 1;
    if (DAT_1074220c < DAT_107596a4) {
      if (DAT_1074220c == 2) {
        DAT_1074220c = 3;
      }
    }
    else {
      DAT_1074220c = 1;
    }
  }
  uVar2 = FUN_10001900(&DAT_10025d20,DAT_1074220c);
  (**(code **)(iVar3 + 0x1c))("ui_gameType",uVar2);
  FUN_100051b0();
  FUN_10002350();
  iVar3 = FUN_1000d3c0(1);
  if (iVar1 != iVar3) {
    (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentMap",&DAT_100252c0);
    FUN_1001d3d0(1);
  }
  return 1;
}



/* FUN_1000d530 @ 1000d530 size 253 */

int FUN_1000d530(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  
  iVar3 = 0;
  iVar4 = 0;
  if (0 < DAT_1075829c) {
    piVar5 = &DAT_107582a4;
    do {
      if (((param_1 != 1) || (iVar2 = *piVar5, iVar2 == 0)) ||
         ((iVar1 = FUN_100016c0(), iVar1 != 0 &&
          ((iVar2 == 0 ||
           ((iVar1 = FUN_100016c0(), iVar1 != 0 &&
            ((iVar2 == 0 ||
             ((iVar1 = FUN_100016c0(), iVar1 != 0 &&
              ((iVar2 == 0 ||
               ((iVar1 = FUN_100016c0(), iVar1 != 0 &&
                ((iVar2 == 0 ||
                 ((iVar1 = FUN_100016c0(), iVar1 != 0 &&
                  ((iVar2 == 0 || (iVar2 = FUN_100016c0(), iVar2 != 0)))))))))))))))))))))) {
        if (piVar5[4] == 0) {
          iVar2 = FUN_1000d490(iVar3);
          if (iVar2 == 0) goto LAB_1000d616;
          piVar5[4] = 1;
        }
        iVar4 = iVar4 + 1;
      }
LAB_1000d616:
      iVar3 = iVar3 + 1;
      piVar5 = piVar5 + 5;
    } while (iVar3 < DAT_1075829c);
  }
  return iVar4;
}



/* FUN_1001a7e0 @ 1001a7e0 size 253 */

void __fastcall FUN_1001a7e0(int param_1)

{
  char *pcVar1;
  undefined1 local_424 [8];
  undefined1 auStack_41c [16];
  char local_40c [1028];
  uint local_8;
  
  local_8 = DAT_1002a000 ^ (uint)local_424;
  if ((*(uint *)(param_1 + 0x48) & 0x40000) == 0) {
    if ((*(uint *)(param_1 + 0x48) & 0x80000) == 0) {
      pcVar1 = *(char **)(param_1 + 0x130);
      if (pcVar1 == (char *)0x0) {
        if (*(int *)(param_1 + 0x158) == 0) goto LAB_1001a8c4;
        (**(code **)(DAT_106b40d0 + 0x58))(*(int *)(param_1 + 0x158),local_40c,0x400);
        pcVar1 = local_40c;
      }
      FUN_10019f10(pcVar1);
      if (*pcVar1 != '\0') {
        FUN_1001a150(auStack_41c);
        (**(code **)(DAT_106b40d0 + 0x10))
                  (*(undefined4 *)(param_1 + 0x100),*(undefined4 *)(param_1 + 0x104),
                   *(undefined4 *)(param_1 + 0x124),*(undefined4 *)(param_1 + 0x128),auStack_41c,
                   pcVar1,0,0,*(undefined4 *)(param_1 + 300));
      }
    }
    else {
      FUN_1001a3d0();
    }
  }
  else {
    FUN_1001a630();
  }
LAB_1001a8c4:
  __security_check_cookie(local_8 ^ (uint)local_424);
  return;
}



/* FUN_10001400 @ 10001400 size 252 */

int FUN_10001400(char *param_1)

{
  char *pcVar1;
  bool bVar2;
  bool bVar3;
  char *pcVar4;
  char *pcVar5;
  char cVar6;
  
  bVar2 = false;
  bVar3 = false;
  pcVar4 = param_1;
  if (param_1 != (char *)0x0) {
    cVar6 = *param_1;
    pcVar5 = param_1;
    while (cVar6 != '\0') {
      if (cVar6 == '/') {
        if (pcVar5[1] == '/') {
          cVar6 = *pcVar5;
          while ((cVar6 != '\0' && (cVar6 != '\n'))) {
            pcVar1 = pcVar5 + 1;
            pcVar5 = pcVar5 + 1;
            cVar6 = *pcVar1;
          }
        }
        else if (pcVar5[1] == '*') {
          cVar6 = *pcVar5;
          while (cVar6 != '\0') {
            if ((cVar6 == '*') && (pcVar5[1] == '/')) {
              if (*pcVar5 != '\0') {
                pcVar5 = pcVar5 + 2;
              }
              break;
            }
            pcVar1 = pcVar5 + 1;
            pcVar5 = pcVar5 + 1;
            cVar6 = *pcVar1;
          }
        }
        else {
LAB_10001498:
          if (bVar2) {
            *pcVar4 = '\n';
            bVar2 = false;
LAB_100014aa:
            pcVar4 = pcVar4 + 1;
            bVar3 = false;
          }
          else if (bVar3) {
            *pcVar4 = ' ';
            goto LAB_100014aa;
          }
          if (cVar6 != '\"') {
LAB_100014d5:
            *pcVar4 = cVar6;
            pcVar4 = pcVar4 + 1;
            goto LAB_100014e6;
          }
          pcVar5 = pcVar5 + 1;
          *pcVar4 = '\"';
          cVar6 = *pcVar5;
          while (pcVar4 = pcVar4 + 1, cVar6 != '\0') {
            if (cVar6 == '\"') goto LAB_100014d5;
            pcVar5 = pcVar5 + 1;
            *pcVar4 = cVar6;
            cVar6 = *pcVar5;
          }
        }
      }
      else {
        if ((cVar6 == '\n') || (cVar6 == '\r')) {
          bVar2 = true;
        }
        else {
          if ((cVar6 != ' ') && (cVar6 != '\t')) goto LAB_10001498;
          bVar3 = true;
        }
LAB_100014e6:
        pcVar5 = pcVar5 + 1;
      }
      cVar6 = *pcVar5;
    }
  }
  *pcVar4 = '\0';
  return (int)pcVar4 - (int)param_1;
}



/* FUN_10006f30 @ 10006f30 size 250 */

void FUN_10006f30(float *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iStack_408;
  char local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&iStack_408;
  memset(local_404,0,0x400);
  (**(code **)(DAT_106b40a8 + 0x24))("ui_votestring",local_404,0x3ff);
  if (local_404[0] != '\0') {
    iVar1 = (int)*param_1;
    FUN_10003d90(0,param_2);
    if ((0 < iVar1) && (0 < iStack_408)) {
      iVar1 = iVar1 - iStack_408 / 2;
    }
    FUN_10003ec0((float)iVar1,param_1[1],0,param_2,param_3,local_404,0,0,param_4);
  }
  __security_check_cookie(local_4 ^ (uint)&iStack_408);
  return;
}



/* FUN_10017310 @ 10017310 size 250 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10017310(void)

{
  float *in_EAX;
  int iVar1;
  float10 fVar2;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 extraout_ST1;
  float10 extraout_ST1_00;
  float10 fVar3;
  
  if (DAT_106b40cc == in_EAX) {
    if (((uint)in_EAX[0x12] & 0x400) == 0) {
      fVar2 = (float10)in_EAX[1];
      iVar1 = FUN_10021270();
      if (fVar2 < (float10)iVar1 + (float10)_DAT_10029220) goto LAB_10017402;
      iVar1 = FUN_10021270();
      fVar2 = extraout_ST0_00;
      fVar3 = extraout_ST1_00;
    }
    else {
      fVar2 = (float10)*in_EAX;
      iVar1 = FUN_10021270();
      if (fVar2 < (float10)iVar1 + (float10)_DAT_10029220) goto LAB_10017402;
      iVar1 = FUN_10021270();
      fVar2 = extraout_ST0;
      fVar3 = extraout_ST1;
    }
    if (fVar2 <= (float10)iVar1 + fVar3) {
      FUN_10021270();
      return;
    }
  }
LAB_10017402:
  FUN_100171f0();
  return;
}



/* FUN_100208f0 @ 100208f0 size 249 */

undefined4 FUN_100208f0(int param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  if ((((param_1 == 0) || ((*(uint *)(param_1 + 0x48) & 0x100004) == 0)) ||
      (iVar1 = FUN_10015c00(param_2,param_3), iVar1 == 0)) ||
     (iVar1 = 0, *(int *)(param_1 + 0x10c) < 1)) {
    return 0;
  }
  piVar4 = (int *)(param_1 + 0x154);
  do {
    iVar3 = *piVar4;
    if ((((*(uint *)(iVar3 + 0x48) & 0x100004) != 0) && ((*(uint *)(iVar3 + 0x48) & 0x10) == 0)) &&
       (iVar2 = FUN_10015c00(param_2,param_3), iVar2 != 0)) {
      if ((*(int *)(iVar3 + 0x110) != 0) || (*(int *)(iVar3 + 0x130) == 0)) {
        if (((*(byte *)(iVar3 + 0x17c) & 0xc) != 0) && (iVar1 = FUN_10016e70(4), iVar1 == 0)) {
          return 0;
        }
        return 1;
      }
      FUN_10019970(param_2,param_3);
      iVar3 = FUN_10015c00();
      if (iVar3 != 0) {
        return 1;
      }
    }
    iVar1 = iVar1 + 1;
    piVar4 = piVar4 + 1;
    if (*(int *)(param_1 + 0x10c) <= iVar1) {
      return 0;
    }
  } while( true );
}



/* FUN_10012290 @ 10012290 size 248 */

void __fastcall FUN_10012290(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int unaff_ESI;
  int unaff_EDI;
  undefined1 auStack_60 [4];
  float local_5c;
  float local_34;
  float fStack_30;
  float fStack_2c;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)auStack_60;
  local_5c = 1.0 - *(float *)(unaff_EDI + 100);
  (**(code **)(DAT_106b40a8 + 0x84))
            (&local_34,param_2,*(undefined4 *)(unaff_EDI + 0x60),*(undefined4 *)(unaff_EDI + 0x50),
             local_5c,param_3);
  *(undefined4 *)(unaff_ESI + 0x44) = *(undefined4 *)(unaff_EDI + 0x44);
  *(undefined4 *)(unaff_ESI + 0x48) = *(undefined4 *)(unaff_EDI + 0x48);
  *(undefined4 *)(unaff_ESI + 0x4c) = *(undefined4 *)(unaff_EDI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       local_34 * *(float *)(unaff_EDI + 0x1c) + *(float *)(unaff_ESI + 0x44);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x20) * local_34 + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       local_34 * *(float *)(unaff_EDI + 0x24) + *(float *)(unaff_ESI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       *(float *)(unaff_ESI + 0x44) + fStack_30 * *(float *)(unaff_EDI + 0x28);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x2c) * fStack_30 + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       fStack_30 * *(float *)(unaff_EDI + 0x30) + *(float *)(unaff_ESI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       *(float *)(unaff_ESI + 0x44) + fStack_2c * *(float *)(unaff_EDI + 0x34);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x38) * fStack_2c + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       fStack_2c * *(float *)(unaff_EDI + 0x3c) + *(float *)(unaff_ESI + 0x4c);
  FUN_100011c0();
  FUN_100011c0();
  __security_check_cookie(local_4 ^ (uint)auStack_60);
  return;
}



/* FUN_1000a820 @ 1000a820 size 247 */

undefined4 __thiscall
FUN_1000a820(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5
            )

{
  undefined4 uVar1;
  float10 fVar2;
  
  switch(param_2) {
  case 0x201:
    uVar1 = FUN_1000a040();
    return uVar1;
  case 0x203:
    uVar1 = FUN_1000a110();
    return uVar1;
  case 0x205:
    uVar1 = FUN_1000a390();
    return uVar1;
  case 0x206:
    FUN_1000a420();
    break;
  case 0x208:
    FUN_1000a4f0();
    return 0;
  case 0x213:
    uVar1 = FUN_1000a570();
    return uVar1;
  case 0x214:
    uVar1 = FUN_1000a5d0();
    return uVar1;
  case 0x215:
    if ((((param_5 == 0xb2) || (param_5 == 0xb3)) || (param_5 == 0xd)) || (param_5 == 0xa9)) {
      DAT_107597ac = DAT_107597ac ^ 1;
      return 0;
    }
    break;
  case 0x216:
    FUN_1000a640();
    return 0;
  case 0x217:
    FUN_1000a6c0();
    return 0;
  case 0x219:
    uVar1 = FUN_1000a210();
    return uVar1;
  case 0x221:
    uVar1 = FUN_1000a300();
    return uVar1;
  case 0x226:
    fVar2 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("cg_crosshairHealth",param_1);
    if (fVar2 == (float10)0) {
      uVar1 = FUN_1000a790();
      return uVar1;
    }
  }
  return 0;
}



/* FUN_100147a0 @ 100147a0 size 247 */

void __fastcall FUN_100147a0(float *param_1,float *param_2,float param_3)

{
  float fVar1;
  float fVar2;
  float *in_EAX;
  
  fVar2 = DAT_10029234;
  fVar1 = param_3 * (*param_1 - *param_2) + *param_2;
  *in_EAX = fVar1;
  if (0.0 <= fVar1) {
    if (fVar2 < fVar1) {
      *in_EAX = fVar2;
    }
  }
  else {
    *in_EAX = 0.0;
  }
  fVar1 = param_2[1] + param_3 * (param_1[1] - param_2[1]);
  in_EAX[1] = fVar1;
  if (0.0 <= fVar1) {
    if (fVar2 < fVar1) {
      in_EAX[1] = fVar2;
    }
  }
  else {
    in_EAX[1] = 0.0;
  }
  fVar1 = param_2[2] + param_3 * (param_1[2] - param_2[2]);
  in_EAX[2] = fVar1;
  if (0.0 <= fVar1) {
    if (fVar2 < fVar1) {
      in_EAX[2] = fVar2;
    }
  }
  else {
    in_EAX[2] = 0.0;
  }
  fVar1 = param_2[3] + (param_1[3] - param_2[3]) * param_3;
  in_EAX[3] = fVar1;
  if (fVar1 < 0.0) {
    in_EAX[3] = 0.0;
    return;
  }
  if (fVar2 < fVar1) {
    in_EAX[3] = fVar2;
  }
  return;
}



/* FUN_1001e470 @ 1001e470 size 247 */

void FUN_1001e470(int param_1,undefined4 param_2)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  int local_424;
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)&local_424;
  iVar3 = 0;
  puVar2 = (uint *)(param_1 + 0x78);
  do {
    local_424 = 0;
    iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
    if (iVar1 == 0) {
LAB_1001e559:
      __security_check_cookie(local_c ^ (uint)&local_424);
      return;
    }
    iVar1 = local_424;
    if (acStack_410[0] == '-') {
      iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      if (iVar1 == 0) goto LAB_1001e559;
      iVar1 = 1;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_2,"expected float but found %s\n",acStack_410);
      goto LAB_1001e559;
    }
    uVar4 = uStack_414;
    if (iVar1 != 0) {
      uVar4 = uStack_414 ^ DAT_100292a0;
    }
    *puVar2 = uVar4;
    *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 0x200;
    iVar3 = iVar3 + 1;
    puVar2 = puVar2 + 1;
    if (3 < iVar3) {
      __security_check_cookie(local_c ^ (uint)&local_424);
      return;
    }
  } while( true );
}



/* FUN_10016d70 @ 10016d70 size 246 */

void __thiscall FUN_10016d70(char *param_1,int param_2)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined1 *local_808;
  undefined1 local_804 [2048];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_808;
  memset(local_804,0,0x800);
  if (((param_2 != 0) && (param_1 != (char *)0x0)) && (*param_1 != '\0')) {
    FUN_10001750(param_1);
    local_808 = local_804;
LAB_10016dd6:
    do {
      pcVar1 = (char *)FUN_10001500(&local_808,0);
      if ((pcVar1 == (char *)0x0) || (*pcVar1 == '\0')) break;
      pcVar1 = (char *)FUN_10014560();
      if ((*pcVar1 != ';') || (pcVar1[1] != '\0')) {
        iVar3 = 0;
        do {
          if (((&PTR_s_fadein_1002a018)[iVar3 * 2] != (undefined *)0x0) &&
             (iVar2 = FUN_100016c0(), iVar2 == 0)) {
            (*(code *)(&PTR_FUN_1002a01c)[iVar3 * 2])(param_2,&local_808);
            goto LAB_10016dd6;
          }
          iVar3 = iVar3 + 1;
        } while (iVar3 < 0x17);
        (**(code **)(DAT_106b40d0 + 0x50))(&local_808);
      }
    } while( true );
  }
  __security_check_cookie(local_4 ^ (uint)&local_808);
  return;
}



/* FUN_100195b0 @ 100195b0 size 246 */

undefined4 FUN_100195b0(void)

{
  int iVar1;
  int iVar2;
  int unaff_ESI;
  bool bVar3;
  
  iVar1 = *(int *)(unaff_ESI + 0x114);
  bVar3 = iVar1 == -1;
  if (bVar3) {
    *(undefined4 *)(unaff_ESI + 0x114) = 0;
  }
  if (*(int *)(unaff_ESI + 0x114) < *(int *)(unaff_ESI + 0x10c)) {
    do {
      *(int *)(unaff_ESI + 0x114) = *(int *)(unaff_ESI + 0x114) + 1;
      if ((*(int *)(unaff_ESI + 0x10c) <= *(int *)(unaff_ESI + 0x114)) && (!bVar3)) {
        bVar3 = true;
        *(undefined4 *)(unaff_ESI + 0x114) = 0;
      }
      iVar2 = FUN_10016fc0((float)*(int *)(DAT_106b40d0 + 0xf0),(float)*(int *)(DAT_106b40d0 + 0xf4)
                          );
      if (iVar2 != 0) {
        FUN_1001d600();
        return *(undefined4 *)(unaff_ESI + 0x154 + *(int *)(unaff_ESI + 0x114) * 4);
      }
    } while (*(int *)(unaff_ESI + 0x114) < *(int *)(unaff_ESI + 0x10c));
  }
  *(int *)(unaff_ESI + 0x114) = iVar1;
  return 0;
}



/* FUN_10012190 @ 10012190 size 245 */

void __fastcall FUN_10012190(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int unaff_ESI;
  int unaff_EDI;
  float local_38;
  float local_34;
  float fStack_30;
  float fStack_2c;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_38;
  local_38 = 1.0 - *(float *)(unaff_EDI + 100);
  (**(code **)(DAT_106b40a8 + 0x84))
            (&local_34,param_2,*(undefined4 *)(unaff_EDI + 0x60),*(undefined4 *)(unaff_EDI + 0x50),
             local_38,param_3);
  *(undefined4 *)(unaff_ESI + 0x44) = *(undefined4 *)(unaff_EDI + 0x44);
  *(undefined4 *)(unaff_ESI + 0x48) = *(undefined4 *)(unaff_EDI + 0x48);
  *(undefined4 *)(unaff_ESI + 0x4c) = *(undefined4 *)(unaff_EDI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       *(float *)(unaff_ESI + 0x44) + local_34 * *(float *)(unaff_EDI + 0x1c);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x20) * local_34 + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       local_34 * *(float *)(unaff_EDI + 0x24) + *(float *)(unaff_ESI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       *(float *)(unaff_ESI + 0x44) + fStack_30 * *(float *)(unaff_EDI + 0x28);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x2c) * fStack_30 + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       fStack_30 * *(float *)(unaff_EDI + 0x30) + *(float *)(unaff_ESI + 0x4c);
  *(float *)(unaff_ESI + 0x44) =
       *(float *)(unaff_ESI + 0x44) + fStack_2c * *(float *)(unaff_EDI + 0x34);
  *(float *)(unaff_ESI + 0x48) =
       *(float *)(unaff_EDI + 0x38) * fStack_2c + *(float *)(unaff_ESI + 0x48);
  *(float *)(unaff_ESI + 0x4c) =
       fStack_2c * *(float *)(unaff_EDI + 0x3c) + *(float *)(unaff_ESI + 0x4c);
  FUN_100011c0();
  *(undefined4 *)(unaff_ESI + 100) = *(undefined4 *)(unaff_EDI + 100);
  __security_check_cookie(local_4 ^ (uint)&local_38);
  return;
}



/* FUN_100194b0 @ 100194b0 size 245 */

undefined4 FUN_100194b0(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int unaff_ESI;
  bool bVar4;
  
  iVar2 = *(int *)(unaff_ESI + 0x114);
  bVar4 = iVar2 < 0;
  if (bVar4) {
    *(int *)(unaff_ESI + 0x114) = *(int *)(unaff_ESI + 0x10c) + -1;
  }
  if (-1 < *(int *)(unaff_ESI + 0x114)) {
    do {
      piVar1 = (int *)(unaff_ESI + 0x114);
      *piVar1 = *piVar1 + -1;
      if ((*piVar1 < 0) && (!bVar4)) {
        bVar4 = true;
        *(int *)(unaff_ESI + 0x114) = *(int *)(unaff_ESI + 0x10c) + -1;
      }
      iVar3 = FUN_10016fc0((float)*(int *)(DAT_106b40d0 + 0xf0),(float)*(int *)(DAT_106b40d0 + 0xf4)
                          );
      if (iVar3 != 0) {
        FUN_1001d600();
        return *(undefined4 *)(unaff_ESI + 0x154 + *(int *)(unaff_ESI + 0x114) * 4);
      }
    } while (*(uint *)(unaff_ESI + 0x114) < 0x80000000);
  }
  *(int *)(unaff_ESI + 0x114) = iVar2;
  return 0;
}



/* FUN_100207f0 @ 100207f0 size 244 */

void FUN_100207f0(void)

{
  int iVar1;
  char *pcVar2;
  undefined4 uVar3;
  int *piVar4;
  int iVar5;
  undefined4 *puVar6;
  int iVar7;
  
  iVar5 = 0;
  if (0 < DAT_106b40e4) {
    puVar6 = &DAT_106b4a50;
    do {
      if (puVar6 != (undefined4 *)0x130) {
        if (puVar6[-0x42] != 0) {
          uVar3 = (**(code **)(DAT_106b40d0 + 0xb8))(puVar6[-0x42],0,0,0,0);
          (**(code **)(DAT_106b40d0 + 0xbc))(uVar3);
        }
        iVar7 = 0;
        if (0 < (int)puVar6[-9]) {
          piVar4 = puVar6 + 9;
          do {
            if ((*piVar4 != 0) && (iVar1 = *(int *)(*piVar4 + 0x28), iVar1 != 0)) {
              uVar3 = (**(code **)(DAT_106b40d0 + 0xb8))(iVar1,0,0,0,0);
              (**(code **)(DAT_106b40d0 + 0xbc))(uVar3);
            }
            iVar7 = iVar7 + 1;
            piVar4 = piVar4 + 1;
          } while (iVar7 < (int)puVar6[-9]);
        }
        pcVar2 = (char *)*puVar6;
        if ((pcVar2 != (char *)0x0) && (*pcVar2 != '\0')) {
          (**(code **)(DAT_106b40d0 + 0xac))(pcVar2);
        }
      }
      iVar5 = iVar5 + 1;
      puVar6 = puVar6 + 0x455;
    } while (iVar5 < DAT_106b40e4);
  }
  return;
}



/* FUN_1000da60 @ 1000da60 size 240 */

void FUN_1000da60(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  char *pcVar4;
  int iVar5;
  char *pcVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  int local_14;
  int local_10;
  int local_c;
  undefined **local_8;
  
  local_14 = 0;
  local_c = 0;
  if (PTR_s_sv_hostname_1002af48 != (undefined *)0x0) {
    local_8 = &PTR_s_sv_hostname_1002af48;
    iVar7 = 0;
    do {
      local_10 = 0;
      if (0 < *(int *)(param_1 + 0xd00)) {
        piVar8 = (int *)((local_14 + 4) * 0x10 + param_1);
        piVar9 = (int *)(param_1 + 0x40);
        do {
          if (((((char *)piVar9[1] != (char *)0x0) && (*(char *)piVar9[1] == '\0')) &&
              (iVar2 = *piVar9, *local_8 != (undefined *)0x0)) &&
             ((iVar2 != 0 && (iVar5 = FUN_100016c0(), iVar5 == 0)))) {
            iVar5 = *piVar8;
            iVar3 = piVar8[3];
            *piVar8 = iVar2;
            piVar8[3] = piVar9[3];
            *piVar9 = iVar5;
            piVar9[3] = iVar3;
            pcVar4 = *(char **)((int)&PTR_DAT_1002af4c + iVar7);
            pcVar6 = pcVar4;
            do {
              cVar1 = *pcVar6;
              pcVar6 = pcVar6 + 1;
            } while (cVar1 != '\0');
            if (pcVar6 != pcVar4 + 1) {
              *piVar8 = (int)pcVar4;
            }
            local_14 = local_14 + 1;
            piVar8 = piVar8 + 4;
          }
          local_10 = local_10 + 1;
          piVar9 = piVar9 + 4;
        } while (local_10 < *(int *)(param_1 + 0xd00));
      }
      local_c = local_c + 1;
      iVar7 = local_c * 8;
      local_8 = &PTR_s_sv_hostname_1002af48 + local_c * 2;
    } while (*local_8 != (undefined *)0x0);
  }
  return;
}



/* ___DllMainCRTStartup @ 10020c50 size 240 */

/* WARNING: Function: __SEH_prolog4 replaced with injection: SEH_prolog4 */
/* WARNING: Function: __SEH_epilog4 replaced with injection: EH_epilog3 */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* Library Function - Single Match
    ___DllMainCRTStartup
   
   Library: Visual Studio 2010 Release */

int __fastcall ___DllMainCRTStartup(undefined4 param_1,int param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 local_20;
  
  local_20 = 1;
  _DAT_1002a008 = param_2;
  if ((param_2 == 0) && (DAT_1002c4c0 == 0)) {
    local_20 = 0;
    goto LAB_10020d42;
  }
  if ((param_2 == 1) || (param_2 == 2)) {
    if (DAT_1002210c != (code *)0x0) {
      local_20 = (*DAT_1002210c)(param_3,param_2,param_1);
    }
    if (local_20 == 0) goto LAB_10020d42;
    local_20 = __CRT_INIT_12(param_3,param_2,param_1);
    if (local_20 == 0) goto LAB_10020d42;
  }
  local_20 = _DllMain_12(param_3,param_2,param_1);
  if ((param_2 == 1) && (local_20 == 0)) {
    _DllMain_12(param_3,0,param_1);
    __CRT_INIT_12(param_3,0,param_1);
    if (DAT_1002210c != (code *)0x0) {
      (*DAT_1002210c)(param_3,0,param_1);
    }
  }
  if ((param_2 == 0) || (param_2 == 3)) {
    iVar1 = __CRT_INIT_12(param_3,param_2,param_1);
    if (iVar1 == 0) {
      local_20 = 0;
    }
    if ((local_20 != 0) && (DAT_1002210c != (code *)0x0)) {
      local_20 = (*DAT_1002210c)(param_3,param_2,param_1);
    }
  }
LAB_10020d42:
  FUN_10020d5b();
  return local_20;
}



/* FUN_10003c20 @ 10003c20 size 236 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10003c20(float param_1,float param_2,float param_3,float param_4,float param_5)

{
  float fVar1;
  
  fVar1 = _DAT_10746420 * param_1 + DAT_10746424;
  param_2 = _DAT_1074641c * param_2;
  param_3 = param_3 * _DAT_10746420;
  param_4 = _DAT_1074641c * param_4;
  param_5 = _DAT_1074641c * param_5;
  (**(code **)(DAT_106b40a8 + 0x78))(fVar1,param_2,param_3,param_5,0,0,0,0,DAT_10758274);
  (**(code **)(DAT_106b40a8 + 0x78))
            (fVar1,(param_2 + param_4) - param_5,param_3,param_5,0,0,0,0,DAT_10758274);
  return;
}



/* FUN_1001ed80 @ 1001ed80 size 236 */

void FUN_1001ed80(int param_1,undefined4 param_2)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 local_420 [1044];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)local_420;
  FUN_1001da70();
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
  if (iVar2 != 0) {
    FUN_100016c0();
    uVar3 = FUN_10014560();
    *(undefined4 *)(param_1 + 0x158) = uVar3;
    uVar3 = DAT_10029230;
    puVar1 = *(undefined4 **)(param_1 + 0x288);
    if ((puVar1 != (undefined4 *)0x0) &&
       ((((iVar2 = *(int *)(param_1 + 0x110), iVar2 == 4 || (iVar2 == 9)) || (iVar2 == 0xb)) ||
        (((iVar2 == 0xd || (iVar2 == 10)) || ((iVar2 == 0xe || (iVar2 == 0)))))))) {
      *puVar1 = DAT_10029230;
      puVar1[1] = uVar3;
      puVar1[2] = uVar3;
    }
    __security_check_cookie(local_c ^ (uint)local_420);
    return;
  }
  __security_check_cookie(local_c ^ (uint)local_420);
  return;
}



/* FUN_10003b30 @ 10003b30 size 231 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10003b30(float param_1,float param_2,float param_3,float param_4,float param_5)

{
  float fVar1;
  
  fVar1 = _DAT_10746420 * param_1 + DAT_10746424;
  param_2 = _DAT_1074641c * param_2;
  param_3 = _DAT_10746420 * param_3;
  param_4 = _DAT_1074641c * param_4;
  param_5 = _DAT_10746420 * param_5;
  (**(code **)(DAT_106b40a8 + 0x78))(fVar1,param_2,param_5,param_4,0,0,0,0,DAT_10758274);
  (**(code **)(DAT_106b40a8 + 0x78))
            ((fVar1 + param_3) - param_5,param_2,param_5,param_4,0,0,0,0,DAT_10758274);
  return;
}



/* FUN_100167b0 @ 100167b0 size 230 */

void FUN_100167b0(int param_1,undefined4 param_2)

{
  char *pcVar1;
  int iVar2;
  int iVar3;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  undefined4 local_8;
  undefined4 local_4;
  
  pcVar1 = (char *)FUN_10001500(param_2,0);
  if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
    FUN_10014560();
    iVar2 = FUN_10014ba0();
    if (iVar2 != 0) {
      iVar2 = FUN_10014ba0();
      if (iVar2 != 0) {
        pcVar1 = (char *)FUN_10001500(param_2,0);
        if ((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) {
          iVar2 = atoi(pcVar1);
          iVar3 = FUN_100148a0(&local_24);
          if (iVar3 != 0) {
            FUN_100165e0(*(undefined4 *)(param_1 + 0x134),local_10,local_c,local_8,local_4,local_20,
                         local_1c,local_18,local_14,iVar2,local_24);
          }
        }
      }
    }
  }
  return;
}



/* FUN_1000ac00 @ 1000ac00 size 229 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_1000ac00(void)

{
  char cVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  char *pcVar5;
  int iVar6;
  char *pcVar7;
  char local_1004 [4096];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_1004;
  DAT_10761be8 = (**(code **)(DAT_106b40a8 + 0x4c))("video",&DAT_10027238,local_1004,0x1000);
  if (DAT_10761be8 != 0) {
    if (0x100 < DAT_10761be8) {
      DAT_10761be8 = 0x100;
    }
    iVar6 = 0;
    pcVar5 = local_1004;
    if (0 < DAT_10761be8) {
      do {
        pcVar2 = pcVar5;
        do {
          cVar1 = *pcVar2;
          pcVar2 = pcVar2 + 1;
        } while (cVar1 != '\0');
        if ((pcVar5 + (int)(pcVar2 + (-4 - (int)(pcVar5 + 1))) != (char *)0x0) &&
           (iVar3 = FUN_100016c0(), iVar3 == 0)) {
          pcVar5[(int)(pcVar2 + (-4 - (int)(pcVar5 + 1)))] = '\0';
        }
        cVar1 = *pcVar5;
        pcVar7 = pcVar5;
        while (cVar1 != '\0') {
          iVar3 = toupper((int)*pcVar7);
          *pcVar7 = (char)iVar3;
          pcVar7 = pcVar7 + 1;
          cVar1 = *pcVar7;
        }
        uVar4 = FUN_10014560();
        (&DAT_107617e8)[iVar6] = uVar4;
        iVar6 = iVar6 + 1;
        pcVar5 = pcVar5 + (int)(pcVar2 + (1 - (int)(pcVar5 + 1)));
      } while (iVar6 < DAT_10761be8);
    }
  }
  __security_check_cookie(local_4 ^ (uint)local_1004);
  return;
}



/* FUN_1001da70 @ 1001da70 size 229 */

void FUN_1001da70(void)

{
  int iVar1;
  int in_EAX;
  void *_Dst;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  if (*(int *)(in_EAX + 0x288) == 0) {
    iVar1 = *(int *)(in_EAX + 0x110);
    if (iVar1 == 6) {
      _Dst = (void *)FUN_100144c0();
      *(void **)(in_EAX + 0x288) = _Dst;
      if (_Dst != (void *)0x0) {
        memset(_Dst,0,0x1a8);
        return;
      }
    }
    else {
      if (((((iVar1 != 4) && (iVar1 != 9)) && (iVar1 != 0xb)) && ((iVar1 != 0xd && (iVar1 != 10))))
         && ((iVar1 != 0xe && (iVar1 != 0)))) {
        if (iVar1 != 0xc) {
          if (iVar1 == 7) {
            uVar2 = FUN_100144c0();
            *(undefined4 *)(in_EAX + 0x288) = uVar2;
            return;
          }
          if ((iVar1 != 0xf) && (iVar1 != 0x10)) {
            return;
          }
        }
        uVar2 = FUN_100144c0();
        *(undefined4 *)(in_EAX + 0x288) = uVar2;
        return;
      }
      puVar3 = (undefined4 *)FUN_100144c0();
      *(undefined4 **)(in_EAX + 0x288) = puVar3;
      if (puVar3 != (undefined4 *)0x0) {
        *puVar3 = 0;
        puVar3[1] = 0;
        puVar3[2] = 0;
        puVar3[3] = 0;
        puVar3[4] = 0;
        puVar3[5] = 0;
        puVar3[6] = 0;
      }
      if ((*(int *)(in_EAX + 0x110) == 4) && (*(int *)(*(int *)(in_EAX + 0x288) + 0x14) == 0)) {
        *(undefined4 *)(*(int *)(in_EAX + 0x288) + 0x14) = 0x100;
      }
    }
  }
  return;
}



/* FUN_10018280 @ 10018280 size 228 */

void FUN_10018280(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  float *pfVar5;
  float10 fVar6;
  float10 extraout_ST0;
  float local_408;
  undefined1 local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_408;
  iVar1 = *(int *)(param_1 + 0x288);
  local_408 = 0.0;
  if (iVar1 != 0) {
    if (*(int *)(iVar1 + 0x184) == 0) {
      fVar6 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(*(undefined4 *)(param_1 + 0x158));
      local_408 = (float)fVar6;
    }
    else {
      (**(code **)(DAT_106b40d0 + 0x58))(*(undefined4 *)(param_1 + 0x158),local_404,0x400);
    }
    iVar2 = *(int *)(iVar1 + 0x180);
    iVar4 = 0;
    if (0 < iVar2) {
      fVar6 = (float10)local_408;
      pfVar5 = (float *)(iVar1 + 0x100);
      do {
        if (*(int *)(iVar1 + 0x184) == 0) {
          if ((float10)*pfVar5 == fVar6) break;
        }
        else if ((pfVar5[-0x20] != 0.0) &&
                (iVar3 = FUN_100016c0(), fVar6 = extraout_ST0, iVar3 == 0)) break;
        iVar4 = iVar4 + 1;
        pfVar5 = pfVar5 + 1;
      } while (iVar4 < iVar2);
    }
  }
  __security_check_cookie(local_4 ^ (uint)&local_408);
  return;
}



/* FUN_1000a210 @ 1000a210 size 226 */

undefined4 FUN_1000a210(void)

{
  int iVar1;
  int iVar2;
  int in_EAX;
  undefined4 uVar3;
  
  iVar2 = DAT_106b40a8;
  if (in_EAX == 0xb2) {
LAB_1000a22d:
    if (in_EAX != 0xb3) {
      DAT_1074502c = DAT_1074502c + 1;
      goto LAB_1000a250;
    }
  }
  else if (in_EAX != 0xb3) {
    if ((in_EAX != 0xd) && (in_EAX != 0xa9)) {
      return 0;
    }
    goto LAB_1000a22d;
  }
  DAT_1074502c = DAT_1074502c + -1;
LAB_1000a250:
  while( true ) {
    if (DAT_1074502c < 0) {
      DAT_1074502c = DAT_107596a4 + -1;
    }
    else if (DAT_107596a4 <= DAT_1074502c) {
      DAT_1074502c = 0;
    }
    iVar1 = (&DAT_107596ac)[DAT_1074502c * 2];
    if (((iVar1 != 6) && (iVar1 != 7)) && (iVar1 != 8)) break;
    DAT_1074502c = DAT_1074502c + 1;
  }
  uVar3 = FUN_10001900(&DAT_10025d20,DAT_1074502c);
  (**(code **)(iVar2 + 0x1c))("ui_netGameType",uVar3);
  iVar2 = DAT_106b40a8;
  uVar3 = FUN_10001900(&DAT_10025d20,(&DAT_107596ac)[DAT_1074502c * 2]);
  (**(code **)(iVar2 + 0x1c))("ui_actualnetGameType",uVar3);
  (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentNetMap",&DAT_100252c0);
  FUN_1000d3c0(0);
  FUN_1001d3d0(4);
  return 1;
}



/* FUN_10017410 @ 10017410 size 226 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

float10 FUN_10017410(void)

{
  float fVar1;
  float *pfVar2;
  float *in_EAX;
  float10 fVar3;
  float fVar4;
  float fStack_c;
  float local_8;
  
  pfVar2 = (float *)in_EAX[0xa2];
  if (in_EAX[0x4c] == 0.0) {
    local_8 = *in_EAX;
  }
  else {
    local_8 = in_EAX[0x42] + in_EAX[0x40] + (float)_DAT_10029220;
  }
  if ((pfVar2 == (float *)0x0) && (in_EAX[0x56] != 0.0)) {
    return (float10)local_8;
  }
  fVar3 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(in_EAX[0x56]);
  fStack_c = (float)fVar3;
  fVar1 = *pfVar2;
  fVar4 = fVar1;
  if ((fStack_c < fVar1) || (fVar4 = pfVar2[1], pfVar2[1] < fStack_c)) {
    fStack_c = fVar4;
  }
  return (float10)(((fStack_c - fVar1) / (pfVar2[1] - fVar1)) * (float)_DAT_10029218 + local_8);
}



/* FUN_100181a0 @ 100181a0 size 224 */

void FUN_100181a0(int param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  float *pfVar4;
  int iVar5;
  float10 fVar6;
  float10 extraout_ST0;
  float local_408;
  undefined1 local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_408;
  iVar3 = *(int *)(param_1 + 0x288);
  local_408 = 0.0;
  if (iVar3 != 0) {
    if (*(int *)(iVar3 + 0x184) == 0) {
      fVar6 = (float10)(**(code **)(DAT_106b40d0 + 0x5c))(*(undefined4 *)(param_1 + 0x158));
      local_408 = (float)fVar6;
    }
    else {
      (**(code **)(DAT_106b40d0 + 0x58))(*(undefined4 *)(param_1 + 0x158),local_404,0x400);
    }
    iVar1 = *(int *)(iVar3 + 0x180);
    iVar5 = 0;
    if (0 < iVar1) {
      iVar2 = *(int *)(iVar3 + 0x184);
      fVar6 = (float10)local_408;
      pfVar4 = (float *)(iVar3 + 0x100);
      do {
        if (iVar2 == 0) {
          if ((float10)*pfVar4 == fVar6) break;
        }
        else if ((pfVar4[-0x20] != 0.0) &&
                (iVar3 = FUN_100016c0(), fVar6 = extraout_ST0, iVar3 == 0)) break;
        iVar5 = iVar5 + 1;
        pfVar4 = pfVar4 + 1;
      } while (iVar5 < iVar1);
    }
  }
  __security_check_cookie(local_4 ^ (uint)&local_408);
  return;
}



/* FUN_100159a0 @ 100159a0 size 223 */

void __fastcall FUN_100159a0(float *param_1)

{
  float *pfVar1;
  int iVar2;
  float *pfVar3;
  float fVar4;
  float fVar5;
  float local_c;
  float local_8;
  
  if (param_1 != (float *)0x0) {
    fVar4 = *param_1;
    fVar5 = param_1[1];
    if (param_1[0xd] != 0.0) {
      fVar4 = param_1[0x11] + fVar4;
      fVar5 = param_1[0x11] + fVar5;
    }
    iVar2 = 0;
    if (0 < (int)param_1[0x43]) {
      pfVar3 = param_1 + 0x55;
      do {
        pfVar1 = (float *)*pfVar3;
        if (pfVar1 != (float *)0x0) {
          local_c = fVar5;
          local_8 = fVar4;
          if (pfVar1[0xd] != 0.0) {
            local_8 = pfVar1[0x11] + fVar4;
            local_c = pfVar1[0x11] + fVar5;
          }
          pfVar1[0x42] = 0.0;
          pfVar1[0x43] = 0.0;
          *pfVar1 = pfVar1[4] + local_8;
          pfVar1[1] = pfVar1[5] + local_c;
          pfVar1[2] = pfVar1[6];
          pfVar1[3] = pfVar1[7];
        }
        iVar2 = iVar2 + 1;
        pfVar3 = pfVar3 + 1;
      } while (iVar2 < (int)param_1[0x43]);
    }
  }
  return;
}



/* FUN_1001e380 @ 1001e380 size 223 */

void FUN_1001e380(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined1 auStack_424 [4];
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  iVar4 = 0;
  puVar3 = (uint *)(param_1 + 0x88);
  do {
    bVar1 = false;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
    if (iVar2 == 0) {
LAB_1001e44e:
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
    if (acStack_410[0] == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      if (iVar2 == 0) goto LAB_1001e44e;
      bVar1 = true;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_2,"expected float but found %s\n",acStack_410);
      goto LAB_1001e44e;
    }
    uVar5 = uStack_414;
    if (bVar1) {
      uVar5 = uStack_414 ^ DAT_100292a0;
    }
    *puVar3 = uVar5;
    iVar4 = iVar4 + 1;
    puVar3 = puVar3 + 1;
    if (3 < iVar4) {
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
  } while( true );
}



/* FUN_1001e570 @ 1001e570 size 223 */

void FUN_1001e570(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined1 auStack_424 [4];
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  iVar4 = 0;
  puVar3 = (uint *)(param_1 + 0x98);
  do {
    bVar1 = false;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
    if (iVar2 == 0) {
LAB_1001e63e:
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
    if (acStack_410[0] == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      if (iVar2 == 0) goto LAB_1001e63e;
      bVar1 = true;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_2,"expected float but found %s\n",acStack_410);
      goto LAB_1001e63e;
    }
    uVar5 = uStack_414;
    if (bVar1) {
      uVar5 = uStack_414 ^ DAT_100292a0;
    }
    *puVar3 = uVar5;
    iVar4 = iVar4 + 1;
    puVar3 = puVar3 + 1;
    if (3 < iVar4) {
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
  } while( true );
}



/* FUN_1001fc20 @ 1001fc20 size 223 */

void FUN_1001fc20(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined1 auStack_424 [4];
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  iVar4 = 0;
  puVar3 = (uint *)(param_1 + 0x134);
  do {
    bVar1 = false;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
    if (iVar2 == 0) {
LAB_1001fcee:
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
    if (acStack_410[0] == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      if (iVar2 == 0) goto LAB_1001fcee;
      bVar1 = true;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_2,"expected float but found %s\n",acStack_410);
      goto LAB_1001fcee;
    }
    uVar5 = uStack_414;
    if (bVar1) {
      uVar5 = uStack_414 ^ DAT_100292a0;
    }
    *puVar3 = uVar5;
    iVar4 = iVar4 + 1;
    puVar3 = puVar3 + 1;
    if (3 < iVar4) {
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
  } while( true );
}



/* FUN_1001fd10 @ 1001fd10 size 223 */

void FUN_1001fd10(int param_1,undefined4 param_2)

{
  bool bVar1;
  int iVar2;
  uint *puVar3;
  int iVar4;
  uint uVar5;
  undefined1 auStack_424 [4];
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  iVar4 = 0;
  puVar3 = (uint *)(param_1 + 0x144);
  do {
    bVar1 = false;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
    if (iVar2 == 0) {
LAB_1001fdde:
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
    if (acStack_410[0] == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
      if (iVar2 == 0) goto LAB_1001fdde;
      bVar1 = true;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_2,"expected float but found %s\n",acStack_410);
      goto LAB_1001fdde;
    }
    uVar5 = uStack_414;
    if (bVar1) {
      uVar5 = uStack_414 ^ DAT_100292a0;
    }
    *puVar3 = uVar5;
    iVar4 = iVar4 + 1;
    puVar3 = puVar3 + 1;
    if (3 < iVar4) {
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
  } while( true );
}



/* FUN_10012ca0 @ 10012ca0 size 220 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_10012ca0(void)

{
  ushort uVar1;
  int unaff_ESI;
  uint uVar2;
  
  uVar2 = *(uint *)(unaff_ESI + 0x42c) & 0xffffff7f;
  if (uVar2 == 8) {
    uVar2 = 7;
  }
  if (*(uint *)(unaff_ESI + 0x458) == (uint)(uVar2 != 7)) {
    *(undefined4 *)(unaff_ESI + 0x460) = DAT_1004fe5c;
    uVar1 = FUN_10021270();
    *(float *)(unaff_ESI + 0x45c) = (float)uVar1 * (float)_DAT_100292b8;
    *(uint *)(unaff_ESI + 0x458) = (uint)(uVar2 == 7);
  }
  return;
}



/* FUN_100011c0 @ 100011c0 size 219 */

void __fastcall FUN_100011c0(float *param_1,float *param_2)

{
  float *in_EAX;
  
  *param_2 = param_1[2] * in_EAX[6] + param_1[1] * in_EAX[3] + *param_1 * *in_EAX;
  param_2[1] = param_1[2] * in_EAX[7] + in_EAX[1] * *param_1 + in_EAX[4] * param_1[1];
  param_2[2] = param_1[2] * in_EAX[8] + in_EAX[2] * *param_1 + in_EAX[5] * param_1[1];
  param_2[3] = in_EAX[6] * param_1[5] + param_1[3] * *in_EAX + param_1[4] * in_EAX[3];
  param_2[4] = param_1[5] * in_EAX[7] + param_1[3] * in_EAX[1] + param_1[4] * in_EAX[4];
  param_2[5] = param_1[5] * in_EAX[8] + param_1[3] * in_EAX[2] + param_1[4] * in_EAX[5];
  param_2[6] = in_EAX[6] * param_1[8] + param_1[6] * *in_EAX + param_1[7] * in_EAX[3];
  param_2[7] = param_1[8] * in_EAX[7] + param_1[6] * in_EAX[1] + param_1[7] * in_EAX[4];
  param_2[8] = param_1[8] * in_EAX[8] + param_1[6] * in_EAX[2] + param_1[7] * in_EAX[5];
  return;
}



/* FUN_100053c0 @ 100053c0 size 217 */

void FUN_100053c0(void)

{
  int in_EAX;
  undefined4 uVar1;
  int iVar2;
  undefined4 *unaff_EDI;
  
  iVar2 = DAT_10742f8c;
  if (in_EAX == 0) {
    iVar2 = DAT_10744ccc;
  }
  if ((iVar2 < 0) || (DAT_1075add0 < iVar2)) {
    if (in_EAX == 0) {
      DAT_10744ccc = 0;
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentMap",&DAT_100252c0);
    }
    else {
      DAT_10742f8c = 0;
      (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentNetMap");
    }
    iVar2 = 0;
  }
  if ((&DAT_1075ae30)[iVar2 * 0x19] == -1) {
    uVar1 = (**(code **)(DAT_106b40a8 + 0x5c))((&DAT_1075addc)[iVar2 * 0x19]);
    (&DAT_1075ae30)[iVar2 * 0x19] = uVar1;
  }
  iVar2 = (&DAT_1075ae30)[iVar2 * 0x19];
  if (iVar2 < 1) {
    iVar2 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/unknownmap");
  }
  FUN_10002c50(*unaff_EDI,unaff_EDI[1],unaff_EDI[2],unaff_EDI[3],iVar2);
  DAT_10766b00 = 1;
  return;
}



/* FUN_1000f6d0 @ 1000f6d0 size 213 */

void FUN_1000f6d0(void)

{
  char *pcVar1;
  int iVar2;
  undefined4 uVar3;
  int local_4;
  
  local_4 = FUN_100044f0();
  if (local_4 != 0) {
    pcVar1 = (char *)FUN_10001500(&local_4,1);
    while ((((pcVar1 != (char *)0x0 && (*pcVar1 != '\0')) && (*pcVar1 != '}')) &&
           (iVar2 = FUN_100016c0(), iVar2 != 0))) {
      iVar2 = FUN_100016c0();
      if (iVar2 == 0) {
        uVar3 = 0;
LAB_1000f73f:
        iVar2 = FUN_1000f340(uVar3);
        if (iVar2 == 0) {
          return;
        }
      }
      else {
        iVar2 = FUN_100016c0();
        if (iVar2 == 0) {
          uVar3 = 1;
          goto LAB_1000f73f;
        }
        iVar2 = FUN_100016c0();
        if (iVar2 == 0) {
          FUN_1000f4c0();
        }
      }
      pcVar1 = (char *)FUN_10001500(&local_4,1);
    }
  }
  return;
}



/* FUN_100196b0 @ 100196b0 size 213 */

void FUN_100196b0(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int *piVar4;
  int local_4;
  
  local_4 = 0;
  if (0 < DAT_106b40e4) {
    piVar2 = &DAT_106b494c;
    do {
      if (piVar2 != (int *)0x2c) {
        if ((piVar2[1] == 5) && (-1 < *piVar2)) {
          (**(code **)(DAT_106b40d0 + 0xbc))(*piVar2);
          *piVar2 = -1;
        }
        iVar3 = 0;
        if (0 < piVar2[0x38]) {
          piVar4 = piVar2 + 0x4a;
          do {
            iVar1 = *piVar4;
            if ((*(int *)(iVar1 + 0x30) == 5) && (-1 < *(int *)(iVar1 + 0x2c))) {
              (**(code **)(DAT_106b40d0 + 0xbc))(*(int *)(iVar1 + 0x2c));
              *(undefined4 *)(iVar1 + 0x2c) = 0xffffffff;
            }
            if (*(int *)(*piVar4 + 0x110) == 8) {
              (**(code **)(DAT_106b40d0 + 0xbc))(-*(int *)(*piVar4 + 0x38));
            }
            iVar3 = iVar3 + 1;
            piVar4 = piVar4 + 1;
          } while (iVar3 < piVar2[0x38]);
        }
      }
      local_4 = local_4 + 1;
      piVar2 = piVar2 + 0x455;
    } while (local_4 < DAT_106b40e4);
  }
  return;
}



/* FUN_10015d50 @ 10015d50 size 211 */

void FUN_10015d50(int param_1,undefined4 param_2)

{
  char *pcVar1;
  int iVar2;
  double dVar3;
  
  pcVar1 = (char *)FUN_10001500(param_2,0);
  if (((pcVar1 != (char *)0x0) && (*pcVar1 != '\0')) && (iVar2 = FUN_10014560(), iVar2 != 0)) {
    iVar2 = FUN_100016c0();
    if (iVar2 == 0) {
      *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 0x400000;
      param_1 = param_1 + 0x88;
    }
    else {
      iVar2 = FUN_100016c0();
      if (iVar2 == 0) {
        *(uint *)(param_1 + 0x48) = *(uint *)(param_1 + 0x48) | 0x200;
        param_1 = param_1 + 0x78;
      }
      else {
        iVar2 = FUN_100016c0();
        if (iVar2 != 0) {
          return;
        }
        param_1 = param_1 + 0x98;
      }
    }
    if (param_1 != 0) {
      iVar2 = 0;
      do {
        pcVar1 = (char *)FUN_10001500(param_2,0);
        if (pcVar1 == (char *)0x0) {
          return;
        }
        if (*pcVar1 == '\0') {
          return;
        }
        dVar3 = atof(pcVar1);
        *(float *)(param_1 + iVar2 * 4) = (float)dVar3;
        iVar2 = iVar2 + 1;
      } while (iVar2 < 4);
    }
  }
  return;
}



/* FUN_100149d0 @ 100149d0 size 209 */

void FUN_100149d0(undefined4 param_1)

{
  bool bVar1;
  int iVar2;
  int unaff_EBX;
  int iVar3;
  uint uVar4;
  int local_420 [3];
  uint uStack_414;
  char acStack_410 [1028];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)local_420;
  iVar3 = 0;
  do {
    bVar1 = false;
    iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_420);
    if (iVar2 == 0) {
LAB_10014a8b:
      __security_check_cookie(local_c ^ (uint)local_420);
      return;
    }
    if (acStack_410[0] == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_1,local_420);
      if (iVar2 == 0) goto LAB_10014a8b;
      bVar1 = true;
    }
    if (local_420[0] != 3) {
      FUN_10014710(param_1,"expected float but found %s\n",acStack_410);
      goto LAB_10014a8b;
    }
    uVar4 = uStack_414;
    if (bVar1) {
      uVar4 = uStack_414 ^ DAT_100292a0;
    }
    *(uint *)(unaff_EBX + iVar3 * 4) = uVar4;
    iVar3 = iVar3 + 1;
    if (3 < iVar3) {
      __security_check_cookie(local_c ^ (uint)local_420);
      return;
    }
  } while( true );
}



/* FUN_10006600 @ 10006600 size 208 */

void FUN_10006600(void)

{
  int iVar1;
  float *unaff_ESI;
  
  if ((DAT_10742f8c < 0) || (DAT_1075add0 < DAT_10742f8c)) {
    DAT_10742f8c = 0;
    (**(code **)(DAT_106b40a8 + 0x1c))("ui_currentNetMap",&DAT_100252c0);
  }
  if (-1 < DAT_107644b4) {
    (**(code **)(DAT_106b40a8 + 300))(DAT_107644b4);
    (**(code **)(DAT_106b40a8 + 0x134))
              (DAT_107644b4,(int)*unaff_ESI,(int)unaff_ESI[1],(int)unaff_ESI[2],(int)unaff_ESI[3]);
    (**(code **)(DAT_106b40a8 + 0x130))(DAT_107644b4);
    return;
  }
  iVar1 = DAT_107644b0;
  if (DAT_107644b0 < 1) {
    iVar1 = (**(code **)(DAT_106b40a8 + 0x5c))("menu/art/unknownmap");
  }
  FUN_10002c50(*unaff_ESI,unaff_ESI[1],unaff_ESI[2],unaff_ESI[3],iVar1);
  return;
}



/* FUN_1001d3d0 @ 1001d3d0 size 207 */

void FUN_1001d3d0(int param_1)

{
  undefined4 *puVar1;
  int in_EAX;
  int iVar2;
  int iVar3;
  int *piVar4;
  
  if (in_EAX == 0) {
    iVar2 = FUN_1001d390();
  }
  else {
    iVar2 = FUN_10016160();
  }
  if (iVar2 != 0) {
    iVar3 = 0;
    if (0 < *(int *)(iVar2 + 0x10c)) {
      piVar4 = (int *)(iVar2 + 0x154);
      while (*(float *)(*piVar4 + 0x280) != (float)param_1) {
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 1;
        if (*(int *)(iVar2 + 0x10c) <= iVar3) {
          return;
        }
      }
      puVar1 = *(undefined4 **)(*(int *)(iVar2 + 0x154 + iVar3 * 4) + 0x288);
      puVar1[3] = 0;
      *puVar1 = 0;
      *(undefined4 *)(*(int *)(iVar2 + 0x154 + iVar3 * 4) + 0x284) = 0;
      iVar2 = *(int *)(iVar2 + 0x154 + iVar3 * 4);
      (**(code **)(DAT_106b40d0 + 0x88))
                (*(undefined4 *)(iVar2 + 0x280),*(undefined4 *)(iVar2 + 0x284),
                 *(undefined4 *)(iVar2 + 0x158));
    }
  }
  return;
}



/* FUN_1001f9d0 @ 1001f9d0 size 207 */

void FUN_1001f9d0(int param_1,undefined4 param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 local_420 [1044];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)local_420;
  iVar1 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
  if (iVar1 != 0) {
    FUN_100016c0();
    uVar2 = FUN_10014560();
    *(undefined4 *)(param_1 + 0x100) = uVar2;
    if (*(int *)(DAT_106b40d0 + 0xf240) == 0) {
      (**(code **)(DAT_106b40d0 + 0x40))(*(undefined4 *)(param_1 + 0x100),0x30,DAT_106b40d0 + 0x108)
      ;
      *(undefined4 *)(DAT_106b40d0 + 0xf240) = 1;
    }
    __security_check_cookie(local_c ^ (uint)local_420);
    return;
  }
  __security_check_cookie(local_c ^ (uint)local_420);
  return;
}



/* FUN_1000a6c0 @ 1000a6c0 size 203 */

undefined4 FUN_1000a6c0(void)

{
  int in_EAX;
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  if ((((in_EAX != 0xb2) && (in_EAX != 0xb3)) && (in_EAX != 0xd)) && (in_EAX != 0xa9)) {
    return 0;
  }
  FUN_10008b60();
  if (DAT_107597c8 == 0) {
    return 0;
  }
  (**(code **)(DAT_106b40a8 + 0x28))("cg_selectedPlayer");
  iVar1 = FUN_10021270();
  if (in_EAX == 0xb3) {
    iVar1 = iVar1 + -1;
  }
  else {
    iVar1 = iVar1 + 1;
  }
  if (DAT_107597b4 < iVar1) {
    iVar1 = 0;
LAB_1000a727:
    iVar3 = iVar1;
    if (iVar3 != DAT_107597b4) {
      (**(code **)(DAT_106b40a8 + 0x1c))("cg_selectedPlayerName",&DAT_1075a1cc + iVar3 * 0x28);
      goto LAB_1000a764;
    }
  }
  else {
    iVar3 = DAT_107597b4;
    if (-1 < iVar1) goto LAB_1000a727;
  }
  (**(code **)(DAT_106b40a8 + 0x1c))("cg_selectedPlayerName","Everyone");
LAB_1000a764:
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025d20,iVar3);
  (**(code **)(iVar1 + 0x1c))("cg_selectedPlayer",uVar2);
  return 0;
}



/* FUN_10001830 @ 10001830 size 201 */

/* WARNING: Function: __alloca_probe replaced with injection: alloca_probe */

void FUN_10001830(char *param_1,int param_2,char *param_3)

{
  uint uVar1;
  char local_7d04 [32000];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_7d04;
  uVar1 = vsprintf(local_7d04,param_3,&stack0x00000010);
  if (31999 < uVar1) {
    FUN_10001e70(0,"Com_sprintf: overflowed bigbuffer");
  }
  if (param_2 <= (int)uVar1) {
    FUN_10001ee0("Com_sprintf: overflow of %i in %i\n",uVar1,param_2);
  }
  if (param_1 == (char *)0x0) {
    FUN_10001e70(0,"Q_strncpyz: NULL dest");
  }
  if (param_2 < 1) {
    FUN_10001e70(0,"Q_strncpyz: destsize < 1");
  }
  strncpy(param_1,local_7d04,param_2 - 1);
  param_1[param_2 + -1] = '\0';
  __security_check_cookie(local_4 ^ (uint)local_7d04);
  return;
}



/* FUN_1001dd50 @ 1001dd50 size 200 */

void FUN_1001dd50(int param_1,undefined4 param_2)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined1 auStack_424 [4];
  undefined1 local_420 [1044];
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  FUN_1001da70();
  piVar1 = *(int **)(param_1 + 0x288);
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))(param_2,local_420);
  if (iVar2 != 0) {
    FUN_100016c0();
    uVar3 = FUN_10014560();
    uVar3 = (**(code **)(DAT_106b40d0 + 0x1c))(uVar3);
    *(undefined4 *)(param_1 + 0x138) = uVar3;
    iVar2 = rand();
    *piVar1 = iVar2 % 0x168;
    __security_check_cookie(local_c ^ (uint)auStack_424);
    return;
  }
  __security_check_cookie(local_c ^ (uint)auStack_424);
  return;
}



/* FUN_1000a420 @ 1000a420 size 197 */

undefined4 FUN_1000a420(void)

{
  int iVar1;
  int in_EAX;
  undefined4 uVar2;
  
  if (in_EAX == 0xb2) {
LAB_1000a444:
    if (in_EAX == 0xb3) goto LAB_1000a44b;
    DAT_1074148c = DAT_1074148c + 1;
    if (DAT_1074148c == 1) {
      DAT_1074148c = 2;
      goto LAB_1000a49e;
    }
  }
  else {
    if (in_EAX != 0xb3) {
      if ((in_EAX != 0xd) && (in_EAX != 0xa9)) {
        return 0;
      }
      goto LAB_1000a444;
    }
LAB_1000a44b:
    DAT_1074148c = DAT_1074148c + -1;
    if (DAT_1074148c == 1) {
      DAT_1074148c = 0;
      goto LAB_1000a49e;
    }
  }
  if (DAT_1074148c < 4) {
    if (DAT_1074148c < 0) {
      DAT_1074148c = 3;
    }
  }
  else {
    DAT_1074148c = 0;
  }
LAB_1000a49e:
  FUN_1000d740();
  if (DAT_1074148c != 2) {
    FUN_10011a30(1);
  }
  iVar1 = DAT_106b40a8;
  uVar2 = FUN_10001900(&DAT_10025d20,DAT_1074148c);
  (**(code **)(iVar1 + 0x1c))("ui_netSource",uVar2);
  return 1;
}



/* FUN_1000a040 @ 1000a040 size 196 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_1000a040(void)

{
  float fVar1;
  int iVar2;
  int in_EAX;
  int iVar3;
  undefined4 uVar4;
  float10 fVar5;
  float fVar6;
  
  if ((((in_EAX != 0xb2) && (in_EAX != 0xb3)) && (in_EAX != 0xd)) && (in_EAX != 0xa9)) {
    return 0;
  }
  fVar5 = (float10)(**(code **)(DAT_106b40a8 + 0x28))("handicap");
  iVar2 = DAT_106b40a8;
  fVar1 = (float)fVar5;
  fVar6 = DAT_10029380;
  if ((DAT_10029380 <= fVar1) && (fVar6 = fVar1, (float)_DAT_10029378 < fVar1)) {
    fVar6 = DAT_10029374;
  }
  if (in_EAX == 0xb3) {
    iVar3 = (int)fVar6 + -5;
  }
  else {
    iVar3 = (int)fVar6 + 5;
  }
  if (iVar3 < 0x65) {
    if (iVar3 < 0) {
      iVar3 = 100;
    }
  }
  else {
    iVar3 = 5;
  }
  uVar4 = FUN_10001900(&DAT_10025920,iVar3);
  (**(code **)(iVar2 + 0x1c))("handicap",uVar4);
  return 1;
}



/* FUN_10003d90 @ 10003d90 size 195 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_10003d90(int param_1,int param_2,undefined4 param_3,float param_4)

{
  int *unaff_ESI;
  int *unaff_EDI;
  float local_20;
  float fStack_1c;
  float local_18 [2];
  float fStack_10;
  float fStack_8;
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)&local_20;
  if (DAT_106b40a4 == _DAT_10029214) {
    DAT_106b40a4 = ((float)DAT_1075824c / (float)_DAT_10029288) * (float)_DAT_10029218;
  }
  local_20 = DAT_106b40a4 * param_4;
  if (param_1 != 0) {
    if (param_2 == 0) {
      param_2 = -1;
    }
    (**(code **)(DAT_106b40a8 + 0x17c))(param_1,0,param_3,local_20,param_2,local_18);
    local_20 = (fStack_10 - local_18[0]) / _DAT_10746420;
    fStack_1c = fStack_8 / _DAT_1074641c;
    if (unaff_ESI != (int *)0x0) {
      *unaff_ESI = (int)local_20;
    }
    if (unaff_EDI != (int *)0x0) {
      *unaff_EDI = (int)fStack_1c;
    }
  }
  __security_check_cookie(local_4 ^ (uint)&local_20);
  return;
}



/* FUN_1000d3c0 @ 1000d3c0 size 194 */

void FUN_1000d3c0(int param_1)

{
  int iVar1;
  char *_Str;
  undefined4 *puVar2;
  byte bVar3;
  undefined1 local_404 [1024];
  uint local_4;
  
  local_4 = DAT_1002a000 ^ (uint)local_404;
  bVar3 = 0;
  iVar1 = (**(code **)(DAT_106b40a8 + 0xc0))(0,local_404,0x400);
  if (iVar1 != 0) {
    _Str = (char *)FUN_10001940();
    iVar1 = atoi(_Str);
    bVar3 = (iVar1 < 0) - 1U & (byte)iVar1;
  }
  iVar1 = 0;
  if (0 < DAT_1075add0) {
    puVar2 = &DAT_1075ae34;
    do {
      *puVar2 = 0;
      if (((1 << (bVar3 & 0x1f) & puVar2[-0x13]) != 0) &&
         ((param_1 == 0 || ((puVar2[-0x13] & 4) != 0)))) {
        *puVar2 = 1;
      }
      iVar1 = iVar1 + 1;
      puVar2 = puVar2 + 0x19;
    } while (iVar1 < DAT_1075add0);
  }
  __security_check_cookie(local_4 ^ (uint)local_404);
  return;
}



/* FUN_1001e190 @ 1001e190 size 194 */

undefined4 FUN_1001e190(int param_1)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  int local_1c;
  int local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 local_c;
  
  FUN_1001da70();
  iVar2 = *(int *)(param_1 + 0x288);
  if ((iVar2 == 0) || (iVar1 = FUN_10014ae0(), iVar1 == 0)) {
    return 0;
  }
  if (0x20 < local_1c) {
    local_1c = 0x20;
  }
  *(int *)(iVar2 + 0x1c) = local_1c;
  local_18 = 0;
  if (0 < local_1c) {
    puVar3 = (undefined4 *)(iVar2 + 0x24);
    do {
      iVar2 = FUN_10014ae0();
      if (iVar2 == 0) {
        return 0;
      }
      iVar2 = FUN_10014ae0();
      if (iVar2 == 0) {
        return 0;
      }
      iVar2 = FUN_10014ae0();
      if (iVar2 == 0) {
        return 0;
      }
      puVar3[-1] = local_14;
      local_18 = local_18 + 1;
      *puVar3 = local_10;
      puVar3[1] = local_c;
      puVar3 = puVar3 + 3;
    } while (local_18 < local_1c);
  }
  return 1;
}



/* FUN_1000f9f0 @ 1000f9f0 size 191 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall FUN_1000f9f0(undefined4 param_1)

{
  (**(code **)(DAT_106b40a8 + 0xbc))(&DAT_1075561c,param_1);
  DAT_106b40a4 = 0;
  if (DAT_10758248 * 0x1e0 + DAT_1075824c * -0x280 != 0 &&
      DAT_1075824c * 0x280 <= DAT_10758248 * 0x1e0) {
    DAT_10746424 = ((float)DAT_10758248 - (float)_DAT_10029280 * (float)DAT_1075824c) *
                   (float)_DAT_10029278;
    _DAT_1074641c = (float)DAT_1075824c * (float)_DAT_10029270;
    _DAT_10746420 =
         (((float)DAT_1075824c / (float)_DAT_10029268) * (float)_DAT_10029260) /
         (float)_DAT_10029258;
    return;
  }
  DAT_10746424 = 0.0;
  _DAT_1074641c = (float)DAT_1075824c * (float)_DAT_10029250;
  _DAT_10746420 = (float)DAT_10758248 * (float)_DAT_10029248;
  return;
}



/* FUN_100148d0 @ 100148d0 size 187 */

void FUN_100148d0(void)

{
  bool bVar1;
  int iVar2;
  uint *unaff_EBX;
  undefined1 auStack_424 [4];
  int local_420;
  uint uStack_414;
  char cStack_410;
  uint local_c;
  
  local_c = DAT_1002a000 ^ (uint)auStack_424;
  bVar1 = false;
  iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
  if (iVar2 != 0) {
    if (cStack_410 == '-') {
      iVar2 = (**(code **)(DAT_106b40a8 + 0x16c))();
      if (iVar2 == 0) goto LAB_10014949;
      bVar1 = true;
    }
    if (local_420 == 3) {
      if (bVar1) {
        uStack_414 = uStack_414 ^ DAT_100292a0;
      }
      *unaff_EBX = uStack_414;
      __security_check_cookie(local_c ^ (uint)auStack_424);
      return;
    }
    FUN_10014710();
  }
LAB_10014949:
  __security_check_cookie(local_c ^ (uint)auStack_424);
  return;
}



/* FUN_10001d60 @ 10001d60 size 186 */

uint FUN_10001d60(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  byte *unaff_EBX;
  uint uStack00000004;
  
  uStack00000004 = (uint)*unaff_EBX;
  iVar1 = FUN_10021270();
  if (0xff < iVar1) {
    iVar1 = 0xff;
  }
  uStack00000004 = (uint)unaff_EBX[1];
  uVar2 = FUN_10021270();
  if (0xff < (int)uVar2) {
    uVar2 = 0xff;
  }
  uStack00000004 = (uint)unaff_EBX[2];
  uVar3 = FUN_10021270();
  if (0xff < (int)uVar3) {
    uVar3 = 0xff;
  }
  return (uVar3 & 0xff) << 8 | iVar1 << 0x18 | (uVar2 & 0xff) << 0x10 | 0xff;
}



