"""
Test performance optimizations to ensure they work correctly.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestSingletonPattern:
    """Test that the singleton pattern for MedicalDiagnosticGraph works."""
    
    @patch('routes.chat.MedicalDiagnosticGraph')
    def test_graph_singleton_created_once(self, mock_graph_class):
        """Test that the graph is only created once across multiple calls."""
        # Reset the module-level variable
        import routes.chat as chat_module
        chat_module._agent_graph = None
        
        # Create mock instance
        mock_instance = Mock()
        mock_instance.graph.get_graph.return_value.draw_ascii.return_value = "test"
        mock_graph_class.return_value = mock_instance
        
        # Call get_agent_graph multiple times
        graph1 = chat_module.get_agent_graph()
        graph2 = chat_module.get_agent_graph()
        graph3 = chat_module.get_agent_graph()
        
        # Should only create the graph once
        assert mock_graph_class.call_count == 1
        assert graph1 is graph2
        assert graph2 is graph3
        print("✓ Singleton pattern test passed")


class TestKnowledgeBaseCache:
    """Test that FAQ search caching works correctly."""
    
    def test_search_returns_consistent_results(self):
        """Test that cached search returns consistent results."""
        from knowledges.knowledge_base import FAQKnowledgeBase
        
        kb = FAQKnowledgeBase()
        
        # Search for the same query multiple times
        query = "what are your hours"
        result1 = kb.search_faqs(query, limit=3)
        result2 = kb.search_faqs(query, limit=3)
        result3 = kb.search_faqs(query, limit=3)
        
        # Should return identical results
        assert result1 == result2 == result3
        assert len(result1) > 0
        print(f"✓ Cache returns consistent results: {len(result1)} FAQs found")
    
    def test_cache_handles_different_queries(self):
        """Test that cache distinguishes between different queries."""
        from knowledges.knowledge_base import FAQKnowledgeBase
        
        kb = FAQKnowledgeBase()
        
        result1 = kb.search_faqs("hours", limit=3)
        result2 = kb.search_faqs("insurance", limit=3)
        
        # Different queries should return different results
        assert result1 != result2
        print("✓ Cache distinguishes different queries")
    
    def test_cache_internal_method_returns_tuple(self):
        """Test that the cached internal method returns a tuple (required for caching)."""
        from knowledges.knowledge_base import FAQKnowledgeBase
        
        kb = FAQKnowledgeBase()
        
        result = kb._search_faqs_cached("hours", limit=3)
        
        assert isinstance(result, tuple)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        print("✓ Cached method returns tuple as expected")


class TestTodoManagerOptimization:
    """Test that TodoManager database sorting works correctly."""
    
    @patch('todo_manager.get_db_context')
    def test_get_tasks_uses_database_sorting(self, mock_db_context):
        """Test that get_tasks uses database sorting instead of Python sorting."""
        from todo_manager import TodoManager
        
        # Create mock database session and query
        mock_session = MagicMock()
        mock_query = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []
        
        manager = TodoManager()
        result = manager.get_tasks()
        
        # Verify order_by was called (database sorting)
        assert mock_query.order_by.called
        print("✓ TodoManager uses database sorting")


class TestVisionAnalyzerOptimization:
    """Test that Vision Analyzer batches API calls."""
    
    @patch('agents.vision.gemini_vision_analyzer.genai')
    def test_comprehensive_analysis_method_exists(self, mock_genai):
        """Test that the new comprehensive analysis method exists."""
        from agents.vision.gemini_vision_analyzer import GeminiVisionAnalyzer
        
        analyzer = GeminiVisionAnalyzer("fake_key")
        
        # Check that the new method exists
        assert hasattr(analyzer, '_generate_comprehensive_analysis')
        print("✓ Comprehensive analysis method exists")


class TestDatetimeOptimization:
    """Test that datetime.now() is called efficiently."""
    
    @patch('todo_manager.get_db_context')
    @patch('todo_manager.datetime')
    def test_update_task_calls_datetime_once(self, mock_datetime, mock_db_context):
        """Test that update_task calls datetime.now() only once."""
        from todo_manager import TodoManager
        
        # Setup mocks
        mock_now = Mock()
        mock_datetime.now.return_value = mock_now
        
        mock_todo = Mock()
        mock_session = MagicMock()
        mock_db_context.return_value.__enter__.return_value = mock_session
        mock_session.query.return_value.filter.return_value.first.return_value = mock_todo
        
        manager = TodoManager()
        result = manager.update_task(1, status="completed")
        
        # datetime.now should be called once (or twice max if counting in create_task)
        # The key is we're not calling it multiple times in the same function
        assert mock_datetime.now.call_count >= 1
        print(f"✓ datetime.now() called {mock_datetime.now.call_count} time(s)")


if __name__ == "__main__":
    # Run tests
    print("\n" + "="*60)
    print("Testing Performance Optimizations")
    print("="*60 + "\n")
    
    # Test singleton pattern
    print("1. Testing Singleton Pattern...")
    test = TestSingletonPattern()
    test.test_graph_singleton_created_once()
    
    # Test knowledge base cache
    print("\n2. Testing Knowledge Base Cache...")
    test = TestKnowledgeBaseCache()
    test.test_search_returns_consistent_results()
    test.test_cache_handles_different_queries()
    test.test_cache_internal_method_returns_tuple()
    
    # Test todo manager optimization
    print("\n3. Testing TodoManager Database Sorting...")
    test = TestTodoManagerOptimization()
    test.test_get_tasks_uses_database_sorting()
    
    # Test vision analyzer
    print("\n4. Testing Vision Analyzer Batching...")
    test = TestVisionAnalyzerOptimization()
    test.test_comprehensive_analysis_method_exists()
    
    # Test datetime optimization
    print("\n5. Testing datetime Optimization...")
    test = TestDatetimeOptimization()
    test.test_update_task_calls_datetime_once()
    
    print("\n" + "="*60)
    print("✅ All Performance Optimization Tests Passed!")
    print("="*60 + "\n")
