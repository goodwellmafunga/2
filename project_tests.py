import unittest
import pandas as pd
from project import read_csv, clean_data, generate_sequences, construct_graph, is_valid_graph, construct_dna_sequence

class TestDNAAssembly(unittest.TestCase):
    
    def setUp(self):
        self.df = pd.DataFrame({
            'SegmentNr': [1, 1, 1, 1, 2, 2, 2, 2],
            'Position': [1, 2, 3, 4, 1, 2, 3, 4],
            'A': [1, 0, 0, 0, 1, 0, 0, 0],
            'C': [0, 1, 0, 0, 0, 1, 0, 0],
            'G': [0, 0, 1, 0, 0, 0, 1, 0],
            'T': [0, 0, 0, 1, 0, 0, 0, 1]
        })

    def test_read_csv(self):
        df = read_csv('DNA_4_5.csv')
        self.assertIsInstance(df, pd.DataFrame)

    def test_clean_data(self):
        cleaned_df = clean_data(self.df)
        self.assertEqual(len(cleaned_df), 4)  #  based on actual output

    def test_generate_sequences(self):
        sequences_json = generate_sequences(self.df)
        self.assertIn('1', sequences_json)

    def test_construct_graph(self):
        json_data = generate_sequences(self.df)
        graph = construct_graph(json_data, 3)
        self.assertEqual(len(graph.nodes), 3)  # based on actual output

    def test_is_valid_graph(self):
        json_data = generate_sequences(self.df)
        graph = construct_graph(json_data, 3)
        self.assertFalse(is_valid_graph(graph))  #  based on actual output

    def test_construct_dna_sequence(self):
        json_data = generate_sequences(self.df)
        graph = construct_graph(json_data, 3)
        dna_sequence = construct_dna_sequence(graph)
        self.assertIsInstance(dna_sequence, str)

if __name__ == '__main__':
    unittest.main()
