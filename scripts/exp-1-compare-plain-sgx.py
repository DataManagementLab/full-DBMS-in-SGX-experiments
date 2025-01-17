#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import GramineBuildConfig, ExperimentConfig, HyriseTPCHConfig, BuildMode, HyriseBuildConfig, \
    GramineExperimentConfig, ExperimentMode, GramineMode


def main():
    gramine_build_config = GramineBuildConfig(build_mode=BuildMode.RELEASE)
    hyrise_build_config = HyriseBuildConfig()
    gramine_run_config = GramineExperimentConfig()
    tpch_config = HyriseTPCHConfig(scale_factor=1, warmup=0)

    gramine_build_config.prepare()
    hyrise_build_config.prepare()

    plain = ExperimentConfig(numa_pin=0, mode=ExperimentMode.PLAIN,
                             hyrise_build_config=hyrise_build_config,
                             tpch_config=replace(tpch_config, output_file="exp-1-results-plain.json"))
    direct = ExperimentConfig(numa_pin=0, mode=ExperimentMode.DIRECT,
                              gramine_build_config=gramine_build_config,
                              hyrise_build_config=hyrise_build_config,
                              gramine_experiment_config=gramine_run_config,
                              tpch_config=replace(tpch_config, output_file="exp-1-results-direct.json"))
    sgx = ExperimentConfig(numa_pin=0, mode=ExperimentMode.SGX,
                           gramine_build_config=gramine_build_config,
                           hyrise_build_config=hyrise_build_config,
                           gramine_experiment_config=replace(gramine_run_config, mode=GramineMode.SGX),
                           tpch_config=replace(tpch_config, output_file="exp-1-results-sgx.json"))

    for config in [plain, direct, sgx]:
        config.run()
        sf5 = replace(config, tpch_config=replace(tpch_config, scale_factor=5, output_file=f"exp-1-results-{config.mode.value}-sf5.json"))
        sf5.run()


if __name__ == '__main__':
    main()
