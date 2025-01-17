#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_throughputs_latencies
from helpers.plot import PLOT_DEFAULTS


def plot(input_files=None, plots=None):
    if input_files is None:
        input_files = ["exp-1-results-plain", "exp-1-results-direct", "exp-1-results-sgx"]
    if plots is None:
        plots = ["exp-1-latencies.png", "exp-1-throughput.png", "exp-1-relative-throughput.png"]
    latencies, throughputs = load_throughputs_latencies(*input_files)

    sns.barplot(latencies, x="Query", y="Latency in ms", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / plots[0], **PLOT_DEFAULTS)
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / plots[1], **PLOT_DEFAULTS)
    plt.close()

    throughputs.set_index(["Mode", "Query"], inplace=True)
    throughputs.columns = ["Slowdown"]
    slowdown_direct = throughputs.loc["direct", :] / throughputs.loc["plain", :]
    slowdown_sgx = throughputs.loc["sgx", :] / throughputs.loc["plain", :]

    slowdown_direct["Mode"] = 'Direct'
    slowdown_sgx["Mode"] = 'SGX'

    slowdowns = pd.concat([slowdown_direct, slowdown_sgx], axis=0)
    slowdowns = slowdowns.reset_index()
    average_slowdowns = slowdowns.groupby("Mode")["Slowdown"].mean()

    sns.barplot(slowdowns, x="Query", y="Slowdown", hue="Mode")

    plt.axhline(y=average_slowdowns["Direct"], color=sns.color_palette()[0], linestyle="--")
    plt.axhline(y=average_slowdowns["SGX"], color=sns.color_palette()[1], linestyle="--")

    plt.xticks(rotation=90)
    y_ticks = list(plt.yticks()[0]) + [average_slowdowns["Direct"], average_slowdowns["SGX"]]
    plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / plots[2], **PLOT_DEFAULTS)
    plt.close()


def main():
    plot()
    plot(["exp-1-results-PLAIN-sf5", "exp-1-results-DIRECT-sf5", "exp-1-results-SGX-sf5"],
         ["exp-1-latencies-sf5.png", "exp-1-throughput-sf5.png", "exp-1-relative-throughput-sf5.png"])


if __name__ == '__main__':
    main()
