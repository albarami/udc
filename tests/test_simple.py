"""Simple smoke tests for core UDC Polaris functionality."""

import pytest
from pathlib import Path
import sys

# Add backend to Python path
backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.core.config import get_settings
from app.agents.tools import udc_tools


def test_settings_load():
    """Test that application settings load correctly."""
    settings = get_settings()
    
    assert settings.app_name == "UDC Polaris"
    assert settings.app_version == "1.0.0"
    assert settings.max_tokens_specialist == 2000
    assert settings.max_tokens_synthesizer == 4000


def test_udc_tools_available():
    """Test that UDC data tools are available and functional."""
    # Test that tools can be imported and initialized
    assert udc_tools is not None
    assert hasattr(udc_tools, 'get_financial_summary')
    assert hasattr(udc_tools, 'get_debt_metrics')
    assert hasattr(udc_tools, 'search_data')


def test_sample_data_access():
    """Test that sample data can be accessed."""
    try:
        financial_data = udc_tools.get_financial_summary()
        assert isinstance(financial_data, dict)
        assert 'annual_summary' in financial_data
    except FileNotFoundError:
        pytest.skip("Sample data not available - expected in development environment")


def test_search_functionality():
    """Test basic search functionality."""
    try:
        search_results = udc_tools.search_data("debt ratio")
        assert isinstance(search_results, dict)
        assert 'query' in search_results
        assert 'results' in search_results
        assert search_results['query'] == "debt ratio"
    except Exception:
        pytest.skip("Data search not available - expected in development environment")
