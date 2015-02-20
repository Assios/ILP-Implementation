# ILP implementation

An implementation of intuitionistic logic programming in Python.
## Usage
```sh
$ python nprolog.py filename.ilp
```
**Then just run queries!**
## Prolog syntax

This implementation uses a regular Prolog syntax, with some changes to support intuitionistic logic programming. You add facts and rules to an .ilp-file, and then you can run queries on it after loading the file.

### Hypothetical queries
The following line means that nearPopular(A, C) is true if friend(A, C) would make popular(A) true:
```sh
nearPopular(A, C):- =>(popular(A), friend(A, C))
```
