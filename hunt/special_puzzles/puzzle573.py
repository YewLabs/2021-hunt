
from django.http import FileResponse

from spoilr.decorators import *

import hunt.special_puzzles.dna.utils as utils

import io
import sys

# DNA

LETTERS_DIR = '2021-hunt/hunt/special_puzzles/dna/letters'
CHROM_FASTA = '2021-hunt/hunt/special_puzzles/dna/genome/chromosomes.fasta'
CHROM_DATA = None
PIXEL_GRID = None

DATA_INITIALIZED = False

def initialize():
    global CHROM_DATA, PIXEL_GRID, DATA_INITIALIZED
    CHROM_DATA = utils.get_chromosomes(CHROM_FASTA)
    PIXEL_GRID = utils.get_pixel_grid(LETTERS_DIR)
    DATA_INITIALIZED = True

@require_puzzle_access
def puzzle573_view(request):
    global CHROM_DATA, PIXEL_GRID, DATA_INITIALIZED
    if not DATA_INITIALIZED:
        initialize()
    num_reads = request.GET.get('numreads', '100')
    read_len = request.GET.get('readlen', '100')
    try:
        num_reads = int(num_reads)
        read_len = int(read_len)
    except:
        num_reads = 100
        read_len = 100
    reads = utils.get_reads(num_reads, read_len, CHROM_DATA)
    data = utils.get_fastq(reads, PIXEL_GRID)
    return HttpResponse(data, content_type='application/octet-stream')
