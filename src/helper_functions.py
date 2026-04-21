"""
Helper functions for telegram notifications and file cleanup.
"""

import os
import asyncio
from telegram import Bot
from loguru import logger
from typing import List, Union
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, Article


def send_telegram(message: str):
    """
    Sends a message via Telegram to the predefined BOT/Chat ID in config.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram credentials not configured. Skipping Telegram notification.")
        return

    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def send_telegram_async():
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

    loop.run_until_complete(send_telegram_async())
    loop.close()


def add_source_link(article: Article):

    if not article.link:
        logger.error("No link can be fetched from Article.")
        return

    try:
        domain = article.link.split('/')[2]
        article.summary = (article.summary or "") + f" ({domain})"

    except IndexError:
        logger.error(f"Unable to extract domain from link: {article.link}")


def cleanup_local_files(articles: List[Article], pdf_path: Union[str, list]):
    """
    Delete local images for each article, plus PDF(s).
    pdf_path can be a single string or a list of strings.
    """

    # 1) Delete image files
    for art in articles:
        if art.local_image_path and os.path.exists(art.local_image_path):
            try:
                os.remove(art.local_image_path)
            except Exception as e:
                logger.error(f"Error deleting local image {art.local_image_path}: {e}")

    # 2) Delete PDF
    if pdf_path is None:
        pass
    else:
        if isinstance(pdf_path, str):
            pdf_path = [pdf_path]
        for p in pdf_path:
            if p and os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:
                    logger.error(f"Error deleting local PDF file {p}: {e}")