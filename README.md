# Pickle-compatible h5py wrapper
This module provides a wrapper for the `h5py` classes to allow pickling of h5py objects.
Basically the arguments to the `h5py.File` call are saved, and a new file is opened when
a `Group`, `Dataset` or `File` is unpickled. Ergo, this will only work well on shared
filesystems, and for reading files (SWMR should be fine too).

### Caching
A Least-Recently-Used (LRU) cache is used to keep `h5pickle.File` objects in based
on the arguments passed to that function. On unpickling that cache is first checked
to prevent us from opening the same file multiple times, and to make using the
same file repeatedly faster.

## Setup
First you need to install the PyPI or conda-forge package, or clone this repository in your path.
```bash
pip install h5pickle
```

```bash
conda config --add channels conda-forge
conda install h5pickle
```

Then you can use h5pickle as a drop-in replacement for h5py.
```python
import h5pickle as h5py
```

Note that not all features of h5py are supported yet. Pull requests are very
welcome. Specifically writing files is problematic, as to do this properly from
multiple processes needs MPI support.

## Usage
```python
import pickle, h5pickle
f = h5pickle.File('filename.h5', 'r', skip_cache=False) # skip_cache = True by default
f2 = pickle.loads(pickle.dumps(f))
f2 == f # True

g = pickle.loads(pickle.dumps(f['/group/'])) # works
d = pickle.loads(pickle.dumps(f['/group/set'])) # works
```

_Be very careful using this with any file open flags other than 'r' in a parallel context_

## References
Inspired by

* https://github.com/mrocklin/hdf5lazy
* https://github.com/dask/dask/issues/922
* https://github.com/pydata/xarray/issues/798
* https://github.com/dask/dask/issues/1777

## License
All code is available under the MIT license
