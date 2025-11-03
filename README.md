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


## Usage

```
usage: rsd [-h] {insert,matrix,link} ...

RSD: A Python library for Real-time SNP Distance estimation.

options:
  -h, --help            show this help message and exit

subcommands:
  {insert,matrix,link}
    insert              Insert sample into SNP database.
    matrix              Extract SNP distance matrix from database.
    link                Link samples in SNP database.
```

The `insert` subcommand allows you to insert a new sample into an existing SNP distance database and compute its distances to other samples.

```bash
usage: rsd insert [-h] --read1 READ1 --read2 READ2 --ref REF --output-db
                  OUTPUT_DB --sample-name SAMPLE_NAME [--min-depth MIN_DEPTH]
                  [--min-af MIN_AF]
                  [--excluded-regions-bed EXCLUDED_REGIONS_BED]
                  [--snp-distance-cutoff SNP_DISTANCE_CUTOFF]
                  [--mapper {bwa,minimap2}] [--caller {freebayes,bcftools}]
                  [--samclip] [--platform {illumina,nanopore}]
                  [--threads THREADS] [--version]

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

Input/Output Options:
  --read1 READ1, -1 READ1
                        First read file
  --read2 READ2, -2 READ2
                        Second read file
  --ref REF, -r REF     Reference genome file
  --output-db OUTPUT_DB, -o OUTPUT_DB
                        Output file
  --sample-name SAMPLE_NAME, -s SAMPLE_NAME
                        Sample name/prefix

Filtering Options:
  --min-depth MIN_DEPTH
                        Minimum depth for consensus generation
  --min-af MIN_AF       Minimum allele frequency for variant calling
  --excluded-regions-bed EXCLUDED_REGIONS_BED
                        BED file with regions to exclude from consensus
  --snp-distance-cutoff SNP_DISTANCE_CUTOFF
                        SNP distance cutoff for database storage

Algorithm Options:
  --mapper {bwa,minimap2}, -m {bwa,minimap2}
                        Mapper to use
  --caller {freebayes,bcftools}, -c {freebayes,bcftools}
                        Variant caller to use
  --samclip             Enable samclip to clip reads with large soft/hard
                        clips
  --platform {illumina,nanopore}
                        Sequencing platform
  --threads THREADS, -t THREADS
                        Number of threads to use
```

The `matrix` subcommand allows you to extract the SNP distance matrix from an existing SNP distance database.

```bash
usage: rsd matrix [-h] --input-db INPUT_DB --output-matrix OUTPUT_MATRIX

options:
  -h, --help            show this help message and exit
  --input-db INPUT_DB, -i INPUT_DB
                        Input SNP database file
  --output-matrix OUTPUT_MATRIX, -o OUTPUT_MATRIX
                        Output SNP distance matrix file
```

The `link` subcommand allows you to examine links between two samples in the SNP distance database to retrieve their SNP distance and extract all different positions.

```bash
usage: rsd link [-h] --input-db INPUT_DB --source SOURCE --target TARGET

options:
  -h, --help            show this help message and exit
  --input-db INPUT_DB, -i INPUT_DB
                        Input SNP database file
  --source SOURCE, -s SOURCE
                        Source sample name
  --target TARGET, -t TARGET
                        Target sample name
```