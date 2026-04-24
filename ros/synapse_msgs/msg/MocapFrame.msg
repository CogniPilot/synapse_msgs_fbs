# Generated from fbs/synapse/synapse_mocap.fbs by scripts/convert_fbs.py.
# Do not edit by hand.

uint64 timestamp_us
uint32 frame_number
MocapMarkerSample[] labeled_markers
MocapMarkerSample[] unlabeled_markers
MocapRigidBodySample[] rigid_bodies
MocapSegmentSample[] skeleton_segments
