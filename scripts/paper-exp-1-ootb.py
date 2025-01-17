#!/usr/bin/env python3
from dataclasses import replace
import random

from helpers.experiment import GramineBuildConfig, ExperimentConfig, HyriseTPCHConfig, BuildMode, HyriseBuildConfig, \
    GramineExperimentConfig, ExperimentMode, GramineMode, announce_experiment


def main():
    announce_experiment("Paper Experiment 1: OOTB Performance")
    c = "paper-exp-1-results"

    gramine_build_config = GramineBuildConfig(build_mode=BuildMode.RELEASE)
    hyrise_build_config = HyriseBuildConfig()
    gramine_run_config = GramineExperimentConfig(mode=GramineMode.SGX, optimize=False)
    tpch_config = HyriseTPCHConfig(scale_factor=5, warmup=0, time=10, scheduler=True, clients=8, cores=8)

    gramine_build_config.prepare()
    hyrise_build_config.prepare()

    plain = ExperimentConfig(numa_pin=0, mode=ExperimentMode.PLAIN,
                             hyrise_build_config=hyrise_build_config,
                             tpch_config=replace(tpch_config, output_file="paper-exp-1-results-plain.json"))
    sgx = ExperimentConfig(numa_pin=0, mode=ExperimentMode.SGX,
                           gramine_build_config=gramine_build_config,
                           hyrise_build_config=hyrise_build_config,
                           gramine_experiment_config=gramine_run_config,
                           tpch_config=replace(tpch_config, output_file="paper-exp-1-results-sgx.json"))


    for config, desc in [(plain, "plain"),
                         (sgx, "sgx")
                        ]:
        for i in range(10):
            config.tpch_config.output_file = f"{c}-{desc}-{i}.json"
            config.run()


if __name__ == '__main__':
    main()
