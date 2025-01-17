#!/usr/bin/env python3

import seaborn as sns
from matplotlib import pyplot as plt

from helpers.extract_results import load_json_files_list, extract_latency_df


def plot_latencies(files):
    latencies = extract_latency_df(files)

    sns.boxplot(latencies, x="Query", y="Latency", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig("img/exp-7-latencies.pdf")
    plt.close()


def main():
    setting_names = ["ordered", "shuffled"]
    files = load_json_files_list([f"exp-7-results-{setting}" for setting in setting_names], setting_names)

    plot_latencies(files)


if __name__ == '__main__':
    main()
