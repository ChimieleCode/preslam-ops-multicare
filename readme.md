# preslam-ops-multicare

This project provides main access points for running structural analysis simulations, including command-line interfaces for modal and time history analyses.

## Access Points

### 1. `run_modal` (Command-Line Interface)
- **Purpose:** Runs modal analysis and exports model/limit state data using specified input files.
- **Usage:**  
    ```bash
    python your_script.py \
      -frame path/to/frame.json \
      -timber path/to/timber.json \
      -steel path/to/steel.json \
      -tendon path/to/tendon.json
    ```
- **Arguments:**
    - `-frame`: Path to frame input file (required)
    - `-timber`: Path to timber input file (required)
    - `-steel`: Path to steel input file (required)
    - `-tendon`: Path to tendon input file (required, see example below)
- **Description:**  
    This entry point runs a modal analysis, builds the OpenSees model, exports limit states, and prints the structure periods. It uses `argparse` for argument parsing and relies on utility functions and modules for processing.

### 2. `run_timehistory` (Command-Line Interface)
- **Purpose:** Runs time history analysis using specified input files and waveform data.
- **Usage:**  
    ```bash
    python your_script.py \
      -frame path/to/frame.json \
      -timber path/to/timber.json \
      -steel path/to/steel.json \
      -tendon path/to/tendon.json \
      -th path/to/th_options.json \
      -waveforms path/to/waveform_folder
    ```
- **Arguments:**
    - `-frame`: Path to frame input file (required)
    - `-timber`: Path to timber input file (required)
    - `-steel`: Path to steel input file (required)
    - `-tendon`: Path to tendon input file (required, see example below)
    - `-th`: Path to time history input options (required)
    - `-waveforms`: Path to waveform input directory (required)
- **Description:**  
    This entry point runs a modal analysis, then performs time history analyses in parallel using multiprocessing. Results are exported to HDF5 and JSON.

### 3. `run_fema` (Command-Line Interface)
- **Purpose:** Runs multiple stripe analysis (MSA) by performing time history analyses at different intensity levels and exports FEMA EDPs.
- **Usage:**  
    ```bash
    python your_script.py \
      -frame path/to/frame.json \
      -timber path/to/timber.json \
      -steel path/to/steel.json \
      -tendon path/to/tendon.json \
      -th path/to/th_options.json \
      -waveforms path/to/waveform_folder \
      -intensities path/to/intensities.json \
      -output path/to/output_fema.json
    ```
- **Arguments:**
    - `-frame`: Path to frame input file (required)
    - `-timber`: Path to timber input file (required)
    - `-steel`: Path to steel input file (required)
    - `-tendon`: Path to tendon input file (required, see example below)
    - `-th`: Path to time history input options (required)
    - `-waveforms`: Path to waveform input directory (required)
    - `-intensities`: Path to intensities data for multiple stripe analysis (required)
    - `-output`: Path to output FEMA file (required)
- **Description:**  
    This entry point runs time history analyses for multiple intensity levels (MSA), imports intensity metadata, computes floor heights, and exports FEMA engineering demand parameters (EDPs) to the specified output file.

## Getting Started

1. Install dependencies as specified in `requirements.txt`.
2. For CLI usage, run the script with the required arguments as shown above.
3. For Python API usage, import the desired function(s) in your script.
4. Prepare the required input parameters.
5. Call the function to perform the analysis.
## Input File Structure and Assembly

All analysis commands require several input files in JSON format. Each file describes a specific component of the structural model. The required files are:

- `frame.json`: Describes the frame geometry and properties.
- `timber.json`: Contains timber element definitions.
- `steel.json`: Contains steel element definitions.
- `tendon.json`: Contains tendon properties (see example below).
- `th_options.json`: (For time history analysis) Specifies time history analysis options.
- `intensities.json`: (For FEMA/MSA) Lists intensity levels for analysis.
- Waveform files: Directory containing ground motion records.

### Example Directory Structure

```
project_folder/
├── frame.json
├── timber.json
├── steel.json
├── tendon.json
├── th_options.json
├── intensities.json
└── waveforms/
    ├── record1.txt
    ├── record2.txt
    └── ...
```

## Input File Examples

Below are example structures for each required input file. Customize these files with parameters relevant to your project.

### `frame.json`

The `frame.json` file defines the main geometric and physical properties of the structural frame. Each key and its unit are described below:

- **masses** (`[tons]`): List of lumped masses for each storey.
- **storey_height** (`[m]`): Height of each storey.
- **span_length** (`[m]`): Length of each span between columns.
- **n_storeys** (`[integer]`): Number of storeys in the frame.
- **n_spans** (`[integer]`): Number of spans in the frame.
- **n_frames** (`[integer]`): Number of frames in the structure.
- **sections** (`[object]`): Contains definitions for columns and beams:
    - **internal_column** / **external_column**:
        - **n_tendons** (`[integer]`): Number of tendons in the column.
        - **tendons_pt** (`[kN]`): Prestressing force from tendons.
        - **axial_load** (`[kN]`): Axial load applied to the column.
        - **top_reinforcement_depth** (`[m]`): Depth of top reinforcement from the top fiber, negative means external.
        - **b** (`[m]`): Width of the column section.
        - **h** (`[m]`): Height of the column section.
        - **connection_stiffness_ratio** (`[ratio]`): Ratio of connection stiffness to member stiffness.
        - **reinforcement_diameter** (`[mm]`): Diameter of reinforcement bars.
        - **reinforcement_count** (`[integer]`): Number of reinforcement bars.
        - **lambda_bar** (`[unitless]`): Slenderness parameter for the external damping devices.
    - **beams** (`[array of objects]`): Each beam section includes:
        - **n_tendons** (`[integer]`): Number of tendons in the beam.
        - **tendons_pt** (`[kN]`): Prestressing force from tendons.
        - **axial_load** (`[kN]`): Axial load applied to the beam.
        - **top_reinforcement_depth** (`[m]`): Depth of top reinforcement from the top fiber.
        - **b** (`[m]`): Width of the beam section.
        - **h** (`[m]`): Height of the beam section.
        - **connection_stiffness_ratio** (`[ratio]`): Ratio of connection stiffness to member stiffness.
        - **reinforcement_diameter** (`[mm]`): Diameter of reinforcement bars.
        - **reinforcement_count** (`[integer]`): Number of reinforcement bars.
        - **lambda_bar** (`[unitless]`): Slenderness parameter for the external damping devices.

This file provides all necessary frame-level data for analysis and model assembly.

```json
{
    "masses": [772, 772, 536],
    "storey_height": 3.6,
    "span_length": 6.5,
    "n_storeys": 3,
    "n_spans": 6,
    "n_frames": 4,
    "sections": {
        "internal_column": {
            "n_tendons": 0,
            "tendons_pt": 0,
            "axial_load": 587,
            "top_reinforcement_depth": -0.065,
            "b": 0.6,
            "h": 0.7,
            "connection_stiffness_ratio": 0.55,
            "reinforcement_diameter": 20,
            "reinforcement_count": 2,
            "lambda_bar": 60
        },
        "external_column": {
            "n_tendons": 0,
            "tendons_pt": 0,
            "axial_load": 338,
            "top_reinforcement_depth": -0.065,
            "b": 0.6,
            "h": 0.7,
            "connection_stiffness_ratio": 0.55,
            "reinforcement_diameter": 20,
            "reinforcement_count": 2,
            "lambda_bar": 60
        },
        "beams": [
            {
                "n_tendons": 6,
                "tendons_pt": 900,
                "axial_load": 0,
                "top_reinforcement_depth": -0.065,
                "b": 0.4,
                "h": 0.7,
                "connection_stiffness_ratio": 0.7,
                "reinforcement_diameter": 16,
                "reinforcement_count": 2,
                "lambda_bar": 60
            },
            {
                "n_tendons": 5,
                "tendons_pt": 750,
                "axial_load": 0,
                "top_reinforcement_depth": -0.065,
                "b": 0.4,
                "h": 0.7,
                "connection_stiffness_ratio": 0.7,
                "reinforcement_diameter": 16,
                "reinforcement_count": 2,
                "lambda_bar": 60
            },
            {
                "n_tendons": 4,
                "tendons_pt": 450,
                "axial_load": 0,
                "top_reinforcement_depth": -0.065,
                "b": 0.4,
                "h": 0.7,
                "connection_stiffness_ratio": 0.7,
                "reinforcement_diameter": 16,
                "reinforcement_count": 2,
                "lambda_bar": 60
            }
        ]
    }
}
```
Defines the frame with 3 storeys, 6 spans, and 4 frames. Specifies storey masses, storey height, and span length. The `sections` object details internal and external column properties (geometry, reinforcement, connection stiffness, and axial loads) and a list of beam sections with their tendon counts, prestressing, reinforcement, and geometry.

### `timber.json`

The `timber.json` file defines the material properties for timber elements. Each key and its unit are described below:

- **id** (`[string]`): Identifier for the timber material or section.
- **fc** (`[kPa]`): Compressive strength of the timber.
- **E** (`[kPa]`): Modulus of elasticity (parallel to grain).
- **G** (`[kPa]`): Shear modulus.
- **Eperp** (`[kPa]`): Modulus of elasticity perpendicular to grain.

This file specifies the fundamental mechanical properties required for timber analysis and modeling.

```json
{
    "id": "LVL44",
    "fc": 44000,
    "E": 13800000,
    "G": 600000,
    "Eperp": 430000
}
```
Defines timber elements and their properties. The `elements` array lists each timber component, specifying its ID, type (e.g., beam), associated material, cross-sectional dimensions (width, height in meters), and 3D location (x, y, z in meters). The `materials` array defines the mechanical properties for each timber material used, such as compressive strength (`fc` in kPa), modulus of elasticity (`E` in kPa), shear modulus (`G` in kPa), and modulus of elasticity perpendicular to grain (`Eperp` in kPa).

This structure is analogous to the `frame.json` format, where each element is described with its geometry, material, and position, and material properties are defined separately for clarity and reuse.

### `steel.json`

The `steel.json` file defines the material properties for steel elements. Each key and its unit are described below:

- **id** (`[string]`): Identifier for the steel material or section.
- **fy** (`[kPa]`): Yield strength of the steel.
- **fu** (`[kPa]`): Ultimate strength of the steel.
- **E** (`[kPa]`): Modulus of elasticity.
- **epsilon_u** (`[unitless]`): Ultimate strain.

This file specifies the fundamental mechanical properties required for steel analysis and modeling.

```json
{
    "id": "S355",
    "fy": 355000,
    "fu": 510000,
    "E": 210000000,
    "epsilon_u": 0.06
}
```
Lists steel elements, sections, materials, and positions.

### `tendon.json`

The `tendon.json` file defines the material and geometric properties for tendon elements. Each key and its unit are described below:

- **id** (`[string]`): Identifier for the tendon material or section.
- **fy** (`[kPa]`): Yield strength of the tendon.
- **fu** (`[kPa]`): Ultimate strength of the tendon.
- **E** (`[kPa]`): Modulus of elasticity.
- **A** (`[m²]`): Cross-sectional area of the tendon.
- **epsilon_u** (`[unitless]`): Ultimate strain.

This file specifies the fundamental mechanical and geometric properties required for tendon analysis and modeling.

```json
{
    "id": "ArMi-NTC2008-6super",
    "fy": 1670000,
    "fu": 1860000,
    "E": 201000000,
    "A": 0.00015,
    "epsilon_u": 0.01
}
```
Describes tendon properties, prestress levels, and anchorage details.

### `th_options.json`

The `th_options.json` file defines the configuration for nonlinear time history (NLTH) analysis cases. Each key and its unit are described below:

- **NLTHCases** (`[array of objects]`): List of time history analysis cases, each with:
    - **id** (`[integer]`): Unique identifier for the analysis case.
    - **time_step_ratio** (`[float]`): Ratio to adjust the base time step (unitless).
    - **scale_factor** (`[float]`): Scaling factor applied to the ground motion record (unitless).
    - **time_step** (`[seconds]`): Time increment for numerical integration.
    - **duration** (`[seconds]`): Total duration of the ground motion record.
    - **filename** (`[string]`): Name of the ground motion file to use for this case.

This file specifies the parameters for each time history analysis, allowing you to configure multiple cases with different records, durations, and scaling factors. Each entry in the `NLTHCases` array corresponds to a separate analysis scenario, referencing a specific waveform file and its associated properties.

```json
{
    "NLTHCases": [
        {
            "id": 1,
            "time_step_ratio": 1,
            "scale_factor": 1,
            "time_step": 0.01,
            "duration": 51.02,
            "filename": "acc_1.txt"
        },
        {
            "id": 2,
            "time_step_ratio": 1,
            "scale_factor": 1,
            "time_step": 0.01,
            "duration": 53.71,
            "filename": "acc_2.txt"
        },
        {
            "id": 3,
            "time_step_ratio": 1,
            "scale_factor": 1,
            "time_step": 0.01,
            "duration": 54.36,
            "filename": "acc_3.txt"
        },
        {
            "id": 4,
            "time_step_ratio": 1,
            "scale_factor": 1,
            "time_step": 0.005,
            "duration": 39.995,
            "filename": "acc_4.txt"
        }
    ]
}
```
Configures time history analysis options such as duration, time step, and damping.

### `intensities.json`
The `intensities.json` file defines the intensity levels and associated metadata for multiple stripe analysis (MSA). Each key and its unit are described below:

- **intensities** (`[array of strings or numbers]`): List of intensity level identifiers or values for each analysis stripe.
- **map** (`[array of arrays of numbers]`): Mapping matrix that associates ground motion records or analysis cases to each intensity level. The id must match one id in the time_history.json.
- **mafe** (`[array of numbers]`): Mean annual frequency of exceedance for each intensity level.
- **SaT1** (`[array of numbers]`): Spectral acceleration at the fundamental period (T1) for each intensity level.
- **cases** (`[integer]`): Number of analysis cases or stripes.
- **modeling_dispersion** (`[float]`): Modeling uncertainty or dispersion parameter (unitless). This can be obtained by the FEMA P-58 manual

This file specifies the intensity levels, their mapping to analysis cases, and relevant metadata required for FEMA/MSA analysis.

```json
{
    "intensities": [
        "Intensity 1",
        "Intensity 2"
    ],
    "map": [
        [1, 2],
        [3, 4]
    ],
    "mafe": [
        0.02,
        0.01
    ],
    "SaT1": [
        0.1,
        0.2
    ],
    "cases": 2,
    "modeling_dispersion": 0.1
}
```
Lists intensity levels for multiple stripe analysis (MSA).

### Waveform Files

Place ground motion records (e.g., `record1.txt`, `record2.txt`) in the `waveforms/` directory. **Each waveform file must be named exactly as specified in the `th_options.json` file under the `filename` field for each analysis case** (e.g., `acc_1.txt`, `acc_2.txt`, etc.).

Each file should contain a single ground motion time series: a plain text list of numerical values, each representing acceleration in meters per second squared (m/s²) at a specific time step.

Each input file should be populated with the relevant parameters for your structure. Refer to the documentation or code comments for required and optional fields for each file type.

<!--
Represents a waveform file containing a list of excitation values.

A waveform file is a data file that stores a sequence of excitation values,
where each value represents acceleration in meters per second squared (m/s²).
These values are typically used to describe the time-varying excitation applied
to a system, such as in vibration analysis or dynamic simulations.

The file format consists of a simple list of numerical values, each corresponding
to the excitation at a specific time step.
-->
