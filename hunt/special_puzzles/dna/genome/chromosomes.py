import copy
import random
import os

#SERINE
#VALINE
#LYSINE
#ALANINE
#GLYCINE
#LEUCINE
#PROLINE
#
#LYSINEETAL


# L: 3 segments, 1500 bp, height 900
#     - 1: 900 down
#     - 2: 600 across
#     - 3: 2 reverse complement
#     - 4: 1 reverse complement
# Y: 3 segments, 1350 bp, height ~710 bp
#     - 1: 525 down/right
#     - 2: 525 up/right
#     - 3: 525 down/left, 2 reverse complement
#     - 4: 300 down
#     - 5: 300 up, 4 reverse complement
#     - 6: 525 up/left, 1 reverse complement
# S: 5 segments, 1200 bp, height 480
#     - 1: 240 left
#     - 2: 240 down
#     - 3: 240 right
#     - 4: 240 down
#     - 5: 240 left
#     - 6: 5 reverse complement
#     - 7: 4 reverse complement
#     - 8: 3 reverse complement
#     - 9: 2 reverse complement
#     - 10: 1 reverse complement
# I: 4 segments, 1050 bp, height 450
#     - 1: 300 right
#     - 2: 150 left, second half of 1 reverse complement
#     - 3: 450 down
#     - 4: 150 right, first half of 5 reverse complement
#     - 5: 300 left
#     - 6: 150 right, second half of 5 reverse complement
#     - 7: 450 up, 3 reverse complement
#     - 8: 150 left, first half of 1 reverse complement
# N: 3 segments, 900 bp
#     - 1: 270 down
#     - 2: 360 up/left
#     - 3: 270 down
#     - 4: 270 up, 3 reverse complement
#     - 5: 360 down/right, 2 reverse complement
#     - 6: 270 up, 1 reverse complement
# E: 5 segments, 750 bp, height 300
#     - 1: 150 left
#     - 2: 150 down, second half of 8 reverse complement
#     - 3: 150 left
#     - 4: 150 right, 3 reverse complement
#     - 5: 150 down, first half of 8 reverse complement
#     - 6: 150 left
#     - 7: 150 right, 6 reverse complement
#     - 8: 300 up
# E: 5 segments, 600 bp, height 240
#     - 1: 120 left
#     - 2: 120 down, second half of 8 reverse complement
#     - 3: 120 left
#     - 4: 120 right, 3 reverse complement
#     - 5: 120 down, first half of 8 reverse complement
#     - 6: 120 left
#     - 7: 120 right, 6 reverse complement
#     - 8: 240 up
# T: 3 segments, 450 bp, height 150
#     - 1: 150 right
#     - 2: 75 left, second half of 1 reverse complement
#     - 3: 150 down
#     - 4: 75 left, second half of 5 reverse complement
#     - 5: 150 left
#     - 6: 75 right, first half of 5 reverse complement
#     - 7: 150 up, 3 reverse complement
#     - 8: 75 right, first half of 5 reverse complement
# A: 5 segments, 300 bp, height ~100 (a little more?)
#     - 1: 120 down/right
#     - 2: 60 up/left, second half of 1 reverse complement
#     - 3: 60 left
#     - 4: 60 down/left, first half of 5 reverse complement
#     - 5: 120 up/left
#     - I: 60 down/right, second half of 5 reverse complement
#     - II: 60 right, 3 reverse complement
#     - III: 60 up/right, first half of 1 reverse complement
# L: 3 segments, 150 bp, height 100
#     - 1: 99 down
#     - 2: 51 across
#     - 3: 2 reverse complement
#     - 4: 1 reverse complement
# Total bp: 8250 = (150 + 1500) * 5

# Define global variables
amino_alpha = "ACDEFGHIKLMNPQRSTVWY"
aas = list(amino_alpha)

alpha = "ACGT"
codons = [x + y + z for x in alpha for y in alpha for z in alpha]

aa2codon = {
    "A":["GCT","GCC","GCA","GCG"],
    "C":["TGT", "TGC"],
    "D":["GAT","GAC"],
    "E":["GAA","GAG"],
    "F":["TTT", "TTC"],
    "G":["GGT","GGC","GGA","GGG"],
    "H":["CAT","CAC"],
    "I":["ATT","ATC","ATA"],
    "K":["AAA","AAG"],
    "L":["CTT","CTC","CTA","CTG","TTA","TTG"],
    "M":["ATG"],
    "N":["AAT","AAC"],
    "P":["CCT","CCC","CCA","CCG"],
    "Q":["CAA","CAG"],
    "R":["CGT","CGC","CGA","CGG","AGA","AGG"],
    "S":["TCT","TCC","TCA","TCG","AGT","AGC"],
    "T":["ACT","ACC","ACA","ACG"],
    "V":["GTT","GTC","GTA","GTG"],
    "W":["TGG"],
    "Y":["TAT","TAC"],
    "_":["TAG","TGA","TAA"]
}

codon2aa = {value:key for key in aa2codon.keys() for value in aa2codon[key]}

print codon2aa

k = 50
used_kmers = set()

rc_dict = {"A":"T", "T":"A", "C":"G", "G":"C"}

reserved_codons = ["ATG", "TAG", "TGA", "TAA",  "TTA", "TCA", "CTA", "CAT"]

def translate(dna):
    aas = [codon2aa[dna[i:i+3]] for i in range(0, len(dna), 3)]
    return "".join(aas)

def save_kmers(seq, k):
    seq_ext = seq + seq[:k]
    for i in range(len(seq)):
        used_kmers.add(seq_ext[i:i+k])
    return used_kmers

def get_message_list(phrase, reserved_codons, rc_dict):
    phrase = "M" + phrase
    phrase_len = len(phrase)
    len2options = {i:[] for i in range(phrase_len + 1)}
    len2options[0] = [""]
    for i in range(phrase_len):
        #print(i)
        char = phrase[i]
        prev_options = len2options[i]
        current_options = []
        for prev_option in prev_options:
            for codon in aa2codon[char]:
                #print(prev_option)
                #print(codon)
                candidate = prev_option + codon
                if check_reserved_codons(candidate[1:], reserved_codons, []):
                    current_options.append(candidate)
        # Hack, maybe work around later
        random.shuffle(current_options)
        current_options = current_options[:100000]
        # End hack
        len2options[i + 1] = current_options
        print(len(current_options))
    return len2options[phrase_len]

def get_end_message_list(phrase, reserved_codons, rc_dict):
    phrase_len = len(phrase)
    len2options = {i:[] for i in range(phrase_len + 1)}
    len2options[0] = aa2codon["_"]
    for i in range(phrase_len):
        print(i)
        char = phrase[i]
        prev_options = len2options[i]
        current_options = []
        rev_codons = [get_reverse_complement(c, rc_dict) for c in aa2codon[char]]
        for prev_option in prev_options:
            for codon in rev_codons:
                candidate = codon + prev_option
                if check_reserved_codons(candidate[:-1], reserved_codons, []):
                    current_options.append(candidate)
        # Hack, maybe work around later
        random.shuffle(current_options)
        current_options = current_options[:100000]
        # End hack
        len2options[i + 1] = current_options
        print(len(current_options))
    return len2options[phrase_len]

def get_message(message_list):
    return random.choice(message_list)
#    valid_sequence = False
#    while not valid_sequence:
#        print("Getting red herring")
#        seq = "ATG" 
#        for char in "REDHERRING":
#            codons = aa2codon[char] 
#            + "".join([random.choice(aa2codon[char]) for char in "REDHERRING"])
#        rev_seq = get_reverse_complement(seq, rc_dict)
#        if check_reserved_codons(seq, reserved_codons) and check_reserved_codons(rev_seq, reserved_codons):
#            valid_sequence = True
#    return seq

def get_random_string(seg, n, reserved_codons, rc_dict, alpha="ACGT"):
    s = seg
    final_length = len(seg) + n
    while len(s) < final_length:
        char_options = list(alpha)
        random.shuffle(char_options)
        while len(char_options) > 1:
            if s[-2:] + char_options[0] in reserved_codons:
                char_options.remove(char_options[0])
            elif get_reverse_complement(s[-2:] + char_options[0], rc_dict) in reserved_codons:
                char_options.remove(char_options[0])
            else:
                break
        new_char = char_options[0]
        s += new_char
    random_string = s[len(seg):]
    return random_string

def make_segment(length, reserved_codons, rc_dict, message_list, end_message_list = None, extra_ends=None):
    seg = ""
    seg += random.choice(aa2codon["M"])
    message = get_message(message_list)
    message_len = len(message)
    seg += message
    if end_message_list: 
        end_message = get_message(end_message_list)
        end_message_len = len(end_message)
    valid_seg = False
    while not valid_seg:
        random_len = length - 6 - message_len
        if end_message_list: 
            random_len -= end_message_len
        if random_len < 0:
            raise ValueError
        random_str = get_random_string(seg, random_len , reserved_codons, rc_dict)
        with_random = seg + random_str
        if end_message_list: 
            with_random += end_message
        if extra_ends: 
            for end_pos in extra_ends: 
                extra_end_message = get_message(end_message_list)
                extra_end_message_len = len(end_message)
                with_random =\
                    with_random[:end_pos - extra_end_message_len] +\
                    extra_end_message +\
                    with_random[end_pos:]
        if not check_reserved_codons(with_random, reserved_codons, [0]):
            print("bad random string")
            continue
        if random_str.endswith("CA"):
            continue
        if random_str.endswith("C") or random_str.endswith("T"):
            stop_codons = ["TGA"]
        elif random_str.endswith("A"):
            stop_codons = ["TAG", "TAA"]
        else:
            stop_codons = ["TAG", "TGA", "TAA"]
            random.shuffle(stop_codons)
        valid_stop = False
        while not valid_stop:
            sc = stop_codons[0]
            if check_reserved_codons(random_str + sc, reserved_codons, [len(random_str)]):
                valid_stop = True
                valid_seg = True
            else:
                stop_codons.remove(sc)
                #print(sc)
                #print(stop_codons)
            if len(stop_codons) == 0:
                print("ran out of stop codons")
                break
    seg = with_random + sc
    return seg

def get_reverse_complement(seq, rc_dict):
    chars = list(seq)
    chars.reverse()
    return "".join([rc_dict[char] for char in chars])

def check_kmers(seq, k):
    seq_passes = True
    for i in range(len(seq) - k):
        if seq[i:i+k] in used_kmers:
            seq_passes = False
    return seq_passes

def check_reserved_codons(seq, reserved_codons, reserved_pos, verbose=False):
    seq_passes = True
    for i in range(len(seq)):
        if i in reserved_pos:
            continue
        if seq[i:i+3] in reserved_codons:
            if verbose:
                print(i, seq[i:i+3])
                print(seq)
            seq_passes = False
    return seq_passes

def check_sequence(seq, k, reserved_codons, reserved_pos):
    seq_ext = seq + seq[:k]
    unique_kmers = check_kmers(seq_ext, k)
    no_start_stop =  check_reserved_codons(seq, reserved_codons, reserved_pos, verbose=True)
    print("unique kmers: " + str(unique_kmers))
    print("no reserved codons: " + str(no_start_stop))
    sequence_passes = unique_kmers and no_start_stop
    return sequence_passes

def get_reserved_pos(seq_lens):
    reserved_pos = []
    cum_len = 0
    for seq_len in seq_lens:
        reserved_pos.append(cum_len)
        cum_len += seq_len
        reserved_pos.append(cum_len - 3)
    return reserved_pos

def get_L1_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # L: 3 segments, 1500 bp, height 900
    #     - 1: 900 up
    #     - 2: 900 down, 1 reverse complement
    #     - 3: 600 right, 4 reverse complement
    #     - 4: 600 left
    valid_sequence = False
    while not valid_sequence:
        print("Making L1")
        # Make segments
        seq_lens = [900, 900, 600, 600]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(900, reserved_codons, rc_dict, message_list, end_message_list)
        seg2 = get_reverse_complement(seg1, rc_dict)
        seg4 = make_segment(600, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = get_reverse_complement(seg4, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        seq = seg1 + seg2 + seg3 + seg4
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        #print(seq)
    save_kmers(seq, k)
    return seq

def get_Y_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # Y: 3 segments, 1350 bp, height ~710 bp
    #     - 1: 525 down/right
    #     - 2: 525 up/right
    #     - 3: 525 down/left, 2 reverse complement
    #     - 4: 300 down
    #     - 5: 300 up, 4 reverse complement
    #     - 6: 525 up/left, 1 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making Y")
        # Make segments
        seq_lens = [390, 480, 480, 480, 480, 390]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(390, reserved_codons, rc_dict, message_list, end_message_list)
        seg2 = make_segment(480, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = get_reverse_complement(seg2, rc_dict)
        seg4 = make_segment(480, reserved_codons, rc_dict, message_list, end_message_list)
        seg5 = get_reverse_complement(seg4, rc_dict)
        seg6 = get_reverse_complement(seg1, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq

def get_S_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # S: 5 segments, 1200 bp, height 480
    #     - 1: 240 left
    #     - 2: 240 down
    #     - 3: 240 right
    #     - 4: 240 down
    #     - 5: 240 left
    #     - 6: 5 reverse complement
    #     - 7: 4 reverse complement
    #     - 8: 3 reverse complement
    #     - 9: 2 reverse complement
    #     - 10: 1 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making S")
        # Make segments
        seq_lens = [240, 240, 240, 240, 240, 240, 240, 240, 240, 240]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
        seg2 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
        seg4 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
        seg5 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
        seg6 = get_reverse_complement(seg5, rc_dict)
        seg7 = get_reverse_complement(seg4, rc_dict)
        seg8 = get_reverse_complement(seg3, rc_dict)
        seg9 = get_reverse_complement(seg2, rc_dict)
        seg10 = get_reverse_complement(seg1, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        print
        print translate(seg7)
        print
        print translate(seg8)
        print
        print translate(seg9)
        print
        print translate(seg10)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6 + seg7 + seg8 + seg9 + seg10
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq

def get_I_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # I: 4 segments, 1050 bp, height 450
    #     - 1: 150 left, second half of 8 reverse complement
    #     - 2: 450 down
    #     - 3: 150 right, first half of 4 reverse complement
    #     - 4: 300 left
    #     - 5: 150 right, second half of 4 reverse complement
    #     - 6: 450 up, 2 reverse complement
    #     - 7: 150 left, first half of 8 reverse complement
    #     - 8: 300 right
    valid_sequence = False
    while not valid_sequence:
        print("Making I")
        # Make segments
        seq_lens = [150, 450, 150, 300, 150, 450, 150, 300]
        reserved_pos = get_reserved_pos(seq_lens)
        seg8 = make_segment(300, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [150])
        seg1 = get_reverse_complement(seg8[150:], rc_dict)
        seg2 = make_segment(450, reserved_codons, rc_dict, message_list, end_message_list)
        seg4 = make_segment(300, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [150])
        seg3 = get_reverse_complement(seg4[:150], rc_dict)
        seg5 = get_reverse_complement(seg4[150:], rc_dict)
        seg6 = get_reverse_complement(seg2, rc_dict)
        seg7 = get_reverse_complement(seg8[:150], rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        print
        print translate(seg7)
        print
        print translate(seg8)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6 + seg7 + seg8
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq


def get_N_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # N: 3 segments, 900 bp
    #     - 1: 270 down
    #     - 2: 360 up/left
    #     - 3: 270 down
    #     - 4: 270 up, 3 reverse complement
    #     - 5: 360 down/right, 2 reverse complement
    #     - 6: 270 up, 1 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making N")
        # Make segments
        seq_lens = [270, 360, 270, 270, 360, 270]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(270, reserved_codons, rc_dict, message_list, end_message_list)
        seg2 = make_segment(360, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = make_segment(270, reserved_codons, rc_dict, message_list, end_message_list)
        seg4 = get_reverse_complement(seg3, rc_dict)
        seg5 = get_reverse_complement(seg2, rc_dict)
        seg6 = get_reverse_complement(seg1, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq

def get_E1_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # E: 5 segments, 750 bp, height 300
    #     - 1: 300 up
    #     - 2: 150 right
    #     - 3: 150 left, reverse complement of 2
    #     - 4: 150 down, second half of 1 reverse complement
    #     - 5: 150 right
    #     - 6: 150 left, 5 reverse complement
    #     - 7: 150 down, first half of 1 reverse complement
    #     - 8: 150 right
    #     - 9: 150 left, 8 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making E1")
        # Make segments
        seq_lens = [300, 150, 150, 150, 150, 150, 150, 150, 150]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(300, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [150])
        seg2 = make_segment(150, reserved_codons, rc_dict, message_list, end_message_list)
        seg5 = make_segment(150, reserved_codons, rc_dict, message_list, end_message_list)
        seg8 = make_segment(150, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = get_reverse_complement(seg2, rc_dict)
        seg4 = get_reverse_complement(seg1[150:], rc_dict)
        seg6 = get_reverse_complement(seg5, rc_dict)
        seg7 = get_reverse_complement(seg1[:150], rc_dict)
        seg9 = get_reverse_complement(seg8, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        print
        print translate(seg7)
        print
        print translate(seg8)
        print
        print translate(seg9)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6 + seg7 + seg8 + seg9
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq    

def get_E2_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # E: 5 segments, 600 bp, height 240
    #     - 1: 240 up
    #     - 2: 120 right
    #     - 3: 120 left, reverse complement of 2
    #     - 4: 120 down, second half of 1 reverse complement
    #     - 5: 120 right
    #     - 6: 120 left, 5 reverse complement
    #     - 7: 120 down, first half of 1 reverse complement
    #     - 8: 120 right
    #     - 9: 120 left, 8 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making E1")
        # Make segments
        seq_lens = [240, 120, 120, 120, 120, 120, 120, 120, 120]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [120])
        seg2 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
        seg5 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
        seg8 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = get_reverse_complement(seg2, rc_dict)
        seg4 = get_reverse_complement(seg1[120:], rc_dict)
        seg6 = get_reverse_complement(seg5, rc_dict)
        seg7 = get_reverse_complement(seg1[:120], rc_dict)
        seg9 = get_reverse_complement(seg8, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        print
        print translate(seg6)
        print
        print translate(seg7)
        print
        print translate(seg8)
        print
        print translate(seg9)
        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6 + seg7 + seg8 + seg9
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq    

#def get_E2_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
#    # E: 5 segments, 600 bp, height 240
#    #     - 1: 120 left
#    #     - 2: 120 down, second half of 8 reverse complement
#    #     - 3: 120 left
#    #     - 4: 120 right, 3 reverse complement
#    #     - 5: 120 down, first half of 8 reverse complement
#    #     - 6: 120 left
#    #     - 7: 120 right, 6 reverse complement
#    #     - 8: 240 up
#    #     - 9: 120 right, reverse complement of 1
#    valid_sequence = False
#    while not valid_sequence:
#        print("Making E2")
#        # Make segments
#        seq_lens = [120, 120, 120, 120, 120, 120, 120, 240, 120]
#        reserved_pos = get_reserved_pos(seq_lens)
#        seg1 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
#        seg3 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
#        seg6 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list)
#        seg8 = make_segment(240, reserved_codons, rc_dict, message_list, end_message_list)
#        seg2 = get_reverse_complement(seg8[120:], rc_dict)
#        seg4 = get_reverse_complement(seg3, rc_dict)
#        seg5 = get_reverse_complement(seg8[:120], rc_dict)
#        seg7 = get_reverse_complement(seg6, rc_dict)
#        seg9 = get_reverse_complement(seg1, rc_dict)
#        seq = seg1 + seg2 + seg3 + seg4 + seg5 + seg6 + seg7 + seg8 + seg9
#        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
#        print("full sequence")
#        print(valid_sequence)
#        print(seq)
#    save_kmers(seq, k)
#    return seq    

def get_T_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # T: 5 segments, 450 bp, height 270
    #     - 1: 270 up
    #     - 2: 90 left, first half of 3 reverse complement
    #     - 3: 180 right
    #     - 4: 90 right, second half of 3 reverse complement
    #     - 5: 270 down, 1 reverse complement
    valid_sequence = False
    while not valid_sequence:
        print("Making T")
        # Make segments
        seq_lens = [270, 90, 180, 90, 270]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(270, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = make_segment(180, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [90])
        seg2 = get_reverse_complement(seg3[:90], rc_dict)
        seg4 = get_reverse_complement(seg3[90:], rc_dict)
        seg5 = get_reverse_complement(seg1, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        seq = seg1 + seg2 + seg3 + seg4 + seg5
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        print(seq)
    save_kmers(seq, k)
    return seq

def get_A_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # A: 5 segments, 300 bp, height ~100 (a little more?)
    #     - 1: 120 up/right
    #     - 2: 120 down/right
    #     - 3: 60 up/left, second half of 2 reverse complement
    #     - 4: 60 left
    #     - 5: 60 down/left, first half of 1 reverse complement
    #     - I: 60 up/right, second half of 1 reverse complement
    #     - II: 60 down/right, first half of 2 reverse complement
    #     - III: 60 left, 4 reverse complement
    valid_sequences = False
    while not valid_sequences:
        print("Making A")
        # Make sequence 1
        seq_lens = [120, 120, 60, 60, 60]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [60])
        seg2 = make_segment(120, reserved_codons, rc_dict, message_list, end_message_list, extra_ends = [60])
        seg3 = get_reverse_complement(seg2[60:], rc_dict)
        seg4 = make_segment(60, reserved_codons, rc_dict, message_list, end_message_list)
        seg5 = get_reverse_complement(seg1[:60], rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        print
        print translate(seg5)
        seq1 = seg1 + seg2 + seg3 + seg4 + seg5
        valid_sequence1 = check_sequence(seq1, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence1)
        print(seq1)
        seq_lens = [60, 60, 60]
        reserved_pos = get_reserved_pos(seq_lens)
        segi = get_reverse_complement(seg1[60:], rc_dict)
        segii = get_reverse_complement(seg4, rc_dict)
        segiii = get_reverse_complement(seg2[:60], rc_dict)
        print
        print translate(segi)
        print
        print translate(segii)
        print
        print translate(segiii)
        seq2 = segi + segii + segiii
        valid_sequence2 = check_sequence(seq2, k, reserved_codons[:4], reserved_pos)
        print("full sequence")
        print(valid_sequence2)
        print(seq2)
        if valid_sequence1 and valid_sequence2:
            valid_sequence = True
        break
    save_kmers(seq1, k)
    save_kmers(seq2, k)
    return seq1, seq2

def get_L2_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
    # L: 3 segments, 1500 bp, height 900
    #     - 1: 90 up
    #     - 2: 90 down, 1 reverse complement
    #     - 3: 60 right, 4 reverse complement
    #     - 4: 60 left
    valid_sequence = False
    while not valid_sequence:
        print("Making L1")
        # Make segments
        seq_lens = [90, 90, 60, 60]
        reserved_pos = get_reserved_pos(seq_lens)
        seg1 = make_segment(90, reserved_codons, rc_dict, message_list, end_message_list)
        seg2 = get_reverse_complement(seg1, rc_dict)
        seg4 = make_segment(60, reserved_codons, rc_dict, message_list, end_message_list)
        seg3 = get_reverse_complement(seg4, rc_dict)
        print
        print translate(seg1)
        print
        print translate(seg2)
        print
        print translate(seg3)
        print
        print translate(seg4)
        seq = seg1 + seg2 + seg3 + seg4
        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
        print("full sequence")
        print(valid_sequence)
        #print(seq)
    save_kmers(seq, k)
    return seq

#def get_L2_sequence(k, rc_dict, reserved_codons, alpha="ACGT"):
#    # L: 3 segments, 150 bp, height 100
#    #     - 1: 99 down
#    #     - 2: 51 across
#    #     - 3: 2 reverse complement
#    #     - 4: 1 reverse complement
#    valid_sequence = False
#    while not valid_sequence:
#        print("Making L2")
#        # Make segments
#        seq_lens = [90, 60, 60, 90]
#        reserved_pos = get_reserved_pos(seq_lens)
#        seg1 = make_segment(90, reserved_codons, rc_dict, message_list, end_message_list)
#        seg2 = make_segment(60, reserved_codons, rc_dict, message_list, end_message_list)
#        seg3 = get_reverse_complement(seg2, rc_dict)
#        seg4 = get_reverse_complement(seg1, rc_dict)
#        seq = seg1 + seg2 + seg3 + seg4
#        valid_sequence = check_sequence(seq, k, reserved_codons, reserved_pos)
#        print("full sequence")
#        print(valid_sequence)
#        print(seq)
#    save_kmers(seq, k)
#    return seq

        #reserved_pos = [0, 96, 99, 147, 150, 198, 201, 297]
        # Check sequence
        #print("seq1")
        #print(seg1)
        #print(check_sequence(seg1, used_kmers, k, reserved_codons, [0, 96]))
        #print("seq2")
        #print(seg2)
        #print(check_sequence(seg2, used_kmers, k, reserved_codons, [0, 48]))
        #print("seq3")
        #print(seg3)
        #print(check_sequence(seg3, used_kmers, k, reserved_codons, [0, 48]))
        #print("seq4")
        #print(seg4)
        #print(check_sequence(seg4, used_kmers, k, reserved_codons, [0, 96]))

#seq_lens = [270, 360, 270]
#reserved_pos = get_reserved_pos(seq_lens)
#print(reserved_pos)

message_file = "/Users/robt/MyCode/Puzzles/MH2021/karyotype/genome/messages.txt"
#message_list = get_message_list("STARTTQSTQPSTRAIGHT", reserved_codons, rc_dict)
#message_list = get_message_list("GENESSTRAIGHT", reserved_codons, rc_dict)
#message_list = get_message_list("GENEENDSANGLES", reserved_codons, rc_dict)
message_list = get_message_list("ANGLEGENEENDS", reserved_codons, rc_dict)
message_list = [elt[3:] for elt in message_list]
with open(message_file, "w") as f: 
    for message in message_list: 
        f.write(message + "\n")
###UNCOMMENT
message_list = []
with open(message_file, "r") as f: 
    for line in f:
        message_list.append(line.strip())

end_message_file = "/Users/robt/MyCode/Puzzles/MH2021/karyotype/genome/end_messages.txt"
end_message_list = get_end_message_list("REV", reserved_codons, rc_dict)
end_message_list = [elt[:-3] for elt in end_message_list]
with open(end_message_file, "w") as f:
    for end_message in end_message_list:
        f.write(end_message + "\n")
end_message_list = []
with open(end_message_file, "r") as f: 
    for line in f:
        end_message_list.append(line.strip())

all_sequences = []

L1 = get_L1_sequence(k, rc_dict, reserved_codons)
Y = get_Y_sequence(k, rc_dict, reserved_codons)
S = get_S_sequence(k, rc_dict, reserved_codons)
I = get_I_sequence(k, rc_dict, reserved_codons)
N = get_N_sequence(k, rc_dict, reserved_codons)
E1 = get_E1_sequence(k, rc_dict, reserved_codons)
E2 = get_E2_sequence(k, rc_dict, reserved_codons)
T = get_T_sequence(k, rc_dict, reserved_codons)
A1, A2 = get_A_sequence(k, rc_dict, reserved_codons)
L2 = get_L2_sequence(k, rc_dict, reserved_codons)

letters = ["L1", "Y", "S", "I", "N", "E1", "E2", "T", "A1", "A2", "L2"]
all_sequences = [L1, Y, S, I, N, E1, E2, T, A1, A2, L2]

print()
print()
for letter, seq in zip(letters, all_sequences):
    print(letter)
    print(seq)

out_fname = "/Users/robt/MyCode/Puzzles/MH2021/karyotype/genome/chromosomes.fasta"
#out_fname = "/Users/robt/MyCode/Puzzles/MH2021/karyotype/genome/debug.fasta"

with open(out_fname, "w") as f:
    for letter, seq in zip(letters, all_sequences):
        f.write(">" + letter + "\n")
        f.write(seq + "\n")

###END UNCOMMENT
#letters=["T"]
#all_sequences = [T]

#print(len(used_kmers))
#print(sum([len(elt) for elt in all_sequences]))

#message_list = get_message_list("HIGHERLEVEL", reserved_codons, rc_dict)
#message_list = [elt[3:] for elt in message_list]

#for elt in message_list:
#    print(elt)
