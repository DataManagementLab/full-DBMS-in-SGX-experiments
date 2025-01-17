#!/usr/bin/env python3
from dataclasses import replace

from helpers.experiment import ExperimentConfig, HyriseTPCHConfig

def main():
    hyrise_config = HyriseTPCHConfig(time=10)
    experiment_config = ExperimentConfig(numa_pin=0, stats=False, optimize=True, debug=0)

    plain = replace(experiment_config, tpch_config=replace(hyrise_config, output_file="exp-2-results-plain.json"))
    direct = replace(experiment_config, mode="direct", log_file="exp-2-log-direct.glog",
                     tpch_config=replace(hyrise_config, output_file="exp-2-results-direct.json"))
    sgx = replace(experiment_config, mode="sgx", log_file="exp-2-log-sgx.glog",
                  tpch_config=replace(hyrise_config, output_file="exp-2-results-sgx.json"))

    for config in [plain, direct, sgx]:
        config.run()


if __name__ == '__main__':
    main()
