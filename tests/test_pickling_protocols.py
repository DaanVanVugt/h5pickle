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

  @unittest.expectedFailure
  def test_0(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    protocol = 0

    h = pickle.loads(pickle.dumps(f, protocol=protocol))
    self.assertEqual(f['a'][()], 1, 'reading from file dataset should give correct result')

    g = pickle.loads(pickle.dumps(f['a'], protocol=protocol))
    self.assertEqual(g[()], 1, 'reading from dataset should give correct result')

    f.close()
    h.close()
    g.file.close()

  @unittest.expectedFailure
  def test_1(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    protocol = 1

    h = pickle.loads(pickle.dumps(f, protocol=protocol))
    self.assertEqual(f['a'][()], 1, 'reading from file dataset should give correct result')

    g = pickle.loads(pickle.dumps(f['a'], protocol=protocol))
    self.assertEqual(g[()], 1, 'reading from dataset should give correct result')

    f.close()
    h.close()
    g.file.close()

  def test_2(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    protocol = 2

    h = pickle.loads(pickle.dumps(f, protocol=protocol))
    self.assertEqual(f['a'][()], 1, 'reading from file dataset should give correct result')

    g = pickle.loads(pickle.dumps(f['a'], protocol=protocol))
    self.assertEqual(g[()], 1, 'reading from dataset should give correct result')

    f.close()
    h.close()
    g.file.close()

  def test_3(self):
    f = h5pickle.File(self.file, 'r', skip_cache=True)
    protocol = 3

    h = pickle.loads(pickle.dumps(f, protocol=protocol))
    self.assertEqual(f['a'][()], 1, 'reading from file dataset should give correct result')

    g = pickle.loads(pickle.dumps(f['a'], protocol=protocol))
    self.assertEqual(g[()], 1, 'reading from dataset should give correct result')

    f.close()
    h.close()
    g.file.close()

  def tearDown(self):
    os.remove(self.file)

if __name__ == '__main__':
    unittest.main()
