from django.core.management import BaseCommand
import asyncio

from telegramBot.bot.handlers import main


class Command(BaseCommand):
    help = 'Start polling of the bot'

    def handle(self, *args, **options):
        asyncio.run(main())
