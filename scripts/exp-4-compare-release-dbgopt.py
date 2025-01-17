#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseTPCHConfig, GramineBuildConfig, MachineConfig


def main():
    hyrise_config = HyriseTPCHConfig(time=10, scale_factor=5, scheduler=True, clients=8, cores=8)
    gramine_release_config = GramineBuildConfig(source_root=MachineConfig["gramine_source_root"], build_mode="release")
    gramine_debugoptimized_config = replace(gramine_release_config, build_mode="debugoptimized")
    experiment_config = ExperimentConfig(numa_pin=0, stats=False, optimize=True, debug=0)

    sgx_release = replace(experiment_config, mode="sgx", log_file="exp-4-log-release.glog",
                          gramine_build_config=gramine_release_config,
                          tpch_config=replace(hyrise_config, output_file="exp-4-results-release-sf5.json"))

    sgx_debug = replace(experiment_config, mode="sgx", log_file="exp-4-log-debugoptimized.glog",
                        gramine_build_config=gramine_debugoptimized_config,
                        tpch_config=replace(hyrise_config, output_file="exp-4-results-debugoptimized-sf5.json"))

    for config in [sgx_release, sgx_debug]:
        # config.gramine_build_config.prepare()
        config.run()


if __name__ == '__main__':
    main()
