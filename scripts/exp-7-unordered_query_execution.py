#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    BuildMode, GramineExperimentConfig, GramineMode, ExperimentMode


def main():
    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()

    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.RELEASE, flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()

    gramine_experiment_config = GramineExperimentConfig(stats=False, optimize=True, debug=0, mode=GramineMode.SGX)
    base_experiment_config = ExperimentConfig(numa_pin=0,  mode=ExperimentMode.SGX,
                                              gramine_experiment_config=gramine_experiment_config,
                                              gramine_build_config=gramine_optimized_config,
                                              hyrise_build_config=hyrise_build_config)

    tpch_ordered_config = HyriseTPCHConfig(time=10, warmup=0, scale_factor=5, scheduler=True, shuffle_queries=False,
                                           output_file="exp-7-results-ordered.json")
    tpch_shuffled_config = replace(tpch_ordered_config, time=220, shuffle_queries=True,
                                   output_file="exp-7-results-shuffled.json")

    for tpch_config in [tpch_ordered_config, tpch_shuffled_config]:
        config = replace(base_experiment_config, tpch_config=tpch_config)
        config.run()


if __name__ == '__main__':
    main()
