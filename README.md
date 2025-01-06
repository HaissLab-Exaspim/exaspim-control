- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Recommended Hardware](#recommended-hardware)
  - [Installation](#installation)
  - [Documentation](#documentation)
  - [Usage](#usage)
- [Support and Contribution](#support-and-contribution)
- [License](#license)

## Overview

This repository provides acquisition software for the expansion-assisted selective plane illumination microscope (ExA-SPIM).

> **Expansion-assisted selective plane illumination microscopy for nanoscale imaging of centimeter-scale tissues.** eLife **12**:RP91979
*https://doi.org/10.7554/eLife.91979.2*

## Getting Started

### Prerequisites

- **Python: >=3.10, <=3.11** (tested)
- We using a virtual environment:
  - [venv](https://docs.python.org/3.11/library/venv.html)
  - Conda: [Anaconda](https://www.anaconda.com/products/individual) or [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
- For control of some specific devices, you will need the appropriate SDK installed:
  - [voxel](https://github.com/AllenNeuralDynamics/voxel):
    - Core drivers, microscope, and acquisition codebase
  - [view](https://github.com/AllenNeuralDynamics/view):
    - Core GUI codebase

> This control software can optionally check I/O bandwidth to a local and externally networked drive location. This requires [fio](https://github.com/axboe/fio) to be installed. For Windows, please install the correct [binary files](https://github.com/axboe/fio/releases).

### Recommended Hardware

> ⚠️ The ExA-SPIM system operates at data rates up to 1.8 GB/sec. Datasets can also be multiple terabytes. Therefore it is recommended to have a large M.2 or U.2/3 NVME drive for data storage.

> ⚠️ Each raw camera is 288 megapixels (14192x10640 px). Live streaming therefore requires on-the-fly generation of multiple resolutions for each raw camera frame at high speed. This repository computes this pyramid using a GPU. Therefore it is recommended to have a decent GPU with at least 16 GB of RAM (i.e. NVIDIA A4000 or above).

### Installation

1. Create a virtual environment and activate it:
    On Windows:

    ```bash
    conda create -n exaspim-control
    conda activate exaspim-control
    ```

    or

    ```bash
    python -m venv exaspim-control
    .\exaspim-control\Scripts\activate
    ```

2. Clone the repository:

    ```bash
    git clone https://github.com/AllenNeuralDynamics/exaspim-control.git && cd exaspim-control
    ```

3. To use the software, in the root directory, run:

    ```bash
    pip install -e .
    ```

4. To develop the code, run:

    ```bash
    pip install -e .[dev]
    ```

5. To install all dependencies including all optional device drivers, run:

    ```bash
    pip install -e .[all]
    ```

### Documentation

- _(coming soon)_

### Usage

Example configuration files for a real experimental system are provided:

> [instrument.yaml](./exaspim-control/experimental/instrument.yaml)
>
> [acquisition.yaml](./exaspim-control/experimental/acquisition.yaml)
>
> [gui_config.yaml](./exaspim-control/experimental/gui_config.yaml)

And the code can be launched by running [```main.py```](./exaspim-control/experimental/main.py)

Files for a [simulated microscope]And the code can be launched by running [```main.py```](./exaspim-control/simulated/) are also available.

## Support and Contribution

If you encounter any problems or would like to contribute to the project,
please submit an [Issue](https://github.com/AllenNeuralDynamics/exaspim-control/issues)
on GitHub.

## License

exaspim-control is licensed under the MIT License. For more details, see
the [LICENSE](LICENSE) file.