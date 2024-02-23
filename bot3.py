import openai  # Correctly import the openai module
from twitchio.ext import commands
from config_secrets.config import OPENAI_API_KEY, TWITCH_TOKEN, TWITCH_CHANNEL

# Set your OpenAI API key directly on the openai module
openai.api_key = OPENAI_API_KEY

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        print(f'Logged in as {self.nick}')

    async def event_message(self, message):
        # Prevent the bot from responding to its own messages
        if message.echo:
            return

        # Process every message to generate a response
        # Be mindful of rate limits and costs associated with OpenAI API usage
        try:
            # Adjust the prompt to fit your needs. You might want to include more context or use a different approach to generate the prompt.
            prompt = f"A viewer says: '{message.content}'. How should a helpful assistant respond?"

            chat_completion = openai.Completion.create(
                model="gpt-3.5-turbo",  # Use the openai module directly
                prompt=prompt,
                max_tokens=60,  # Adjust based on your needs
                temperature=0.7  # Adjust for creativity of the response
            )

            if chat_completion.choices:
                reply = chat_completion.choices[0].text.strip()
                await message.channel.send(reply)
            else:
                await message.channel.send("I'm not sure what to say.")
        except Exception as e:
            print(f"An error occurred while generating a response: {e}")
            await message.channel.send("Sorry, I couldn't generate a response.")

if __name__ == '__main__':
    bot = Bot()
    bot.run()
