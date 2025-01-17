#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode


def main():
    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE)
    hyrise_build_config.prepare()
    tpch_config = HyriseTPCHConfig(time=10, warmup=0, cores=8, clients=8, scheduler=True, scale_factor=5,
                                   output_file="exp-11-results-sgx.json")

    gramine_build_config = GramineBuildConfig(build_mode=BuildMode.RELDBG)
    gramine_build_config.prepare()

    gramine_experiment_config = GramineExperimentConfig(stats=True, profile=True, optimize=True, debug=0,
                                                        mode=GramineMode.SGX)
    experiment_config_sgx = ExperimentConfig(numa_pin=0, mode=ExperimentMode.SGX,
                                             hyrise_build_config=hyrise_build_config,
                                             gramine_build_config=gramine_build_config,
                                             gramine_experiment_config=gramine_experiment_config,
                                             tpch_config=tpch_config)
    experiment_config_sgx.run()


if __name__ == '__main__':
    main()
