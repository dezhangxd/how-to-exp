# how-to-exp
This script is designed to help students who are conducting experiments and collecting data for the first time. It streamlines the process of running experiments and performing statistical analysis on the results.


## prepare environment


```
unzip data.zip
bash connect_and_build_all_solvers.sh
```

Some useful tools:
- `gnomon` for standard runtime


## run experiments
```
bash run_para.sh
```

## cal logs
```
python3 ./cal.py  
```
At the same time, the script will generate a `log.csv` file, which can be used for CDS plotting or other data analyses.


Draw CDF plot: 
```
python3 ./cdf.py res.csv -o cdf.png -c 10
```


## clean this repo
```
bash clean.sh
```