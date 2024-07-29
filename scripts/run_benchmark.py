#!/usr/bin/env python
from ebike.benchmark import Benchmark
from ebike.ik import KDL, PickIK, RelaxedIK
from ebike.robot import UR10
from ebike.scenario import SmallTable

if __name__ == "__main__":
    benchmark = Benchmark(interactive=False)
    benchmark.add_ik(RelaxedIK())
    # benchmark.add_ik(BioIK())
    benchmark.add_ik(PickIK())
    benchmark.add_ik(KDL())
    benchmark.add_scenario(SmallTable())
    benchmark.add_robot(UR10())
    benchmark.run()
    benchmark.print()
    benchmark.plot()
    benchmark.save()
