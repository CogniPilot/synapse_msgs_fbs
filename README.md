# synapse_msgs_fbs

Minimal FlatBuffer schemas for `synapse`.

This repo keeps only the active `synapse` schemas plus a generated minimal ROS
message mirror for those schemas. It contains only the definitions currently
required by the `synapse` firmware and log pipeline:

- `fbs/synapse/synapse_topics.fbs`
- `fbs/synapse/synapse_log.fbs`
- `fbs/synapse/synapse_sil.fbs`
- `msg/synapse/msg/*.msg`

The scope is deliberately small:

- live topic payloads for diagnostics and tooling
- self-describing log envelopes for SD-card logging
- native-sim SITL input payloads
- no legacy ROS package mirror

Regenerate the ROS `.msg` files from the FlatBuffer schemas with:

```sh
python3 convert_fbs.py fbs/synapse --output msg --clean
```

FlatBuffer unions are emitted as discriminated ROS messages with a `type`
field plus one field per variant.
