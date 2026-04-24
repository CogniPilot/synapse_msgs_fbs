# Generated from fbs/synapse/synapse_log.fbs by scripts/convert_fbs.py.
# Do not edit by hand.

uint8 NONE=0
uint8 SCHEMA_RECORD=1
uint8 FLIGHT_SNAPSHOT_RECORD=2
uint8 MOTOR_OUTPUT_RECORD=3
uint8 MOCAP_DEFINITION_RECORD=4
uint8 MOCAP_FRAME_RECORD=5
uint8 type
SchemaRecord schema_record
FlightSnapshotRecord flight_snapshot_record
MotorOutputRecord motor_output_record
MocapDefinitionRecord mocap_definition_record
MocapFrameRecord mocap_frame_record
