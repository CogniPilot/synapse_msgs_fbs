# synapse_msgs_fbs

Minimal FlatBuffer schemas for `synapse`.

This repo keeps the active `synapse` FlatBuffers schemas as the source of truth
plus generated language bindings and a generated ROS 2 interface package. It
contains only the definitions currently required by the `synapse` firmware and
log pipeline:

- `fbs/synapse/synapse_topics.fbs`
- `fbs/synapse/synapse_optical_flow.fbs`
- `fbs/synapse/synapse_mocap.fbs`
- `fbs/synapse/synapse_log.fbs`
- `fbs/synapse/synapse_sil.fbs`
- `ros/synapse_msgs/msg/*.msg`

The scope is deliberately small:

- live topic payloads for diagnostics and tooling
- self-describing log envelopes for SD-card logging
- native-sim SITL input payloads
- ROS 2 interfaces are generated adapters, not the canonical schema

## Language Bindings

The `fbs/synapse` schemas are the source of truth. Generated language bindings
are packaged separately:

- `rust/`: Cargo library crate exposing generated FlatBuffers bindings.
- `python/`: pip-installable package exposing generated Python bindings.
- `ros/synapse_msgs/`: generated ROS 2 interface package.

Use the Rust bindings from another crate with:

```toml
synapse_msgs_fbs = { path = "../synapse_msgs_fbs/rust" }
```

Install the Python bindings locally with:

```sh
pip install ./python
```

Build the generated ROS 2 interface package from a ROS workspace with:

```sh
colcon build --base-paths src/synapse_msgs_fbs/ros --packages-select synapse_msgs
```

Regenerate all checked-in bindings from the FlatBuffer schemas with:

```sh
./scripts/generate_bindings.sh
```

FlatBuffer unions are emitted as discriminated ROS messages with a `type`
field plus one field per variant.
