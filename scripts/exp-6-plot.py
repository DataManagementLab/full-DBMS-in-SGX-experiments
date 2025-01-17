#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

from helpers import paths
from helpers.extract_results import load_json_files_list, extract_throughput_df, extract_latency_df
from helpers.paths import IMG_PATH
from helpers.plot import PLOT_DEFAULTS


def main():
    setting_names = ["plain-jemalloc", "plain-glibc", "default-jemalloc", "default-glibc",
                     "optimized-jemalloc", "optimized-glibc"]
    files = load_json_files_list([f"exp-6-results-{setting}" for setting in setting_names], setting_names)

    latencies = extract_latency_df(files)
    throughputs = extract_throughput_df(files)

    sns.barplot(latencies, x="Query", y="Latency", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-6-latencies.png", **PLOT_DEFAULTS)
    plt.close()

    sns.barplot(throughputs, x="Query", y="Throughput", hue="Mode")
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(IMG_PATH / "exp-6-throughput.png", **PLOT_DEFAULTS)
    plt.close()

    throughputs.set_index(["Mode", "Query"], inplace=True)
    throughputs.columns = ["Relative Throughout"]
    relative_unoptimized = throughputs.loc["default-jemalloc", :] / throughputs.loc["plain-jemalloc", :]
    relative_optimized = throughputs.loc["optimized-glibc", :] / throughputs.loc["plain-jemalloc", :]

    relative_unoptimized["Mode"] = 'Unoptimized'
    relative_optimized["Mode"] = 'Optimized'

    relative = pd.concat([relative_unoptimized, relative_optimized], axis=0)
    relative = relative.reset_index()
    average_relative = relative.groupby("Mode")["Relative Throughout"].mean()

    relative.reset_index(inplace=True)

    sns.barplot(relative, x="Query", y="Relative Throughout", hue="Mode",
                hue_order=['Unoptimized', 'Optimized'])

    plt.axhline(y=average_relative["Unoptimized"], color=sns.color_palette()[0], linestyle="--")
    plt.axhline(y=average_relative["Optimized"], color=sns.color_palette()[1], linestyle="--")

    plt.xticks(rotation=90)
    plt.ylim(top=1)
    y_ticks = list(plt.yticks()[0]) + [average_relative["Unoptimized"], average_relative["Optimized"]]
    plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-6-relative-throughput.png", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    main()
