import openai
from twitchio.ext import commands
from config_secrets.config import OPENAI_API_KEY, TWITCH_TOKEN, TWITCH_CHANNEL

# Initialize OpenAI with your API key
openai.api_key = OPENAI_API_KEY

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
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say a friendly hello to a Twitch viewer."}
                ]
            )
            await message.channel.send(response.choices[0].message['content'])

if __name__ == '__main__':
    bot = Bot()
    bot.run()
