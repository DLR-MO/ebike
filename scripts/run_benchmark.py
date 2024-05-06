#!/usr/bin/env python
from ebike.benchmark import Benchmark
from ebike.ik import KDL
from ebike.robot import UR10
from ebike.scenario import Barrel

if __name__ == "__main__":
    benchmark = Benchmark(interactive=True)
    benchmark.add_ik(KDL())
    benchmark.add_scenario(Barrel())
    benchmark.add_robot(UR10())
    benchmark.run()
    benchmark.plot()
