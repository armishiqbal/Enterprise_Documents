"""
Tests for Phase 1: Application Configuration and Setup.
"""
import unittest
from pathlib import Path
from src.config import Config, logger


class TestConfig(unittest.TestCase):
    """Test suite for Config module and logging."""

    def test_config_paths(self):
        """Verify upload and vector store paths are instantiated as Path objects."""
        self.assertIsInstance(Config.UPLOAD_DIR, Path)
        self.assertIsInstance(Config.VECTOR_STORE_DIR, Path)

    def test_config_directories_exist(self):
        """Verify data directories exist on filesystem."""
        self.assertTrue(Config.UPLOAD_DIR.exists())
        self.assertTrue(Config.VECTOR_STORE_DIR.exists())

    def test_chunk_settings(self):
        """Verify chunk size and overlap defaults are valid integers."""
        self.assertIsInstance(Config.CHUNK_SIZE, int)
        self.assertIsInstance(Config.CHUNK_OVERLAP, int)
        self.assertGreater(Config.CHUNK_SIZE, 0)
        self.assertGreaterEqual(Config.CHUNK_OVERLAP, 0)
        self.assertLess(Config.CHUNK_OVERLAP, Config.CHUNK_SIZE)

    def test_logger_initialization(self):
        """Verify logger instance is properly initialized."""
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "rag_document")


if __name__ == "__main__":
    unittest.main()
