# Quake Live Steam Mapping Round 290

Date: 2026-05-24

Scope: retail Steam-auth networking handshake reconstruction across client
`getchallenge`, server challenge storage, and direct-connect auth handoff.

## Evidence

Primary retail signals:

- `references/analysis/quakelive_symbol_aliases.json` maps
  `sub_4B9150` to `CL_CheckForResend`, `sub_4DF430` to
  `SV_GetChallenge`, and `sub_4E0750` to `SV_DirectConnect`.
- `references/analysis/quakelive_symbol_aliases.json` maps
  `sub_460550` to `SteamClient_GetSteamID` and `sub_4605C0` to
  `SteamClient_GetAuthSessionTicket`.
- `references/hlil/quakelive/quakelive_steam.exe/quakelive_steam.exe_hlil_split/quakelive_steam.exe_hlil_part04.txt`
  shows retail `CL_CheckForResend` copying `getchallenge `, storing the
  SteamID low/high words after the command, copying the auth-ticket bytes, and
  sending a packet sized as ticket length plus the fixed OOB/payload header.
- The same HLIL split shows retail `SV_GetChallenge` using a `0x400` challenge
  table with a `0x2b8` stride, copying SteamID words and ticket bytes into the
  challenge entry, rejecting absent tickets with `No Steam auth token.`, and
  rejecting oversized tickets with `Auth token too large.`.
- `references/reverse-engineering/ghidra/quakelive_steam/decompile_top_functions.c`
  shows retail `SV_DirectConnect` copying SteamID from the selected challenge
  entry into the client and publishing the server-owned `steam` userinfo key
  before qagame `ClientConnect`.

## Source Reconstruction

The source now carries the retail challenge-auth wire contract through these
owners:

- `QL_STEAM_AUTH_TICKET_MAX_LENGTH`,
  `QL_STEAM_AUTH_TICKET_HEX_LENGTH`, and
  `QL_STEAM_CHALLENGE_TOKEN_MIN_LENGTH` define the bounded Steam ticket
  storage used by client and server networking.
- `NET_OutOfBandRaw` sends binary OOB payloads without Huffman compression so
  the challenge packet can preserve embedded zero bytes in SteamID/ticket data.
- `NET_ProtocolSupportsPlatformAuth` exposes the active protocol profile's
  Steam-era platform auth capability.
- `QL_ClientAuth_RequestSteamChallengeTicket` obtains the local SteamID and raw
  auth-ticket bytes while sharing the retained ticket-handle cancellation owner
  used by disconnect cleanup.
- `CL_BuildSteamChallengeRequest` builds the retail payload after the OOB
  marker: command, space, SteamID low word, SteamID high word, raw ticket.
- `SV_ParseSteamChallengeAuth` parses and validates the same payload from the
  original OOB `msg_t`, stores SteamID and raw ticket bytes in `challenge_t`,
  and returns retail-facing rejection messages.
- `SV_CapturePlatformAuthFromChallenge` moves retained challenge auth into
  `client_t`, encodes the raw ticket for the existing Steamworks
  `BeginAuthSession` wrapper, and marks auth pending before qagame
  `ClientConnect`.
- `SV_DirectConnect` now publishes `steam` and `steamid` userinfo from the
  server-owned challenge identity before qagame sees the connecting client.

## Guardrails

Observed:

- Default builds still keep online services disabled by
  `QL_BUILD_ONLINE_SERVICES=0`; the new client builder falls back to a bare
  `getchallenge` when platform auth is not compiled or not available.
- LAN/local bypass behavior is preserved. The strict Steam-auth parser is only
  used after the existing LAN challenge-response fast path.
- The existing connect-userinfo auth capture remains as a compatibility
  fallback when no challenge-carried ticket is available.
- The Steamworks wrapper implementation was not reworked in this round, to
  avoid overlapping the concurrent Steamworks plan session.

## Validation

Focused source and C-probe tests:

- `python -m pytest tests/test_engine_netcode_parity.py tests/test_platform_services.py -q`
  passed with 95 tests.

Parity estimate for networking after this round:

- Full engine networking, including Steam auth and content lanes: 88% -> 92%.
- Core UDP/netchan/gamestate/snapshot mechanics excluding Steam auth policy:
  97% -> 97%.

