#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode


def main():
    c = "paper-exp-4-results"

    hyrise_build_config_default = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config_default.prepare()
    hyrise_build_config_opt = HyriseBuildConfig(build_mode=BuildMode.RELEASE,
                                                flags=["-DUSE_JEMALLOC=OFF", "-DUNROLL=ON", "-DAGG_UNROLL_FACTOR=4"])
    hyrise_build_config_opt.prepare()
    tpch_config = HyriseTPCHConfig(warmup=10, cores=8, clients=8, scheduler=True, scale_factor=10)
    experiment_config_plain = ExperimentConfig(numa_pin=0,
                                               mode=ExperimentMode.PLAIN,
                                               hyrise_build_config=hyrise_build_config_default,
                                               tpch_config=replace(tpch_config, output_file=c + "-plain.json"))

    experiment_config_plain_opt = replace(experiment_config_plain,
                                          hyrise_build_config=hyrise_build_config_opt,
                                          tpch_config=replace(tpch_config, output_file=c + "-plain-opt.json"))

    experiment_config_plain_mitigation = replace(experiment_config_plain, mitigation=True,
                                                 tpch_config=replace(tpch_config,
                                                                     output_file=c + "-plain-mitigation.json"))

    experiment_config_mitigation_opt = replace(experiment_config_plain_mitigation,
                                          hyrise_build_config=hyrise_build_config_opt,
                                          tpch_config=replace(tpch_config, output_file=c + "-mitigation-opt.json"))

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config_sgx = GramineExperimentConfig(debug=0, mode=GramineMode.SGX)
    experiment_config_sgx = replace(experiment_config_plain, mode=ExperimentMode.SGX,
                                    gramine_build_config=gramine_optimized_config,
                                    gramine_experiment_config=gramine_experiment_config_sgx,
                                    tpch_config=replace(tpch_config, output_file=c + "-sgx.json"))

    experiment_config_sgx_opt = replace(experiment_config_sgx,
                                        hyrise_build_config=hyrise_build_config_opt,
                                        tpch_config=replace(tpch_config, output_file=c + "-sgx-opt.json"))

    for config in [experiment_config_plain, experiment_config_plain_opt,
                   experiment_config_plain_mitigation, experiment_config_mitigation_opt,
                   experiment_config_sgx, experiment_config_sgx_opt]:
        config.run()


if __name__ == '__main__':
    main()
