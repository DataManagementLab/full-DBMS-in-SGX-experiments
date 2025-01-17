#!/usr/bin/env python3

from helpers.experiment import ExperimentConfig, HyriseBuildConfig, HyriseTPCHConfig, GramineBuildConfig, \
    GramineExperimentConfig, GramineMode, ExperimentMode, BuildMode, MachineConfig


def main():
    # Directly use the independent hyrise source on the server instead of the subproject to test stuff without
    # committing all the time.
    hyrise_build_config = HyriseBuildConfig(build_mode=BuildMode.DEBUG,
                                            source_root=MachineConfig["hyrise_source_root"],
                                            flags=["-DUSE_JEMALLOC=OFF"])
    hyrise_build_config.prepare()
    gramine_optimized_config = GramineBuildConfig(build_mode=BuildMode.RELEASE, flags=["-Dlist_check=disabled"])
    gramine_optimized_config.prepare()
    gramine_experiment_config = GramineExperimentConfig(stats=False, profile=False, optimize=False, debug=0,
                                                        mode=GramineMode.SGX)
    tpch_config = HyriseTPCHConfig(time=10, warmup=0, cores=8, clients=8, scheduler=True, scale_factor=10,
                                   output_file="test-run.json")

    experiment_config = ExperimentConfig(numa_pin=None, mode=ExperimentMode.SGX,
                                         hyrise_build_config=hyrise_build_config,
                                         gramine_build_config=gramine_optimized_config,
                                         gramine_experiment_config=gramine_experiment_config,
                                         tpch_config=tpch_config)
    experiment_config.run()


if __name__ == '__main__':
    main()
