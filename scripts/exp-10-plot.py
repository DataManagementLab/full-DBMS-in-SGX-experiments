#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_throughputs_latencies, load_json_files_list, extract_latency_df, \
    extract_throughput_df
from helpers.plot import PLOT_DEFAULTS


def main():
    setting_names = ["plain", "plain-mitigation", "direct", "direct-mitigation", "sgx"]
    files = load_json_files_list([f"exp-10-results-{setting}" for setting in setting_names], setting_names)

    latencies = extract_latency_df(files)
    throughputs = extract_throughput_df(files)

    sns.barplot(latencies, x="Query", y="Latency in ms", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-10-latencies.png", **PLOT_DEFAULTS)
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-10-throughputs.png", **PLOT_DEFAULTS)
    plt.close()

    throughputs.set_index(["Mode", "Query"], inplace=True)
    throughputs.columns = ["Relative Throughput"]
    slowdown_mitigation = throughputs.loc["plain-mitigation", :] / throughputs.loc["plain", :]
    slowdown_direct = throughputs.loc["direct", :] / throughputs.loc["plain", :]
    slowdown_direct_mitigation = throughputs.loc["direct-mitigation", :] / throughputs.loc["plain", :]
    slowdown_sgx = throughputs.loc["sgx", :] / throughputs.loc["plain", :]

    slowdown_mitigation["Mode"] = "plain-mitigation"
    slowdown_direct["Mode"] = "direct"
    slowdown_direct_mitigation["Mode"] = "direct-mitigation"
    slowdown_sgx["Mode"] = "sgx"

    slowdown = pd.concat([slowdown_mitigation, slowdown_direct, slowdown_direct_mitigation, slowdown_sgx], axis=0)

    sns.barplot(slowdown, x="Query", y="Relative Throughput", hue='Mode', hue_order=setting_names[1:],
                palette=sns.color_palette()[1:])
    average_slowdowns = slowdown.groupby('Mode')["Relative Throughput"].mean()

    for i, setting in enumerate(setting_names[1:]):
        plt.axhline(y=average_slowdowns[setting], color=sns.color_palette()[i + 1], linestyle="--")

    plt.xticks(rotation=90)
    # y_ticks = list(plt.yticks()[0]) + list(average_slowdowns)
    # plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-10-relative-throughput.png", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    main()
