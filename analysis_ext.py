import os
import sys
import json
import random
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

def add_op_sets(set1, set2):
    sum = {}
    union_keys = set().union(set1.keys(), set2.keys())
    for k in union_keys:
        if k in set1 and k in set2:
            sum[k] = set1[k] + set2[k]
        elif k in set1:
            sum[k] = set1[k]
        else:
            sum[k] = set2[k]
    return sum

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
    if len(sys.argv) != 2:
        print('[-] architecture name is required')
        print('ex) python preprocess_ext.py < arm | mips | option >')
        sys.exit(0)

    architecture = sys.argv[1]
    train_set = {}
    if architecture == 'option':
        compilers = ['gcc_' + architecture, 'clang_' + architecture]
        centers = {}
        for c in compilers:
            train_set[c] = []
            with open(os.path.join(c.split('_')[0], 'center.json')) as f:
                centers[c] = json.load(f)
        
    else:
        train_set_size = 15
        compilers = ['gcc_' + architecture, 'clang_' + architecture]
        op_sets = {c: [] for c in compilers}
        for c in compilers:
            random_train_set = []
            for i in range(train_set_size):
                x = random.choice(os.listdir(c))
                while '.json' in x or x in random_train_set:
                    x = random.choice(os.listdir(c))
                random_train_set.append(x)
            train_set[c] = random_train_set
            print(f'- train set for [{c}] : {random_train_set}')

            for filename in os.listdir(c):
                if filename.endswith('.json'): continue
                binary = os.path.join(c, filename)
                op_set = get_frequency_vector(binary)
                if filename in random_train_set:
                    op_sets[c].append(op_set)
        
        centers = {}
        for c in compilers:
            n = len(op_sets[c])
            sum = {}
            for ops in op_sets[c]:
                sum = add_op_sets(sum, ops)
            sum = {k: v/n for k,v in sum.items()}
            centers[c] = sum
            with open(os.path.join(c, 'center.json'), 'w') as f:
                json.dump(sum, f)
            
    same = 0
    diff = 0
    for c in compilers:
        same_c = 0
        diff_c = 0
        for filename in os.listdir(c):
            if filename in train_set[c] or filename.endswith('.json'): continue
            binary = os.path.join(c, filename)
            target = get_frequency_vector(binary)

            dis_with_gcc = get_distance(target, centers['gcc_' + architecture])
            dis_with_clang = get_distance(target, centers['clang_' + architecture])

            if dis_with_gcc < dis_with_clang:
                label = 'gcc_' + architecture
            else:
                label = 'clang_' + architecture
            
            if label == c:
                same_c += 1
                same += 1
            else:
                diff_c += 1
                diff += 1
        print(f'[+] {c} : correct : {same_c}, wrong : {diff_c}')
    
    if same + diff != 0:
        print(f'\ntotal accuracy : {same / (same+diff) * 100 : .2f}')
            
