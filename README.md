# synapse_msgs_fbs

Minimal FlatBuffer schemas for `cerebri`.

This repo keeps only the active `cerebri` schemas plus a generated minimal ROS
message mirror for those schemas. It contains only the definitions currently
required by the `cerebri` firmware and log pipeline:

- `fbs/cerebri/cerebri_topics.fbs`
- `fbs/cerebri/cerebri_log.fbs`
- `fbs/cerebri/cerebri_sil.fbs`
- `msg/cerebri/msg/*.msg`

The scope is deliberately small:

- live topic payloads for diagnostics and tooling
- self-describing log envelopes for SD-card logging
- native-sim SITL input payloads
- no legacy ROS package mirror

Regenerate the ROS `.msg` files from the FlatBuffer schemas with:

```sh
python3 convert_fbs.py fbs/cerebri --output msg --clean
```

FlatBuffer unions are emitted as discriminated ROS messages with a `type`
field plus one field per variant.
