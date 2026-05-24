# Networking Parity Audit - 2026-05-24

## Scope

This audit re-checks the engine networking implementation against the retail
Steam Quake Live binary. It is intentionally limited to evidence collection and
parity classification. No source implementation changes were made as part of
this audit.

Primary retail target:

- `assets/quakelive/quakelive_steam.exe`
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil.txt`
- `references/reverse-engineering/ghidra/quakelive_steam/`
- `references/analysis/quakelive_symbol_aliases.json`

Primary local source surfaces:

- `src/code/qcommon/common.c`
- `src/code/qcommon/qcommon.h`
- `src/code/qcommon/net_chan.c`
- `src/code/client/cl_main.c`
- `src/code/client/cl_net_chan.c`
- `src/code/client/cl_parse.c`
- `src/code/client/cl_cgame.c`
- `src/code/server/sv_main.c`
- `src/code/server/sv_client.c`
- `src/code/server/sv_init.c`
- `src/code/server/sv_net_chan.c`
- `src/code/server/sv_snapshot.c`
- `src/code/server/sv_game.c`
- `src/common/platform/platform_steamworks.c`

This pass does not rely on a live game launch. Static source and committed
reference evidence were sufficient to identify the next strict-parity gap.

## Executive Summary

The repository is substantially ahead of the stale top section in
`docs/plans/network-parity-plan.md`. The current tree has strong parity for
protocol 91 selection, netchan packet layout, qport handling, fragmentation,
reliable XOR encode/decode, server netchan queueing, gamestate/configstring
bootstrap, long configstring chunks, snapshot parsing, server info/status keys,
and much of the Steamworks UGC/server-auth callback surface.

The next major strict-parity gap is the retail Steam authentication challenge
handshake. Retail QL does not send a bare `getchallenge` for non-LAN Steam
connections. The retail client prefixes `getchallenge `, appends its SteamID,
then appends the raw Steam auth ticket. The retail server parses that binary
payload in `SV_GetChallenge`, stores SteamID and auth-ticket bytes in a much
larger challenge entry, and later moves those fields into the accepted client
during `SV_DirectConnect`.

The current source still sends a plain `getchallenge` from `CL_CheckForResend`
and still keeps `challenge_t` at the classic Quake III shape with no retained
SteamID or auth token. Server-side auth has been reconstructed around connect
userinfo keys (`steamid`, `auth`, `author`, `author2`) instead of the retail
challenge-carried token. That makes the local auth bridge useful, but it is not
wire-compatible with the observed retail Steam handshake yet.

Secondarily, the current source rejects challenge and direct-connect requests
when `sv_vac` is disabled. The inspected retail networking paths advertise and
consume VAC/secure mode state, but the retail `SV_GetChallenge` evidence does
not show the current local rejection string or behavior. This should be treated
as a likely parity gap, with one more string-wide check before changing
behavior.

Audit-only parity estimate:

- Full engine networking, including Steam auth and content lanes: before
  audit 88%, after audit 88%.
- Core UDP/netchan/gamestate/snapshot mechanics excluding Steam auth policy:
  before audit 97%, after audit 97%.

The percentages did not change because this was an audit round, but confidence
in the remaining high-impact gap increased.

## Evidence Inventory

### Retail Symbol And Import Evidence

Observed facts:

- `references/reverse-engineering/ghidra/quakelive_steam/imports.txt:216-238`
  imports Steam client/server APIs including `SteamAPI_Init`,
  `SteamGameServer`, `SteamGameServerNetworking`,
  `SteamGameServerStats`, `SteamGameServerUGC`, `SteamGameServer_Init`,
  `SteamGameServer_RunCallbacks`, `SteamNetworking`, `SteamUGC`,
  `SteamUser`, and `SteamUserStats`.
- `references/analysis/quakelive_symbol_aliases.json:2192` promotes
  `sub_460550` as `SteamClient_GetSteamID`.
- `references/analysis/quakelive_symbol_aliases.json:2194` promotes
  `sub_4605C0` as `SteamClient_GetAuthSessionTicket`.
- `references/analysis/quakelive_symbol_aliases.json:2280` promotes
  `sub_465FD0` as `SteamServer_BeginAuthSession`.
- `references/analysis/quakelive_symbol_aliases.json:2314-2320` promotes
  the Steam Workshop queue, finalize, callback, init, and request-download
  functions.
- `references/analysis/quakelive_symbol_aliases.json:2834` promotes
  `sub_4B9150` as `CL_CheckForResend`.
- `references/analysis/quakelive_symbol_aliases.json:3213` promotes
  `sub_4D6C90` as `Netchan_Init`.
- `references/analysis/quakelive_symbol_aliases.json:3368` promotes
  `sub_4DF430` as `SV_GetChallenge`.
- `references/analysis/quakelive_symbol_aliases.json:3382` promotes
  `sub_4E0750` as `SV_DirectConnect`.
- `references/analysis/quakelive_symbol_aliases.json:3460` promotes
  `sub_4E4CD0` as `SV_Netchan_Encode`.

Inference:

- The networking reconstruction should treat the Steam-era retail binary as
  the owner for protocol handshake, platform auth, workshop bootstrapping, and
  server callback behavior. Classic Q3 paths are useful only when the retail
  binary still carries the same behavior.

### Retail Handshake Evidence

Observed facts:

- Retail `CL_CheckForResend` builds a connect userinfo containing protocol
  `0x5b`, qport, and challenge before sending `connect "userinfo"`.
  See
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:16045-16064`.
- Retail `CL_CheckForResend` calls `SteamClient_GetAuthSessionTicket`, then
  `SteamClient_GetSteamID`, copies `getchallenge `, stores the SteamID words,
  copies the auth-ticket bytes, and sends an out-of-band packet whose length is
  `ticketLen + 0x19`.
  See
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:16075-16088`.
- Retail `SV_GetChallenge` uses a `0x400` entry challenge table with a stride
  of `0x2b8`, not the small classic Q3 challenge entry.
  See
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:48870-48890`.
- Retail `SV_GetChallenge` derives token length from the packet cursor size,
  rejects short or oversized tickets with `No Steam auth token.` or
  `Auth token too large.`, copies SteamID words from payload offsets, copies
  the auth ticket into the challenge entry, stores ticket length, then sends
  `challengeResponse`.
  See
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt:48914-48918`.
- Retail connectionless dispatch explicitly routes `getchallenge` to
  `SV_GetChallenge` and `connect` to `SV_DirectConnect`.
  See
  `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part05.txt:2916-2924`.
- Retail `SV_DirectConnect` copies SteamID from the selected challenge entry
  into client fields and writes a `steam` userinfo key before qagame
  `ClientConnect`.
  See
  `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c:15808-15825`.

Inference:

- The strict retail Steam network contract is challenge-carried auth, not
  connect-userinfo-carried auth.
- Retail server auth ownership begins no later than direct connect from the
  retained challenge ticket. The game receives a userinfo string with a
  server-populated `steam` key.

## Current Source Parity Matrix

| Surface | Source status | Verdict | Notes |
| --- | --- | --- | --- |
| Protocol number | `QL_RETAIL_PROTOCOL_VERSION` is `91`; `PROTOCOL_VERSION` aliases it. | Strong parity | Source anchors: `src/code/qcommon/qcommon.h:233-234`. |
| Protocol profile | Active profile is retail Steam and carries command/key/policy booleans. | Strong parity | Source anchors: `src/code/qcommon/common.c:151-152`, `src/code/qcommon/common.c:969-974`, `src/code/qcommon/common.c:1382-1408`. |
| Demo protocol | Demo protocol list includes retail 91. | Strong parity | Source anchor: `src/code/qcommon/common.c:1408`. |
| OOB command names | Profile helpers own `getchallenge`, `challengeResponse`, `connect`, `connectResponse`, download commands, configstring key names. | Strong parity for names | The command name contract is in place; payload shape is not complete for `getchallenge`. |
| Client challenge request | Client sends bare `getchallenge`. | Gap | Source anchor: `src/code/client/cl_main.c:6755`. Retail appends SteamID and auth ticket. |
| Client connect request | Client sends protocol/qport/challenge in quoted userinfo, compressed when profile says. | Strong parity for connect leg | Source anchors: `src/code/client/cl_main.c:6765-6780`. |
| Server challenge table | `challenge_t` has only address, challenge, timing, connected flag. | Gap | Source anchor: `src/code/server/server.h:204-214`. Retail entry stride is `0x2b8` and stores SteamID/ticket bytes. |
| Server challenge auth parsing | Server does not parse SteamID/auth-ticket bytes from `getchallenge`. | Gap | Source anchor: `src/code/server/sv_client.c:1871-1965`. |
| VAC disabled behavior | Server rejects challenge and direct connect when `sv_vac` is zero. | Likely gap | Source anchors: `src/code/server/sv_client.c:1882-1889`, `src/code/server/sv_client.c:2118-2124`. Inspected retail challenge evidence rejects missing/oversized auth token, not disabled VAC. |
| Direct connect auth source | Server captures `steamid`/`auth` fragments from connect userinfo. | Partial | Source anchors: `src/code/server/sv_client.c:238-283`, `src/code/server/sv_client.c:2317-2326`. Retail gets SteamID/ticket from the challenge entry. |
| Direct connect auth order | Source begins platform auth after qagame accepts the user. | Partial | Source anchor: `src/code/server/sv_client.c:2342`. Retail direct-connect evidence starts from retained Steam auth before or during setup and writes `steam` before qagame. |
| Server-populated `steam` userinfo key | Not observed in source direct-connect path. | Gap | Retail evidence writes `steam` into userinfo at `decompile_top_functions.c:15823`. |
| Netchan header/qport | Client-to-server qport and sequence header are retained. | Strong parity | Source anchors: `src/code/qcommon/net_chan.c:199-205`, `src/code/qcommon/net_chan.c:273-275`, `src/code/qcommon/net_chan.c:325-329`. |
| Fragment sizing | `FRAGMENT_SIZE` is `MAX_PACKETLEN - 100`, matching retail `0x514`. | Strong parity | Source anchor: `src/code/qcommon/net_chan.c:52`. |
| Fragment transmit/process | Transmit-next-fragment, transmit, and process paths match the retail shape. | Strong parity | Source anchors: `src/code/qcommon/net_chan.c:184-231`, `src/code/qcommon/net_chan.c:240-262`, `src/code/qcommon/net_chan.c:294-426`. |
| Reliable XOR codec | Client and server encode/decode are gated by the protocol profile. | Strong parity | Source anchors: `src/code/client/cl_net_chan.c:29-166`, `src/code/server/sv_net_chan.c:29-208`. |
| Server netchan queue | Retail `#462` queued netchan behavior is retained. | Strong parity | Source anchors: `src/code/server/sv_net_chan.c:131-194`. |
| Gamestate parse/send | Configstrings, baselines, EOF, clientNum, checksumFeed, and FS restart are present. | Strong parity | Source anchors: `src/code/client/cl_parse.c:384-453`, `src/code/server/sv_client.c:2461-2528`. |
| Long configstrings | `bcs0`, `bcs1`, and `bcs2` handling exists on client and retail HLIL. | Strong parity | Source anchor: `src/code/client/cl_cgame.c:5760-5774`; retail anchors: `hlil_part04.txt:6687-6798`. |
| Snapshot parse | Delta source validation, areamask, playerstate, and packet entities are retained. | Strong parity | Source anchor: `src/code/client/cl_parse.c:193-260`. |
| Server info/status keys | Server advertises retail-profile protocol and keys including VAC/server type/bot players. | Strong parity | Source anchors: `src/code/server/sv_main.c:1171-1240`. |
| Steam GameServer wrappers | Server init/auth/session/callback wrappers are present. | Mostly strong | Source anchors include `src/common/platform/platform_steamworks.c:4153-4190`; the wrapper cannot close the handshake gap by itself. |
| Workshop/UGC queue | Request, queue, finalize, install, and download-result paths mirror retail function evidence. | Strong parity with policy gate | Source anchors: `src/code/client/cl_main.c:1325-1398`, `src/code/client/cl_main.c:4822-4858`, `src/common/platform/platform_steamworks.c:3512-3674`; retail anchors: `hlil_part02.txt:40768-41058`. |
| Online services default | `QL_BUILD_ONLINE_SERVICES` defaults to disabled by policy. | Intentional divergence | This follows repository rules and should stay behind the policy gate, even though retail used live Steam services. |
| Modern Steam adapters | Source labels missing WebAPI auth-ticket and modern P2P adapter gaps. | Non-retail-modern gap | Source anchors: `src/common/platform/platform_steamworks.c:4970`, `src/common/platform/platform_steamworks.c:5441`. |

## Findings

### NET-F1: Retail Steam auth challenge payload is missing

Severity: Critical for strict retail network parity.

Observed retail behavior:

- Client obtains an auth ticket and SteamID before challenge request.
- Client sends `getchallenge ` plus binary SteamID and ticket bytes.
- Server rejects non-LAN challenge packets that do not carry a usable token.
- Server stores SteamID and auth-ticket bytes in the challenge entry.

Observed source behavior:

- `CL_CheckForResend` sends only `NET_GetChallengeRequestCommand()` in the
  `CA_CONNECTING` branch.
- `challenge_t` has no SteamID, auth-ticket length, or auth-ticket buffer.
- `SV_GetChallenge` sends a normal challenge response once legacy Q3
  authorization is bypassed.
- The reconstructed platform auth lane expects `steamid` and token data in
  connect userinfo instead.

Impact:

- A local retail-compatible server would not enforce the observed Steam auth
  challenge packet shape.
- A local retail-compatible client would not satisfy a strict retail server's
  `getchallenge` expectations.
- `SV_BeginPlatformAuthSession` is only effective when something else injects
  auth data into connect userinfo, which is not what retail evidence shows.

Confidence: High. The client HLIL, server HLIL, promoted symbol names, and
current source all point to the same mismatch.

Recommended implementation direction:

1. Add policy-gated client challenge auth state that requests a Steam auth
   session ticket for `CA_CONNECTING`, retains the handle until disconnect or
   rejection, and builds the retail binary `getchallenge` payload.
2. Extend `challenge_t` with SteamID low/high words, auth-ticket length, and a
   bounded auth-ticket buffer matching the retail `0x200` maximum.
3. Teach `SV_GetChallenge` to parse and validate the Steam-auth challenge
   payload when platform auth is supported and the address is not LAN.
4. Move challenge-retained SteamID/token into the `client_t` before qagame
   `ClientConnect`, and keep the existing connect-userinfo capture as a
   compatibility fallback only.
5. Add packet-construction and parser tests that assert the `ticketLen + 0x19`
   wire size, SteamID offsets, no-token rejection, too-large-token rejection,
   and LAN/local fallback behavior.

### NET-F2: Server direct-connect auth ownership is shifted to userinfo

Severity: High for strict Steam server auth parity.

Observed retail behavior:

- `SV_DirectConnect` copies SteamID from the selected challenge entry into the
  client slot.
- Local connections use the local SteamID/ticket path.
- The server writes a `steam` key into userinfo before calling qagame
  `ClientConnect`.
- Steam server auth begins from the retained ticket data.

Observed source behavior:

- `SV_CapturePlatformAuthFromUserinfo` reads `steamid`, `auth`, `author`, and
  `author2` from connect userinfo.
- `SV_GameClientConnect` runs before `SV_BeginPlatformAuthSession`.
- The source has useful telemetry and pending-state handling, but the auth
  data source is not retail-accurate.

Impact:

- Qagame auth checks can pass only if non-retail connect userinfo auth keys
  are present before `SV_GameClientConnect`.
- The game-visible identity key is likely wrong or incomplete compared with
  retail's server-populated `steam` key.

Confidence: High for the userinfo-source mismatch; medium-high for the exact
internal ordering because the decompile is less readable than the packet-level
HLIL.

Recommended implementation direction:

1. Populate `client_t` auth fields from the matched challenge entry before
   qagame connection.
2. Set the retail `steam` key in the userinfo string from the server-owned
   SteamID. Preserve local compatibility keys only if existing game or UI
   code requires them.
3. Re-run game import auth tests to ensure `trap_VerifySteamAuth` sees pending
   auth before the first qagame `ClientConnect`.

### NET-F3: `sv_vac 0` rejection appears non-retail

Severity: Medium-high for server configuration parity.

Observed retail behavior:

- Retail imports and uses Steam GameServer secure/auth APIs.
- Inspected retail `SV_GetChallenge` evidence shows rejection for missing or
  oversized Steam auth tokens.
- This pass did not find the local rejection text `VAC is disabled on this
  server` in the inspected retail challenge/direct-connect evidence.

Observed source behavior:

- `SV_GetChallenge` rejects immediately when `sv_vac` is absent or zero.
- `SV_DirectConnect` repeats the same rejection.
- `sv_vac` is also advertised in server info/status and used for telemetry.

Impact:

- A server with `sv_vac 0` cannot accept clients in the local source, while
  retail likely treated VAC as secure-mode selection and advertised state.
- This may make disabled-VAC test servers less retail-like than intended.

Confidence: Medium-high. The inspected retail functions strongly suggest a
gap, but a final string-wide retail check should precede behavior changes.

Recommended implementation direction:

1. Run a final retail string/reference search for the local rejection message
   and nearby VAC branches.
2. If no retail rejection is found, remove the hard challenge/direct-connect
   rejection and keep `sv_vac` as advertised secure-mode policy.
3. Keep fake VAC-ban testing behind `net_fakevacban`; do not overload
   `sv_vac 0` as an auth failure.

### NET-F4: Retail LAN/local auth exceptions need to be preserved while fixing Steam auth

Severity: Medium.

Observed retail behavior:

- `SV_GetChallenge` contains LAN/server-type gating before challenge-table
  handling.
- `SV_DirectConnect` has a local-address path that obtains local SteamID and
  auth ticket directly rather than copying from a remote challenge entry.

Observed source behavior:

- LAN addresses currently receive immediate challenge responses.
- Local-address checks already exist in platform auth validation and should not
  be broken by a stricter remote Steam-auth parser.

Impact:

- The next implementation round must not accidentally require a Steam auth
  blob for loopback or LAN probe scenarios.

Confidence: Medium. The exception shape is visible, but exact retail policy
for dedicated/listen/local combinations needs a focused pass if behavior is
changed.

Recommended implementation direction:

- Keep LAN/local bypass tests beside the new auth-ticket parser tests.
- Document which bypass is retail-observed and which bypass is repository
  policy for offline development.

## Strong Parity Areas

### Protocol Profile And Key Contracts

The retail protocol constant is reconstructed as `91`, demo protocol handling
uses the same value, and server/client paths now query profile helpers instead
of scattering hard-coded literals. This is a solid base for the remaining
handshake work because the gap is payload ownership, not command naming.

### Netchan Transport

The classic netchan mechanics line up well with retail QL:

- qport appears only on client-to-server packets.
- fragment size matches the retail `MAX_PACKETLEN - 100` shape.
- transmit, transmit-next-fragment, and process paths preserve the retail
  high-bit fragment marker and reassembly model.
- client and server reliable XOR codecs are profile-gated.
- the server-side `#462` queue behavior is reconstructed and logged.

No new low-level netchan action item was found in this audit.

### Gamestate, Configstrings, And Snapshots

The gamestate bootstrap flow is close to retail:

- server writes pending reliable commands, `svc_gamestate`, configstrings,
  baselines, EOF, client number, and checksum feed.
- client parses configstrings, baselines, EOF, client number, checksum feed,
  systeminfo changes, file-system restart, and download start.
- long configstring chunk commands `bcs0`, `bcs1`, and `bcs2` are present.
- snapshot parsing retains the expected delta-frame and areamask checks.

No new gamestate or snapshot action item was found in this audit.

### Steamworks UGC And Server Callback Surface

The Steamworks wrapper and client workshop bootstrap have strong evidence
coverage:

- UGC item install info and download-item vtable offsets match the retail
  evidence.
- workshop request, queue, complete, install, and download-result log strings
  align with retail HLIL strings.
- server auth session, validation callback, P2P session request, and stats
  wrapper surfaces exist.

These paths remain policy-gated by `QL_BUILD_ONLINE_SERVICES`, which is an
intentional repository divergence from retail live-service behavior.

## Open Questions

1. Exact retail behavior for `sv_vac 0`: the current local hard rejection looks
   suspect, but one more targeted string/control-flow pass should confirm
   whether any retail path rejects clients solely because VAC is disabled.
2. Exact local/listen/dedicated branch matrix for challenge auth: retail has
   LAN and local exceptions; the next implementation should preserve them with
   tests rather than flattening all non-auth packets into one rejection.
3. Exact lifetime for the client auth-ticket handle: retail obtains the ticket
   during resend. The reconstructed client should define cancellation points
   for challenge rejection, disconnect, reconnect, and server switch.
4. Whether the game module expects only `steam` or also local compatibility
   aliases such as `steamid`: source currently has many local consumers of
   `steamid`, so a bridge may need to set both while treating `steam` as the
   retail-owned key.

## Recommended Next Work

Priority order for the next implementation round:

1. Reconstruct the retail Steam-auth `getchallenge` payload end to end.
2. Extend `challenge_t` and direct-connect handoff to carry SteamID and auth
   ticket from challenge to client.
3. Set server-owned `steam` userinfo before qagame `ClientConnect`.
4. Revisit `sv_vac 0` hard rejection after a final retail string/control-flow
   confirmation.
5. Add focused tests for challenge payload construction, parser rejection
   cases, challenge-to-client auth transfer, LAN/local bypasses, and qagame
   pending-auth visibility.

These items should be kept separate from the concurrent Steamworks-plan
session: Steamworks wrappers already exist, but this audit's next gap is the
engine-level packet contract that consumes those wrappers.

