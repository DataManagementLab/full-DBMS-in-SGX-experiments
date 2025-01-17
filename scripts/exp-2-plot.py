#!/usr/bin/env python3

import seaborn as sns
import pandas as pd
from matplotlib import pyplot as plt

from helpers.extract_results import load_throughputs_latencies


def main():
    latencies, throughputs = load_throughputs_latencies("exp-2-results-plain", "exp-2-results-direct",
                                                        "exp-2-results-sgx")

    sns.barplot(latencies, x="Query", y="Latency", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("img/exp-2-latencies.pdf")
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("img/exp-2-throughput.pdf")
    plt.close()

    throughputs.set_index(["Mode", "Query"], inplace=True)
    throughputs.columns = ["Slowdown"]
    slowdown_direct = 1 - throughputs.loc["direct", :] / throughputs.loc["plain", :]
    slowdown_sgx = 1 - throughputs.loc["sgx", :] / throughputs.loc["plain", :]

    slowdown_direct["Mode"] = 'Direct'
    slowdown_sgx["Mode"] = 'SGX'

    slowdowns = pd.concat([slowdown_direct, slowdown_sgx], axis=0)
    slowdowns = slowdowns.reset_index()
    average_slowdowns = slowdowns.groupby("Mode")["Slowdown"].mean()

    sns.barplot(slowdowns, x="Query", y="Slowdown", hue="Mode")

    plt.axhline(y=average_slowdowns["Direct"], color=sns.color_palette()[0], linestyle="--")
    plt.axhline(y=average_slowdowns["SGX"], color=sns.color_palette()[1], linestyle="--")

    plt.xticks(rotation=90)
    y_ticks = [0, 0.1, 0.2, 0.3, 0.4, 0.5, average_slowdowns["Direct"], average_slowdowns["SGX"]]
    plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig("img/exp-2-slowdown.pdf")
    plt.close()


if __name__ == '__main__':
    main()
