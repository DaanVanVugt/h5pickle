"""
Test whether pickling hdf5 datasets works in single_process mode
"""

import unittest
import tempfile
import pickle
import os
import h5py
import h5pickle

class PicklingTest(unittest.TestCase):
  file = tempfile.mkstemp(suffix='.h5')[1]
  def setUp(self):
    with h5py.File(self.file, 'w') as f:
      f['a'] = 1

  def test_readonly_skip_cache(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    self.assertEqual(f['a'][()], 1, 'can read from file')

    g = pickle.loads(pickle.dumps(f['a']))

    self.assertEqual(g[()], 1, 'reading from dataset should give correct result')

    f.close()
    g.file.close()

if __name__ == '__main__':
    unittest.main()
