#!/usr/bin/env python
from ebike.benchmark import Benchmark
from ebike.ik import KDL, BioIK, PickIK, TracIK
from ebike.robot import UR10
from ebike.scenario import Random

if __name__ == "__main__":
    benchmark = Benchmark(interactive=True)
    benchmark.add_ik(KDL())
    benchmark.add_ik(TracIK())
    benchmark.add_ik(PickIK())
    benchmark.add_ik(BioIK())
    benchmark.add_scenario(Random())
    benchmark.add_robot(UR10())
    benchmark.run()
    benchmark.print()
    benchmark.plot()
