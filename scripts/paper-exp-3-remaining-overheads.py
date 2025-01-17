#!/usr/bin/env python3
from dataclasses import replace
import random

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode, announce_experiment


def main():
    announce_experiment("Paper Experiment 3: Remaining Overheads")
    c = "paper-exp-3-results"

    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()
    tpch_config = HyriseTPCHConfig(time=10, warmup=0, cores=8, clients=8, scheduler=True, scale_factor=10,
                                   data_prep_cores=16)
    experiment_config_plain = ExperimentConfig(numa_pin=0,
                                               mode=ExperimentMode.PLAIN,
                                               hyrise_build_config=hyrise_build_config,
                                               tpch_config=replace(tpch_config, output_file=c + "-plain.json"))

    experiment_config_plain_mitigation = replace(experiment_config_plain, mitigation=True,
                                                 tpch_config=replace(tpch_config,
                                                                     output_file=c + "-plain-mitigation.json"))

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config_sgx = GramineExperimentConfig(debug=0, mode=GramineMode.SGX)
    experiment_config_sgx = replace(experiment_config_plain, mode=ExperimentMode.SGX,
                                    gramine_build_config=gramine_optimized_config,
                                    gramine_experiment_config=gramine_experiment_config_sgx,
                                    tpch_config=replace(tpch_config, output_file=c + "-sgx.json",
                                                        data_prep_cores=1))

    for config, desc in [(experiment_config_plain, "plain"),
                         (experiment_config_plain_mitigation, "plain-mitigation"),
                         (experiment_config_sgx, "sgx")
                         ]:
        for i in range(10):
            config.tpch_config.output_file = f"{c}-{desc}-{i}.json"
            config.run()


if __name__ == '__main__':
    main()
