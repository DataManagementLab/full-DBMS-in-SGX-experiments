import json
from typing import Iterable, Optional

import pandas as pd
from pandas import DataFrame

import helpers.paths as paths


CSV_SETTINGS = {"header": 0, "skipinitialspace": True}


def load_json_files(direct: str, plain: str, sgx: str) -> list[(dict, str)]:
    with open(paths.RESULT_PATH / f"{plain}.json") as f_plain, open(
            paths.RESULT_PATH / f"{direct}.json") as f_direct, open(paths.RESULT_PATH / f"{sgx}.json") as f_sgx:
        j_plain = json.load(f_plain)
        j_direct = json.load(f_direct)
        j_sgx = json.load(f_sgx)
    data = [(j_plain, "plain"), (j_direct, "direct"), (j_sgx, "sgx")]
    return data


def load_json_files_list(files: Iterable[str], names: Optional[list] = None) -> list[(dict, str)]:
    dicts: list[(dict, str)] = []

    if names is None:
        for i, file in enumerate(files):
            with open(paths.RESULT_PATH / f"{file}.json") as f:
                dicts.append((json.load(f), f"File {i + 1}"))
    else:
        for name, file in zip(names, files, strict=True):
            with open(paths.RESULT_PATH / f"{file}.json") as f:
                dicts.append((json.load(f), name))

    return dicts


def rename_files(files: list[(dict, str)], names: list[str]):
    return [(d, s) for (d, _), s in zip(files, names, strict=True)]


def load_throughputs_latencies(plain, direct, sgx) -> (DataFrame, DataFrame):
    data = load_json_files(direct, plain, sgx)
    return extract_latency_df(data), extract_throughput_df(data)


def extract_throughput_df(data: list[(dict, str)]) -> DataFrame:
    throughputs = pd.concat([extract_throughput(result_dict, mode) for result_dict, mode in data], axis=0,
                            ignore_index=True)
    return throughputs


def extract_latency_df(data: list[(dict, str)]) -> DataFrame:
    latencies = pd.concat([extract_latencies(result_dict, mode) for result_dict, mode in data], axis=0,
                          ignore_index=True)
    return latencies


def extract_average_latency(result_dict: dict, mode) -> DataFrame:
    average_latency = [
        (f"Q{i + 1}", (sum(run["duration"] for run in query["successful_runs"]) / len(query["successful_runs"]))) for
        i, query in enumerate(result_dict["benchmarks"])]

    df = DataFrame(average_latency, columns=["Query", "Average Latency"])
    df["Mode"] = mode

    return df


def extract_latencies(result_dict: dict, mode) -> DataFrame:
    latencies = [(f"Q{i + 1}", run["duration"]) for i, query in enumerate(result_dict["benchmarks"]) for run in
                 query["successful_runs"]]

    df = DataFrame(latencies, columns=["Query", "Latency"])
    df["Mode"] = mode
    df["Latency in ms"] = df["Latency"] // 10 ** 6

    return df


def extract_throughput(result_dict: dict, mode) -> DataFrame:
    throughput = [(f"Q{query["name"].split(' ')[1].lstrip('0')}", query["items_per_second"]) for i, query in enumerate(result_dict["benchmarks"])]

    df = DataFrame(throughput, columns=["Query", "Throughput"])
    df["Mode"] = mode

    return df
