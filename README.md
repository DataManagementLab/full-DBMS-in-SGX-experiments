# SGX Full DBMS Experiments using Hyrise and Gramine

This is the repository containing our experiments investigating the Hyrise in-memory DBMS in SGXv2 using Gramine for the
paper "Towards High-performance and Trusted Cloud DBMSs".

## Abstract

> Cloud Database Management Systems (DBMSs), such as cloud-native analytical or serverless databases, are experiencing 
> rapid growth in adoption due to their flexibility and scalability. However, recent incidents with cloud providers show
> that the traditional model of a trusted provider/admin no longer applies to protect the customers' data. One promising
> solution that can prevent a sole reliance on cloud and database service providers are trusted execution environments 
> (TEEs). While past TEEs had many limitations and caused high performance overheads, recent work shows that the support
> of TEEs like Intel SGX for DBMS workloads improved significantly. Thus, it is time to actively integrate TEE 
> technologies into cloud DBMSs to achieve better security that does not rely on the cloud provider. In this paper, we
> discuss directions for how recent TEEs can be used to build efficient and secure databases. We summarize the recent 
> results on Intel SGX's performance for DBMS workloads and lay out the remaining research challenges that must be 
> addressed to achieve optimal performance and thus minimize the performance cost for additional security.

## Requirements

- Ubuntu 24.04
- [All requirements for compiling Hyrise](https://github.com/hyrise/hyrise/wiki/Step-by-Step-Guide)
- [All requirements for compiling Gramine](https://github.com/DataManagementLab/full-DBMS-in-SGX-Gramine/blob/main/Documentation/devel/building.rst)
- Python package requirements
   ```shell
   sudo apt install build-essential libcap-dev
   ```
- Python packages from `requirements.txt`

## Running the benchmarks

- Clone the repository and both submodules (slightly customized versions of Hyrise and Gramine)
- Move `configs/machine-config.json` to your home directory and adapt the configuration to your desired run directory,
  compiler versions and linker.
- Create a virtual environment, activate it, install `requirements.txt` into it, deactivate it
- **Do not activate the virtual environment!** Instead, set an alias to the python executable in the environment:
  ```shell
  alias vpython=$VIRTUAL_ENV_DIR/bin/python
  ```
  Do this, because the `meson --install` of gramine somehow gets confused by activating the virtual environment and then
  does not install the python packages of gramine to the correct directory.
- Switch to the scripts directory with `cd scripts`
- Run the experiment and plot scripts:
  ```shell
  vpython paper-exp-1-ootb.py
  vpython paper-exp-2-profiling.py
  vpython paper-exp-3-remaining-overheads.py
  vpython paper-exp-4-revision-operator-optimization.py
  ./paper-exp-2-perf-extraction.sh
  vpython paper-plot-1.py
  vpython paper-plot-2.py
  vpython paper-plot-3.py
  vpython paper-plot-4.py
  ```
  The scripts automatically store all results and figures under the run directory specified in `machine-config.json`.
  Compiled versions of gramine are stored under `$HOME/gramine-bin`.
