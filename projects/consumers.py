import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
  async def connect(self):
    # User must be authenticaded
    if self.scope["user"].is_authenticated:
      # Group creation for the user
      self.group_name = f"notif_user_{self.scope['user'].id}"
      
      # Channel sign up to the group
      await self.channel_layer.group_add(
        self.group_name,
        self.channel_name
      )
      await self.accept()
    else:
      await self.close()

  async def disconnect(self, close_code):
    if hasattr(self, 'group_name'):
      # Removing group registration
      await self.channel_layer.group_discard(
        self.group_name,
        self.channel_name
      )

  # When a messagge is sent to the group this method is executed
  async def send_notification(self, event):    
    # JSON message and url to the client (browser)
    await self.send(text_data=json.dumps({
      'message': event['message'],
      'url': event['url']
    }))