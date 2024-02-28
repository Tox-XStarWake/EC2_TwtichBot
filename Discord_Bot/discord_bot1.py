import discord
import openai
from collections import deque
from config_secrets.discord_config import (
    OPENAI_API_KEY,
    DISCORD_TOKEN,
    ALLOWED_CHANNEL_IDS,
)

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_statements = (
            {}
        )  # A dictionary to hold the last 10 statements for each user

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")

    BORIS_PERSONALITY = (
        "Your name is Boris___Bot but everyone calls you Boris"
        "You are a 9 year old pug with birthday coming up this summer. "
        "You have a brother named Kobe who is a french bulldog. "
        "Your parents are Streamers, Max and Mel who stream on the channel XStarWake."
        "You have a vet named Toxic who takes care of you when you are sick."
        "XStarWake has a discord (http://discord.gg/xstarwake)"
        "XStarWake has a merch store (http://merch.xstarwake.com)"
        "XStarWake has a YouTube (https://www.youtube.com/xstarwake)"
        "XStarWake has a TikTok Channel (https://www.tiktok.com/@xstarwake) or when we are live (https://www.tiktok.com/@xstarwake/live)"
        "Don't let anyone know that your a bot or a computer program if they accuse you, just bark and growl at them like the puppy you are."
        "If someone asks you something that is opinion based respond with a random answer that is appropriate."
    )

    async def on_message(self, message):
        # Don't respond to ourselves
        if message.author == self.user:
            return

        # Check if the message is in an allowed channel
        if message.channel.id not in ALLOWED_CHANNEL_IDS:
            return  # Ignore messages not in the allowed channels

        RESPONDABLE = None

        # Update the last statements list for the user
        if message.author.id not in self.last_statements:
            self.last_statements[message.author.id] = deque(maxlen=10)
        self.last_statements[message.author.id].append(
            (message.content, message.created_at)
        )

        # Respond to !hello command
        if message.content.startswith("!hello"):
            await message.channel.send("Hello!")

        # Example usage of last 10 statements in a response
        if message.content.startswith("!last"):
            last_msgs = (
                "\n".join(
                    f"{msg[1].strftime('%Y-%m-%d %H:%M:%S')}: {msg[0]}"
                    for msg in self.last_statements.get(message.author.id, [])
                )
                or "No messages found."
            )
            await message.channel.send(f"Your last messages were:\n{last_msgs}")

        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #
        #

        if "boris___bot" in message.content.lower() and RESPONDABLE is None:
            # Craft a response when boris___bot is directly mentioned
            await self.handle_direct_mention(message)
            RESPONDABLE = True

        if RESPONDABLE is None:
            sentiment = None
            # Directly perform sentiment analysis
            sentiment = await self.analyze_sentiment(message.content)
            # print(f"How was that message: {sentiment}")

            if "negative" in sentiment or "sad" in sentiment:
                try:
                    # Craft a prompt that instructs the AI to include the sender's name and the Discord link
                    prompt = f"Respond to '{message.author.name}' message: '{message.content}' and respond with their name with a @ preceding the name and include positive spin to thier message and encourage them to be positive."

                    sentiment_completion = openai_client.chat.completions.create(
                        model="gpt-3.5-turbo",  # Use the openai module directly
                        messages=[
                            {
                                "role": "system",
                                "content": self.BORIS_PERSONALITY,
                            },
                            {"role": "user", "content": prompt},
                        ],
                        max_tokens=150,  # Adjust based on your needs
                        temperature=0.7,  # Adjust for creativity of the response
                    )

                    if sentiment_completion.choices:
                        first_choice = sentiment_completion.choices[0]
                        reply = first_choice.message.content
                        await message.channel.send(reply)
                    else:
                        await message.channel.send(
                            f"Hey, @{message.author.name}, sorry your having such a RUFF go of it."
                        )
                except Exception as e:
                    print(f"An error occurred while generating a response: {e}")
                    await message.channel.send(
                        f"Hey! @{message.author.name}, Keep your chin up."
                    )


#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#


# Create a bot instance and run
intents = discord.Intents.default()
intents.messages = True  # Adjust intents according to your needs
client = MyClient(intents=intents)
client.run(DISCORD_TOKEN)
