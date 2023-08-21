from discord.ext import commands
from discord import ClientException
from traceback import print_exc
from dataclasses import dataclass


@dataclass
class BotData:

    client: commands.Bot
    extensions: list[str]
    _token: str
    guild: str

    def __post_init__(self):
        self.on_ready = self.client.event(self.on_ready)
        self.load_extensions()

    def load_extensions(self):
        for x in self.extensions:
            try:
                self.client.load_extension(x)
            except (ClientException, ModuleNotFoundError):
                print(f'Failed to load extension {x}.')
                print_exc()

    async def on_ready(self):
        for guild in self.client.guilds:
            if guild.name == self.guild:
                break

        print(
            f'{self.bot.user} has been started on the given server:\n'
            f'{guild.name}(id: {guild.id})\n'
        )

    def start(self):
        self.bot.run(self.token, reconnect=True)