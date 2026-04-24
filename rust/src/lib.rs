//! Generated Rust bindings for the Synapse FlatBuffers schemas.
//!
//! The schema source of truth lives in `../fbs/synapse`. Regenerate this crate's
//! checked-in bindings with `../scripts/generate_bindings.sh`.

#[allow(warnings)]
pub mod generated;

pub mod topic {
    pub use crate::generated::synapse::topic::*;
}

pub mod log {
    pub use crate::generated::synapse::log::*;
}

pub mod sil {
    pub use crate::generated::synapse::sil::*;
}

pub use generated::synapse;
