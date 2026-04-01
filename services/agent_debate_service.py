"""
AI Agent Debate Service
"""
import asyncio
from typing import List, Dict, Any, Optional
from loguru import logger


class DebateAgent:
    """Represents a debating AI agent with a stance."""
    
    def __init__(self, name: str, stance: str, personality: str):
        self.name = name
        self.stance = stance
        self.personality = personality
    
    def get_system_prompt(self, topic: str) -> str:
        return f"""You are {self.name}, a {self.personality}. Your stance on "{topic}" is: {self.stance}.

Rules:
- Argue passionately for your stance
- Use data, logic, and examples
- Respond directly to your opponent's points
- Keep responses concise (2-3 paragraphs)
- Stay in character at all times"""


class AgentDebateService:
    """Service for running AI agent debates."""
    
    # Predefined debate pairs
    DEBATE_PAIRS = {
        "crypto": {
            "agent1": DebateAgent(
                name="Bull Bot",
                stance="Crypto is the future of finance. Decentralization, transparency, and innovation will revolutionize everything.",
                personality="optimistic crypto analyst"
            ),
            "agent2": DebateAgent(
                name="Bear Bot",
                stance="Crypto is a speculative bubble with no real utility. It's volatile, energy-wasteful, and mostly used for scams.",
                personality="skeptical traditional economist"
            )
        },
        "ai_future": {
            "agent1": DebateAgent(
                name="Optimus",
                stance="AI will solve humanity's biggest problems: disease, climate change, poverty. It's the greatest invention ever.",
                personality="enthusiastic technologist"
            ),
            "agent2": DebateAgent(
                name="Pessimus",
                stance="AI poses existential risks: job loss, surveillance, autonomous weapons. We're building our own replacement.",
                personality="cautious ethicist"
            )
        },
        "defi": {
            "agent1": DebateAgent(
                name="DeFi Maximalist",
                stance="DeFi eliminates middlemen, provides financial freedom, and creates transparent, permissionless markets.",
                personality="crypto DeFi enthusiast"
            ),
            "agent2": DebateAgent(
                name="TradFi Defender",
                stance="DeFi is unregulated, prone to hacks, and lacks consumer protection. Traditional finance exists for good reasons.",
                personality="traditional finance expert"
            )
        },
        "nft": {
            "agent1": DebateAgent(
                name="NFT Visionary",
                stance="NFTs revolution digital ownership, creator economy, and cultural expression. This is just the beginning.",
                personality="digital art collector and creator"
            ),
            "agent2": DebateAgent(
                name="NFT Skeptic",
                stance="NFTs are mostly speculation and hype. The market crashed, most projects failed, and utility is minimal.",
                personality="pragmatic market analyst"
            )
        }
    }
    
    def get_available_topics(self) -> List[Dict[str, str]]:
        """Get available debate topics."""
        return [
            {"id": tid, "name": tid.replace("_", " ").title(), "agents": [pair["agent1"].name, pair["agent2"].name]}
            for tid, pair in self.DEBATE_PAIRS.items()
        ]
    
    async def run_debate(
        self,
        topic: str,
        rounds: int = 3,
        custom_topic: Optional[str] = None
    ) -> Dict[str, Any]:
        """Run a debate between two AI agents."""
        if topic in self.DEBATE_PAIRS:
            pair = self.DEBATE_PAIRS[topic]
            agent1 = pair["agent1"]
            agent2 = pair["agent2"]
        else:
            agent1 = DebateAgent("Agent Alpha", "For", "analytical debater")
            agent2 = DebateAgent("Agent Beta", "Against", "critical debater")
        
        debate_topic = custom_topic or topic.replace("_", " ")
        
        messages = [
            {"role": "system", "content": agent1.get_system_prompt(debate_topic)},
            {"role": "user", "content": f"Present your opening argument on: {debate_topic}"}
        ]
        
        transcript = []
        
        for round_num in range(1, rounds + 1):
            # Agent 1 speaks
            arg1 = f"**{agent1.name}** (Round {round_num}):\n*[Simulated argument based on stance: {agent1.stance[:80]}...]*"
            transcript.append({"speaker": agent1.name, "round": round_num, "argument": arg1})
            
            # Agent 2 responds
            arg2 = f"**{agent2.name}** (Round {round_num}):\n*[Simulated counter-argument based on stance: {agent2.stance[:80]}...]*"
            transcript.append({"speaker": agent2.name, "round": round_num, "argument": arg2})
        
        return {
            "topic": debate_topic,
            "rounds": rounds,
            "agents": [agent1.name, agent2.name],
            "transcript": transcript,
            "status": "completed"
        }


agent_debate_service = AgentDebateService()
