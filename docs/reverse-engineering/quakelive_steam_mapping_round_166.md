# quakelive_steam.exe Mapping Round 166

Date: 2026-04-27

Scope: exact retained `libzmq` `stream_engine.cpp` recovery plus the adjacent
engine-owned renderer and Win32 packet helpers around the old queue heads
`0x00421830`, `0x00437710`, and `0x004EE260`. This pass stayed mapping-only,
but every alias in it is source-backed.

## Summary

This round resolved `10` additional `quakelive_steam.exe` rows.
Classification mix:

- `3` engine-owned functions
- `7` platform-service-owned functions
- `0` CRT/STL/support-library functions
- `0` Awesomium functions
- `0` Steam SDK support functions

The useful outcome is that the old `stream_engine.cpp` seam is no longer split
between a single public `plug` name and a pile of anonymous teardown/read/write
helpers. The retained constructor, destructor, private `unplug`, public
`terminate`, disconnect path, and socket I/O wrappers now read cleanly as a
real `zmq::stream_engine_t` ownership band, while the old renderer and Win32
network queue heads resolve directly to `RB_SwapBuffers`, `Sys_GetPacket`, and
`Sys_SendPacket`.

## Queue Results

| # | Function | Size | Classification | Resolution | Confidence | Debt decision |
| ---: | --- | ---: | --- | --- | --- | --- |
| 1 | `sub_437710` | `513` | engine-owned | `RB_SwapBuffers` | High | Closed from the exact overdraw stencil readback, debug stat print lane, `qglFinish`, `"***************** RB_SwapBuffers"` log comment, and `GLimp_EndFrame` tail in the checked-in renderer. |
| 2 | `sub_421830` | `512` | platform-service-owned | `zmq_stream_engine_t_dtor` | High | Closed from the exact `!plugged` assertion, `closesocket` retirement, encoder/decoder deletion, endpoint-string teardown, and base-class unwind from retained `stream_engine.cpp`. |
| 3 | `sub_4EE260` | `505` | engine-owned | `Sys_GetPacket` | High | Closed from the exact dual-socket `recvfrom` loop, `WSAEWOULDBLOCK` / `WSAECONNRESET` skip path, SOCKS relay header unwrap, oversize-packet reject, and `cursize` return path in `win_net.c`. |
| 4 | `sub_4216B0` | `332` | platform-service-owned | `zmq_stream_engine_t_ctor` | High | Closed from the exact stream-engine vtable install, greeting buffer setup, `options`/endpoint copy, nonblocking socket setup, sndbuf/rcvbuf tuning, and peer-name fallback path from the retained constructor. |
| 5 | `sub_423700` | `271` | platform-service-owned | `zmq_stream_engine_t_error` | High | Closed from the exact `session` assertion, disconnect event callback, `session->detach()`, `unplug()`, and `delete this` termination path in upstream `stream_engine.cpp`. |
| 6 | `sub_4EE460` | `268` | engine-owned | `Sys_SendPacket` | High | Closed from the exact address-type dispatch, optional SOCKS encapsulation header, `sendto` transmit path, broadcast-not-available skip, and `NET_SendPacket` error print in `win_net.c`. |
| 7 | `sub_4238E0` | `208` | platform-service-owned | `zmq_stream_engine_t_read` | High | Closed from the exact `recv` wrapper, `WSAEWOULDBLOCK` zero-byte read behavior, peer-failure error set (`WSAENETDOWN` / `WSAECONNRESET` / `WSAENOTCONN` family), and orderly-shutdown `-1` path. |
| 8 | `sub_423810` | `204` | platform-service-owned | `zmq_stream_engine_t_write` | High | Closed from the exact `send` wrapper, speculative-write `WSAEWOULDBLOCK` zero-byte success, and peer-failure collapse to `-1` for the Windows stream engine transmit lane. |
| 9 | `sub_421D70` | `190` | platform-service-owned | `zmq_stream_engine_t_unplug` | High | Closed from the exact `plugged` assertion, fd removal, `io_object_t::unplug` base cleanup, and session disconnect path, reinforced by its reuse from both `terminate` and `error`. |
| 10 | `sub_421E30` | `25` | platform-service-owned | `zmq_stream_engine_t_terminate` | High | Closed from the exact `i_engine`-slot wrapper that subtracts the base offset, calls `unplug()`, and then dispatches the deleting destructor, matching source `terminate() { unplug(); delete this; }`. |

## Evidence Notes

- The retained ZeroMQ tranche is anchored by upstream
  [`stream_engine.cpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/stream_engine.cpp)
  and
  [`stream_engine.hpp`](https://github.com/zeromq/libzmq/blob/v3.2.5/src/stream_engine.hpp).
  The constructor, destructor, `unplug`, `terminate`, `error`, `write`, and
  `read` bodies all preserve the same assertions, socket calls, and ownership
  transitions as the retail HLIL.
- `sub_421E30` is especially stable because the committed HLIL keeps the
  `i_engine` vtable slot and the `arg1 - 8` base adjustment before the final
  deleting-destructor dispatch, which is the exact C++ lowering for
  `stream_engine_t::terminate()`.
- `sub_437710` is the checked-in renderer
  [`RB_SwapBuffers`](../../src/code/renderer/tr_backend.c) body. The HLIL keeps
  the same overdraw accumulation, optional debug-stat prints, `GLimp_EndFrame`,
  and `backEnd.projection2D = qfalse` reset as source.
- `sub_4EE260` and `sub_4EE460` are the checked-in Win32
  [`Sys_GetPacket`](../../src/code/win32/win_net.c) and
  [`Sys_SendPacket`](../../src/code/win32/win_net.c) helpers. The SOCKS relay
  unwrap/rewrap path and the exact Windows socket error handling make the match
  one-to-one.
- I intentionally left the larger remaining queue heads `sub_4FC240`,
  `sub_41AD70`, and `sub_4F7B70` for later passes. They still look promising,
  but this round had enough exact source-backed closure without forcing the
  Vorbis, STL, or CZMQ regex seams early.

## Aliases Added

- `sub_4216B0` -> `zmq_stream_engine_t_ctor`
- `sub_421830` -> `zmq_stream_engine_t_dtor`
- `sub_421D70` -> `zmq_stream_engine_t_unplug`
- `sub_421E30` -> `zmq_stream_engine_t_terminate`
- `sub_423700` -> `zmq_stream_engine_t_error`
- `sub_423810` -> `zmq_stream_engine_t_write`
- `sub_4238E0` -> `zmq_stream_engine_t_read`
- `sub_437710` -> `RB_SwapBuffers`
- `sub_4EE260` -> `Sys_GetPacket`
- `sub_4EE460` -> `Sys_SendPacket`

## Verification

Static mapping validation:

- `python -m json.tool references/analysis/quakelive_symbol_aliases.json`
  passed
- scoped duplicate-key scan for the `quakelive_steam` alias block passed with
  `0` duplicates
- recount after this pass: `1910` raw alias entries, `1838` strict Ghidra
  address-backed aliases
- strict Ghidra address-backed coverage: `33.583%` of `5473` functions
- `git diff --check` passed aside from the repo's existing LF -> CRLF
  normalization warnings on touched text files
- no build or runtime launch was needed; this was mapping-only work on the
  committed evidence corpus

Parity estimate after this pass:

- strict-retail Windows replacement target: `100%` before, `100%` after
- repo-wide checked-in tree parity: `98%` before, `98%` after

## Next Queue Head

After this round, the refreshed largest-unaliased queue begins with:

| # | Address | Ghidra name | Size |
| ---: | --- | --- | ---: |
| 1 | `0x004FC240` | `FUN_004fc240` | `537` |
| 2 | `0x0041AD70` | `FUN_0041ad70` | `517` |
| 3 | `0x0043F590` | `FUN_0043f590` | `507` |
| 4 | `0x004F7B70` | `FUN_004f7b70` | `506` |
| 5 | `0x00486D40` | `FUN_00486d40` | `504` |
| 6 | `0x004E6730` | `FUN_004e6730` | `504` |
| 7 | `0x0050C790` | `FUN_0050c790` | `503` |
| 8 | `0x004B4100` | `FUN_004b4100` | `502` |
| 9 | `0x00510050` | `FUN_00510050` | `501` |
| 10 | `0x00475200` | `FUN_00475200` | `497` |

The next pass can return to the deferred `vorbisfile.c` recursive search lane
at `sub_4FC240`, take the STL/iostream queue head at `sub_41AD70`, or keep
following the retained platform-service seam through the remaining `zrex.c`
and adjacent host/network leftovers.
