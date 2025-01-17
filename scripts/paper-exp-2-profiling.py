#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import GramineBuildConfig, ExperimentConfig, HyriseTPCHConfig, BuildMode, HyriseBuildConfig, \
    GramineExperimentConfig, ExperimentMode, GramineMode, announce_experiment


def main():
    announce_experiment("Paper Experiment 2: Profiling")

    gramine_build_config = GramineBuildConfig(build_mode=BuildMode.RELDBG)
    hyrise_build_config = HyriseBuildConfig()
    gramine_run_config = GramineExperimentConfig(mode=GramineMode.SGX, optimize=False, stats=True, profile=True)
    tpch_config = HyriseTPCHConfig(scale_factor=5, warmup=0, time=10, scheduler=True, clients=8, cores=8)

    gramine_build_config.prepare()
    hyrise_build_config.prepare()

    for i in range(10):
        sgx = ExperimentConfig(numa_pin=0, mode=ExperimentMode.SGX,
                               perf_file_name=f"paper-2-perf-{i}.data",
                               gramine_build_config=gramine_build_config,
                               hyrise_build_config=hyrise_build_config,
                               gramine_experiment_config=gramine_run_config,
                               tpch_config=replace(tpch_config, output_file=f"paper-exp-2-results-sgx-{i}.json"))

        sgx.run()


if __name__ == '__main__':
    main()
