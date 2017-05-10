#!/usr/bin/python
import unittest
from sdapi import SDAPI

class TestSDAPI(unittest.TestCase):
    def setUp(self):
        self.default_collection_name = "PUBLICSEARCH"
        self.default_collection_id = "97"
        self.default_doi = "10.15252/embj.201592559"
        self.default_article_title = "Toxic gain of function from mutant FUS protein is crucial to trigger cell autonomous motor neuron loss"
        self.default_journal = "The EMBO journal"
        self.default_panel_list = ['20934', '20936', '20937', '20938', '20939', '20940']
        self.default_panel_id = "20936"
        self.default_panel_label = "Figure 1-B"
    
    def test_request_collection(self):
        #./sdapi.py --collection PUBLICSEARCH
        self.assertEqual(SDAPI.request_collection(self.default_collection_name).id, 
        self.default_collection_id)    

    def test_request_article_list(self):
        self.assertEqual(len(SDAPI.request_article_list(self.default_collection_id).doi_list), 713)
        
    def test_request_article(self):
        #./sdapi.py --doi 10.15252/embj.201592559
        self.assertEqual(SDAPI.request_article(self.default_doi, self.default_collection_id).title, self.default_article_title)
        self.assertEqual(SDAPI.request_article(self.default_doi, self.default_collection_id).journal, self.default_journal)
        
    def test_request_figure(self):
        #./sdapi.py -D "10.15252/embj.201592559" -F 1
        self.assertEqual(SDAPI.request_figure(self.default_doi, self.default_collection_id, 1).panels, self.default_panel_list)
        
    def test_request_panel(self):
        #./sdapi.py --panel 20936
        self.assertEqual(SDAPI.request_panel(self.default_panel_id).label, self.default_panel_label)
        self.assertEqual(len(SDAPI.request_panel(self.default_panel_id).tags['entities']), 5)
        
if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSDAPI)
    unittest.TextTestRunner(verbosity=2).run(suite)