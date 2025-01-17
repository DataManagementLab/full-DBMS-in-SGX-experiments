import os
import pathlib
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Callable

import prctl
import termcolor

import helpers.paths as paths
from helpers.config import MachineConfig


@dataclass
class HyriseTPCHConfig:
    scale_factor: int = 1
    warmup: int = 1
    time: int = 60
    scheduler: bool = False
    clients: int = 1
    cores: int = 1
    data_prep_cores: int = 1
    shuffle_queries: bool = False
    output_file: str = "out.json"
    queries: list = field(default_factory=list)

    def to_parameter_list(self):
        if len(self.queries) > 0:
            queries = self.queries
        else:
            queries = [str(i) for i in range(1, 23)]

        return ["-s", str(self.scale_factor),
                "-t", str(self.time),
                "-w", str(self.warmup),
                f"--scheduler={str(self.scheduler).lower()}",
                "--cores", str(self.cores),
                "--clients", str(self.clients),
                "--data_preparation_cores", str(self.data_prep_cores),
                "--mode", "Shuffled" if self.shuffle_queries else "Ordered",
                "-o", f"results/{self.output_file}",
                "-q", ",".join(queries)]


class BuildMode(Enum):
    RELEASE = 0
    DEBUG = 1
    RELDBG = 2

    def cmake(self) -> str:
        if self == BuildMode.RELEASE:
            return "Release"
        if self == BuildMode.DEBUG:
            return "Debug"
        if self == BuildMode.RELDBG:
            return "RelWithDebInfo"

    def meson(self) -> str:
        if self == BuildMode.RELEASE:
            return "release"
        if self == BuildMode.DEBUG:
            return "debug"
        if self == BuildMode.RELDBG:
            return "debugoptimized"


@dataclass
class GramineBuildConfig:
    source_root: pathlib.Path = paths.SOURCE_ROOT / "gramine"
    build_mode: BuildMode = BuildMode.RELDBG
    install_root_dir: pathlib.Path = pathlib.Path.home() / "gramine-bin"
    direct: bool = True
    sgx: bool = True
    debug_configuration: bool = False
    flags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.source_root, str):
            self.source_root = pathlib.Path(self.source_root)
        if isinstance(self.install_root_dir, str):
            self.install_root_dir = pathlib.Path(self.install_root_dir)

    def get_config_descriptor(self) -> str:
        flag_str = '-'.join([flag[2:] for flag in self.flags]).replace('=', '-')
        return f"auto-{self.build_mode.meson()}{'-' if len(self.flags) else ''}{flag_str}"

    def get_build_dir(self) -> pathlib.Path:
        return self.source_root / f"buildDir-auto-{self.get_config_descriptor()}"

    def get_install_dir(self) -> pathlib.Path:
        return self.install_root_dir / self.get_config_descriptor()

    def configure(self):
        build_dir = self.get_build_dir()
        build_dir.mkdir(exist_ok=True)

        meson_args: list[str] = ["meson",
                                 "setup",
                                 "--reconfigure",
                                 f"--buildtype={self.build_mode.meson()}",
                                 f"--prefix={self.get_install_dir()}",
                                 f"-Ddirect={'enabled' if self.direct else 'disabled'}",
                                 f"-Dsgx={'enabled' if self.sgx else 'disabled'}",
                                 str(build_dir),
                                 str(self.source_root)]
        meson_args += self.flags
        run_batch(meson_args, "Gramine meson configuration failed", print_output=self.debug_configuration)

    def compile(self):
        build_dir = self.get_build_dir()
        if not build_dir.is_dir():
            raise ValueError("Build directory does not exist!")

        meson_args: list[str] = ["meson", "compile", "-C", str(build_dir)]
        run_batch(meson_args, "Gramine meson build failed", print_output=self.debug_configuration)

    def install(self):
        build_dir = self.get_build_dir()
        if not build_dir.is_dir():
            raise ValueError("Build directory does not exist!")

        meson_args: list[str] = ["meson", "install", "-C", str(build_dir)]
        run_batch(meson_args, "Gramine meson install failed", print_output=self.debug_configuration)

    def prepare(self):
        self.configure()
        self.compile()
        self.install()

    def get_gramine_env(self):
        gramine_install_dir = self.get_install_dir()
        env = get_env()
        env['PATH'] = f"{gramine_install_dir}/bin:{env['PATH']}"
        env['PYTHONPATH'] = f"{gramine_install_dir}/lib/python{sys.version[:4]}/site-packages:{env['PYTHONPATH']}"
        env['PKG_CONFIG_PATH'] = f"{gramine_install_dir}/lib/x86_64-linux-gnu/pkgconfig:{env['PKG_CONFIG_PATH']}"
        return os.environ | env


class GramineMode(Enum):
    SGX = "SGX"
    DIRECT = "DIRECT"


@dataclass
class GramineExperimentConfig:
    mode: GramineMode = GramineMode.DIRECT
    debug: int = 0
    stats: bool = False
    optimize: bool = False
    profile: bool = False
    log_file: str = "default.glog"
    debug_configuration: bool = False
    source_root: pathlib.Path = paths.SOURCE_ROOT / "manifests" / "hyrise"
    install_root_dir: pathlib.Path = pathlib.Path.home() / "bin"

    def __post_init__(self):
        if isinstance(self.source_root, str):
            self.source_root = pathlib.Path(self.source_root)
        if isinstance(self.install_root_dir, str):
            self.install_root_dir = pathlib.Path(self.install_root_dir)

    def install(self):
        shutil.copy(self.source_root / "Makefile", self.install_root_dir)
        shutil.copy(self.source_root / "tpch-bench.manifest.template", self.install_root_dir)

    def make_gramine_config(self, environment):
        self.install()
        make_arguments = ["make",
                          f"SGX={int(self.mode == GramineMode.SGX)}",
                          f"DEBUG={self.debug}",
                          f"STATS={int(self.stats)}",
                          f"OPTIMIZE={int(self.optimize)}",
                          f"LOG_FILE=logs/{self.log_file}",
                          f"PROFILE={int(self.profile)}", ]
        clean_arguments = ["make", "clean"]

        run_batch(clean_arguments, "Make clean failed", print_output=self.debug_configuration,
                  environment=environment, print_environment=True, cwd=self.install_root_dir)
        run_batch(make_arguments, "Make Gramine config failed", print_output=self.debug_configuration,
                  environment=environment, print_environment=True, cwd=self.install_root_dir)


@dataclass
class HyriseBuildConfig:
    source_root: pathlib.Path = paths.SOURCE_ROOT / "hyrise"
    build_mode: BuildMode = BuildMode.RELEASE
    debug_configuration: bool = False
    install_root_dir: pathlib.Path = pathlib.Path.home() / "bin"
    flags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.source_root, str):
            self.source_root = pathlib.Path(self.source_root)
        if isinstance(self.install_root_dir, str):
            self.install_root_dir = pathlib.Path(self.install_root_dir)

    def get_build_dir(self) -> pathlib.Path:
        flag_string = '-'.join([flag[2:] for flag in self.flags]).replace('=', '-')
        build_dir_name = f"cmake-build-auto-{self.build_mode.cmake()}{'-' if len(self.flags) else ''}{flag_string}"
        return self.source_root / build_dir_name

    def configure(self):
        build_dir = self.get_build_dir()
        build_dir.mkdir(exist_ok=True)

        cmake_args: list[str] = ["cmake",
                                 "-G", "Ninja",
                                 "-DCMAKE_MAKE_PROGRAM=ninja",
                                 f"-DCMAKE_C_COMPILER={MachineConfig['hyrise_c_compiler']}",
                                 f"-DCMAKE_CXX_COMPILER={MachineConfig['hyrise_cpp_compiler']}",
                                 f"-DHYRISE_LINKER={MachineConfig['hyrise_linker']}",
                                 f"-DCMAKE_BUILD_TYPE={self.build_mode.cmake()}",
                                 "-B", str(build_dir),
                                 "-S", str(self.source_root)]
        cmake_args += self.flags
        run_batch(cmake_args, "Hyrise cmake configuration failed", print_output=self.debug_configuration)

    def compile(self):
        build_dir = self.get_build_dir()
        if not build_dir.is_dir():
            raise ValueError("Build directory does not exist!")

        cmake_args: list[str] = ["cmake", "--build", str(build_dir), "-t", "hyriseBenchmarkTPCH"]
        run_batch(cmake_args, "Hyrise build failed", print_output=self.debug_configuration)

    def install(self):
        build_dir = self.get_build_dir()
        bin_dir = self.install_root_dir
        lib_dir = bin_dir / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)

        termcolor.cprint(f"Installing Hyrise from {build_dir}", color="blue")

        shutil.copy(build_dir / "hyriseBenchmarkTPCH", bin_dir)
        shutil.copy(build_dir / "lib" / "libhyrise_impl.so", lib_dir)

        if '-DUSE_JEMALLOC=OFF' not in self.flags:
            shutil.copy(build_dir / "third_party/jemalloc/lib/libjemalloc.so.2", lib_dir)

    def prepare(self):
        self.configure()
        self.compile()
        self.install()


class ExperimentMode(Enum):
    PLAIN = "PLAIN"
    DIRECT = "DIRECT"
    SGX = "SGX"


@dataclass
class ExperimentConfig:
    mode: ExperimentMode = ExperimentMode.PLAIN
    numa_pin: Optional[int] = None
    perf: bool = False
    perf_file_name: str = "perf.data"
    mitigation: bool = False
    gramine_build_config: Optional[GramineBuildConfig] = None
    hyrise_build_config: HyriseBuildConfig = field(default_factory=HyriseBuildConfig)
    gramine_experiment_config: Optional[GramineExperimentConfig] = None
    tpch_config: HyriseTPCHConfig = field(default_factory=HyriseTPCHConfig)
    install_root_dir: pathlib.Path = pathlib.Path.home() / "bin"

    def __post_init__(self):
        if isinstance(self.install_root_dir, str):
            self.install_root_dir = pathlib.Path(self.install_root_dir)

    def to_parameter_list(self):
        if self.numa_pin is None:
            numa_options = []
        else:
            numa_options = ["numactl", "-N", str(self.numa_pin), "-m", str(self.numa_pin), "--"]

        if self.perf and self.mode != ExperimentMode.SGX:
            perf_options = ["perf", "record", "-e", "cpu-clock", "-F", "101", "--call-graph", "dwarf",
                            "-o", self.perf_file_name, "--"]
        elif self.perf and self.mode == ExperimentMode.SGX:
            print("Perf not available for Gramine SGX mode. Use GramineExperimentConfig.profile=True.")
            perf_options = []
        else:
            perf_options = []

        if self.mode == ExperimentMode.PLAIN:
            application = ["./hyriseBenchmarkTPCH"]
        elif self.mode == ExperimentMode.SGX:
            application = ["gramine-sgx", "tpchbench"]
        elif self.mode == ExperimentMode.DIRECT:
            application = ["gramine-direct", "tpchbench"]
        else:
            raise ValueError(f"Unrecognized mode: {self.mode}")

        return numa_options + perf_options + application + self.tpch_config.to_parameter_list()

    def run(self):
        if self.gramine_build_config is None:
            env = get_env()
        else:
            env = self.gramine_build_config.get_gramine_env()
        if self.mode != ExperimentMode.PLAIN:
            if self.gramine_build_config is None:
                raise ValueError("Gramine Build Config required for modes sgx and direct!")
            self.gramine_experiment_config.make_gramine_config(env)
            (self.install_root_dir / "logs").mkdir(exist_ok=True)

        parameters = self.to_parameter_list()

        if self.mitigation:
            def disable_write_position_speculation():
                try:
                    prctl.set_speculation_ctrl(prctl.SPEC_STORE_BYPASS, 1 << 2)  # set 3rd bit from the right
                except Exception as e:
                    print("set_speculation_ctrl failed")
                    print(e)
        else:
            disable_write_position_speculation = None

        (self.install_root_dir / "results").mkdir(exist_ok=True)
        debug_print(parameters, environment=env, cwd=self.install_root_dir,
                    preexec_fn=disable_write_position_speculation)
        run_stream(parameters, environment=env, cwd=self.install_root_dir,
                   preexec_fn=disable_write_position_speculation)

        self.move_perf_file()

    def move_perf_file(self):
        if self.gramine_experiment_config is None or not self.gramine_experiment_config.profile:
            return

        # rename the latest profile result
        p_files = [(path, path.stat().st_mtime) for path in self.install_root_dir.glob("sgx-perf*.data")]

        if len(p_files) == 0:
            print("Unable to find profile result! Not moved!")

        max_path: pathlib.Path = None
        max_time = 0

        for (path, time) in p_files:
            if time > max_time:
                max_path = path
                max_time = time

        (self.install_root_dir / "gramine-perf-logs").mkdir(exist_ok=True)

        destination_path = self.install_root_dir / "gramine-perf-logs" / self.perf_file_name
        shutil.move(max_path, destination_path)

        print(f"Moved {max_path} to {destination_path}")


def debug_print(command: list[str], *, environment: Optional[dict] = None, cwd: Optional[pathlib.Path] = None,
                preexec_fn: Optional[Callable[[], None]] = None) -> None:
    termcolor.cprint(f"Running {' '.join(command)}", color="blue")
    termcolor.cprint(datetime.now().astimezone().replace(microsecond=0).isoformat(), color="blue")
    not_set: list[str] = []
    if environment is not None:
        termcolor.cprint("In environment:" +
              f"\n  PATH={environment['PATH'][:environment['PATH'].find(':')]}" +
              f"\n  PYTHONPATH={environment['PYTHONPATH']}" +
              f"\n  PKG_CONFIG_PATH={environment['PKG_CONFIG_PATH']}",
              color="light_blue")
    else:
        not_set.append("environment")
    if cwd is not None:
        termcolor.cprint(f"In working directory: {cwd}", color="light_blue")
    else:
        not_set.append("cwd")
    if preexec_fn is not None:
        termcolor.cprint(f"Running preexec_fn: {preexec_fn.__name__}", color="light_blue")
    else:
        not_set.append("preexec_fn")
    termcolor.cprint(f"Not set: {','.join(not_set)}", color="light_blue")


def run_batch(args: list[str], error_message: str, *, environment: Optional[dict] = None,
              cwd: Optional[pathlib.Path] = None, print_output: bool = False,
              print_environment=False):
    if environment is None and print_environment:
        environment = os.environ

    try:
        debug_print(args, environment=environment, cwd=cwd)
        output = subprocess.check_output(args, env=environment, cwd=cwd).decode(sys.stdout.encoding)
        if print_output:
            print(output)
    except subprocess.CalledProcessError as e:
        termcolor.cprint(error_message, color="red", attrs=["bold"])
        termcolor.cprint(f"Error code: {e.returncode}", color="red", attrs=["bold"])
        print("stdout:")
        print(e.stdout.decode(sys.stdout.encoding))
        print("stderr:")
        print(e.stderr.decode(sys.stdout.encoding))


def run_stream(args: list[str], *, environment: Optional[dict] = None, cwd: Optional[pathlib.Path] = None,
               preexec_fn: Optional[Callable[[], None]] = None):
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               encoding="utf-8", env=environment, cwd=cwd, preexec_fn=preexec_fn)
    for line in iter(process.stdout.readline, ""):
        sys.stdout.write(line)


def get_env():
    path = os.environ.get("PATH", "")
    pythonpath = os.environ.get("PYTHONPATH", "")
    pkg_config_path = os.environ.get("PKG_CONFIG_PATH", "")

    return {"PATH": path, "PYTHONPATH": pythonpath, "PKG_CONFIG_PATH": pkg_config_path}

def announce_experiment(name: str):
    print("\n\n")
    termcolor.cprint(f"Starting {name}!", color="green", attrs=["bold"])
    termcolor.cprint(f"Start time {datetime.now().astimezone().replace(microsecond=0).isoformat()}", color="green")
