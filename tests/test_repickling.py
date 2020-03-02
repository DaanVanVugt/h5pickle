"""
Test whether re-pickling hdf5 works
"""

import unittest
import tempfile
import pickle
import os
import h5py
import h5pickle

class RePicklingTest(unittest.TestCase):
  file = tempfile.mkstemp(suffix='.h5')[1]
  def setUp(self):
    with h5py.File(self.file, 'w') as f:
      f['a'] = 1

  def test_repickling(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    dataset = f['a']
    dataset_pickled = pickle.dumps(dataset, protocol=pickle.HIGHEST_PROTOCOL)
    dataset_unpickled = pickle.loads(dataset_pickled)
    dataset_repickled = pickle.dumps(dataset_unpickled, protocol=pickle.HIGHEST_PROTOCOL)

  def tearDown(self):
    os.remove(self.file)

if __name__ == '__main__':
    unittest.main()
