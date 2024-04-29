# SPDX-License-Identifier: MIT

import subprocess
import pandas as pd


def get_xacro(xacro_file, xacro_args=None):
    if xacro_args is None:
        cmd_args = []
    else:
        cmd_args = [f"{k}:={v}" for k, v in xacro_args.items()]
    return subprocess.check_output(['xacro', xacro_file] + cmd_args, universal_newlines=True)


def result_to_df(result):
    df = pd.DataFrame()
    df['reached'] = [d.reached for d in result]
    df['ik_time'] = [d.ik_time for d in result]
    return df