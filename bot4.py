from openai import OpenAI
from twitchio.ext import commands
from config_secrets.config import OPENAI_API_KEY, TWITCH_TOKEN, TWITCH_CHANNEL

# Set your OpenAI API key directly on the openai module
# Initialize OpenAI with your API key
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    # headers={"OpenAI-Organization": "XStarWake"}
)

# RESPONDABLE = False


class Bot(commands.Bot):

    BORIS_PERSONALITY = (
        "You are a 9 year old pug with birthday coming up this summer. "
        "You have a brother named Kobe who is a french bulldog. "
        "Your parents are Twitch Streamers Max and Mel who stream on the channel XStarWake."
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

    # def get_sentiment_prompt(self, message):
    #     return f"Analyze the sentiment of this message and categorize it as Positive, Happy, Negative, Sad, Unknown, or Neutral: '{message}'"

    async def analyze_sentiment(self, message):

        sentiment_prompt = f"Analyze the sentiment of this message and categorize it as Positive, Happy, Negative, Sad, Unknown, or Neutral: '{message}'"

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

            sentiment = response.choices[0].text.strip()
            return sentiment

        except Exception as e:
            print(f"An error occurred while analyzing sentiment: {e}")
            return "Unknown"  # Fallback sentiment in case of an error

    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    async def event_message(self, message):
        # Prevent the bot from responding to its own messages or to messages it has already responded to
        if message.echo or message.id in self.responded_messages:
            return

        message_content_lower = message.content.lower()
        user_prompt = f"{message.author.name}'s message: '{message.content}'"
        context = None
        link = None

        if "what" in message_content_lower or "have" in message_content_lower:

            # Determine the context and craft the AI prompt
            if "discord" in message_content_lower:  # and RESPONDABLE is False:
                context = "an invitation to join our Discord community"
                link = "http://discord.gg/xstarwake"
                # RESPONDABLE = True
            elif "merch" in message_content_lower:  # and RESPONDABLE is False:
                context = "an invitation to check out our merch store"
                link = "http://merch.xstarwake.com"
                # RESPONDABLE = True
            else:
                # If the message doesn't match any specific context, skip processing
                return

        if (
            context is not None and link is not None
        ):  # Ensure context and link are assigned
            try:
                # Craft a prompt that instructs the AI to include the sender's name and the Discord link
                prompt = f"Respond to {user_prompt} and include @{user_prompt}, {context} at {link}."

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

        # Directly perform sentiment analysis
        sentiment = await self.analyze_sentiment(message.content)

        print(f"How was that message: {sentiment}")

        if "Negative" in sentiment or "Sad" in sentiment:
            try:
                # Craft a prompt that instructs the AI to include the sender's name and the Discord link
                prompt = f"Respond to '{message.author.name}' message: '{message.content}' and respond with their name with a @ preceding the name and include positive spin to thier message and encourage them to be positive."

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
                        f"Hey, @{message.author.name}, sorry your having such a RUFF go of it."
                    )
            except Exception as e:
                print(f"An error occurred while generating a response: {e}")
                await message.channel.send(
                    f"Hey! @{message.author.name}, Keep your chin up."
                )

        # Process every message to generate a response
        # Be mindful of rate limits and costs associated with OpenAI API usage
        # try:
        #     # Adjust the prompt to fit your needs. You might want to include more context or use a different approach to generate the prompt.
        #     prompt = f"A viewer says: '{message.content}'."  # How should a helpful assistant respond?"

        #     chat_completion = openai_client.chat.completions.create(
        #         messages=[
        #             {
        #                 "role": "system",
        #                 "content": "You are a 9 year old pug with birthday coming up this summer. You have a brother named kobe who is a french bulldog. Your parents are Twitch Streamers Max and Mel who stream on the channel XStarWake.",
        #             },
        #             {"role": "user", "content": prompt},
        #         ],
        #         model="gpt-3.5-turbo",  # Use the openai module directly
        #         max_tokens=160,  # Adjust based on your needs
        #         temperature=0.7,  # Adjust for creativity of the response
        #     )

        #     if chat_completion.choices:
        #         first_choice = chat_completion.choices[0]
        #         reply = first_choice.message.content
        #         await message.channel.send(reply)
        #     else:
        #         await message.channel.send("Uhhh... Woof Woof?")
        # except Exception as e:
        #     print(f"An error occurred while generating a response: {e}")
        #     await message.channel.send(
        #         "Someone yell at @Toxic__Salt I'm not feeling well."
        #     )


if __name__ == "__main__":
    bot = Bot()
    bot.run()
