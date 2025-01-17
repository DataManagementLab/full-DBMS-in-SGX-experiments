#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, ExperimentMode, BuildMode, \
    GramineBuildConfig, GramineExperimentConfig, GramineMode


def main():
    c = "exp-13-results"

    hyrise_build_config_default = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"],
                                                    debug_configuration=True)
    hyrise_build_config_join = HyriseBuildConfig(build_mode=BuildMode.RELEASE,
                                              flags=["-DUSE_JEMALLOC=OFF", "-DUNROLL_JOIN=ON"],
                                              debug_configuration=True)
    hyrise_build_config_agg = HyriseBuildConfig(build_mode=BuildMode.RELEASE,
                                              flags=["-DUSE_JEMALLOC=OFF", "-DUNROLL_AGG=ON", "-DAGG_UNROLL_FACTOR=4"],
                                              debug_configuration=True)

    hyrise_build_configs = [(hyrise_build_config_default, "none"),
                            (hyrise_build_config_join, "join"),
                            (hyrise_build_config_agg, "agg")]

    for config, _ in hyrise_build_configs:
        config.configure()
        config.compile()

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config_sgx = GramineExperimentConfig(debug=0, mode=GramineMode.SGX)

    tpch_config = HyriseTPCHConfig(warmup=10, cores=8, clients=8, scheduler=True, scale_factor=10)
    for config, config_name in hyrise_build_configs:
        config.install()

        experiment_config = ExperimentConfig(numa_pin=0,
                                             mode=ExperimentMode.PLAIN,
                                             hyrise_build_config=config,
                                             tpch_config=replace(tpch_config,
                                                                 output_file=f"{c}-{config_name}.json"))

        experiment_config_mitigation = replace(experiment_config, mitigation=True,
                                               tpch_config=replace(tpch_config,
                                                                   output_file=f"{c}-{config_name}-mitigation.json"))

        experiment_config_sgx = replace(experiment_config, mode=ExperimentMode.SGX,
                                        gramine_build_config=gramine_optimized_config,
                                        gramine_experiment_config=gramine_experiment_config_sgx,
                                        tpch_config=replace(tpch_config, output_file=f"{c}-{config_name}-sgx.json"))

        experiment_config.run()
        experiment_config_mitigation.run()
        experiment_config_sgx.run()


if __name__ == '__main__':
    main()
