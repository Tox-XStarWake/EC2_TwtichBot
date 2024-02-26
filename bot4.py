from openai import OpenAI
from twitchio.ext import commands
from config_secrets.config import OPENAI_API_KEY, TWITCH_TOKEN, TWITCH_CHANNEL

# Set your OpenAI API key directly on the openai module
# Initialize OpenAI with your API key
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    # headers={"OpenAI-Organization": "XStarWake"}
)


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=TWITCH_TOKEN, prefix="!", initial_channels=[TWITCH_CHANNEL]
        )

    async def event_ready(self):
        print(f"Logged in as {self.nick}")

    async def event_message(self, message):
        # Prevent the bot from responding to its own messages
        if message.echo:
            return
        message_content_lower = message.content.lower()

        if (
            "what" in message_content_lower or "have" in message_content_lower
        ) and "discord" in message_content_lower:
            try:
                # Craft a prompt that instructs the AI to include the sender's name and the Discord link
                prompt = f"Respond to '{message.author.name}' message: '{message.content}' and respond with their name with a @ preceding the name and include an invitation to join our Discord community at http://discord.gg/xstarwake."

                chat_completion = OpenAI.ChatCompletion.create(
                    model="gpt-3.5-turbo",  # Use the openai module directly
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a 9 year old pug with birthday coming up this summer. You have a brother named Kobe who is a french bulldog. Your parents are Twitch Streamers Max and Mel who stream on the channel XStarWake.",
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
                        f"Hey, @{message.author.name}, don't forget to join our Discord at http://discord.gg/xstarwake!"
                    )
            except Exception as e:
                print(f"An error occurred while generating a response: {e}")
                await message.channel.send(
                    f"Hey! @{message.author.name}, feel free to join our Discord at http://discord.gg/xstarwake!"
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
