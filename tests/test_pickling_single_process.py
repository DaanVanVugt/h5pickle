"""
Test whether pickling hdf5 handles works in single_process mode
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
    f = h5pickle.File(self.file, 'a', skip_cache=True)
    self.assertEqual(f['a'][()], 1, 'can read from file')

    g = pickle.loads(pickle.dumps(f, protocol=pickle.HIGHEST_PROTOCOL))

    self.assertEqual(g['a'][()], 1, 'reading from dataset should give correct result')
    # Since cache is skipped I want 2 different handles
    self.assertNotEqual(id(f), id(g), 'pickling and unpickling should create new file handle')
    self.assertTrue(g.skip_cache, 'skip_cache should be propagated')

    f.close()
    g.close()

  def test_readonly(self):
    f = h5pickle.File(self.file, 'a', skip_cache=False)

    g = pickle.loads(pickle.dumps(f, protocol=pickle.HIGHEST_PROTOCOL))

    # Due to the caching mechanism f and g should be the same
    self.assertEqual(id(f), id(g), 'pickling and unpickling should use cache')

    self.assertEqual(g['a'][()], 1, 'reading from dataset should give correct result')

    # skip_cache should be propagated (but they're the same so kind of meaningless test)
    self.assertFalse(g.skip_cache, 'skip_cache should be propagated')

    f.close()

  def tearDown(self):
    os.remove(self.file)


class PicklingWritableTest(unittest.TestCase):
  file = tempfile.mkstemp(suffix='.h5')[1]
  def test_create_writable_file(self):
    f = h5pickle.File(self.file, 'w', skip_cache=True)

    got_oserror = False
    try:
      g = pickle.loads(pickle.dumps(f, protocol=pickle.HIGHEST_PROTOCOL))
      # We expect an error here, since we cannot open on multiple processes
    except OSError:
      got_oserror = True

    self.assertTrue(got_oserror, 'Forbidden to open write-only file twice')

    f.close()
    os.remove(self.file)


if __name__ == '__main__':
    unittest.main()
