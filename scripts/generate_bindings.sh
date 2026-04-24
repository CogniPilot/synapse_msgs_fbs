#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
schema_dir="${repo_root}/fbs/synapse"

bootstrap_flatc() {
  local bootstrap_dir="${TMPDIR:-/tmp}/synapse-msgs-fbs-flatc"
  rm -rf "${bootstrap_dir}"
  mkdir -p "${bootstrap_dir}"

  cat > "${bootstrap_dir}/Cargo.toml" <<'TOML'
[package]
name = "synapse-msgs-fbs-flatc"
version = "0.0.0"
edition = "2024"

[build-dependencies]
flatbuffers-build = { version = "=0.2.4", features = ["vendored"] }
TOML
  cat > "${bootstrap_dir}/build.rs" <<'RS'
fn main() {}
RS
  mkdir -p "${bootstrap_dir}/src"
  cat > "${bootstrap_dir}/src/lib.rs" <<'RS'
pub fn flatc_bootstrap() {}
RS

  cargo check --quiet --manifest-path "${bootstrap_dir}/Cargo.toml"
  find "${bootstrap_dir}/target/debug/build" -path "*/out/bin/flatc" -type f -print -quit
}

resolve_flatc() {
  if [[ -n "${FLATC:-}" ]]; then
    echo "${FLATC}"
  elif command -v flatc >/dev/null 2>&1; then
    command -v flatc
  else
    bootstrap_flatc
  fi
}

flatc_bin="$(resolve_flatc)"
if [[ -z "${flatc_bin}" ]]; then
  echo "failed to locate or bootstrap flatc" >&2
  exit 1
fi

schemas=(
  "${schema_dir}/synapse_topics.fbs"
  "${schema_dir}/synapse_optical_flow.fbs"
  "${schema_dir}/synapse_mocap.fbs"
  "${schema_dir}/synapse_log.fbs"
  "${schema_dir}/synapse_sil.fbs"
)

mkdir -p "${repo_root}/rust/src/generated" "${repo_root}/python"
rm -rf "${repo_root}/msg"

"${flatc_bin}" --rust --rust-module-root-file -o "${repo_root}/rust/src/generated" "${schemas[@]}"
"${flatc_bin}" --python -o "${repo_root}/python" "${schemas[@]}"

REPO_ROOT="${repo_root}" python3 - <<'PY'
from pathlib import Path
import os

repo_root = Path(os.environ["REPO_ROOT"])
generated = repo_root / "rust" / "src" / "generated"

groups = {
    "topic": [
        "vec_2f_generated",
        "vec_3f_generated",
        "quaternionf_generated",
        "rate_triplet_generated",
        "attitude_euler_generated",
        "rc_channels_16_generated",
        "control_status_generated",
        "motor_values_4f_generated",
        "motor_raw_4u_16_generated",
        "flight_snapshot_generated",
        "motor_output_generated",
        "vehicle_optical_flow_data_generated",
        "vehicle_optical_flow_generated",
        "vehicle_optical_flow_vel_data_generated",
        "vehicle_optical_flow_vel_generated",
        "mocap_marker_sample_generated",
        "mocap_rigid_body_sample_generated",
        "mocap_segment_sample_generated",
        "mocap_marker_definition_generated",
        "mocap_rigid_body_definition_generated",
        "mocap_segment_definition_generated",
        "mocap_definition_generated",
        "mocap_frame_generated",
    ],
    "log": [
        "schema_record_generated",
        "flight_snapshot_record_generated",
        "motor_output_record_generated",
        "mocap_definition_record_generated",
        "mocap_frame_record_generated",
        "record_payload_generated",
        "log_record_generated",
    ],
    "sil": [
        "sim_input_generated",
    ],
}

lines = [
    "// Module root for checked-in FlatBuffers-generated Rust bindings.",
    "pub mod synapse {",
    "  use super::*;",
]
for namespace, modules in groups.items():
    lines.append(f"  pub mod {namespace} {{")
    lines.append("    use super::*;")
    for module in modules:
        if not (generated / "synapse" / namespace / f"{module}.rs").exists():
            continue
        lines.append(f"    mod {module};")
        lines.append(f"    pub use self::{module}::*;")
    lines.append(f"  }} // {namespace}")
lines.append("} // synapse")
lines.append("")

(generated / "mod.rs").write_text("\n".join(lines))
PY

python3 "${repo_root}/scripts/convert_fbs.py" "${schema_dir}" \
  --output "${repo_root}/ros" \
  --ros-package synapse_msgs \
  --clean
