#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_throughputs_latencies, load_json_files_list, extract_latency_df, \
    extract_throughput_df
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def main():
    files = load_json_files_list([f"paper-exp-3-results-plain-{i}" for i in range(10)], ["Ordered"] * 10)
    files += load_json_files_list([f"paper-exp-3-results-shuffle-plain-{i}" for i in range(10)], ["Shuffled"] * 10)
    files += load_json_files_list([f"paper-exp-3-results-sgx-{i}" for i in range(5)], ["Ordered SGX"] * 5)
    files += load_json_files_list([f"paper-exp-3-results-shuffle-sgx-{i}" for i in range(5)], ["Shuffled SGX"] * 5)

    throughputs = extract_throughput_df(files)

    print(throughputs.groupby(["Mode", "Query"])["Throughput"].describe().to_string())

    min_df = throughputs.groupby(["Mode", "Query"])["Throughput"].min()
    max_df = throughputs.groupby(["Mode", "Query"])["Throughput"].max()

    rel_spread = (max_df - min_df) / min_df

    print(rel_spread.sort_values().to_string())

    configure_seaborn()

    # plt.figure(figsize=(6, 3.25))
    p = sns.catplot(throughputs, col="Query", x="Mode", hue="Mode", y="Throughput", sharey=False)

    for ax in p.axes.flat:
        ax.set_ylim(bottom=0)

    # sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)
    # plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-14-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    main()
