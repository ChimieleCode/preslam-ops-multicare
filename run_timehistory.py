import argparse

from pathlib import Path
from multiprocessing import Pool
import os
from functools import partial

import src.scripts as scr
import src.analysis_definition as analyze
import src.hdf5_exporter as exhdf5
import src.utils as util
import model.paths as pth

from run_modal import main_modal


CLOUD_HDF5_OUTPUT_PATH: Path = Path('./output/cloud_data.hdf5')


# Picklable function TH
def run_time_history(frame_paths, waveform_folder, time_history) -> bool:
    """This function performs a single TH"""
    frame = scr.import_frame_data(**frame_paths)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    structure_periods = analyze.run_modal_analysis(frame)
    status = analyze.run_time_history_analysis(
        frame=frame,
        time_history_analysis=time_history,
        structure_periods=structure_periods,
        waveform_folder=waveform_folder
    )
    # returns if the analysis Failed
    return status


def main_time_history(
    frame_paths: dict[str, Path],
    th_options_path: Path,
    waveform_folder: Path
):
    main_modal(frame_paths)

    # Run time histories analyses
    timehistory_analyses = scr.import_time_history_analysis(th_options_path)
    util.clean_directory(pth.OUTPUT_TH_DIR_PATH)

    num_cpus = os.cpu_count() or 1
    with Pool(processes=max(1, num_cpus - 1)) as pool:
        state = pool.map(partial(run_time_history, frame_paths, waveform_folder), timehistory_analyses)
        # Status output
        util.export_to_json(
            filepath=pth.OUTPUT_TH_DIR_PATH / 'status.json',
            data=dict(
                zip(
                    range(1, len(state) + 1),
                    state
                )
            )
        )

    # Export TH
    exhdf5.export_CLOUD_to_HDF5(
        time_history_folder=pth.OUTPUT_TH_DIR_PATH,
        hdf5_save_path=CLOUD_HDF5_OUTPUT_PATH,
        time_history_input_data=th_options_path
    )


def parse_args():
    parser = argparse.ArgumentParser(description="Run time history analysis with specified input files and options.")
    parser.add_argument('-frame', dest='frame_input_path', required=True, help='Path to frame input file')
    parser.add_argument('-timber', dest='timber_input_path', required=True, help='Path to timber input file')
    parser.add_argument('-steel', dest='steel_input_path', required=True, help='Path to steel input file')
    parser.add_argument('-tendon', dest='tendon_input_path', required=True, help='Path to tendon input file')
    parser.add_argument('-th', dest='th_options', required=True, help='Path to time history input options')
    parser.add_argument('-waveforms', dest='waveform_folder', required=True, help='Path to waveform input directory')
    return parser.parse_args()


if __name__ == '__main__':

    args = parse_args()
    
    frame_paths = dict(
        frame_path=Path(args.frame_input_path),
        timber_path=Path(args.timber_input_path),
        steel_path=Path(args.steel_input_path),
        tendon_path=Path(args.tendon_input_path)
    )

    main_time_history(
        frame_paths=frame_paths,
        th_options_path=Path(args.th_options),
        waveform_folder=Path(args.waveform_folder)
    )
