#coding=utf-8

import argparse
import time

import logger

def main():
    parser = argparse.ArgumentParser(description="process some interger about the miner os program")
    parser.add_argument("--command_interval", type=int, default=5, help="interval between command loop resquest(second)")
    parser.add_argument("--report_interval", type=int, default=15, help="interval between report requests( second )")
    parser.add_argument("--log_scan_interval", type=int, default=30, help="interval between log scan and upload requests (second)")
    parser.add_argument("--miner_interval", type=int, default=10, help="interval between miner requests (second)")
    args = parser.parse_args()

    time.sleep(5)
    # client collector


