import argparse
import csv
import h5py

import numpy as np
import numpy.typing as npt

from pathlib import Path

import src.utils as util

from run_timehistory import main_time_history, CLOUD_HDF5_OUTPUT_PATH


def main_msa(
    frame_paths: dict[str, Path],
    th_options_path: Path,
    intensities_msa_path: Path,
    waveform_folder: Path,
    output_path: Path
):
    main_time_history(
        frame_paths,
        th_options_path,
        waveform_folder
    )

    # Import the intensities metadata
    intenisty_dct = util.import_from_json(intensities_msa_path)

    # floor height
    floor_height = util.import_from_json(frame_paths['frame_path'])['storey_height']

    export_fema_edps(CLOUD_HDF5_OUTPUT_PATH, intenisty_dct, output_path, floor_height)


def export_fema_edps(hdf5_path: Path, 
                     intenisty_dct: dict, 
                     output_path: Path, 
                     floor_height: float):
    """
    Exports the EDPs from the time history analyses to a FEMA format CSV file.
    :param intenisty_dct: Dictionary containing the intensity data.
    :param hdf5_path: Path to the HDF5 file containing the time history results.
    :param floor_height: Height of each floor in meters.
    :param output_path: Path to the output CSV file.
    """
    # Header
    csv_body: list[list] = []
    csv_body.append(['Non-Linear'])

    # Header first part 
    csv_body.append(['Intensity #', 'Name', '# Demand Vectors', 'Modeling Dispersion', 'SA(T)', 'SA(T1)', 'MAFE'])

    # Body first part
    # need to read T1
    T1 = 1
    for i, (intensity, sa_t1, mafe) in enumerate(zip(intenisty_dct['intensities'], intenisty_dct['SaT1'], intenisty_dct['mafe']), start=1):
        csv_body.append(
            [
                i,
                intensity,
                intenisty_dct['cases'],
                intenisty_dct['modeling_dispersion'],
                sa_t1,
                T1,
                mafe
            ]
        )

    # Add an empty line
    csv_body.append([])

    # Header second part
    base_header = ['Intensity #', 'Demand Type', 'Floor', 'Dir']
    dynamic_header = [f'EQ{i}' for i in range(1, intenisty_dct['cases'] + 1)]
    csv_body.append(base_header + dynamic_header)

    # Body second part
    for i, th_ids in enumerate(intenisty_dct['map'], start=1):

        # Get the EDPs from the HDF5 file
        edp_dct = compute_edp_from_hdf5(
            hdf5_path=hdf5_path,
            th_ids=th_ids,
            floor_height=floor_height
        )
        # Storey Drift Ratio and Accelerations
        for key in ['Story Drift Ratio', 'Acceleration']:
            for floor, edps in enumerate(edp_dct[key], start=1):
                for dir_ in [1, 2]:  # Assuming dir 1 and 2 for two horizontal directions
                    csv_body.append(
                        [i, key, floor, dir_] + edps.tolist()
                    )

        # Residual Drift Ratio
        csv_body.append(
            [i, 'Residual Drift', '', ''] + edp_dct['Residual Drift']
        )
    
    # Write to CSV file
    with open(output_path, 'w', newline='') as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerows(csv_body)
    

def get_idr_from_hdf5(hdf5_path: Path, group_name: str, floor_height: float) -> tuple[npt.NDArray, float]:
    """
    Extracts inter-story drift ratios (IDRs) from an HDF5 file.
    :param hdf5_path: Path to the HDF5 file.
    :param group_name: Name of the group in the HDF5 file containing the displacements.
    :param floor_height: Height of each floor in meters.
    :return: A tuple containing the maximum IDRs for each floor and the last IDR (residual drift ratio).
    """
    G = 9.81  # Acceleration due to gravity in m/s^2

    with h5py.File(hdf5_path, 'r') as f:
        group = f[group_name]
        # Drop first column which is time
        disps = group['displacements'][:, 1:]

    # Calculate the delta displacement between floors
    delta_disp = np.diff(disps, axis=1)

    # Compute idrs
    idrs = np.abs(delta_disp) / floor_height

    # Compute the maximum idrs
    max_idrs = np.max(idrs, axis=0)

    # Compute last idrs (residual drift ratio)
    last_idrs = np.max(idrs[-1, :])

    return max_idrs, last_idrs


def get_acc_from_hdf5(hdf5_path: Path, group_name: str) -> npt.NDArray:
    """
    Retrieves all acceleration values from the 'accelerations' table in the specified group of an HDF5 file.
    :param hdf5_path: Path to the HDF5 file.
    :param group_name: Name of the group in the HDF5 file containing the accelerations.
    :return: A NumPy array containing the acceleration values.
    """
    G = 9.81  # Acceleration due to gravity in m/s^2

    with h5py.File(hdf5_path, 'r') as f:
        group = f[group_name]
        # Drop first column which is time
        accs = group['accelerations'][:, 1:]

        time_series = group['time_series'][:]

    # Add time series to the accelerations to have absolute ones
    # Make the time series to a broadcastable shape
    pad_width = accs.shape[0] - time_series.shape[0]
    time_series = np.pad(time_series, (0, pad_width), mode='constant')
    # Get absolute accelerations
    abs_accs = np.abs(accs + time_series[:, np.newaxis])

    # Compute max accelerations
    max_accs = np.max(abs_accs, axis=0)

    # Make sure to convert to g's
    max_accs_g = max_accs / G

    return max_accs_g



def compute_edp_from_hdf5(hdf5_path: Path, th_ids: list[int], floor_height: float) -> dict[str, list]:
    groups = [f'TH_{th_id:04d}' for th_id in th_ids]

    # Get edps fro  hdf5
    accs = [
    get_acc_from_hdf5(hdf5_path, group) for group in groups
    ]
    idrs, last_idrs = zip(*list(get_idr_from_hdf5(hdf5_path, group, floor_height=floor_height) for group in groups))

    # Create a dictionary to hold the EDPs
    edp_dct = {
        'Story Drift Ratio': list(np.array(idrs).T),
        'Acceleration': list(np.array(accs).T),
        'Residual Drift': list(last_idrs),
    }

    return edp_dct
        
        

def parse_args():
    parser = argparse.ArgumentParser(description="Run time history analysis with specified input files and options.")
    parser.add_argument('-frame', dest='frame_input_path', required=True, help='Path to frame input file')
    parser.add_argument('-timber', dest='timber_input_path', required=True, help='Path to timber input file')
    parser.add_argument('-steel', dest='steel_input_path', required=True, help='Path to steel input file')
    parser.add_argument('-tendon', dest='tendon_input_path', required=True, help='Path to tendon input file')
    parser.add_argument('-th', dest='th_options', required=True, help='Path to time history input options')
    parser.add_argument('-waveforms', dest='waveform_folder', required=True, help='Path to waveform input directory')
    parser.add_argument('-intensities', dest='intensities_msa', required=True, help='Path to the instensities data to perform multiple stripe')
    parser.add_argument('-output', dest='output_path', required=True, help='Path to output fema file')
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()

    frame_paths = dict(
        frame_path=Path(args.frame_input_path),
        timber_path=Path(args.timber_input_path),
        steel_path=Path(args.steel_input_path),
        tendon_path=Path(args.tendon_input_path)
    )

    main_msa(
        frame_paths=frame_paths,
        th_options_path=Path(args.th_options),
        intensities_msa_path=Path(args.intensities_msa),
        waveform_folder=Path(args.waveform_folder),
        output_path=Path(args.output_path)
    )
