from unittest import TestCase

import diff_generator

class DiffGeneratorTestCase(TestCase):
    def test_generate_diff_all_added(self):
        added, removed = diff_generator.generate_diff([], ['a', 'b', 'c'])
        
        self.assertCountEqual(['a', 'b', 'c'], added)
        self.assertCountEqual([], removed)

    def test_generate_diff_all_removed(self):
        added, removed = diff_generator.generate_diff(['a', 'b', 'c'], [])
        
        self.assertCountEqual([], added)
        self.assertCountEqual(['a', 'b', 'c'], removed)

    def test_generate_diff_no_diff(self):
        added, removed = diff_generator.generate_diff(['a', 'b', 'c'], ['a', 'b', 'c'])
        
        self.assertCountEqual([], added)
        self.assertCountEqual([], removed)

    def test_generate_diff(self):
        added, removed = diff_generator.generate_diff(['a', 'b', 'c'], ['d', 'b', 'a'])
        
        self.assertCountEqual(['d'], added)
        self.assertCountEqual(['c'], removed)
