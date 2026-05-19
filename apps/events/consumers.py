import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)

class LiveMetricsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = "live_metrics"
        
        # Join group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
        logger.info(f"🔌 WebSocket connection accepted: {self.channel_name}")

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        logger.info(f"🔌 WebSocket connection closed: {self.channel_name}")

    async def receive(self, text_data):
        # We don't expect client messages for now, but logged for debug
        try:
            data = json.loads(text_data)
            logger.debug(f"Received message from client: {data}")
        except Exception as e:
            logger.warning(f"Error parsing client websocket data: {str(e)}")

    async def broadcast_event(self, event):
        """
        Receive event from group and send it to WebSocket client
        """
        await self.send(text_data=json.dumps(event))
