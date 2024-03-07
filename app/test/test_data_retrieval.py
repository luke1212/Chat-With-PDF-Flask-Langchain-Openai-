import os
import unittest
import file_server
from mockito import mock, when, verify


class TestFileInfo(unittest.TestCase):
    def test_get_file_info(self):
        message = "What is the file info?"
        filename = "example.txt"
        doc_path = "/path/to/docs"
        
        # Mock the dependencies
        file_server = mock()
        os = mock()
        
        # Set up the mock behavior
        when(file_server).embed_doc(doc_path).thenReturn("embedded_doc")
        when(os).join(doc_path, filename).thenReturn("/path/to/docs/example.txt")
        
        # Call the function under test
        v, question, source = file_server.get_file_info(message, filename, file_server, os)
        
        # Verify the expected behavior
        self.assertEqual(v, "embedded_doc")
        self.assertEqual(question, message)
        self.assertEqual(source, "/path/to/docs/example.txt")
        
        # Verify the mock interactions
        verify(file_server).embed_doc(doc_path)
        verify(os).join(doc_path, filename)

if __name__ == '__main__':
    unittest.main()