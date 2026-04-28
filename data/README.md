# Data

This folder contains the collected VibeChecker sensor datasets used for offline analysis and model/rule validation.

## Data Collection Context

VibeChecker collected environmental sensor readings from M5Stack Core2 devices across different location types, including:

- Cafe
- Library
- Club

Each dataset captures real-time environmental readings used to classify the “vibe” of a location.

## Data Fields

Typical fields include:

- `device_id`
- `location_id`
- `timestamp`
- `noise_db`
- `temperature`
- `light`
- `label` or `vibe`

## Dataset Usage

The collected CSV files were used to:

- Validate sensor readings
- Compare environmental patterns across locations
- Tune classification thresholds
- Evaluate VibeChecker’s rule-based classification logic
- Support dashboard visualization

## Notes

- Raw collected CSV files are included for transparency and reproducibility.
- Wi-Fi credentials and device-specific secrets are not included.
- Any generated or temporary files should be excluded from version control.