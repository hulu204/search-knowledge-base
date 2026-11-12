import unittest

from sgt_kb.collection.english_sources import host_is_curated, title_is_relevant


class EnglishSourcesTest(unittest.TestCase):
    def test_search_boundaries_avoid_research_false_positive(self) -> None:
        self.assertFalse(title_is_relevant("Research leadership lessons"))

    def test_rag_boundaries_avoid_storage_false_positive(self) -> None:
        self.assertFalse(title_is_relevant("A new storage format for biology"))

    def test_relevant_search_title_is_selected(self) -> None:
        self.assertTrue(title_is_relevant("Hybrid retrieval with BM25 and vector reranking"))

    def test_recruiting_title_is_rejected_before_ad_match(self) -> None:
        self.assertFalse(title_is_relevant("Hiring engineers for our advertising platform"))

    def test_curated_host_normalizes_www(self) -> None:
        self.assertTrue(host_is_curated("https://www.elastic.co/search-labs/post"))


if __name__ == "__main__":
    unittest.main()
