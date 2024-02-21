import openai
from twitchio.ext import commands

# Initialize OpenAI with your API key
openai.api_key = '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'

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token='anvi7yb4sn4zwazkz4g9lk9z3pyiwo', prefix='!', initial_channels=['xstarwake'])

    async def event_ready(self):
        print(f'Logged in as {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return
        
        # Simple command to respond with a ChatGPT-generated message
        if message.content.startswith('!hello'):
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt="Say a friendly hello to a Twitch viewer.",
                max_tokens=60
            )
            await message.channel.send(response.choices[0].text.strip())

if __name__ == '__main__':
    bot = Bot()
    bot.run()
