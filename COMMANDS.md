
# Docs commands
## Labs
```
jupytext --to py:percent /Users/rodell/scripts/lab10.ipynb
jupytext --to notebook /Users/rodell/fwf/scripts/fbp/kdtree.py
jupytext --to markdown /Users/rodell/scripts/lab4.ipynb
mv /Users/rodell/fwf/scripts/fbp/kdtree.ipynb /Users/rodell/fwf/fwf-docs/source/

make clean
make html
