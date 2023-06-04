#!/usr/bin/env python2
import atexit
import argparse
import logging
import functools
import hashlib
import json
import os
import pickle
import shutil
import subprocess as sp
import sys
import tempfile
import time

import seed_eval as se
import pyinotify
import qsym

logger = logging.getLogger('qsym.afl')


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("-o", dest="output", required=True, help="AFL output directory")
    p.add_argument("-a", dest="afl", required=True, help="AFL name")
    p.add_argument("-t", dest="target", required=True, help="Target directory")
    p.add_argument("-n", dest="name", required=True, help="Qsym name")
    p.add_argument("-f", dest="filename", default=None)
    p.add_argument("-m", dest="mail", default=None)
    p.add_argument("-b", dest="asan_bin", default=None)
    p.add_argument("cmd", nargs="+", help="cmdline, use %s to denote a file" % qsym.utils.AT_FILE)
    return p.parse_args()


def check_args(args):
    if not os.path.exists(args.output):
        raise ValueError('no such directory')
    if not os.path.exists(args.target):
        raise ValueError('Target directory dose not exist')


def read_file(fp):
    edge_id_dict = {}
    with open(fp, "r") as f:
        listOfLines = f.readlines()
    constraints = [se.Constraint() for i in range(len(listOfLines))]
    for idx, line in enumerate(listOfLines):
        lines = line.split()
        lines = list(map(int, lines))
        constraints[idx].constraint_id = lines[0]
        constraints[idx].left_id = lines[1]
        edge_id_dict[lines[1]] = idx
        constraints[idx].right_id = lines[2]
        edge_id_dict[lines[2]] = idx
    return constraints, edge_id_dict


def main():
    args = parse_args()
    check_args(args)

    afl_dir = os.path.join(args.output, args.afl)
    afl_queue = os.path.join(afl_dir, "queue")
    branch_file = os.path.join(args.target, "branchMap.out")
    constraints, edge_id_dict = read_file(branch_file)
    evalutaion = se
    pre_seed_id = -1
    e = qsym.afl.AFLExecutor(args.cmd, args.output, args.afl,
                             args.name, args.filename, args.mail, args.asan_bin)
    while True:
        seed_queue = evalutaion.get_selected_seeds()
        cur_seed_id = seed_queue[0]['seed_id']
        if pre_seed_id == cur_seed_id:
            try:
                e.run()
            finally:
                e.cleanup()
        else:
            pre_seed_id = cur_seed_id
            for i in range(len(seed_queue)):
                index = edge_id_dict[seed_queue[i]["edge_id"]]
                constraints[index].solve_times += 1
                cur_seed_id = seed_queue[i]['seed_id']
                seed_name = evalutaion.get_seed_name(str(cur_seed_id), afl_queue)
                try:
                    e.run_file(seed_name)
                finally:
                    e.cleanup()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
