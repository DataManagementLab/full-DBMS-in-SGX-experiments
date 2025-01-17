#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import CSV_SETTINGS
from helpers.paths import RESULT_PATH
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def including_mitigation():
    plain = pd.read_csv(RESULT_PATH / "btree-plain.csv", **CSV_SETTINGS)
    mitigation = pd.read_csv(RESULT_PATH / "btree-mitigation.csv", **CSV_SETTINGS)
    trusted = pd.read_csv(RESULT_PATH / "btree-trusted.csv", **CSV_SETTINGS)

    setting_names = ["plain", "mitigation", "sgx"]

    plain["setting"] = setting_names[0]
    mitigation["setting"] = setting_names[1]
    trusted["setting"] = setting_names[2]

    data = pd.concat([plain, mitigation, trusted])

    data = data[data["ts"] != 0]

    means = data.groupby(["setting", "readratio"])["ops"].mean()

    slowdown_mitigation = means.loc[setting_names[1], :] / means.loc[setting_names[0], :]
    slowdown_sgx = means.loc[setting_names[2], :] / means.loc[setting_names[0], :]

    figure_hue_names = ["Mitigation", "SGX"]

    slowdown_mitigation = slowdown_mitigation.reset_index()
    slowdown_sgx = slowdown_sgx.reset_index()

    slowdown_mitigation.columns = ["Workload", "Performance Relative\nto Plain CPU"]
    slowdown_sgx.columns = ["Workload", "Performance Relative\nto Plain CPU"]

    slowdown_mitigation["Mode"] = figure_hue_names[0]
    slowdown_sgx["Mode"] = figure_hue_names[1]

    slowdown = pd.concat([slowdown_mitigation, slowdown_sgx], axis=0)
    slowdown.replace({"Workload": {5: "5%R\n95%W", 50: "50%R\n50%W", 95: "95%R\n5%W", 100: "100%R"}}, inplace=True)

    print(slowdown.to_string())

    configure_seaborn()

    palette = [sns.color_palette()[3], sns.color_palette()[2]]
    hatches = ['--', '\\\\']

    plt.figure(figsize=(4.5, 2.5))
    p = sns.barplot(slowdown, x="Workload", y="Performance Relative\nto Plain CPU", hue='Mode', hue_order=figure_hue_names,
                    palette=palette)
    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.5, 1), ncols=2, title=None)

    for i, bar in enumerate(p.patches):
        if i // 4 == 0:
            bar.set_hatch(hatches[0])
        elif i // 4 == 1:
            bar.set_hatch(hatches[1])

    for hatch, handle in zip(hatches, p.axes.get_legend().legend_handles):
        handle.set_hatch(hatch)

    plt.grid(axis='y')
    plt.yticks([0, 0.25, 0.5, 0.75, 1])
    plt.ylim(bottom=0, top=1)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-btree.pdf", **PLOT_DEFAULTS)
    plt.close()


def without_mitigation():
    plain = pd.read_csv(RESULT_PATH / "btree-plain.csv", **CSV_SETTINGS)
    trusted = pd.read_csv(RESULT_PATH / "btree-trusted.csv", **CSV_SETTINGS)

    setting_names = ["plain", "mitigation", "sgx"]

    plain["setting"] = setting_names[0]
    trusted["setting"] = setting_names[2]

    data = pd.concat([plain, trusted])

    data = data[(data["ts"] != 0) & (data["readratio"] < 100)]

    means = data.groupby(["setting", "readratio"])["ops"].mean()

    slowdown_sgx = means.loc[setting_names[2], :] / means.loc[setting_names[0], :]
    slowdown_sgx = slowdown_sgx.reset_index()

    slowdown_sgx.columns = ["Workload", "Performance Relative\nto Plain CPU"]
    slowdown_sgx.replace({"Workload": {5: "5%R 95%W", 50: "50%R 50%W", 95: "95%R 5%W", 100: "100%R"}}, inplace=True)

    print(slowdown_sgx.to_string())

    configure_seaborn()

    plt.figure(figsize=(6, 2.5))
    p = sns.barplot(slowdown_sgx, x="Workload", y="Performance Relative\nto Plain CPU", color=sns.color_palette()[2])

    for bar in p.patches:
        bar.set_hatch('\\\\')

    plt.ylim(bottom=0, top=1)
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-btree-no-mitigation.pdf", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    including_mitigation()
    without_mitigation()
