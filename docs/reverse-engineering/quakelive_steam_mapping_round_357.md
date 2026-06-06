# Quake Live Steam Host Mapping Round 357

Date: 2026-06-06

Focus: retained ZeroMQ/CZMQ support wiring for the server-owned `idZMQ`
runtime, especially the `zsock`, `zactor`, `zstr`, `zauth`, and `zsys`
helpers around `0x004F5100..0x004F76E0`.

## Evidence Sources

- Owning retail binary: `assets/quakelive/quakelive_steam.exe`.
- Canonical HLIL:
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
  and the split files in the adjacent `quakelive_steam.exe_hlil_split/`
  directory.
- Companion Ghidra corpus:
  `references/reverse-engineering/ghidra/quakelive_steam/functions.csv`,
  `analysis_symbols.txt`, and `decompile_top_functions.c`.
- Existing retained source boundary:
  `src/code/server/sv_zmq.c`.
- Corroborating CZMQ source shape:
  [`zsock.c`](https://github.com/zeromq/czmq/blob/v3.0.2/src/zsock.c),
  [`zactor.c`](https://github.com/zeromq/czmq/blob/v3.0.2/src/zactor.c),
  [`zstr.c`](https://github.com/zeromq/czmq/blob/v3.0.2/src/zstr.c),
  [`zauth.c`](https://github.com/zeromq/czmq/blob/v3.0.2/src/zauth.c),
  and [`zsys.c`](https://github.com/zeromq/czmq/blob/v3.0.2/src/zsys.c).

## Observed Retail Facts

The Quake Live host does not merely call a few libzmq exports directly. It
embeds a CZMQ-style layer and routes server ZMQ work through it:

- `idZMQ_RegisterCvarsAndInitRcon` registers the retail cvar set, creates a
  `zauth` actor when RCON is enabled, sends the actor `VERBOSE`/`PLAIN`
  control commands, creates a ROUTER socket, assigns ZAP domain `"rcon"`,
  toggles PLAIN server mode from `zmq_rcon_password`, enables router mandatory
  delivery, binds the endpoint, and logs `zmq RCON socket: %s`.
- `idZMQ_InitStatsPublisher` reuses the same actor lane, creates a PUB socket,
  assigns ZAP domain `"stats"`, toggles PLAIN server mode from
  `zmq_stats_password`, binds the resolved endpoint, and logs
  `zmq PUB socket: %s`.
- The actor path is anchored by the `0x5CAFE` zactor tag, `_beginthreadex`,
  child-thread priority inheritance, `zsys_create_pipe`, startup handshake via
  `zsock_wait`, and `$TERM` teardown.
- The socket wrapper path is anchored by the `0x4CAFE` zsock tag,
  `0xDEADBEEF` destroy marker, source paths such as
  `..\..\..\..\src\zsock.c`, and `zsys_socket`/`zsys_close` ownership.
- The auth path is anchored by `inproc://zeromq.zap.01`, the `ALLOW`, `DENY`,
  `PLAIN`, `CURVE`, `GSSAPI`, `VERBOSE`, and `$TERM` commands, plus existing
  ZAP request and mechanism aliases from earlier rounds.
- The option setters line up with libzmq option IDs: `ZMQ_ZAP_DOMAIN` `0x37`,
  `ZMQ_PLAIN_SERVER` `0x2c`, `ZMQ_ROUTER_MANDATORY` `0x21`, `ZMQ_TYPE`
  `0x10`, `ZMQ_RCVMORE` `0x0d`, and the expected HWM/linger/IPv6/time-out
  integer options.

## New Aliases Added

| Raw symbol | Alias | Evidence |
| --- | --- | --- |
| `sub_4F5100` | `zsock_new_checked` | Allocates zsock, stamps `0x4CAFE`, calls `zsys_socket`, and carries `src\zsock.c:0x3f`. |
| `sub_4F5190` | `zsock_destroy_checked` | Validates zsock, stamps `0xDEADBEEF`, calls `zsys_close`, frees endpoint/cache/self. |
| `sub_4F51E0` | `zsock_destroy` | Thin unchecked wrapper over `zsock_destroy_checked(..., NULL, 0)`. |
| `sub_4F5600` | `zsock_signal` | Builds a signal zmsg and sends it through the supplied socket. |
| `sub_4F5630` | `zsock_wait` | Receives/discards zmsgs until `zmsg_signal` returns a non-negative status. |
| `sub_4F5690` | `zsock_is` | Tests the `0x4CAFE` object tag. |
| `sub_4F56B0` | `zsock_resolve` | Resolves zactor pipes, zsock handles, and raw libzmq handles. |
| `sub_4F5750` | `zsock_set_zap_domain` | Sets option `0x37` from a string length. |
| `sub_4F5790` | `zsock_set_plain_server` | Sets option `0x2c` from an integer argument. |
| `sub_4F57C0` | `zsock_set_ipv6` | Sets option `0x2a` during `zsys_socket` setup. |
| `sub_4F57F0` | `zsock_type` | Gets option `0x10`. |
| `sub_4F5830` | `zsock_set_sndhwm` | Sets option `0x17`. |
| `sub_4F5860` | `zsock_set_rcvhwm` | Sets option `0x18`. |
| `sub_4F5890` | `zsock_set_linger` | Sets option `0x11`. |
| `sub_4F58C0` | `zsock_set_sndtimeo` | Sets option `0x1c`, used by zactor teardown. |
| `sub_4F58F0` | `zsock_rcvmore` | Gets option `0x0d`. |
| `sub_4F5930` | `zsock_new_pub_checked` | Creates a PUB zsock, attaches endpoints, destroys on attach failure. |
| `sub_4F5980` | `zsock_set_router_mandatory` | Verifies ROUTER type before setting option `0x21`. |
| `sub_4F59D0` | `s_thread_shim` | Windows zactor shim calling the actor handler, signaling, destroying pipe, and `_endthreadex`. |
| `sub_4F5A30` | `zactor_new` | Allocates `0x5CAFE` actor, creates pipe, starts suspended thread, waits for handshake. |
| `sub_4F5B50` | `zactor_destroy` | Sends `$TERM`, waits for child signal, destroys pipe, stamps `0xDEADBEEF`. |
| `sub_4F5BC0` | `zactor_is` | Tests the `0x5CAFE` actor tag. |
| `sub_4F5BE0` | `zactor_resolve` | Returns the actor pipe handle or the original object. |
| `sub_4F5C10` | `s_send_string` | Static zstr sender that creates a zmq message and applies `ZMQ_SNDMORE`. |
| `sub_4F5CB0` | `zstr_recv` | Receives a zmq message and returns a malloced, NUL-terminated string. |
| `sub_4F5D60` | `zstr_send` | Sends a single string, substituting `""` for NULL. |
| `sub_4F5D90` | `zstr_sendm` | Sends a string frame with MORE. |
| `sub_4F5DB0` | `zstr_sendx` | Builds a multipart zmsg from varargs and sends it. |
| `sub_4F5E10` | `zstr_free` | Frees a string and clears the caller's pointer. |
| `sub_4F5E30` | `zmalloc` | Zeroing allocator with CZMQ fatal out-of-memory reporting. |
| `sub_4F5EA0` | `zauth_self_destroy` | Destroys zauth lists/poller, unbinds ZAP endpoint, frees self. |
| `sub_4F5F10` | `zauth_self_new` | Creates zauth self, binds `inproc://zeromq.zap.01`, and builds poller. |
| `sub_4F69F0` | `zauth` | Actor body: initializes auth self, signals ready, polls pipe/ZAP socket, dispatches auth. |
| `sub_4F6AA0` | `zsys_close` | Removes tracked socket ref, decrements open count, calls `zmq_close`. |
| `sub_4F6B30` | `zsys_sockname` | Maps libzmq socket type numbers to names including ROUTER, XPUB, XSUB, STREAM, SERVER, CLIENT. |
| `sub_4F6BB0` | `zsys_handler_reset` | Removes the Win32 console handler and resets handler state. |
| `sub_4F6BF0` | `s_signal_handler` | Sets CZMQ interrupted state for the default signal handler. |
| `sub_4F6C00` | `zsys_file_exists` | Uses the adjacent file-mode/stat lane to test existence. |
| `sub_4F6C50` | `zsys_file_mode` | Windows `GetFileAttributesA` mode translation for file/dir/read/write bits. |
| `sub_4F6CA0` | `zsys_file_stable` | Checks mtime age and returns whether the file is older than one second. |
| `sub_4F6D10` | `zsys_vprintf` | Allocating `_vsnprintf`/`_vscprintf` formatter. |
| `sub_4F7070` | `zsys_shutdown` | atexit shutdown, dangling socket diagnostics, context termination, mutex cleanup. |
| `sub_4F71B0` | `zsys_create_pipe` | Creates PAIR sockets, applies pipe HWM, binds/connects `inproc://pipe-%04x-%04x`. |
| `sub_4F72A0` | `zsys_handler_set` | Installs or removes the Win32 console handler. |
| `sub_4F72F0` | `zsys_catch_interrupts` | Honors `ZSYS_SIGHANDLER` and enables the default handler. |
| `sub_4F7360` | `zsys_sprintf` | Varargs wrapper over `zsys_vprintf`. |
| `sub_4F76E0` | `zsys_socket` | Initializes zsys, creates libzmq socket, applies defaults, tracks filename/line refs. |

## Source Reconstruction Boundary

No writable source change was made in this pass. The current
`src/code/server/sv_zmq.c` reconstruction already keeps the Quake Live-only
online service surface behind `QL_BUILD_ONLINE_SERVICES`, defaults to disabled
behavior, and models the retail server-owned surface with compatible cvars,
endpoint logs, stats publication, RCON peer handling, ZAP domain/plain-server
setup, password-file updates, and fallback transcript behavior.

The retail binary bundles CZMQ actor/auth machinery directly. Reintroducing
that full actor stack into writable source would expand online-service code
that the repository policy intentionally gates off. For parity work, the
useful reconstruction outcome here is the stronger map from `idZMQ` to the
retail CZMQ helpers and the explicit confirmation that the retained source
divergence is a policy-bounded compatibility layer, not an unmapped gameplay
or engine subsystem.

## Inference Boundary

Confidence is high for the aliases above because each name is supported by at
least two signals: retail call relationships, object tags/source paths,
ZeroMQ option constants, command strings, or upstream CZMQ source shape. The
upstream source is corroborating only; the committed HLIL/Ghidra corpus remains
the authoritative evidence for retail ownership and control flow.

The smaller `zsys` configuration setters around `0x004F6DB0..0x004F6E70`
remain intentionally unaliased in this pass. Their behavior is clear
(`ZSYS_INTERFACE`, IPv6 address strings, log identity, and log sender setup),
but the exact function names are version-sensitive enough that promoting them
would be weaker than the surrounding aliases.

## Verification

- `references/analysis/quakelive_symbol_aliases.json` parses through
  `ConvertFrom-Json`.
- This pass adds `47` Steam-host address aliases.
- Address-keyed `quakelive_steam` coverage moved from `2810 / 5473`
  (`51.343%`) to `2857 / 5473` (`52.202%`) within this checkout.
- No game/runtime launch was performed; this was a static evidence and mapping
  pass.

## Parity Estimate

- Focused `idZMQ` to CZMQ helper map:
  **before 68% -> after 94%**. The principal remaining gap is exact naming for
  minor `zsys` environment/logging helpers rather than server ZMQ behavior.
- Retained writable `sv_zmq.c` reconstruction:
  **unchanged at 92%** for the online-service-gated compatibility surface.
- Repository-wide retail source parity:
  **unchanged at approximately 98%**; this round improves evidence coverage and
  future reconstruction confidence without claiming a new gameplay/runtime
  source change.
