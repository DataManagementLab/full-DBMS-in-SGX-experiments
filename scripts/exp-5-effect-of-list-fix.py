#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseTPCHConfig, GramineBuildConfig, MachineConfig


def main():
    hyrise_config = HyriseTPCHConfig(time=10, warmup=0, scale_factor=5, scheduler=True, clients=8, cores=8)
    gramine_default_config = GramineBuildConfig(source_root=MachineConfig["gramine_source_root"], build_mode="release",
                                                flags=["-Dlist_check=enabled"], debug_configuration=True)
    gramine_optimized_config = replace(gramine_default_config, flags=["-Dlist_check=disabled"])
    experiment_config = ExperimentConfig(numa_pin=0, stats=False, optimize=True, debug=0)

    baseline = replace(experiment_config, mode="plain",
                       tpch_config=replace(hyrise_config, output_file="exp-5-results-baseline.json"))
    gramine_default_direct = replace(experiment_config, mode="direct", log_file="exp-5-log-default-direct.glog",
                                     gramine_build_config=gramine_default_config,
                                     tpch_config=replace(hyrise_config,
                                                         output_file="exp-5-results-default-direct.json"))
    gramine_default_sgx = replace(experiment_config, mode="sgx", log_file="exp-5-log-default-sgx.glog",
                                  gramine_build_config=gramine_default_config,
                                  tpch_config=replace(hyrise_config, output_file="exp-5-results-default-sgx.json"))

    gramine_optimized_direct = replace(experiment_config, mode="direct", log_file="exp-5-log-optimized-direct.glog",
                                       gramine_build_config=gramine_optimized_config,
                                       tpch_config=replace(hyrise_config,
                                                           output_file="exp-5-results-optimized-direct.json"))
    gramine_optimized_sgx = replace(experiment_config, mode="sgx", log_file="exp-5-log-optimized-sgx.glog",
                                    gramine_build_config=gramine_optimized_config,
                                    tpch_config=replace(hyrise_config, output_file="exp-5-results-optimized-sgx.json"))

    for config in [gramine_default_direct, gramine_default_sgx]: #, gramine_optimized_direct, gramine_optimized_sgx]:
        if config.mode == "direct":
            config.gramine_build_config.prepare()
        config.run()


if __name__ == '__main__':
    main()
