import io
import sys
import random
import numpy as np
from PIL import Image

def get_chromosomes(fasta_fname):
    """ Returns a dictionary with:
        key: chromosome name (L1, Y, S, etc...)
        value: DNA sequence "ATGACGT..."
    """
    data = {}
    with open(fasta_fname, "r") as f:
        for line in f:
            if line.startswith(">"):
                if "seq" in locals():
                    data[chrom_name] = seq
                chrom_name = line.strip()[1:]
                seq = ""
            else:
                seq += line.strip()
        data[chrom_name] = seq
    return data

def get_reads(num_reads, read_len, chrom_data):
    """
        Arguments:
            num_reads (int): number of reads to generate
            read_len (int): length of reads to generate
            chrom_data: dictionary of chromosome names:sequences

        Returns:
            list of num_reads sequences of chromosomes, with length read_len
            chromosomes to sequence are chosen randomly
            # Took out random starting positions within chromosome to nerf
    """
    chrom_names, seqs = zip(*chrom_data.items())
    num_seqs = len(seqs)
    seq_idxs = random.sample(range(num_seqs), num_seqs)
    if num_reads < len(seq_idxs):
        seq_idxs = seq_idxs[:num_reads]
    else: 
        to_add = num_reads - len(seq_idxs)
        for i in range(min(to_add, 20-num_seqs)):
            seq_idxs.insert(
                random.choice(range(len(seq_idxs))), 
                random.choice(range(num_seqs))
            )
        if len(seq_idxs) < num_reads:
            to_add = num_reads - len(seq_idxs)
            seq_idxs = seq_idxs +\
                [random.choice(range(num_seqs)) for i in range(to_add)]
    reads = []
    for read_idx in range(num_reads):
        #seq_idx = random.choice(range(num_seqs))
        seq_idx = seq_idxs[read_idx]
        chrom_name = chrom_names[seq_idx]
        seq = seqs[seq_idx]
        seq_len = len(seq)
        #read_pieces = [seq for j in range(read_len//seq_len)] +\
        #    [seq[:read_len%seq_len]]
        #read = "".join(read_pieces)
        num_repeats = read_len//seq_len + 2
        start_pos = random.choice(range(seq_len))
        read = seq * num_repeats
        read = read[start_pos:start_pos + read_len]
        reads.append(read)
    return reads

def get_pixel_grid(letters_dir):
    word = "KARYOTYPE"
    # Load images and convert to ascii art
    pixel_grids = []
    for letter in word:
        # Load image
        in_file = "{0}/{1}.png".format(letters_dir, letter)
        im = Image.open(in_file)
        pixels = np.array(im.getdata())
        tot_px = len(pixels)
        h_px = 100
        w_px = 100
        pixels = pixels.reshape([h_px, w_px, 4])
        pixels = pixels.astype('uint8')
        pixels = pixels[:,:,0]
        pixel_grids.append(pixels)
    stacked_pixel_grids = np.vstack(pixel_grids)
    return stacked_pixel_grids

def get_fastq(reads, pixel_grid, out_fname=None):
    dark_chars = "$MWmw&#gNGQBKERZDOC@dpqHSAaeXVPbkhUFzTr"
    light_chars = "sxyunvIYJj{}ilftocL[])(\/|!\"^~;:-_,'.`"
    ascii_lines = []
    pixels_height, pixels_width = pixel_grid.shape
    for idx, read in enumerate(reads):
        read_len = len(read)
        pixel_line = np.concatenate(
            [pixel_grid[idx%pixels_height] for j in range(read_len//pixels_width)] +\
            [pixel_grid[idx%pixels_height][:read_len%pixels_width]]
        )
        ascii_line = []
        for pixel in pixel_line:
            if pixel == 0:
                ascii_line.append(random.choice(light_chars))
            elif pixel == 255:
                ascii_line.append(random.choice(dark_chars))
            else:
                print("invalid pixel!!!")
        ascii_lines.append("".join(ascii_line))

    if out_fname:
        with open(out_fname, "w") as f:
            read_idx = 0
            for read, ascii_line in zip(reads, ascii_lines):
                f.write("@{0}".format(read_idx) + "\n")
                f.write("{0}\n".format(read))
                f.write("+\n")
                f.write("{0}\n".format(ascii_line))
                read_idx += 1
    else:
        out = ''
        read_idx = 0
        for read, ascii_line in zip(reads, ascii_lines):
            out += ("@{0}".format(read_idx) + "\n")
            out += ("{0}\n".format(read))
            out += ("+\n")
            out += ("{0}\n".format(ascii_line))
            read_idx += 1
        return out

#pixel_grid = get_pixel_grid()
