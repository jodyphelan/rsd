import argparse
import rsd
import pathogenprofiler as pp
import logging
logging.basicConfig(level=logging.INFO)


def cli_main(args):

    filters = {
        'af_hard': args.min_af,
        'dp_hard': args.min_depth,
    }

    if args.read1:
        fastq_obj = pp.Fastq(
            r1=args.read1,
            r2=args.read2,
        )

        bam_obj = fastq_obj.map_to_ref(
            ref_file=args.ref,
            prefix=args.sample_name,
            sample_name=args.sample_name,
            aligner=args.mapper,
            platform=args.platform,
            threads=args.threads
        )
    else:
        bam_obj = pp.Bam(
            bam_file=args.bam,
            sample_name=args.sample_name,
            platform=args.platform
        )

    vcf_obj = bam_obj.call_variants(
        ref_file = args.ref,
        caller = args.caller,
        filters = filters, 
        threads = args.threads, 
        samclip = args.samclip, 
        cli_args = vars(args)
    )

    low_depth_mask_filename = f"{args.sample_name}.low_dp.bed"
    pp.generate_low_dp_mask(
        bam=bam_obj.bam_file, 
        ref=args.ref, 
        outfile=low_depth_mask_filename,
        min_dp=args.min_depth
    )

    consensus_filename = f"{args.sample_name}.consensus.fasta"
    excluded_regions = args.excluded_regions_bed if args.excluded_regions_bed else low_depth_mask_filename
    pp.prepare_sample_consensus(
        sample_name=args.sample_name,
        ref=args.ref,
        input_vcf=vcf_obj.filename,
        output_file=consensus_filename,
        excluded_regions=excluded_regions,
        low_dp_regions=low_depth_mask_filename,
    )

    consensus_vcf_filename = f"{args.sample_name}.consensus.vcf"
    pp.consensus_fasta_to_vcf(
        consensus_fasta=consensus_filename,
        ref=args.ref,
        outfile=consensus_vcf_filename
    )

    snp_db = pp.SnpDistDB(args.output_db)

    snp_db.store(
        sample_name=args.sample_name,
        vcf_file=consensus_vcf_filename,
        taxa="bacteria",
        cutoff=args.snp_distance_cutoff
    )

    logging.info(f"Sample {args.sample_name} inserted into database {args.output_db}.")
    
def cli_matrix(args):
    snp_db = pp.SnpDistDB(args.input_db)
    samples,distance_matrix = snp_db.extract_matrix()
    print(samples)
    print(distance_matrix)

def cli_link(args):
    snp_db = pp.SnpDistDB(args.input_db)
    link = snp_db.inspect_link(
        source=args.source,
        target=args.target
    )
    print(link)


def file(path: str) -> str:
    """Check if file exists."""
    try:
        with open(path, 'r'):
            return path
    except FileNotFoundError:
        raise argparse.ArgumentTypeError(f"File {path} does not exist.")

def entrypoint():

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable verbose output'
    )

    parser = argparse.ArgumentParser(
        description="RSD: A Python library for Real-time SNP Distance estimation."
    )
    # create subparser 
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand")

    ### Add insert subparser ###

    subparser_insert = subparsers.add_parser("insert", parents=[base_parser], help="Insert sample into SNP database.")
    input = subparser_insert.add_argument_group("Input/Output Options")
    # add mutually exclusive group for input
    group = input.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--read1',
        '-1',
        help='First read file',
        required=True,
        type=file
    )
    input.add_argument(
        '--read2',
        '-2',
        help='Second read file',
        required=True,
        type=file
    )
    group.add_argument(
        '--bam',
        '-a',
        help='BAM/CRAM file',
        required=False,
        type=file
    )
    input.add_argument(
        '--ref',
        '-r',
        help='Reference genome file',
        required=True,
        type=file
    )
    input.add_argument(
        '--output-db',
        '-o',
        help='Output file',
        required=True
    )
    input.add_argument(
        '--sample-name',
        '-s',
        help='Sample name/prefix',
        required=True
    )

    filtering = subparser_insert.add_argument_group("Filtering Options")
    filtering.add_argument(
        '--min-depth',
        help='Minimum depth for consensus generation',
        type=int,
        default=10
    )
    filtering.add_argument(
        '--min-af',
        help='Minimum allele frequency for variant calling',
        type=float,
        default=0.75
    )
    filtering.add_argument(
        '--excluded-regions-bed',
        help='BED file with regions to exclude from consensus',
        type=file,
        default=None
    )
    filtering.add_argument(
        '--snp-distance-cutoff',
        help='SNP distance cutoff for database storage',
        type=int,
        default=10
    )

    
    algorithms = subparser_insert.add_argument_group("Algorithm Options")
    algorithms.add_argument(
        '--mapper',
        '-m',
        help='Mapper to use',
        default='bwa',
        choices=['bwa', 'minimap2']
    )
    algorithms.add_argument(
        '--caller',
        '-c',
        help='Variant caller to use',
        default='freebayes',
        choices=['freebayes', 'bcftools']
    )
    algorithms.add_argument(
        '--samclip',
        help='Enable samclip to clip reads with large soft/hard clips',
        action='store_true',
    )
    algorithms.add_argument(
        '--platform',
        help='Sequencing platform',
        default='illumina',
        choices=['illumina', 'nanopore']
    )
    algorithms.add_argument(
        '--threads',
        '-t',
        help='Number of threads to use',
        type=int,
        default=1
    )
    subparser_insert.add_argument(
        '--version',
        action='version',
        version=f'RSD v{rsd.__version__}',
    )
    subparser_insert.set_defaults(func=cli_main)
    
    ### End insert subparser ###

    ### Add extract subparser ###
    subparser_matrix = subparsers.add_parser("matrix", parents=[base_parser], help="Extract SNP distance matrix from database.")
    subparser_matrix.add_argument(
        '--input-db',
        '-i',
        help='Input SNP database file',
        required=True
    )
    subparser_matrix.add_argument(
        '--output-matrix',
        '-o',
        help='Output SNP distance matrix file',
        required=True
    )
    subparser_matrix.set_defaults(func=cli_matrix)

    ### End extract subparser ###

    ### Add link subparser ###
    link_subparser = subparsers.add_parser("link", parents=[base_parser], help="Link samples in SNP database.")
    link_subparser.add_argument(
        '--input-db',
        '-i',
        help='Input SNP database file',
        required=True
    )
    link_subparser.add_argument(
        '--source',
        '-s',
        help='Source sample name',
        type=str,
        required=True
    )
    link_subparser.add_argument(
        '--target',
        '-t',
        help='Target sample name',
        type=str,
        required=True
    )
    link_subparser.set_defaults(func=cli_link)
    
    ### End link subparser ###

    ### Parse arguments ###

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

