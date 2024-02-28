import asyncio
from openai import OpenAI
from twitchio.ext import commands
from collections import deque
from datetime import datetime
from config_secrets.config import (
    OPENAI_API_KEY,
    TWITCH_TOKEN,
    TWITCH_CHANNEL,
    TWITCH_NICK,
)

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
)


class Bot(commands.Bot):

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

    DOCTOR_PERSONALITY = (
        "You are a 20+ year experienced psychiatrist. "
        "You also have 20+ years experience being a Psychologist. "
        "Because of your past experience you also are a great Therapist."
    )

    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN, prefix="!", initial_channels=[TWITCH_CHANNEL]
        )
        self.responded_messages = set()  # Set to track messages Boris has responded to
        self.user_messages = {}  # Stores the last 10 messages per user

    async def event_ready(self):
        print(f"Logged in as | {TWITCH_NICK}")

    async def event_disconnect(self, _):
        print("Disconnected from the server. Attempting to reconnect...")
        await self.attempt_reconnect()

    async def attempt_reconnect(self, max_retries=5):
        for attempt in range(max_retries):
            try:
                await self.connect()
                print("Reconnected successfully.")
                break
            except Exception as e:
                wait = 2**attempt  # Exponential backoff
                print(f"Reconnect attempt failed: {e}. Retrying in {wait} seconds...")
                await asyncio.sleep(wait)
        else:
            print(
                "Maximum reconnect attempts reached. Please check your connection or Twitch API status."
            )

    def add_user_message(self, username, message):
        if username not in self.user_messages:
            self.user_messages[username] = deque(maxlen=10)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.user_messages[username].append((timestamp, message))

    async def handle_direct_mention(self, message):
        user_messages = self.user_messages.get(message.author.name, [])
        user_context = " ".join(
            [f"[{timestamp}] {msg}" for timestamp, msg in user_messages]
        )

        try:
            user_dm = f"You need to respond to {message.author.name}'s message as Boris: '{message.content}'. This is this users recent chat history with timestamps of when they said it: '{user_context}'. Analyze those message to help you respond more naturally but don't say things like chat history in your response just act like its just part of your memory."

            dm_response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": self.BORIS_PERSONALITY,
                    },
                    {"role": "user", "content": user_dm},
                ],
                max_tokens=200,
                temperature=0.7,
            )

            if dm_response.choices:
                first_choice = dm_response.choices[0]
                reply = first_choice.message.content
                await message.channel.send(reply)

            else:
                # Fallback message in case there's no response generated
                await message.channel.send(
                    f"Hey @{message.author.name}, how can I assist you today?"
                )

        except Exception as e:
            print(f"An error occurred while responding to direct mention: {e}")
            # Fallback message in case of an error
            await message.channel.send(
                "Oops! I ran into an issue. I might be sick might want to let Toxic know I need to see the vet soon. Can you try asking again?"
            )

    async def analyze_sentiment(self, message):

        sentiment_prompt = f"Analyze the sentiment of this message and categorize it as Positive, Happy, Negative, Sad, Unknown, or Neutral: '{message}'. The only catch is I want a single word response of a category and if you can't classify it reply with Unknown."

        try:
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use the openai module directly
                messages=[
                    {
                        "role": "system",
                        "content": self.DOCTOR_PERSONALITY,
                    },
                    {"role": "user", "content": sentiment_prompt},
                ],
                max_tokens=60,  # Adjust based on your needs
                temperature=0.35,  # Adjust for creativity of the response
            )

            sentiment = response.choices[0].message.content.lower()
            return sentiment

        except Exception as e:
            print(f"An error occurred while analyzing sentiment: {e}")
            return "Unknown"  # Fallback sentiment in case of an error

    async def event_message(self, message):
        # Prevent the bot from responding to its own messages or to messages it has already responded to
        if message.echo or message.id in self.responded_messages:
            return

        self.add_user_message(message.author.name, message.content)

        message_content_lower = message.content.lower()
        user_prompt = f"{message.author.name}'s message: '{message.content}'"
        context = None
        link = None
        RESPONDABLE = None

        if "what" in message_content_lower or "have" in message_content_lower:

            # Determine the context and craft the AI prompt
            if "discord" in message_content_lower and RESPONDABLE is None:
                context = "an invitation to join our Discord community"
                link = "http://discord.gg/xstarwake"
                RESPONDABLE = True
            elif "merch" in message_content_lower and RESPONDABLE is None:
                context = "an invitation to check out our merch store"
                link = "http://merch.xstarwake.com"
                RESPONDABLE = True
            # else:
            #     # If the message doesn't match any specific context, skip processing
            #     return

        if (
            context is not None and link is not None and RESPONDABLE is not None
        ):  # Ensure context and link are assigned
            try:
                # Craft a prompt that instructs the AI to include the sender's name and the Discord link
                prompt = f"Respond to {user_prompt} and include @{message.author.name}, {context} at {link}."

                chat_completion = openai_client.chat.completions.create(
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

                if chat_completion.choices:
                    first_choice = chat_completion.choices[0]
                    reply = first_choice.message.content
                    await message.channel.send(reply)
                else:
                    await message.channel.send(
                        f"Hey, @{message.author.name}, check out {link} !"
                    )
            except Exception as e:
                print(f"An error occurred while generating a response: {e}")
                await message.channel.send(
                    f"Hey, @{message.author.name}, you should check out {link} !"
                )

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


if __name__ == "__main__":
    bot = Bot()
    bot.run()
