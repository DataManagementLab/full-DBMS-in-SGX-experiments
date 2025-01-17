#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    ExperimentMode, GramineExperimentConfig, BuildMode


def main():
    tpch_base_config = HyriseTPCHConfig(time=10, warmup=0, scale_factor=5, scheduler=True)
    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()
    experiment_config_plain = ExperimentConfig(numa_pin=0,  mode=ExperimentMode.PLAIN,
                                               hyrise_build_config=hyrise_build_config)

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE,
                                                  flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config = GramineExperimentConfig(stats=False, optimize=True, debug=0)

    experiment_config_sgx = replace(experiment_config_plain, mode=ExperimentMode.SGX,
                                    gramine_experiment_config=gramine_experiment_config,
                                    gramine_build_config=gramine_optimized_config)

    for num_cores in [1, 2, 4, 8, 14, 15, 16]:
        config_plain = replace(experiment_config_plain,
                               tpch_config=replace(tpch_base_config, cores=num_cores, clients=num_cores,
                                                   output_file=f"exp-8-results-plain-{num_cores}.json"))
        config_plain.run()
        config_sgx = replace(experiment_config_sgx,
                             tpch_config=replace(tpch_base_config, cores=num_cores, clients=num_cores,
                                                 output_file=f"exp-8-results-sgx-{num_cores}.json"))
        config_sgx.run()


if __name__ == '__main__':
    main()
