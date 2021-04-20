import sys
import argparse
import utils as automated_topology

parser = argparse.ArgumentParser(description="Associate Mininet namespace to host namespace")

parser.add_argument(
            "-s",
            "--scenario",
            type=str,
            help="run with start or stop option ",
)

args = parser.parse_args()

if args.scenario:
    if args.scenario == "start":
        automated_topology.start_topology(args.scenario)
    elif args.scenario == "stop":
        automated_topology.stop_topology(args.scenario)
    else:
        print("invalid argumment: ", args.scenario)
        print("Use start or stop argumments")
