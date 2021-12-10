import os
import sys
import json
import math
import subprocess as sp

def parse(opcodes):
    op_set = {}
    n = 0.0
    for op in opcodes.split('\n'):
        if '/tmp' in op or '' == op: continue
        n += 1
        if op in op_set:
            op_set[op] += 1
        else:
            op_set[op] = 1
    op_set = {k: v/n for k,v in op_set.items()}
    return op_set

def get_frequency_vector(binary):
    if os.path.isfile(binary + '.json'):
        with open(binary + '.json') as f:
            target = json.load(f)
    else:
        p = sp.run(['dotnet', 'fsi', 'sequence_opcode.fsx', binary], capture_output=True, text=True)
        target = parse(p.stdout)
        with open(binary + '.json', 'w') as f:
            json.dump(target, f)
    return target

def get_distance(b1, b2):
    dis = 0
    union_keys = set().union(b1.keys(), b2.keys())
    for k in union_keys:
        if k in b1 and k in b2:
            dis += math.pow(b1[k] - b2[k], 2)
        elif k in b1:
            dis += math.pow(b1[k], 2)
        else:
            dis += math.pow(b2[k], 2)
    return math.sqrt(dis)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('[-] architecture, binary is required')
        print('ex) python predict_ext.py < arm | mips | option > < binary >')
        sys.exit(0)

    architecture = sys.argv[1]
    if architecture == 'option':
        with open('gcc/center.json') as f:
            gcc = json.load(f)
        with open('clang/center.json') as f:
            clang = json.load(f)
    else:
        with open(f'gcc_{architecture}/center.json') as f:
            gcc = json.load(f)
        with open(f'clang_{architecture}/center.json') as f:
            clang = json.load(f)

    binary = sys.argv[2]
    target = get_frequency_vector(binary)
    
    dis_with_gcc = get_distance(target, gcc)
    dis_with_clang = get_distance(target, clang)

    if dis_with_gcc < dis_with_clang:
        prediction = 'gcc'    
    else:
        prediction = 'clang'
    
    print(f'[+] prediction : {prediction}')
    print(f' - distance with [gcc] : {dis_with_gcc}')
    print(f' - distance with [clang] : {dis_with_clang}')