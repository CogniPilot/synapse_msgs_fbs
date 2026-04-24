// Module root for checked-in FlatBuffers-generated Rust bindings.
pub mod synapse {
  use super::*;
  pub mod topic {
    use super::*;
    mod vec_2f_generated;
    pub use self::vec_2f_generated::*;
    mod vec_3f_generated;
    pub use self::vec_3f_generated::*;
    mod quaternionf_generated;
    pub use self::quaternionf_generated::*;
    mod rate_triplet_generated;
    pub use self::rate_triplet_generated::*;
    mod attitude_euler_generated;
    pub use self::attitude_euler_generated::*;
    mod rc_channels_16_generated;
    pub use self::rc_channels_16_generated::*;
    mod control_status_generated;
    pub use self::control_status_generated::*;
    mod motor_values_4f_generated;
    pub use self::motor_values_4f_generated::*;
    mod motor_raw_4u_16_generated;
    pub use self::motor_raw_4u_16_generated::*;
    mod flight_snapshot_generated;
    pub use self::flight_snapshot_generated::*;
    mod motor_output_generated;
    pub use self::motor_output_generated::*;
    mod vehicle_optical_flow_data_generated;
    pub use self::vehicle_optical_flow_data_generated::*;
    mod vehicle_optical_flow_generated;
    pub use self::vehicle_optical_flow_generated::*;
    mod vehicle_optical_flow_vel_data_generated;
    pub use self::vehicle_optical_flow_vel_data_generated::*;
    mod vehicle_optical_flow_vel_generated;
    pub use self::vehicle_optical_flow_vel_generated::*;
    mod mocap_marker_sample_generated;
    pub use self::mocap_marker_sample_generated::*;
    mod mocap_rigid_body_sample_generated;
    pub use self::mocap_rigid_body_sample_generated::*;
    mod mocap_segment_sample_generated;
    pub use self::mocap_segment_sample_generated::*;
    mod mocap_marker_definition_generated;
    pub use self::mocap_marker_definition_generated::*;
    mod mocap_rigid_body_definition_generated;
    pub use self::mocap_rigid_body_definition_generated::*;
    mod mocap_segment_definition_generated;
    pub use self::mocap_segment_definition_generated::*;
    mod mocap_definition_generated;
    pub use self::mocap_definition_generated::*;
    mod mocap_frame_generated;
    pub use self::mocap_frame_generated::*;
  } // topic
  pub mod log {
    use super::*;
    mod schema_record_generated;
    pub use self::schema_record_generated::*;
    mod flight_snapshot_record_generated;
    pub use self::flight_snapshot_record_generated::*;
    mod motor_output_record_generated;
    pub use self::motor_output_record_generated::*;
    mod mocap_definition_record_generated;
    pub use self::mocap_definition_record_generated::*;
    mod mocap_frame_record_generated;
    pub use self::mocap_frame_record_generated::*;
    mod record_payload_generated;
    pub use self::record_payload_generated::*;
    mod log_record_generated;
    pub use self::log_record_generated::*;
  } // log
  pub mod sil {
    use super::*;
    mod sim_input_generated;
    pub use self::sim_input_generated::*;
  } // sil
} // synapse
