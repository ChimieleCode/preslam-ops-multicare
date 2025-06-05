import argparse

from pathlib import Path
from multiprocessing import Pool

import src.scripts as scr
import src.analysis_definition as analyze
import src.hdf5_exporter as exhdf5
import src.utils as util
import model.paths as pth

# Import config data
import model.config as config
 
cfg: config.MNINTConfig
cfg = util.import_configuration(config.CONFIG_PATH, object_hook=config.MNINTConfig)


CLOUD_HDF5_OUTPUT_PATH: Path = Path('./output/cloud_data.hdf5')


# Picklable function TH
def run_time_history(time_history) -> bool:
    """This function performs a single TH"""
    frame = scr.import_frame_data(**frame_paths)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    structure_periods = analyze.run_modal_analysis(frame)
    status = analyze.run_time_history_analysis(
        frame=frame,
        time_history_analysis=time_history,
        structure_periods=structure_periods
    )
    # returns if the analysis Failed
    return status


def main(
    frame_path: Path,
    timber_path: Path,
    steel_path: Path,
    tendon_path: Path,
    th_options_path: Path,
    th_folder_path: Path,
    output_folder_path: Path
):
    # Define some global variables
    global frame_paths
    frame_paths = dict(
        frame_path=frame_path,
        timber_path=timber_path,
        steel_path=steel_path,
        tendon_path=tendon_path
    )

    frame = scr.import_frame_data(**frame_paths)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    scr.print_model(pth.MODEL_OUTPUT_PATH)
    scr.export_limit_states(frame, pth.LIMIT_STATE_GAP_VALUES)

    # Modal analysis is run if a TH is also performed
    if cfg.analysis.run_modal or cfg.analysis.run_timehistory or cfg.analysis.run_IDA:
        structure_periods = analyze.run_modal_analysis(frame)
        print(structure_periods)


    # TIME HISTORY MULTI PROCESSING
    if cfg.analysis.run_timehistory:
        timehistory_analyses = scr.import_time_history_analysis(th_options_path)
        util.clean_directory(pth.OUTPUT_TH_DIR_PATH)

        with Pool(processes=cfg.performance_options.processes) as pool:
            state = pool.map(run_time_history, timehistory_analyses)
            # Status output
            util.export_to_json(
                filepath=output_folder_path / 'status.json',
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

        # Elaborate csvs for fema pact
        # todo


def parse_args():
    parser = argparse.ArgumentParser(description="Run time history analysis with specified input files and options.")
    parser.add_argument('-frame', dest='frame_input_path', required=True, help='Path to frame input file')
    parser.add_argument('-timber', dest='timber_input_path', required=True, help='Path to timber input file')
    parser.add_argument('-steel', dest='steel_input_path', required=True, help='Path to steel input file')
    parser.add_argument('-tendon', dest='tendon_input_path', required=True, help='Path to tendon input file')
    parser.add_argument('-th-options', dest='th_options', required=True, help='Path to time history input options')
    parser.add_argument('-th-folder', dest='th_folder', required=True, help='Path to time history input folder')
    parser.add_argument('-output', dest='output_path', required=True, help='Path to output directory')
    return parser.parse_args()


# Profile Mode
if __name__ == '__main__':

    args = parse_args()

    main(
        frame_path=Path(args.frame_input_path),
        timber_path=Path(args.timber_input_path),
        steel_path=Path(args.steel_input_path),
        tendon_path=Path(args.tendon_input_path),
        th_options_path=Path(args.th_options),
        th_folder_path=Path(args.th_folder),
        output_folder_path=Path(args.output_path)
    )
