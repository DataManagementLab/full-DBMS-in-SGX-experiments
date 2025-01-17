#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import load_throughputs_latencies, load_json_files_list, extract_latency_df, \
    extract_throughput_df
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


setting_names = ["NP", "NM",
                 "AP", "AM",
                 "JP", "JM", "JS"]


def plot_absolute(throughputs):
    p = sns.catplot(throughputs, col="Query", y="Throughput", x="Mode", kind="bar", sharey=False)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-13-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()


def plot_relative(throughputs):
    throughputs = throughputs.set_index(["Mode", "Query"])
    throughputs.columns = ["Relative Throughput"]
    slowdowns = []
    for i in range(1, 6, 2):
        slowdowns.append(throughputs.loc[setting_names[i], :] / throughputs.loc[setting_names[i - 1], :] - 1)

    figure_hue_names = ["None", "Agg", "Join"]

    for name, df in zip(figure_hue_names, slowdowns):
        df["Mode"] = name

    slowdown = pd.concat(slowdowns, axis=0)

    # plt.figure(figsize=(6, 3.25))
    p = sns.barplot(slowdown, x="Query", y="Relative Throughput", hue='Mode', hue_order=figure_hue_names)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)

    average_slowdowns = slowdown.groupby('Mode')["Relative Throughput"].mean()

    for i, setting in enumerate(figure_hue_names):
        plt.axhline(y=average_slowdowns[setting], color=sns.color_palette()[i], linestyle="--")

    plt.axhline(y=0, color="grey", linestyle="--")

    plt.xticks(rotation=90)
    plt.ylim(bottom=-1, top=1)
    # y_ticks = list(plt.yticks()[0]) + list(average_slowdowns)
    # plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-13-relative-throughput.pdf", **PLOT_DEFAULTS)
    plt.close()


def plot_improvement_plain(throughputs):
    throughputs = throughputs.set_index(["Mode", "Query"])
    throughputs.columns = ["Relative Throughput"]
    slowdowns = []
    for i in [2, 4]:
        slowdowns.append(throughputs.loc[setting_names[i], :] / throughputs.loc[setting_names[0], :] - 1)

    figure_hue_names = ["Unroll Agg Rel.", "Unroll Join Rel."]

    for name, df in zip(figure_hue_names, slowdowns):
        df["Mode"] = name

    slowdown = pd.concat(slowdowns, axis=0)

    palette = [sns.color_palette()[3], sns.color_palette()[2]]
    hatches = ['--', '\\\\']

    plt.figure(figsize=(6, 3.25))
    p = sns.barplot(slowdown, x="Query", y="Relative Throughput", hue='Mode', hue_order=figure_hue_names)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)

    average_slowdowns = slowdown.groupby('Mode')["Relative Throughput"].mean()

    for i, bar in enumerate(p.patches):
       if i // 22 == 0:
           bar.set_hatch(hatches[0])
       elif i // 22 == 1:
           bar.set_hatch(hatches[1])

    for hatch, handle in zip(hatches, p.axes.get_legend().legend_handles):
       handle.set_hatch(hatch)

    for i, setting in enumerate(figure_hue_names):
        plt.axhline(y=average_slowdowns[setting], color=sns.color_palette()[i], linestyle="--")

    plt.axhline(y=0, color="grey", linestyle="--")

    plt.xticks(rotation=90)
    plt.ylim(bottom=-1, top=1)
    # y_ticks = list(plt.yticks()[0]) + list(average_slowdowns)
    # plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-13-improvement-plain.pdf", **PLOT_DEFAULTS)
    plt.close()


def plot_improvement_mititgation(throughputs):
    throughputs = throughputs.set_index(["Mode", "Query"])
    throughputs.columns = ["Relative Throughput"]
    slowdowns = []
    for i in [3, 5]:
        slowdowns.append(throughputs.loc[setting_names[i], :] / throughputs.loc[setting_names[1], :] - 1)

    figure_hue_names = ["Mitigation Agg Rel.", "Mitigation Join Rel."]

    for name, df in zip(figure_hue_names, slowdowns):
        df["Mode"] = name

    slowdown = pd.concat(slowdowns, axis=0)

    palette = [sns.color_palette()[3], sns.color_palette()[2]]
    hatches = ['--', '\\\\']

    plt.figure(figsize=(6, 3.25))
    p = sns.barplot(slowdown, x="Query", y="Relative Throughput", hue='Mode', hue_order=figure_hue_names)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)

    average_slowdowns = slowdown.groupby('Mode')["Relative Throughput"].mean()

    for i, bar in enumerate(p.patches):
       if i // 22 == 0:
           bar.set_hatch(hatches[0])
       elif i // 22 == 1:
           bar.set_hatch(hatches[1])

    for hatch, handle in zip(hatches, p.axes.get_legend().legend_handles):
       handle.set_hatch(hatch)

    for i, setting in enumerate(figure_hue_names):
        plt.axhline(y=average_slowdowns[setting], color=sns.color_palette()[i], linestyle="--")

    plt.axhline(y=0, color="grey", linestyle="--")

    plt.xticks(rotation=90)
    plt.ylim(bottom=-1, top=1)
    # y_ticks = list(plt.yticks()[0]) + list(average_slowdowns)
    # plt.yticks(y_ticks, [round(tick, 2) for tick in y_ticks])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "exp-13-improvement-mitigation.pdf", **PLOT_DEFAULTS)
    plt.close()


def main():
    files = [f"exp-13-results-{x}{y}" for x in ["none", "agg", "join"] for y in ["", "-mitigation"]] + ["exp-13-results-join-sgx"]
    files = load_json_files_list(files, setting_names)

    throughputs = extract_throughput_df(files)

    configure_seaborn()
    plot_absolute(throughputs)
    plot_relative(throughputs)
    plot_improvement_plain(throughputs)
    plot_improvement_mititgation(throughputs)


if __name__ == '__main__':
    main()
