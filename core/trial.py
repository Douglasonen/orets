from whatsapp_web import WhatsApp

# Initialize
whatsapp = WhatsApp()

# Login (scan QR)
whatsapp.login(qr_callback=lambda qr: print(f"Scan QR: {qr}"))

# Send a message
whatsapp.send_message(to="256705404739@c.us", message="Hello from Python!")

# Listen for incoming messages
@whatsapp.on_message()
def handle_message(msg):
    print(f"New message: {msg}")
    if msg.text.lower() == "hi":
        msg.reply("Hello back!")

# Keep the session alive
whatsapp.run()