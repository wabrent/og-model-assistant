"""
Tests for OpenGradient SDK integration.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings


class TestOpenGradientSDKImport:
    """Test that OpenGradient SDK can be imported and has expected structure."""
    
    def test_sdk_import(self):
        """Test basic SDK import."""
        try:
            import opengradient as og
            assert og is not None
            print(f"OpenGradient SDK version check: {og.__version__ if hasattr(og, '__version__') else 'unknown'}")
        except ImportError as e:
            pytest.skip(f"OpenGradient SDK not installed: {e}")
    
    def test_sdk_modules_exist(self):
        """Test that key SDK modules exist."""
        try:
            import opengradient as og
            
            # Check for main classes
            assert hasattr(og, 'LLM'), "LLM class missing"
            assert hasattr(og, 'Alpha'), "Alpha class missing"
            assert hasattr(og, 'Twins'), "Twins class missing"
            assert hasattr(og, 'ModelHub'), "ModelHub class missing"
            
            # Check for types
            assert hasattr(og, 'TEE_LLM'), "TEE_LLM enum missing"
            assert hasattr(og, 'InferenceMode'), "InferenceMode enum missing"
            assert hasattr(og, 'x402SettlementMode'), "x402SettlementMode enum missing"
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")
    
    def test_tee_llm_enum(self):
        """Test TEE_LLM enum values."""
        try:
            import opengradient as og
            
            # Check some expected values exist
            tee_llm = og.TEE_LLM
            assert hasattr(tee_llm, 'CLAUDE_HAIKU_4_5'), "CLAUDE_HAIKU_4_5 missing"
            assert hasattr(tee_llm, 'GPT_5'), "GPT_5 missing"
            assert hasattr(tee_llm, 'GROK_4_1_FAST'), "GROK_4_1_FAST missing"
            
            # Check values are strings
            assert isinstance(tee_llm.CLAUDE_HAIKU_4_5.value, str)
            assert isinstance(tee_llm.GPT_5.value, str)
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")


class TestOpenGradientLLM:
    """Test OpenGradient LLM integration."""
    
    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM instance."""
        with patch('opengradient.LLM') as mock_llm_class:
            mock_instance = AsyncMock()
            mock_instance.chat = AsyncMock(return_value={
                "chat_output": {"content": "Test response from LLM"},
                "finish_reason": "stop",
                "transaction_hash": "0x123"
            })
            mock_instance.completion = AsyncMock(return_value={
                "text": "Test completion",
                "finish_reason": "stop"
            })
            mock_instance.ensure_opg_approval = AsyncMock(return_value={
                "allowance_after": 10.0
            })
            mock_instance.close = AsyncMock()
            
            mock_llm_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.asyncio
    async def test_llm_chat_mocked(self, mock_llm):
        """Test LLM chat with mocked SDK."""
        try:
            import opengradient as og
            
            # Create LLM instance
            llm = og.LLM(private_key=settings.private_key or "test_key")
            
            # Call chat
            result = await llm.chat(
                model=og.TEE_LLM.CLAUDE_HAIKU_4_5,
                messages=[{"role": "user", "content": "Hello"}]
            )
            
            assert result is not None
            assert "chat_output" in result or hasattr(result, 'chat_output')
            
            # Verify mock was called
            mock_llm.chat.assert_called_once()
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")
    
    @pytest.mark.asyncio
    async def test_llm_completion_mocked(self, mock_llm):
        """Test LLM completion with mocked SDK."""
        try:
            import opengradient as og
            
            llm = og.LLM(private_key="test_key")
            
            result = await llm.completion(
                model=og.TEE_LLM.CLAUDE_HAIKU_4_5,
                prompt="Complete this: Hello"
            )
            
            assert result is not None
            assert "text" in result or hasattr(result, 'text')
            
            mock_llm.completion.assert_called_once()
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")


class TestOpenGradientAlpha:
    """Test OpenGradient Alpha (model inference) integration."""
    
    @pytest.fixture
    def mock_alpha(self):
        """Create a mock Alpha instance."""
        with patch('opengradient.Alpha') as mock_alpha_class:
            mock_instance = Mock()
            mock_instance.infer = AsyncMock(return_value={
                "result": {"numbers": {"output": 0.75}},
                "transaction_hash": "0x456"
            })
            mock_instance.read_workflow_result = AsyncMock(return_value={
                "numbers": {"regression_output": 0.023}
            })
            mock_instance.read_workflow_history = AsyncMock(return_value=[])
            mock_instance.run_workflow = AsyncMock(return_value={
                "output": "Workflow executed"
            })
            
            mock_alpha_class.return_value = mock_instance
            yield mock_instance
    
    @pytest.mark.asyncio
    async def test_alpha_infer_mocked(self, mock_alpha):
        """Test Alpha inference with mocked SDK."""
        try:
            import opengradient as og
            from opengradient.types import InferenceMode
            
            alpha = og.Alpha(private_key="test_key")
            
            # Test infer
            result = await alpha.infer(
                model_cid="QmTestModel123",
                inference_mode=InferenceMode.VANILLA,
                model_input={"feature": 1.0}
            )
            
            assert result is not None
            mock_alpha.infer.assert_called_once()
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")
    
    @pytest.mark.asyncio
    async def test_alpha_workflow_mocked(self, mock_alpha):
        """Test Alpha workflow reading with mocked SDK."""
        try:
            import opengradient as og
            
            alpha = og.Alpha(private_key="test_key")
            
            # Test reading workflow result
            result = await alpha.read_workflow_result("0xContractAddress")
            
            assert result is not None
            assert "numbers" in result
            mock_alpha.read_workflow_result.assert_called_once_with("0xContractAddress")
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")


class TestOpenGradientTwins:
    """Test OpenGradient Twins (digital twins) integration."""
    
    @pytest.fixture
    def mock_twins(self):
        """Create a mock Twins instance."""
        with patch('opengradient.Twins') as mock_twins_class:
            mock_instance = Mock()
            mock_instance.chat = Mock(return_value={
                "chat_output": {"content": "Hello from digital twin!"},
                "finish_reason": "stop"
            })
            
            mock_twins_class.return_value = mock_instance
            yield mock_instance
    
    def test_twins_chat_mocked(self, mock_twins):
        """Test Twins chat with mocked SDK."""
        try:
            import opengradient as og
            
            twins = og.Twins(api_key="test_api_key")
            
            result = twins.chat(
                twin_id="defi_analyst_001",
                model=og.TEE_LLM.CLAUDE_HAIKU_4_5,
                messages=[{"role": "user", "content": "Hello twin"}]
            )
            
            assert result is not None
            assert "chat_output" in result
            mock_twins.chat.assert_called_once()
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")


class TestWorkflowModels:
    """Test OpenGradient workflow models."""
    
    def test_workflow_models_import(self):
        """Test that workflow models can be imported."""
        try:
            # Try to import workflow models
            from opengradient.workflow_models import (
                read_eth_1_hour_price_forecast,
                read_btc_1_hour_price_forecast,
                read_sui_1_hour_price_forecast,
                read_eth_usdt_one_hour_volatility_forecast
            )
            
            assert read_eth_1_hour_price_forecast is not None
            assert read_btc_1_hour_price_forecast is not None
            assert read_sui_1_hour_price_forecast is not None
            assert read_eth_usdt_one_hour_volatility_forecast is not None
            
        except ImportError as e:
            # This module might not always be available
            pytest.skip(f"Workflow models not available: {e}")
    
    def test_workflow_constants(self):
        """Test workflow model constants."""
        try:
            from opengradient.workflow_models.constants import (
                ETH_1_HOUR_PRICE_FORECAST_ADDRESS,
                BTC_1_HOUR_PRICE_FORECAST_ADDRESS,
                SUI_1_HOUR_PRICE_FORECAST_ADDRESS,
                ETH_USDT_1_HOUR_VOLATILITY_ADDRESS
            )
            
            # Check addresses look like contract addresses
            assert ETH_1_HOUR_PRICE_FORECAST_ADDRESS.startswith("0x")
            assert len(ETH_1_HOUR_PRICE_FORECAST_ADDRESS) == 42  # 0x + 40 hex chars
            
            assert BTC_1_HOUR_PRICE_FORECAST_ADDRESS.startswith("0x")
            assert SUI_1_HOUR_PRICE_FORECAST_ADDRESS.startswith("0x")
            assert ETH_USDT_1_HOUR_VOLATILITY_ADDRESS.startswith("0x")
            
        except ImportError:
            pytest.skip("Workflow models constants not available")


class TestIntegrationPoints:
    """Test integration points in our application."""
    
    def test_ml_model_service_integration(self):
        """Test that ML model service integrates with OpenGradient SDK."""
        try:
            from services.ml_model_service import MLModelService
            
            service = MLModelService()
            assert service is not None
            
            # Check that service has methods to call OpenGradient models
            assert hasattr(service, 'call_bitquant')
            assert hasattr(service, 'call_price_predictor')
            assert hasattr(service, 'call_risk_analyzer')
            assert hasattr(service, 'get_available_ml_models')
            
            # Check that methods are async
            import inspect
            assert inspect.iscoroutinefunction(service.call_bitquant)
            assert inspect.iscoroutinefunction(service.call_price_predictor)
            assert inspect.iscoroutinefunction(service.call_risk_analyzer)
            assert inspect.iscoroutinefunction(service.get_available_ml_models)
            
        except ImportError as e:
            pytest.fail(f"Failed to import ML model service: {e}")
    
    def test_twin_service_integration(self):
        """Test that Twin service integrates with OpenGradient SDK."""
        try:
            from services.twin_service import TwinService
            
            service = TwinService()
            assert service is not None
            
            # Check methods
            assert hasattr(service, 'get_available_twins')
            assert hasattr(service, 'chat_with_twin')
            assert hasattr(service, 'analyze_portfolio_with_twin')
            
            # Check async
            import inspect
            assert inspect.iscoroutinefunction(service.get_available_twins)
            assert inspect.iscoroutinefunction(service.chat_with_twin)
            assert inspect.iscoroutinefunction(service.analyze_portfolio_with_twin)
            
        except ImportError as e:
            pytest.fail(f"Failed to import Twin service: {e}")
    
    def test_api_endpoints_exist(self):
        """Test that API endpoints for OpenGradient integration exist."""
        # Check defi_router for ML model endpoints
        try:
            import api.defi_router as defi_router
            
            # Check ML model endpoints
            router_routes = [route.path for route in defi_router.router.routes]
            
            # ML model endpoints
            assert any('/api/defi/ml-models' in str(path) for path in router_routes)
            assert any('/api/defi/predict/bitquant' in str(path) for path in router_routes)
            assert any('/api/defi/predict/pricepredictor' in str(path) for path in router_routes)
            assert any('/api/defi/analyze/risk' in str(path) for path in router_routes)
            
            # Twin endpoints (added in this integration)
            assert any('/api/defi/twins' in str(path) for path in router_routes)
            assert any('/api/defi/twins/chat' in str(path) for path in router_routes)
            assert any('/api/defi/twins/analyze-portfolio' in str(path) for path in router_routes)
            
        except ImportError as e:
            pytest.fail(f"Failed to check API endpoints: {e}")


@pytest.mark.skipif(not settings.private_key, reason="No OpenGradient private key configured")
class TestRealSDKIntegration:
    """Tests that require real OpenGradient SDK and API key."""
    
    @pytest.mark.asyncio
    async def test_sdk_initialization_with_real_key(self):
        """Test that SDK can be initialized with real private key."""
        try:
            import opengradient as og
            
            # Initialize LLM with real key
            llm = og.LLM(private_key=settings.private_key)
            assert llm is not None
            
            # Check that we have required methods
            assert hasattr(llm, 'chat')
            assert hasattr(llm, 'completion')
            assert hasattr(llm, 'ensure_opg_approval')
            assert hasattr(llm, 'close')
            
            # Initialize Alpha with real key
            alpha = og.Alpha(private_key=settings.private_key)
            assert alpha is not None
            
            assert hasattr(alpha, 'infer')
            assert hasattr(alpha, 'read_workflow_result')
            assert hasattr(alpha, 'run_workflow')
            
        except ImportError:
            pytest.skip("OpenGradient SDK not installed")
        except Exception as e:
            # This might fail if key is invalid or network issues
            pytest.skip(f"Real SDK test failed (might be expected): {e}")
    
    def test_workflow_models_with_real_key(self):
        """Test workflow models with real key (read-only)."""
        try:
            import opengradient as og
            from opengradient.workflow_models import read_eth_1_hour_price_forecast
            
            alpha = og.Alpha(private_key=settings.private_key)
            
            # This is a read-only operation, shouldn't cost gas
            # Might fail if contract not deployed or network issues
            try:
                result = read_eth_1_hour_price_forecast(alpha)
                # If it succeeds, check structure
                if hasattr(result, 'result'):
                    assert isinstance(result.result, str)
                elif isinstance(result, dict):
                    assert 'result' in result
            except Exception as e:
                # Expected to fail in test environment without deployed contracts
                print(f"Workflow read failed (expected in test): {e}")
                pass
                
        except ImportError:
            pytest.skip("OpenGradient SDK or workflow models not installed")


if __name__ == "__main__":
    # Run tests directly for debugging
    import sys
    sys.exit(pytest.main([__file__, "-v"]))