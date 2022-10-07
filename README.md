# Non_paternity

## General
`run_non_paternity` simulates non_paternity events on to individuals in a networkx directed graph. This program is a python script that uses a networkx pacage to traverse node networks.  

## Inputs 
.nx files - containing the edge graph of parent child relations respectivly
```
1 3 {}
1 7 {}
1 6 {}
```
.txt files - contaning individual id, birth_year, and gender
```
profileid   gender  birth_year
1	male	1900
2	female	1905
3	male	1920
```

## Output
A new .nx file containing an updated edgelist will be created. using the -o flag will rename the file output. 

## Parameters
`-o` output file name

`-f` pedigree file path

`-c` changes the probability of a non paternity event per individual

`-p` file path for .txt file containing attributes of individuals

## Example
```
python non_pat_atty.py -f testfam.nx -p test_fam_profile.txt -c .25 -o new_test_fam
```
