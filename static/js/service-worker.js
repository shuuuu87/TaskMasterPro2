self.addEventListener('push', function(event) {
  const data = event.data.json();
  const title = data.title || "ProductivityPilot";
  const options = {
    body: data.body || "You have a new notification!",
    icon: '/static/icon.png', // Optional: add your icon
  };
  event.waitUntil(self.registration.showNotification(title, options));
});