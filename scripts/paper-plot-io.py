#!/usr/bin/env python3

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt

import helpers.paths as paths
from helpers.extract_results import CSV_SETTINGS
from helpers.paths import RESULT_PATH
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def main():
    plain = pd.read_csv(RESULT_PATH / "io_latencies_untrusted.csv", **CSV_SETTINGS)
    trusted = pd.read_csv(RESULT_PATH / "io_latencies_trusted.csv", **CSV_SETTINGS)

    setting_names = ["sgx_fwrite", "sgx_seal_data+OCALL", "untrusted"]

    plain["setting"] = setting_names[2]
    trusted["setting"] = trusted["seal"].replace({True: setting_names[1], False: setting_names[0]})

    data = pd.concat([plain, trusted])

    means = data.groupby(["setting", "datasize"])["latency_cycles"].mean().reset_index()
    means["I/O Cost in Cycles/Byte"] = means["latency_cycles"] / means["datasize"]
    means["I/O Size"] = means["datasize"]

    order = [setting_names[2], setting_names[1], setting_names[0]]

    configure_seaborn()
    plt.figure(figsize=(4.5, 2.5))
    p = sns.lineplot(means, x="I/O Size", y="I/O Cost in Cycles/Byte",
                     hue='setting', hue_order=order, style='setting', style_order=order,
                     markers=True)

    sns.move_legend(p, "lower center", frameon=False, bbox_to_anchor=(0.45, 1), ncols=3, title=None,
                    columnspacing=0.5, handletextpad=0.2, fontsize=9)

    plt.yscale("log")
    plt.xscale("log")
    plt.yticks([2**n for n in [0, 4, 9, 14]], ["1", "16", "512", "16k"])
    plt.xticks([2 ** n for n in [1, 5, 10, 15, 20]], ["2", "32", "1kB", "32kB", "1MB"])
    plt.xlim((2,2**22))
    plt.minorticks_off()
    plt.grid(True, which="major", axis="y")

    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
    plt.savefig(paths.IMG_PATH / "paper-plot-io.pdf", **PLOT_DEFAULTS)
    plt.close()


if __name__ == '__main__':
    main()
