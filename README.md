# synapse_msgs_fbs

Minimal FlatBuffer schemas for `cerebri2`.

This repo keeps only the active `cerebri2` schemas plus a generated minimal ROS
message mirror for those schemas. It contains only the definitions currently
required by the `cerebri2` firmware and log pipeline:

- `fbs/cerebri2/cerebri2_topics.fbs`
- `fbs/cerebri2/cerebri2_log.fbs`
- `fbs/cerebri2/cerebri2_sil.fbs`
- `msg/cerebri2/msg/*.msg`

The scope is deliberately small:

- live topic payloads for diagnostics and tooling
- self-describing log envelopes for SD-card logging
- native-sim SITL input payloads
- no legacy ROS package mirror

Regenerate the ROS `.msg` files from the FlatBuffer schemas with:

```sh
python3 convert_fbs.py fbs/cerebri2 --output msg --clean
```

FlatBuffer unions are emitted as discriminated ROS messages with a `type`
field plus one field per variant.
