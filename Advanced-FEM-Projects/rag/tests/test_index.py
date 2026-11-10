import unittest

from local_rag import Chunk, chunk_text, retrieve


class IndexTests(unittest.TestCase):
    def test_chunking_handles_empty_and_overlap(self):
        self.assertEqual(chunk_text("   "), [])
        chunks = chunk_text("one two three four five", size=10, overlap=2)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.text for chunk in chunks))
        self.assertIn("two", chunks[1].text)

    def test_retrieval_is_ranked_and_validates_edges(self):
        chunks = [
            Chunk("a", 0, "apples and pears"),
            Chunk("b", 0, "apples apples fruit"),
        ]
        self.assertEqual(retrieve("apples", chunks)[0].source, "b")
        with self.assertRaisesRegex(ValueError, "searchable term"):
            retrieve(" ", chunks)
        with self.assertRaisesRegex(ValueError, "limit"):
            retrieve("apples", chunks, limit=0)

    def test_chunk_parameters_are_checked(self):
        with self.assertRaisesRegex(ValueError, "smaller"):
            chunk_text("sample", size=5, overlap=5)


if __name__ == "__main__":
    unittest.main()
