#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode


def main():
    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()
    tpch_base_config = HyriseTPCHConfig(time=10, warmup=0, cores=8, clients=8, scheduler=True)
    tpch_plain_config = replace(tpch_base_config, data_prep_cores=16)
    experiment_config_plain = ExperimentConfig(numa_pin=0, mode=ExperimentMode.PLAIN,
                                               hyrise_build_config=hyrise_build_config)

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config = GramineExperimentConfig(stats=False, optimize=True, debug=0, mode=GramineMode.SGX)
    experiment_config_sgx = replace(experiment_config_plain, mode=ExperimentMode.SGX,
                                    gramine_build_config=gramine_optimized_config,
                                    gramine_experiment_config=gramine_experiment_config)

    for scale_factor in range(13, 16):
        config_plain = replace(experiment_config_plain,
                               tpch_config=replace(tpch_plain_config, scale_factor=scale_factor,
                                                   output_file=f"exp-9-results-plain-{scale_factor}.json"))
        config_plain.run()
        config_sgx = replace(experiment_config_sgx,
                             tpch_config=replace(tpch_base_config, scale_factor=scale_factor,
                                                 output_file=f"exp-9-results-sgx-{scale_factor}.json"))
        config_sgx.run()


if __name__ == '__main__':
    main()
