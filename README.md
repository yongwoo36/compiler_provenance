# Compiler Provenance

This is final project for IS561. 
In this project, we are identify which compiler compile a binary using instruction frequency analysis.

## Usage
### To analyze given 45 binarys
I used `train_set_size` as 5 and 10 for evaluation.
```
python analysis.py <train_set_size>
```

### To predict one binary in given 45 binarys
This command returns the compiler predicted and prints the distance from each compiler frequency vector.
```
python predict.py <binary>
```

### To analyze binarys with different compile options
Before analysis binarys with different compile options, run `python analysis.py 15`. 
It makes more general compiler frequency vector.
```
python analysis_ext.py option
```

### To analyze binarys with different architecture
Default `train_set_size` is 15 in this analysis. It randomly select 15 binarys to calcualte compiler frequency vector.
```
python analysis_ext.py <arm|mips>
```

### To predict one binary in extension dataset
This command returns the compiler predicted and prints the distacne from each compiler frequency vector.
When give a `option` command, it uses the compiler frequency vector calculated using given 45 binarys.
Otherwise, it uses the compiler frequency vector computed in analysis phase. Therefore, in order to generate a more general frequency vector, the analysis step should be performed with a larger number of `train_set_size`.
```
python predict_ext.py <arm|mips|option> <binary>
```