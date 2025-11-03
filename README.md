# rsd: real-time SNP distances for bacterial genomes

> [!WARNING]
> This tool is under active development and should not be used in projection yet.

This tool provides an command-line interface to the rapid SNP distance calculations functionality in `pathogen-profiler`. It estimates SNP distances between bacterial genomes by inserting new samples into a pre-computed SNP distance database. It is designed for real-time surveillance applications where new genomic data is continuously generated.

## Installation

```bash
mamba create -n rsd -c conda-forge -c bioconda pathogen-profiler
mamba activate rsd
pip install git+https://github.com/jodyphelan/pathogen-profiler.git@dev
pip install git+https://github.com/jodyphelan/rsd.git
```