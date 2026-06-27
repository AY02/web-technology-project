def notifications_processor(request):
  if not request.user.is_authenticated:
    return {}
    
  # Last 5 unread notifications
  unread_notifications = request.user.notifications.filter(is_read=False)[:5]
  unread_count = request.user.notifications.filter(is_read=False).count()
  
  return {
    'unread_notifications': unread_notifications,
    'unread_count': unread_count,
  }