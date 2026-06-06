# Quake Live ZMQ/CZMQ Mapping Round 381

Date: 2026-06-06

Focus: recover the retained libzmq `tcp_listener_t` lifecycle, bind/listen
setup, accept event, endpoint publication, fd-watch registration, and
stream-engine handoff that sits opposite the `tcp_connecter_t` reconstruction
from round 379.

## Alias Map

| Symbol | Alias | Confidence |
| --- | --- | --- |
| `sub_419D90` | `zmq_tcp_listener_t_ctor` | High |
| `sub_419E30` | `zmq_tcp_listener_t_scalar_deleting_dtor` | High |
| `sub_419E60` | `zmq_tcp_listener_t_dtor` | High |
| `sub_419F90` | `zmq_tcp_listener_t_process_plug` | High |
| `sub_419FF0` | `zmq_tcp_listener_t_process_term` | High |
| `sub_41A020` | `zmq_tcp_listener_t_in_event` | High |
| `sub_41A2D0` | `zmq_tcp_listener_t_close` | High |
| `sub_41A3D0` | `zmq_tcp_listener_t_get_address` | High |
| `sub_41A490` | `zmq_tcp_listener_t_set_address` | High |
| `sub_41A7C0` | `zmq_tcp_listener_t_accept` | High |
| `sub_41AAD0` | `zmq_tcp_listener_t_io_object_scalar_deleting_dtor` | High |

## Notes

This pass added 8 aliases and re-pinned 3 earlier listener aliases while
leaving endpoint formatting details to a future endpoint-format pass.
