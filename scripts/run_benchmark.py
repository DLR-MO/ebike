#!/usr/bin/env python
from ebike.benchmark import Benchmark
from ebike.ik import KDL, TracIK, PickIK, BioIK
from ebike.scenario import Table, Kallax, SmallTable
from ebike.robot import UR10

if __name__ == '__main__':
    benchmark = Benchmark(interactive=False)
    benchmark.add_ik(KDL())
    benchmark.add_ik(TracIK())
    benchmark.add_ik(PickIK())
    benchmark.add_ik(BioIK())
    benchmark.add_scenario(SmallTable())
    benchmark.add_scenario(Table())
    benchmark.add_scenario(Kallax())
    benchmark.add_robot(UR10())
    benchmark.run()
    benchmark.plot()
