# app/agents/notifier.py
from app.agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from app.core.api_clients import google_client
from app.config import get_settings
import requests
import json
from datetime import datetime
from loguru import logger

settings = get_settings()


class NotifierAgent(BaseAgent):
    """
    Send notifications via Discord webhooks
    Supports rich embeds for visual impact
    """
    
    def __init__(self):
        super().__init__(
            name="Notifier",
            model=settings.NOTIFIER_MODEL,
            api_client=google_client
        )
        self.webhook_url = settings.DISCORD_WEBHOOK_URL
    
    async def process(self, request: AgentRequest) -> AgentResponse:
        try:
            # Get notification type
            notification_type = request.parameters.get("type", "info")
            
            # Generate message content
            message_content = await self._generate_message(request.query, notification_type)
            
            # Create embed data if context provided
            embed_data = self._create_embed(notification_type, request.context)
            
            # Send to Discord
            success = self._send_discord_notification(
                message=message_content,
                embed=embed_data
            )
            
            if not success:
                logger.warning("Discord notification failed, falling back to log")
            
            return AgentResponse(
                agent_name=self.name,
                success=True,
                data={
                    "message": message_content,
                    "channel": "discord" if success else "log",
                    "sent_at": datetime.utcnow().isoformat(),
                    "notification_type": notification_type
                }
            )
            
        except Exception as e:
            logger.error(f"Notifier error: {str(e)}")
            return AgentResponse(
                agent_name=self.name,
                success=False,
                error=str(e)
            )
    
    async def _generate_message(self, query: str, notification_type: str) -> str:
        """Generate notification message using LLM"""
        
        prompt = f"""Create a concise notification message for: {query}

Type: {notification_type}

Keep it short (1-2 sentences), friendly, and action-oriented.
Add relevant emoji based on type (✅ for success, ⚠️ for warning, 📊 for analysis, etc.)"""
        
        try:
            response = await self.api_client.generate_content(
                model_name=self.model,
                prompt=prompt,
                temperature=0.7,
                max_tokens=150
            )
            
            return response.get("text", f"📢 {query}")
        except Exception as e:
            logger.warning(f"LLM message generation failed: {e}")
            return f"📢 {query}"
    
    def _create_embed(self, notification_type: str, context: dict) -> dict:
        """Create Discord embed with rich formatting"""
        
        # Color codes
        colors = {
            "success": 5814783,  # Green
            "warning": 16776960,  # Yellow
            "error": 15548997,   # Red
            "info": 3447003,     # Blue
            "forecast": 10181046, # Purple
            "optimization": 15844367  # Gold
        }
        
        embed = {
            "title": self._get_title(notification_type),
            "color": colors.get(notification_type, colors["info"]),
            "timestamp": datetime.utcnow().isoformat(),
            "footer": {
                "text": "AURA Chain AI Platform"
            },
            "fields": []
        }
        
        # Add fields based on context
        if "forecast" in context:
            forecast_data = context["forecast"]
            embed["fields"].append({
                "name": "📈 Forecast Period",
                "value": f"{forecast_data.get('periods', 'N/A')} days",
                "inline": True
            })
            
        if "savings" in context:
            savings = context["savings"]
            embed["fields"].append({
                "name": "💰 Expected Savings",
                "value": f"₹{savings.get('amount', 0):,.2f} ({savings.get('percentage', 0):.1f}%)",
                "inline": True
            })
        
        if "bullwhip_reduction" in context:
            bullwhip = context["bullwhip_reduction"]
            embed["fields"].append({
                "name": "📉 Bullwhip Reduction",
                "value": f"{bullwhip.get('improvement_percentage', 0):.1f}%",
                "inline": True
            })
        
        if "order_details" in context:
            order = context["order_details"]
            embed["fields"].append({
                "name": "📦 Order Recommendation",
                "value": f"Order {order.get('quantity', 0)} units at reorder point {order.get('reorder_point', 0)}",
                "inline": False
            })
        
        return embed
    
    def _get_title(self, notification_type: str) -> str:
        """Get title based on notification type"""
        titles = {
            "success": "✅ Operation Successful",
            "warning": "⚠️ Warning",
            "error": "❌ Error Occurred",
            "info": "ℹ️ Information",
            "forecast": "📊 Forecast Generated",
            "optimization": "⚙️ Optimization Complete",
            "data_processed": "📁 Data Processed"
        }
        return titles.get(notification_type, "📢 Notification")
    
    def _send_discord_notification(self, message: str, embed: dict = None) -> bool:
        """Send notification to Discord via webhook"""
        
        if not self.webhook_url or self.webhook_url == "YOUR_WEBHOOK_URL_HERE":
            logger.info(f"Discord webhook not configured. Message: {message}")
            return False
        
        try:
            payload = {
                "content": message,
                "username": "AURA Chain Bot",
                "avatar_url": "https://i.imgur.com/4M34hi2.png"  # Optional: Add bot avatar
            }
            
            if embed and embed.get("fields"):
                payload["embeds"] = [embed]
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=5
            )
            
            if response.status_code == 204:
                logger.info(f"Discord notification sent: {message[:50]}...")
                return True
            else:
                logger.warning(f"Discord API error: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Discord webhook failed: {str(e)}")
            return False
    
    # Helper method for other agents to send quick notifications
    @staticmethod
    def send_quick_notification(
        message: str,
        notification_type: str = "info",
        context: dict = None
    ):
        """Static method for other agents to send notifications"""
        notifier = NotifierAgent()
        
        try:
            notifier._send_discord_notification(
                message=message,
                embed=notifier._create_embed(notification_type, context or {})
            )
        except Exception as e:
            logger.error(f"Quick notification failed: {e}")