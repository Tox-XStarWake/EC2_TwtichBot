import discord


# Assuming Python 3.8+ for the use of ":="
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        # Logic to track messages by users
        # This is where you would implement tracking of the last 10 statements

        if message.content.startswith("!hello"):
            await message.channel.send("Hello!")


# Create a bot instance and run
token = "YOUR_BOT_TOKEN_HERE"
intents = discord.Intents.default()  # Adjust intents according to your needs
intents.messages = (
    True  # Make sure to enable intents in your bot settings on the developer portal
)

client = MyClient(intents=intents)
client.run(token)
