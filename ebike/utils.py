# SPDX-License-Identifier: MIT
import os.path
import sqlite3
import subprocess

import pandas as pd


def get_xacro(xacro_file, xacro_args=None):
    if xacro_args is None:
        cmd_args = []
    else:
        cmd_args = [f"{k}:={v}" for k, v in xacro_args.items()]
    return subprocess.check_output(
        ["xacro", xacro_file] + cmd_args, universal_newlines=True
    )


def result_to_df(result):
    df = pd.DataFrame()
    df["reached"] = [d.reached for d in result]
    df["ik_time"] = [d.ik_time for d in result]
    return df


def ensure_db_exists():
    if not os.path.exists("results.db"):
        with sqlite3.connect("results.db") as conn:
            cur = conn.cursor()
            sql = "CREATE TABLE experiments (id integer primary key, robot varchar(255), scenario varchar(255), solver varchar(255), time text)"
            cur.execute(sql)
            sql = "CREATE TABLE results (id integer primary key, experiment_id integer references experiments(id), reached integer, ik_time REAL)"
            cur.execute(sql)
            conn.commit()


def save_result(robot, scenario, solver, start_time, result):
    ensure_db_exists()
    with sqlite3.connect("results.db") as conn:
        cur = conn.cursor()
        sql = "INSERT INTO experiments (robot, scenario, solver, time) VALUES (?, ?, ?, ?)"
        cur.execute(
            sql, (robot, scenario, solver, start_time.isoformat(" ", "milliseconds"))
        )
        conn.commit()
        experiment_id = cur.lastrowid
        for d in result[0]:
            sql = (
                "INSERT INTO results (experiment_id, reached, ik_time) VALUES (?, ?, ?)"
            )
            cur.execute(sql, (experiment_id, d.reached, d.ik_time))
        conn.commit()
