#!/usr/bin/env python3
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import Series
import termcolor

import helpers.paths as paths
from helpers.plot import PLOT_DEFAULTS, configure_seaborn


def extract_data(input_file_path):
    try:
        with open(input_file_path) as f:
            lines = [line for line in f.readlines() if len(line) > 0 and line[0] == ' ']
    except OSError:
        termcolor.cprint(f"Could not open {input_file_path}! Did you run paper-exp-2-perf-extraction.sh?", color="red")
        exit(1)

    table = [line.split(maxsplit=5) for line in lines]

    # np.array(table).reshape(-1, len(table))

    df = pd.DataFrame(data=table, columns=["Overhead", "Samples", "Command", "Shared Object", "Point", "Symbol"])
    df["Symbol"] = df["Symbol"].astype(str).str[:-1]
    df["Samples"] = df["Samples"].astype(int)

    samples_per_so = df.groupby("Shared Object")["Samples"].sum()
    samples_total = df["Samples"].sum()

    mem_functions = [
        ("libsysdb.so", "free_vma"),
        ("libsysdb.so", "get_mem_obj_from_mgr_enlarge.constprop.0"),
        ("libsysdb.so", "bkeep_mmap_fixed"),
        ("libsysdb.so", "dump_vmas"),
        ("libsysdb.so", "avl_tree_prev"),
        ("libsysdb.so", "bkeep_mmap_any_in_range"),
        ("libpal.so", "memset"),
    ]

    rows_with_mem_functions_index = Series(data=[False] * len(df))

    for lib, func in mem_functions:
        rows_with_mem_functions_index |= (df["Shared Object"] == lib) & (df["Symbol"] == func)

    rows_with_mem_functions = df.loc[rows_with_mem_functions_index]

    samples_memory_management = rows_with_mem_functions["Samples"].sum()

    print(samples_per_so.to_string())
    print(samples_memory_management)

    relative_so = samples_per_so / samples_total
    relative_memory_management = samples_memory_management / samples_total
    relative_libos_mm = samples_memory_management / (samples_per_so["libsysdb.so"] + samples_per_so["libpal.so"])

    relative_so = relative_so.reset_index()
    relative_so.columns = ["Library", "Runtime\nPercentage"]

    libraries = {
        "ld-linux-x86-64.so.2": "others",
        "libboost_container.so.1.83.0": "others",
        "libc.so.6": "libc",
        "hyriseBenchmarkTPCH": "Hyrise",
        "libhyrise_impl.so": "Hyrise",
        "libjemalloc.so.2": "others",
        "libpal.so": "LibOS",
        "libstdc++.so.6.0.33": "others",
        "libsysdb.so": "LibOS",
        "libtbb.so.12.11": "others",
        "libm.so.6": "others",
        "[unknown]": "others"
    }

    relative_so["Library"] = relative_so["Library"].replace(libraries)
    relative_so = relative_so.groupby("Library").sum().reset_index()

    print(f"Percentage in memory management: {relative_memory_management:.3f}")
    print(f"Percentage LibOS in memory management: {relative_libos_mm:.3f}")

    return relative_so


def plot():
    files = [paths.RESULT_PATH / f"perf-before-opt-{i}.txt" for i in range(10)]
    relative_so = pd.concat([extract_data(file) for file in files], axis=0)
    print(relative_so.to_string())

    configure_seaborn()
    plt.figure(figsize=(4.5, 2.25))
    p = sns.barplot(x="Library", y="Runtime\nPercentage", order=["LibOS", "Hyrise", "libc", "others"], data=relative_so,
                    color=sns.color_palette()[2], errorbar="sd")

    for bar in p.patches:
        bar.set_hatch('\\\\')
    plt.ylim(top=1, bottom=0)
    plt.grid(axis='y')
    plt.yticks([0, 0.2, 0.4, 0.6, 0.8, 1], ["0%", "20%", "40%", "60%", "80%", "100%"])
    plt.tight_layout()
    plt.savefig(paths.IMG_PATH / "paper-plot-2.pdf", **PLOT_DEFAULTS)
    plt.close()


def main():
    plot()


if __name__ == '__main__':
    main()
