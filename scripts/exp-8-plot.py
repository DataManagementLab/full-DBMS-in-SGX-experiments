#!/usr/bin/env python3

import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt

from helpers.extract_results import load_json_files_list, extract_throughput_df, extract_latency_df
from helpers.paths import IMG_PATH
from helpers.plot import PLOT_DEFAULTS


def plot_throughput(files):
    throughputs = extract_throughput_df(files)
    extracts_throughputs = throughputs["Mode"].str.extract(r'(?P<SGX>sgx|plain)-(?P<Threads>\d+)')
    throughputs = pd.concat([throughputs, extracts_throughputs], axis=1)

    throughputs = throughputs[throughputs["Query"].isin(["Q1", "Q15"])]

    f = sns.catplot(throughputs, x="SGX", y="Throughput", hue="Threads", col="Query", kind="bar", sharey=False,
                    legend="auto")

    sns.move_legend(f, "lower center", bbox_to_anchor=(.5, 1), ncol=7, title=None, frameon=False)

    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-8-throughput.png", **PLOT_DEFAULTS)
    plt.close()

    throughputs.set_index(["SGX", "Threads", "Query"], inplace=True)
    throughputs.drop(columns=["Mode"], inplace=True)
    throughputs.columns = ["Slowdown"]
    slowdown_throughput = 1 - throughputs.loc["sgx", :] / throughputs.loc["plain", :]

    slowdown_throughput.reset_index(inplace=True)
    f = sns.catplot(slowdown_throughput, x="Threads", y="Slowdown", col="Query", kind="bar",
                    order=[1, 2, 4, 8, 14, 15, 16],
                    col_order=["Q1", "Q15"])  # [f"Q{n}" for n in range(1, 23)])

    sns.move_legend(f, "lower center", bbox_to_anchor=(.5, 1), ncol=3, title=None, frameon=False)

    for ax in f.axes.flat:
        ax.set_ylim(top=1)

    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-8-throughput-slowdown.png", **PLOT_DEFAULTS)
    plt.close()


def plot_latencies(files):
    latencies = extract_latency_df(files)
    extracts_latencies = latencies["Mode"].str.extract(r'(?P<SGX>sgx|plain)-(?P<Threads>\d+)')
    latencies = pd.concat([latencies, extracts_latencies], axis=1)

    sns.catplot(latencies, x="SGX", y="Latency", hue="Threads", col="Query", kind="bar", sharey=False)
    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-8-latencies.pdf", **PLOT_DEFAULTS)
    plt.close()

    latencies.set_index(["SGX", "Threads", "Query"], inplace=True)
    latencies.drop(columns=["Mode"], inplace=True)
    latencies.columns = ["Slowdown"]

    mean_latencies = latencies.groupby(level=[0, 1, 2])["Slowdown"].mean()

    slowdown_latencies = mean_latencies.loc["sgx"] / mean_latencies.loc["plain"]

    slowdown_latencies = slowdown_latencies.reset_index()
    sns.catplot(slowdown_latencies, x="Threads", y="Slowdown", col="Query", kind="bar",
                order=[1, 2, 4, 8, 14, 15, 16],
                col_order=[f"Q{n}" for n in range(1, 23)])

    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-8-latency-slowdown.pdf", **PLOT_DEFAULTS)
    plt.close()


def main():
    cores = [1, 2, 4, 8, 14, 15, 16]
    setting_names = [f"plain-{n}" for n in cores] + [f"sgx-{n}" for n in cores]
    files = load_json_files_list([f"exp-8-results-{setting}" for setting in setting_names], setting_names)

    plot_throughput(files)
    #plot_latencies(files)


if __name__ == '__main__':
    main()
