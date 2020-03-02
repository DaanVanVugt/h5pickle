try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
setup(
  name = 'h5pickle',
  packages = ['h5pickle'], # this must be the same as the name above
  version = '0.4.2',
  description = 'Wrap h5py objects to allow pickling',
  author = 'Daan van Vugt',
  author_email = 'daanvanvugt@gmail.com',
  url = 'https://github.com/exteris/h5pickle', # use the URL to the github repo
  download_url = 'https://github.com/exteris/h5pickle/archive/0.4.2.tar.gz', # I'll explain this in a second
  keywords = ['h5py', 'hdf5', 'pickle', 'dask', 'python'], # arbitrary keywords
  install_requires = [
    'h5py',
    'cachetools',
  ],
  classifiers = [],
)
