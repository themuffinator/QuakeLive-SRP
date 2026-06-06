# Quake Live ZMQ/CZMQ Mapping Round 361

Date: 2026-06-06

Focus: bundled ZeroMQ/CZMQ helper reconstruction around `idZMQ`, ZAP
authentication, message/frame transport, certificate loading, and config-file
wiring in `quakelive_steam.exe`.

## Retail Evidence

- Owning binary: `assets/quakelive/quakelive_steam.exe`.
- Structured companion corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/metadata.txt`
  reports an x86 Windows executable with 5,473 functions, 351 imports, and
  4,377 promoted analysis symbols.
- Ghidra function corpus confirms the key anonymous helpers are present at
  `0x004F6D10`, `0x004F8960`, `0x004F8F50`, `0x004F90B0`,
  `0x004F9B90`, `0x004FA0C0`, `0x004FAF60`, `0x004FB200`,
  `0x004FBB00`, and `0x004FBD90`.
- Import corroboration includes `Sleep`, `GetSystemTimeAsFileTime`,
  `FindFirstFileA`, `_time64`, `fopen`, `fread`, `fprintf`, `strftime`, and
  `vfprintf`, matching the observed `zclock`, `zdir`, `zfile`, and logging
  helper bodies.
- Canonical control-flow evidence:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  preserves embedded CZMQ source paths such as `src\zmsg.c`, `src\zframe.c`,
  `src\zhashx.c`, `src\zpoller.c`, `src\zcertstore.c`, `src\zdir.c`,
  `src\zfile.c`, `src\zhash.c`, and `src\zconfig.c`.
- Upstream source comparison used CZMQ v3.0.2:
  [zsys.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zsys.c),
  [zclock.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zclock.c),
  [zmsg.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zmsg.c),
  [zframe.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zframe.c),
  [zhashx.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zhashx.c),
  [zpoller.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zpoller.c),
  [zcertstore.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zcertstore.c),
  [zdir.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zdir.c),
  [zfile.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zfile.c),
  [zhash.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zhash.c), and
  [zconfig.c](https://github.com/zeromq/czmq/blob/v3.0.2/src/zconfig.c).

## Alias Reconstruction

This pass added 124 high-confidence aliases to
`references/analysis/quakelive_symbol_aliases.json`.

- `zsys` and `zclock`: named the Win32 handler shim, pipe HWM accessor,
  interface/log identity setters, log sender wiring, `s_log`, `zsys_error`,
  `zsys_info`, `s_filetime_to_msec`, `zclock_sleep`, `zclock_time`, and
  `zclock_log`.
- `zmsg` and `zframe`: mapped constructors, destructors, send/receive,
  frame append/pop helpers, signal message construction, string conversion,
  size/data accessors, and more-flag state.
- `zhashx` and `zpoller`: mapped the Bernstein hash, item lookup/insert/
  destroy, rehash/purge, public insert/update/lookup/load/refresh APIs, and
  poller construction/rebuild/wait/termination helpers.
- `zcertstore`, `zdir`, and `zcert`: mapped certificate-store insert/lookup/
  disk reload, directory traversal and flattening helpers, certificate load/
  destroy/public-key/meta helpers, and Win32 directory-entry population.
- `zlist`, `zlistx`, `zchunk`, `zdigest`, and `zfile`: mapped the list
  traversal/mutation surface, listx detach/delete/purge/destructor path,
  chunk allocation/data/size/read access, digest destroy, and file open/read/
  close/restat/name/size/directory helpers.
- `zhash` and `zconfig`: mapped the simple hash constructor/destructor/
  insert machinery plus ZPL config locate/get/destroy and parser helpers for
  indentation, name characters, names, end-of-line validation, and values.

## Observed Facts

- The retail `zmsg` and `zframe` objects preserve the CZMQ magic tags
  `0x3cafe` and `0x2cafe`; `zchunk` preserves `0x1cafe`.
- `zmsg_new_signal` and `zmsg_signal` use the CZMQ signal sentinel
  `0x7766554433221100 + status` and the expected one-frame/eight-byte
  validation.
- `zclock_sleep`, `zclock_time`, and `zclock_log` match the Win32 CZMQ bodies:
  `Sleep`, `GetSystemTimeAsFileTime` plus millisecond conversion, and
  `_time64`/`strftime`/`vprintf` logging.
- The `zpoller` object rebuild path allocates parallel poll item and reader
  arrays from `zlist_size`, resolves `zsock`/`zactor` readers, and polls with
  `ZMQ_POLLIN`.
- `zcertstore_s_load_certs_from_disk` purges the in-memory hashx, loads a
  recursive `zdir` flatten list, excludes `_secret$` files through `zrex`, and
  inserts certificates by public Z85 key.
- `zconfig_chunk_load` uses `zchunk_data` and `zchunk_size`, then relies on
  the now-named static parser helpers to construct the root ZPL tree.

## Inference Boundary

Confidence is high for the named CZMQ helpers because HLIL control flow,
embedded source paths, magic tags, import usage, and upstream CZMQ v3.0.2
implementations agree. A few adjacent retail-only string setters at
`0x004F6DE0` and `0x004F6E10` remain intentionally unmapped: they behave like
global IPv6 address setters, but their exact CZMQ fork names were not
corroborated by the v3.0.2 source line.

This pass does not change `idZMQ` game-source behavior, does not enable live
online services, and does not claim live ZAP/CURVE authentication parity. It
improves the reverse-engineering map used to keep future source reconstruction
anchored to retail helper ownership.

## Parity Estimate

- Focused retail ZMQ/CZMQ helper mapping:
  **before 62% -> after 84%**.
- ZMQ-related source reconstruction confidence, including the existing
  `idZMQ` public/RCON publication wiring:
  **before 73% -> after 78%**.
- Overall Quake Live source parity:
  **before 55.2% -> after 55.3%**.
