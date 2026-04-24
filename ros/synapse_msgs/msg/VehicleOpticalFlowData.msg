# Generated from fbs/synapse/synapse_optical_flow.fbs by scripts/convert_fbs.py.
# Do not edit by hand.

int64 timestamp_us
Vec2f pixel_flow
Vec3f delta_angle
float32 distance_m
uint32 integration_timespan_us
uint8 quality
float32 max_flow_rate
float32 min_ground_distance
float32 max_ground_distance
