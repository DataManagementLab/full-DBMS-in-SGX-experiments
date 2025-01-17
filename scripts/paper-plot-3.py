#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_throughputs_latencies, load_json_files_list, extract_latency_df, \
    extract_throughput_df
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def main():
    setting_names = ["Plain CPU", "Plain CPU M", "Gramine SGX"]
    queries = [f"Q{i}" for i in range(1, 23)]
    files = load_json_files_list([f"paper-exp-3-results-plain-{i}" for i in range(10)], setting_names[:1] * 10)
    files += load_json_files_list([f"paper-exp-3-results-plain-mitigation-{i}" for i in range(10)], setting_names[1:2] * 10)
    files += load_json_files_list([f"paper-exp-3-results-sgx-{i}" for i in range(10)], setting_names[2:] * 10)

    throughputs = extract_throughput_df(files)

    configure_seaborn()

    plt.figure(figsize=(6, 3.25))
    p = sns.catplot(throughputs, x="Mode", y="Throughput", hue="Mode", col="Query", kind="strip", sharey=False)
    # sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)
    for ax in p.axes.flat:
        ax.set_ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-3-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()

    throughputs = throughputs.groupby(["Mode", "Query"]).mean()
    throughputs.columns = ["Relative Throughput"]
    slowdown_mitigation = throughputs.loc[setting_names[1], :] / throughputs.loc[setting_names[0], :]
    slowdown_sgx = throughputs.loc[setting_names[2], :] / throughputs.loc[setting_names[0], :]

    slowdown_sgx_mitigation = throughputs.loc[setting_names[2], :] / throughputs.loc[setting_names[1], :]
    print(slowdown_sgx_mitigation.to_string())
    print(slowdown_sgx_mitigation.mean())

    figure_hue_names = ["Mitigation", "SGX"]

    slowdown_mitigation["Mode"] = figure_hue_names[0]
    slowdown_sgx["Mode"] = figure_hue_names[1]

    slowdown = pd.concat([slowdown_mitigation, slowdown_sgx], axis=0)

    palette = [sns.color_palette()[3], sns.color_palette()[2]]
    hatches = ['--', '\\\\']

    plt.figure(figsize=(4.5, 2.5))
    p = sns.barplot(slowdown, x="Query", y="Relative Throughput", hue='Mode', hue_order=figure_hue_names, order=queries,
                    palette=palette)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)

    average_slowdowns = slowdown.groupby('Mode')["Relative Throughput"].mean()
    print(average_slowdowns.to_string())

    for i, bar in enumerate(p.patches):
        if i // 22 == 0:
            bar.set_hatch(hatches[0])
        elif i // 22 == 1:
            bar.set_hatch(hatches[1])

    for hatch, handle in zip(hatches, p.axes.get_legend().legend_handles):
        handle.set_hatch(hatch)

    for i, setting in enumerate(figure_hue_names):
        plt.axhline(y=average_slowdowns[setting], color=palette[i], linestyle="--")

    plt.xticks(rotation=90)
    plt.ylim(bottom=0, top=1)
    plt.yticks([0, 0.25, 0.5, 0.75, 1])
    plt.grid(axis='y')
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-3-relative-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    main()
