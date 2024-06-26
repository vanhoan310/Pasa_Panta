from glob import glob
import os
import subprocess
import multiprocessing
import re
import shutil
import random
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq


def create_poa(seq_file):
    filename = os.path.basename(seq_file)
    result_file = os.path.join(out_dir, filename)
    cmd = (f'abpoa {seq_file} -o {result_file} -r1 -t {matrix_file} '
            '-O 11,0 -E 1,0 -p -c 2> /dev/null')
    os.system(cmd)

def create_poa_in_parallel(seq_files):

    with multiprocessing.Pool(processes=threads) as pool:
        pool.map(create_poa, seq_files)

def create_mafft(seq_file):
    filename = os.path.basename(seq_file)
    result_file = os.path.join(out_dir, filename)
    cmd = f"mafft --auto --quiet --thread 1 {seq_file} > {result_file}" # 9:43
    # cmd = f"mafft --retree 2 --quiet --thread 1 {seq_file} > {result_file}"  # 3:36
    # cmd = f"mafft --retree 1 --maxiterate 0  --quiet --thread 1 {seq_file} > {result_file}" # 3:21
    # cmd = f"mafft --auto --maxiterate 10 --quiet --thread 1 {seq_file} > {result_file}" # 10:01
    
    os.system(cmd)

def create_mafft_in_parallel(seq_files):

    with multiprocessing.Pool(processes=threads) as pool:
        pool.map(create_mafft, seq_files)

def split_by_length(seq_list, ratio):
    first_seqs = []
    second_seqs = []
    
    index_jump = int(1/ratio)

    for i, seq_tuple in enumerate(seq_list,0):
        if i % index_jump == 0:
            first_seqs.append(seq_tuple)
        else:
            second_seqs.append(seq_tuple)
    
    return first_seqs, second_seqs


def split_by_length_2(seq_list):
    prev_len = 1
    first_seqs = []
    second_seqs = []
    for seq_tuple in seq_list:
        seq_len = len(seq_tuple[1])
        if seq_len / prev_len > 1.1:
            first_seqs.append(seq_tuple)
            prev_len = seq_len
        else:
            second_seqs.append(seq_tuple)

    return first_seqs, second_seqs


def split_random(seq_list, ratio):
    random.seed(62)
    random.shuffle(seq_list)
    total_num = len(seq_list)
    first_seqs_len = int(total_num * ratio)
    first_seqs = seq_list[:first_seqs_len]
    second_seqs = seq_list[first_seqs_len:]
    return first_seqs, second_seqs

def split_seq_file(seq_file):
    seq_list = []
    with open(seq_file, 'r') as fh:
        for record in SeqIO.parse(fh, "fasta"):
            seq_id = record.id
            seq = str(record.seq)
            seq_list.append((seq_id, seq))

    seq_list.sort(key= lambda x:len(x[1])) # sort sequences by length
    
    # first_seqs, second_seqs = split_random(seq_list, 0.2)
    first_seqs, second_seqs = split_by_length(seq_list, 0.2)
    
    filename = os.path.basename(seq_file)
    mafft_seq = os.path.join(out_dir, filename + '.1.seq')
    with open(mafft_seq, 'w') as fh:
        for seq_id, seq in first_seqs: 
            new_record = SeqRecord(Seq(seq), id = seq_id, description = '')
            SeqIO.write(new_record, fh, 'fasta')
    
    poa_seq = os.path.join(out_dir, filename + '.2.seq')
    with open(poa_seq, 'w') as fh:
        for seq_id, seq in second_seqs: 
            new_record = SeqRecord(Seq(seq), id = seq_id, description = '')
            SeqIO.write(new_record, fh, 'fasta')

    return mafft_seq, poa_seq


def new_method(seq_file):
    filename = os.path.basename(seq_file)

    mafft_seq, poa_seq = split_seq_file(seq_file)

    mafft_msa_file = os.path.join(out_dir, filename + '.1.aln')
    cmd = ("mafft --localpair --maxiterate 1000 --quiet --thread 1 "
           f"{mafft_seq} > {mafft_msa_file}")
    os.system(cmd)

    result_file = os.path.join(out_dir, filename)
    cmd = (f'abpoa {poa_seq} -i {mafft_msa_file} -o {result_file} -r1 '
           f'-t {matrix_file} -O 11,0 -E 1,0 -p -c 2> /dev/null')
    os.system(cmd)


def new_method_parallel(seq_files):
    with multiprocessing.Pool(processes=threads) as pool:
        pool.map(new_method, seq_files)

def run_qscore(seq_file):
    filename = os.path.basename(seq_file)
    ref_file = os.path.join(ref_dir, filename)
    test_file = os.path.join(out_dir, filename)
    cmd = (f"qscore -test {test_file} -ref {ref_file} "
            "-seqdiffwarn -truncname -quiet")
    output = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    result = re.match(
        r'Test=.+;Ref=.+;Q=([\d\.]+);TC=([\d\.]+)', 
        output.stdout.rstrip())
    if result == None:
        return filename, 0, 0
    else:
        SPS = result.group(1)
        CS = result.group(2)
        return filename, SPS, CS

def compare(seq_files):
    with multiprocessing.Pool(processes=threads) as pool:
        results = pool.map(run_qscore, seq_files)

    sum_SPS = 0
    sum_CS = 0
    for filename, SPS, CS in results:
        print(filename, round(float(SPS), 2), round(float(CS), 2), sep='\t')
        sum_SPS += float(SPS)
        sum_CS += float(CS)

    print(round(sum_SPS, 2))
    print(round(sum_CS, 2))

def extract_precompute_result(result_file):
    sum_SPS = 0
    sum_CS = 0
    for line in open(result_file, 'r'):
        line = line.rstrip()
        result = re.match(r'Test=.+;Ref=(.+);Q=([\d\.]+);TC=([\d\.]+)', line)
        if result == None:
            print(line)
        else:
            ID = result.group(1)
            SPS = result.group(2)
            CS = result.group(3)
            print(ID, SPS, CS, sep='\t')
            sum_SPS += float(SPS)
            sum_CS += float(CS)

    print(sum_SPS, sum_CS, sep='\t')

def get_gene_list(gene_id_file):
    gene_id_list = []
    for line in open(gene_id_file):
        gene_id = line.rstrip()
        gene_id_list.append(gene_id)

    return gene_id_list

if __name__ == "__main__":
    global threads
    threads = 8
    
    global matrix_file # Blosum matrix file for POA
    matrix_file = '/home/noideatt/TA/pan-genome/BLOSUM62.mtx'

    global out_dir # directory contain the resulting MSA
    out_dir = '/home/noideatt/TA/evaluate_msa/bench/bench/bali3/mafft'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    
    global ref_dir # directory contain the reference MSA
    ref_dir = '/home/noideatt/TA/evaluate_msa/bench/bench/bali3/ref'
    
    # directory of input sequences 
    in_dir = '/home/noideatt/TA/evaluate_msa/bench/bench/bali3/in' 
    seqid_file = '/home/noideatt/TA/evaluate_msa/seq_id.txt'
    seqid_list = get_gene_list(seqid_file)

    seq_files = [in_dir+'/'+seq_id for seq_id in seqid_list]

    # seq_files = glob(f'{in_dir}/*') # get all input sequence in input directory

    # create_poa_in_parallel(seq_files)
    # create_mafft_in_parallel(seq_files)
    
    new_method_parallel(seq_files)

    # precompute_dir = '/home/noideatt/TA/evaluate_msa/bench/bench/bali3/qscore'
    # precompute_files = glob(f'{precompute_dir}/*')
    # for f in precompute_files:
    #     print(os.path.basename(f))
    #     extract_precompute_result(f)



    