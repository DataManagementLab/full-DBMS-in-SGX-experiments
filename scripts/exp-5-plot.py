#!/usr/bin/env python3

import seaborn as sns
from matplotlib import pyplot as plt

from helpers.extract_results import load_json_files_list, extract_throughput_df, extract_latency_df


def main():
    setting_names = ["baseline", "default-direct", "default-sgx", "optimized-direct", "optimized-sgx"]
    files = load_json_files_list([f"exp-5-results-{setting}" for setting in setting_names], setting_names)

    latencies = extract_latency_df(files)
    throughputs = extract_throughput_df(files)

    sns.barplot(latencies, x="Query", y="Latency", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("img/exp-5-latencies.pdf")
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("img/exp-5-throughput.pdf")
    plt.close()

    # throughputs.set_index(["Mode", "Query"], inplace=True)
    # throughputs.columns = ["Slowdown"]
    # slowdown_direct = 1 - throughputs.loc["direct", :] / throughputs.loc["plain", :]
    # slowdown_sgx = 1 - throughputs.loc["sgx", :] / throughputs.loc["plain", :]
    #
    # slowdown_direct["Mode"] = 'Direct'
    # slowdown_sgx["Mode"] = 'SGX'
    #
    # slowdowns = pd.concat([slowdown_direct, slowdown_sgx], axis=0)
    # slowdowns = slowdowns.reset_index()
    # average_slowdowns = slowdowns.groupby("Mode")["Slowdown"].mean()
    #
    # sns.barplot(slowdowns, x="Query", y="Slowdown", hue="Mode")
    #
    # plt.axhline(y=average_slowdowns["Direct"], color=sns.color_palette()[0], linestyle="--")
    # plt.axhline(y=average_slowdowns["SGX"], color=sns.color_palette()[1], linestyle="--")
    #
    # plt.xticks(rotation=90)
    # y_ticks = list(plt.yticks()[0]) + [average_slowdowns["Direct"], average_slowdowns["SGX"]]
    # plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    # plt.tight_layout()
    # plt.savefig("img/exp-3-slowdown.pdf")
    # plt.close()


if __name__ == '__main__':
    main()
