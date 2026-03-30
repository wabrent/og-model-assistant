"""
Digital Twins (twin.fun) service for fetching twin market data.
"""
import httpx
from typing import List, Dict, Any, Optional
from loguru import logger


class TwinsService:
    """Service for interacting with twin.fun Digital Twins."""
    
    SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/opengradient/twinfun"
    
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def get_twins(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all digital twins with market data."""
        query = """
        query GetTwins($limit: Int!) {
            digitalTwins(first: $limit, orderBy: totalVolumeETH, orderDirection: desc) {
                id
                owner
                url
                currentSupply
                lastPrice
                marketPrice
                marketCap
                totalVolumeETH
                totalTrades
                totalBuys
                totalSells
                createdAt
                lastTradeAt
            }
        }
        """
        try:
            response = await self.client.post(
                self.SUBGRAPH_URL,
                json={"query": query, "variables": {"limit": limit}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("digitalTwins", [])
        except Exception as e:
            logger.error(f"Get twins error: {e}")
            return []
    
    async def get_twin(self, twin_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific twin by ID."""
        query = """
        query GetTwin($id: ID!) {
            digitalTwin(id: $id) {
                id
                owner
                url
                currentSupply
                lastPrice
                marketPrice
                marketCap
                totalVolumeETH
                totalTrades
                totalBuys
                totalSells
                createdAt
                lastTradeAt
                holders(first: 10, orderBy: balance, orderDirection: desc) {
                    trader { id }
                    balance
                }
            }
        }
        """
        try:
            response = await self.client.post(
                self.SUBGRAPH_URL,
                json={"query": query, "variables": {"id": twin_id}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("digitalTwin")
        except Exception as e:
            logger.error(f"Get twin error: {e}")
            return None
    
    async def get_twin_trades(self, twin_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Get recent trades for a twin."""
        query = """
        query TwinTrades($id: ID!, $limit: Int!) {
            trades(first: $limit, orderBy: timestamp, orderDirection: desc,
                   where: { digitalTwin: $id }) {
                id
                isBuy
                shareAmount
                ethAmount
                pricePerShare
                totalCost
                supplyAfter
                timestamp
                trader { id }
            }
        }
        """
        try:
            response = await self.client.post(
                self.SUBGRAPH_URL,
                json={"query": query, "variables": {"id": twin_id, "limit": limit}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("trades", [])
        except Exception as e:
            logger.error(f"Get twin trades error: {e}")
            return []
    
    async def get_top_holders(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top holders across all twins."""
        query = """
        query TopHolders($limit: Int!) {
            holders(first: $limit, orderBy: balance, orderDirection: desc) {
                id
                balance
                digitalTwin { id }
                trader { id }
            }
        }
        """
        try:
            response = await self.client.post(
                self.SUBGRAPH_URL,
                json={"query": query, "variables": {"limit": limit}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {}).get("holders", [])
        except Exception as e:
            logger.error(f"Get top holders error: {e}")
            return []
    
    async def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol-wide statistics."""
        query = """
        query ProtocolStats {
            protocolStats(first: 1, orderBy: timestamp, orderDirection: desc) {
                totalVolumeETH
                totalTrades
                totalTwins
                totalHolders
            }
        }
        """
        try:
            response = await self.client.post(
                self.SUBGRAPH_URL,
                json={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            stats = data.get("data", {}).get("protocolStats", [])
            return stats[0] if stats else {}
        except Exception as e:
            logger.error(f"Get protocol stats error: {e}")
            return {}


twins_service = TwinsService()


async def get_twins_service() -> TwinsService:
    return twins_service
