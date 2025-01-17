#!/usr/bin/env python3

import seaborn as sns
from matplotlib import pyplot as plt

from helpers.extract_results import extract_throughput_df, extract_latency_df, load_json_files_list
from helpers.paths import IMG_PATH


def main(*files: str):
    dicts = load_json_files_list(files)

    latencies = extract_latency_df(dicts)
    throughputs = extract_throughput_df(dicts)

    sns.barplot(latencies, x="Query", y="Latency", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(IMG_PATH / "cmp-latencies.pdf")
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(IMG_PATH / "cmp-throughput.pdf")
    plt.close()


if __name__ == '__main__':
    main("exp-10-results-direct-mitigation", "exp-10-results-plain-mitigation")
