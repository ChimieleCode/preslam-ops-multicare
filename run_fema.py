import argparse

from pathlib import Path

import src.utils as util

from run_timehistory import main_time_history, CLOUD_HDF5_OUTPUT_PATH
from src.fema_parser import export_fema_edps

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
