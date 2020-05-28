# Ensemble
#### First Install Hombrew
```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
```

#### Next Install CDO
```
brew tap moffat/sciencebits
brew install cdo
```
#### Go to files
`cd` to `.nc` files...
- below (`file1`, `file2` etc will be the names of your files...you need to be in the same directory as these files)
  - you can use more or less than 6
-  `ofile` is what you want to call the mean ensemble file

#### Run CDO ensemble 
```
cdo ensmean ifile1 ifile2 ifile3 ifile4 ifile5 ifile6 ofile
```

#### Check file headers for fun
```
ncdump -h ofile
```