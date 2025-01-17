#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_json_files_list, extract_latency_df, \
    extract_throughput_df
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def plot():
    setting_names = ["Plain CPU", "Gramine SGX"]
    queries = [f"Q{i}" for i in range(1,23)]
    files = load_json_files_list([f"paper-exp-1-results-plain-{i}" for i in range(10)], setting_names[:1] * 10)
    files += load_json_files_list([f"paper-exp-1-results-sgx-{i}" for i in range(10)], setting_names[1:2] * 10)

    throughputs = extract_throughput_df(files)

    configure_seaborn()

    plt.figure(figsize=(5,3))
    p = sns.catplot(throughputs, x="Mode", y="Throughput", hue="Mode", col="Query", col_order=queries, kind="swarm",
                    sharey=False)
    #sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)
    for ax in p.axes.flat:
        ax.set_ylim(bottom=0)

    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-1-ootb-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()

    y_name = "Relative Throughput\nin Gramine SGX"
    throughputs = throughputs.groupby(["Mode", "Query"]).mean()
    throughputs.columns = [y_name]
    slowdown_sgx = throughputs.loc["Gramine SGX", :] / throughputs.loc["Plain CPU", :]
    slowdowns = slowdown_sgx.reset_index()
    
    average_slowdown = slowdowns[y_name].mean()
    print(average_slowdown)

    plt.figure(figsize=(4.5, 2.5))
    p = sns.barplot(slowdowns, x="Query", y=y_name, color=sns.color_palette("deep")[2], order=queries)
    plt.axhline(y=average_slowdown, color=sns.color_palette("deep")[2], linestyle="--")
    p.yaxis.set_label_coords(-0.19, 0.45)

    for bar in p.patches:
        bar.set_hatch('\\\\')

    plt.xticks(rotation=90)
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-1-ootb-slowdown.pdf", **PLOT_DEFAULTS)
    plt.close()


def main():
    plot()


if __name__ == '__main__':
    main()
