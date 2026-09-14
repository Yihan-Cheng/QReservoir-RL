"""Hardware migration profiles for the 量池智驭 acceptance package.

These profiles make the software/hardware boundary machine-readable.  They do
not submit cloud jobs and deliberately avoid claiming access to a backend that
has not been configured by the reviewer.
"""

from __future__ import annotations

from copy import deepcopy


_PROFILES = {
    "local-density-matrix": {
        "role": "executed baseline",
        "paradigm": "gate-model density-matrix simulation",
        "status": "implemented and reproducible",
        "interface": "QuantumReservoir.step / trace",
        "evidence": ["state trajectory", "Pauli expectations", "noise-and-shots sweep"],
    },
    "originq-superconducting": {
        "role": "near-term hardware target",
        "paradigm": "superconducting gate-model quantum processor",
        "status": "adapter design and OriginIR route; hardware run pending",
        "interface": "QPanda circuit -> OriginIR -> compile -> submit -> counts",
        "acceptance_fields": [
            "backend_id", "calibration_timestamp", "logical_to_physical_map",
            "compiled_depth", "two_qubit_gate_count", "shots", "raw_counts",
        ],
    },
    "tiangong-kaiwu-cim": {
        "role": "medium-term heterogeneous extension",
        "paradigm": "photonic coherent Ising machine",
        "status": "QUBO adapter and validation protocol planned; platform run pending",
        "interface": "QUBO matrix -> Kaiwu SDK -> samples/energy -> classical verification",
        "candidate_subproblems": [
            "Pauli-observable subset selection",
            "sparse policy readout selection",
            "measurement-group and job scheduling",
        ],
        "acceptance_fields": [
            "qubo_matrix_hash", "penalty_coefficients", "solver_config",
            "sample_count", "best_energy", "feasible_rate", "wall_time",
        ],
    },
}


def backend_profile(name: str) -> dict:
    """Return a defensive copy of a declared backend profile."""
    if name not in _PROFILES:
        raise ValueError(f"Unknown backend profile: {name}")
    return deepcopy(_PROFILES[name])


def list_backend_profiles() -> dict:
    """Return all profiles for acceptance-report generation."""
    return deepcopy(_PROFILES)
