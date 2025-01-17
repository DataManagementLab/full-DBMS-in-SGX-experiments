#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, BuildMode, \
    GramineExperimentConfig, GramineMode, ExperimentMode


def main():
    hyrise_config = HyriseTPCHConfig(time=10, warmup=0, scale_factor=5, scheduler=True, clients=8, cores=8)
    gramine_default_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=enabled"])
    gramine_optimized_config = replace(gramine_default_config, flags=["-Dlist_check=disabled"])

    gramine_default_config.prepare()
    gramine_optimized_config.prepare()

    hyrise_build_config_jemalloc = HyriseBuildConfig(build_mode=BuildMode.RELEASE)
    hyrise_build_config_glibc_malloc = replace(hyrise_build_config_jemalloc, flags=["-DUSE_JEMALLOC=OFF"])

    hyrise_build_config_jemalloc.configure()
    hyrise_build_config_jemalloc.compile()
    hyrise_build_config_glibc_malloc.configure()
    hyrise_build_config_glibc_malloc.compile()

    gramine_experiment_config = GramineExperimentConfig(mode=GramineMode.SGX, stats=False, optimize=True, debug=0)
    experiment_config = ExperimentConfig(numa_pin=0)

    plain_jemalloc = replace(experiment_config, mode=ExperimentMode.PLAIN,
                             hyrise_build_config=hyrise_build_config_jemalloc,
                             tpch_config=replace(hyrise_config, output_file="exp-6-results-plain-jemalloc.json"))

    plain_glibc_malloc = replace(experiment_config, mode=ExperimentMode.PLAIN,
                                 hyrise_build_config=hyrise_build_config_glibc_malloc,
                                 tpch_config=replace(hyrise_config, output_file="exp-6-results-plain-glibc.json"))

    gramine_default_jemalloc = replace(experiment_config, mode=ExperimentMode.SGX,
                                       hyrise_build_config=hyrise_build_config_jemalloc,
                                       gramine_build_config=gramine_default_config,
                                       gramine_experiment_config=replace(gramine_experiment_config,
                                                                         log_file="exp-6-log-default-jemalloc.glog"),
                                       tpch_config=replace(hyrise_config,
                                                           output_file="exp-6-results-default-jemalloc.json"))
    gramine_default_glibc_malloc = replace(experiment_config, mode=ExperimentMode.SGX,
                                           hyrise_build_config=hyrise_build_config_glibc_malloc,
                                           gramine_build_config=gramine_default_config,
                                           gramine_experiment_config=replace(gramine_experiment_config,
                                                                             log_file="exp-6-log-default-glibc.glog"),
                                           tpch_config=replace(hyrise_config,
                                                               output_file="exp-6-results-default-glibc.json"))

    gramine_optimized_jemalloc = replace(experiment_config, mode=ExperimentMode.SGX,
                                         hyrise_build_config=hyrise_build_config_jemalloc,
                                         gramine_build_config=gramine_optimized_config,
                                         gramine_experiment_config=replace(gramine_experiment_config,
                                                                           log_file="exp-6-log-optimized-jemalloc.glog"),
                                         tpch_config=replace(hyrise_config,
                                                             output_file="exp-6-results-optimized-jemalloc.json"))
    gramine_optimized_glibc_malloc = replace(experiment_config, mode=ExperimentMode.SGX,
                                             hyrise_build_config=hyrise_build_config_glibc_malloc,
                                             gramine_build_config=gramine_optimized_config,
                                             gramine_experiment_config=replace(gramine_experiment_config,
                                                                               log_file="exp-6-log-optimized-glibc.glog"),
                                             tpch_config=replace(hyrise_config,
                                                                 output_file="exp-6-results-optimized-glibc.json"))

    for config in [plain_jemalloc, plain_glibc_malloc,
                   gramine_default_jemalloc, gramine_default_glibc_malloc,
                   gramine_optimized_jemalloc, gramine_optimized_glibc_malloc]:
        config.hyrise_build_config.install()
        config.run()


if __name__ == '__main__':
    main()
