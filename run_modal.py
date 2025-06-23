import argparse

from pathlib import Path

import pandas as pd

import src.scripts as scr
import src.analysis_definition as analyze
import model.paths as pth


def main_modal(frame_paths: dict[str, Path]):
    
    frame = scr.import_frame_data(**frame_paths)
    scr.compute_moment_rotation(frame)
    scr.build_opensees_model(frame)
    scr.print_model(pth.MODEL_OUTPUT_PATH)
    scr.export_limit_states(frame, pth.LIMIT_STATE_GAP_VALUES)

    structure_periods = analyze.run_modal_analysis(frame, True)
    print(structure_periods)


def parse_args():
    parser = argparse.ArgumentParser(description="Run time history analysis with specified input files and options.")
    parser.add_argument('-frame', dest='frame_input_path', required=True, help='Path to frame input file')
    parser.add_argument('-timber', dest='timber_input_path', required=True, help='Path to timber input file')
    parser.add_argument('-steel', dest='steel_input_path', required=True, help='Path to steel input file')
    parser.add_argument('-tendon', dest='tendon_input_path', required=True, help='Path to tendon input file')
    return parser.parse_args()


# Profile Mode
if __name__ == '__main__':

    args = parse_args()

    frame_paths = dict(
        frame_path=Path(args.frame_input_path),
        timber_path=Path(args.timber_input_path),
        steel_path=Path(args.steel_input_path),
        tendon_path=Path(args.tendon_input_path)
    )

    main_modal(frame_paths)
