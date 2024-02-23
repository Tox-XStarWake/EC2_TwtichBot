from openai import OpenAI
from twitchio.ext import commands
from config_secrets.config import OPENAI_API_KEY, TWITCH_TOKEN, TWITCH_CHANNEL

# Initialize OpenAI with your API key
openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    # headers={"OpenAI-Organization": "XStarWake"}
)

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        print(f'Logged in as {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return

        # Example command using the OpenAI key
        if message.content.startswith('!hello'):
            try:
                chat_completion = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": message.content[len('!hello'):].strip()}
                    ],
                )
                
                if chat_completion.choices:
                    first_choice = chat_completion.choices[0]
                    reply = first_choice.message.content
                    # reply = first_choice.message['content']  # Ensure correct access to content
                    await message.channel.send(reply)
                else:
                    await message.channel.send("I'm not sure what to say.")
            except Exception as e:
                print(f"An error occurred while generating a response: {e}")
                await message.channel.send("Sorry, I couldn't generate a response.")

if __name__ == '__main__':
    bot = Bot()
    bot.run()
