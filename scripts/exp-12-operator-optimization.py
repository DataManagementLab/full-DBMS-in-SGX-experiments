#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, ExperimentMode, BuildMode


def main():
    c = "paper-exp-4-results"

    hyrise_build_config_default = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"],
                                                    debug_configuration=True)
    hyrise_build_config_2 = HyriseBuildConfig(build_mode=BuildMode.RELEASE,
                                              flags=["-DUSE_JEMALLOC=OFF", "-DUNROLL=ON", "-DAGG_UNROLL_FACTOR=2"],
                                              debug_configuration=True)
    hyrise_build_config_4 = HyriseBuildConfig(build_mode=BuildMode.RELEASE,
                                              flags=["-DUSE_JEMALLOC=OFF", "-DUNROLL=ON", "-DAGG_UNROLL_FACTOR=4"],
                                              debug_configuration=True)

    hyrise_build_configs = [(hyrise_build_config_default, "1"), (hyrise_build_config_2, "2"),
                            (hyrise_build_config_4, "4")]

    for config, _ in hyrise_build_configs:
        config.configure()
        config.compile()

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

        experiment_config.run()
        experiment_config_mitigation.run()


if __name__ == '__main__':
    main()
