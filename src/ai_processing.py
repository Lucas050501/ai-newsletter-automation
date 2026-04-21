import openai
import anthropic
from loguru import logger
from config import CHATGPT_PROMPT_ARTICLE_EXTRACTION, CLAUDE_PROMPT_ARTICLE_SUMMARY, OPENAI_API_KEY, ANTHROPIC_API_KEY, Article


class ArticleCleaner:
    """
    Uses ChatGPT to filter out non-article text from fuzzy OCR content.
    """
    def __init__(self):
        self.api_key_available = bool(OPENAI_API_KEY)
        if self.api_key_available:
            openai.api_key = OPENAI_API_KEY
        else:
            logger.warning("OPENAI_API_KEY not configured. ChatGPT article cleaning will be skipped.")

    def filter_article_text(self, article: Article):
        """
        Takes article.fuzzy_text and updates article.filtered_text.
        """
        if not article.fuzzy_text:
            article.filtered_text = ""
            logger.error("No fuzzy text available for ChatGPT")
            return

        if not self.api_key_available:
            article.filtered_text = ""
            logger.error("OpenAI API key not configured. Skipping article cleaning.")
            return

        text = article.fuzzy_text
        prompt = CHATGPT_PROMPT_ARTICLE_EXTRACTION + text

        try:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt}
                        ],
                    },
                ],
            )

            article.filtered_text = response.choices[0].message.content.strip()
            logger.info(f"ChatGPT filtering done for {article.code}.")

        except Exception as e:
            logger.error(f"Error processing fuzzy text in ChatGPT: {str(e)}")
            article.filtered_text = ""


class ArticleSummarizer:
    """
    Uses Claude to summarize the cleaned article text.
    """
    def __init__(self):
        if ANTHROPIC_API_KEY:
            self.client = anthropic.Client(api_key=ANTHROPIC_API_KEY)
        else:
            self.client = None
            logger.warning("ANTHROPIC_API_KEY not configured. Claude summarization will be skipped.")

    def summarize_article(self, article: Article):
        """
        Takes article.filtered_text and updates article.summary.
        """
        if not article.filtered_text:
            article.summary = ""
            logger.error("No article available for Claude summary")
            return

        if not self.client:
            article.summary = ""
            logger.error("Anthropic API key not configured. Skipping article summarization.")
            return

        current_article = article.filtered_text

        try:

            response = self.client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=1000,
                temperature=1,
                system=CLAUDE_PROMPT_ARTICLE_SUMMARY,
                messages=[
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": current_article}],
                    }
                ],
            )

            response_text = "".join(block.text for block in response.content)
            article.summary = response_text.strip()
            logger.info(f"Claude summary done for {article.code}.")

        except Exception as e:
            logger.error(f"Error summarizing article {article.code} with Claude: {str(e)}")
            article.summary = ""