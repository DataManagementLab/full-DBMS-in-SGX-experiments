#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode


def main():
    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()
    tpch_config = HyriseTPCHConfig(time=10, warmup=0, cores=8, clients=8, scheduler=True, scale_factor=10)
    experiment_config_plain = ExperimentConfig(numa_pin=0, perf=True, perf_file_name="exp-10-perf-plain.data",
                                               mode=ExperimentMode.PLAIN,
                                               hyrise_build_config=hyrise_build_config,
                                               tpch_config=tpch_config)

    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELDBG, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config_sgx = GramineExperimentConfig(stats=True, profile=True, optimize=False, debug=0,
                                                            mode=GramineMode.SGX)
    gramine_experiment_config_direct = GramineExperimentConfig(stats=True, profile=False, optimize=False, debug=0,
                                                               mode=GramineMode.DIRECT)
    experiment_config_sgx = replace(experiment_config_plain, mode=ExperimentMode.SGX,
                                    gramine_build_config=gramine_optimized_config,
                                    gramine_experiment_config=gramine_experiment_config_sgx,
                                    perf_file_name="exp-10-perf-sgx.data")
    experiment_config_direct = replace(experiment_config_sgx, mode=ExperimentMode.DIRECT,
                                       perf_file_name="exp-10-perf-direct.data",
                                       gramine_experiment_config=gramine_experiment_config_direct)

    config_plain = replace(experiment_config_plain,
                           tpch_config=replace(tpch_config, output_file="exp-10-results-plain.json"))
    config_sgx = replace(experiment_config_sgx, tpch_config=replace(tpch_config, output_file="exp-10-results-sgx.json"))
    config_direct = replace(experiment_config_direct, tpch_config=replace(tpch_config,
                                                                          output_file="exp-10-results-direct.json"))
    config_plain_mitigation = replace(experiment_config_plain, mitigation=True, perf_file_name="exp-10-perf-plain-mitigation.data",
                                      tpch_config=replace(tpch_config, output_file="exp-10-results-plain-mitigation.json"))
    config_direct_mitigation = replace(experiment_config_direct, mitigation=True, perf_file_name="exp-10-perf-direct-mitigation.data",
                                       tpch_config=replace(tpch_config, output_file="exp-10-results-direct-mitigation.json"))

    # config_plain.run()
    config_sgx.run()
    # config_direct.run()
    # config_plain_mitigation.run()
    # config_direct_mitigation.run()


if __name__ == '__main__':
    main()
