"""
Pickle-able hdf5 files and datasets by storing opening information
in wrapped h5py classes.

Subclass h5py.File to provide keywords for unpickling
and to wrap any returned subclasses of h5py.

The subclasses are extended to define the object path and to keep the file handle.
The unpickling functions can then create the file and open the object within.
Since the file open call is memoized we will not have multiple copies.

Note that this only works if the filesystem is shared between processes.

Another thing to consider is that the tracking is one-way, i.e. if you create
a file or group yourself based off the object id pickling may fail.

Cache file handles to avoid re-opening on every task.
Use an LRU cache on the File.__new__ function and add a close function to the
cache.

Dependencies:
h5py
cachetools
"""

import h5py
from cachetools import LRUCache

class LRUFileCache(LRUCache):
    """An LRU-cache that tries to close open files on eviction"""
    def popitem(self):
        key, val = LRUCache.popitem(self)
        # Try to close file if we can
        try:
            val.close()
        except AttributeError: # catch close() not being defined
            pass
        return key, val

cache = LRUFileCache(100)


def h5py_wrap_type(obj):
    """Produce our objects instead of h5py default objects"""
    if isinstance(obj, h5py.Dataset):
        return Dataset(obj.id)
    elif isinstance(obj, h5py.Group):
        return Group(obj.id)
    elif isinstance(obj, h5py.File):
        return File(obj.id) # This messes with the cache mechanism... warn?
    elif isinstance(obj, h5py.Datatype):
        return obj # Not supported for pickling yet. Haven't really thought about it
    else:
        return obj # Just return, since we want to wrap h5py.Group.get too



class PickleAbleH5PyObject(object):
    """Save state required to pickle and unpickle h5py objects and groups.
    This class should not be used directly, but is here as a base for inheritance
    for Group and Dataset"""
    def __getstate__(self):
        """Save the current name and a reference to the root file object."""
        return {'name': self.name, 'file': self.file_info}

    def __setstate__(self, state):
        """File is reopened by pickle. Create a dataset and steal its identity"""
        self.__init__(state['file'][state['name']].id)
        self.file_info = state['file']

    def __getnewargs__(self):
        """Override the h5py getnewargs to skip its error message"""
        return ()

class Dataset(PickleAbleH5PyObject, h5py.Dataset):
    """Mix in our pickling class"""
    pass

class Group(PickleAbleH5PyObject, h5py.Group):
    """Overwrite group to allow pickling, and to create new groups and datasets
    of the right type (i.e. the ones defined in this module).
    """
    def __getitem__(self, name):
        obj = h5py_wrap_type(h5py.Group.__getitem__(self, name))
        # If it is a group or dataset copy the current file info in
        if isinstance(obj, Group) or isinstance(obj, Dataset):
            obj.file_info = self.file_info
        return obj


def arghash(*args, **kwargs):
    return hash((args, tuple(sorted(kwargs.items()))))


class File(h5py.File):
    """A subclass of h5py.File that implements a memoized cache and pickling.
    Use this if you are going to be creating h5py.Files of the same file often.

    Pickling is done not with __{get,set}state__ but with __getnewargs_ex__
    which produces the arguments to supply to the __new__ method. This is required
    to allow for memoization of unpickled values.
    """
    def __init__(self, *args, **kwargs):
        """We skip the init method, since it is called at object creation time
        by __new__. This is necessary to have both pickling and caching."""
        pass

    def __new__(cls, *args, **kwargs):
        """Create a new File object with the h5open function, which memoizes
        the file creation. Test if it is still valid and otherwise create a new one.
        """
        skip_cache = kwargs.pop('skip_cache', False)
        hsh = arghash(*args, **kwargs)
        if skip_cache or hsh not in cache:
            self = object.__new__(cls)
            h5py.File.__init__(self, *args, **kwargs)
            # Store args and kwargs for pickling
            self.init_args = args
            self.init_kwargs = kwargs
            self.skip_cache = skip_cache

            if not skip_cache:
                cache[hsh] = self
        else:
            self = cache[hsh]

        self.hsh = hsh
        return self

    def __getitem__(self, name):
        obj = h5py_wrap_type(h5py.Group.__getitem__(self, name))
        # If it is a group or dataset copy the current file info in
        if isinstance(obj, Group) or isinstance(obj, Dataset):
            obj.file_info = self
        return obj

    def __getstate__(self):
        pass

    def __getnewargs_ex__(self):
        kwargs = self.init_kwargs.copy()
        kwargs['skip_cache'] = self.skip_cache
        return self.init_args, kwargs

    def close(self):
        """Override the close function to remove the file also from the cache"""
        h5py.File.close(self)
        for key in list(cache.keys()):
            if cache[key] == self.hsh:
                del cache[key]
