import io
from loguru import logger
from config import Article


class OCRProcessor:
    """
    OCRProcessor class: uses Google Vision to extract text from images for each Article.
    """
    def __init__(self, vision_client):
        """
        vision_client: from GoogleAuthenticator.get_vision_client()
        """
        self.vision_client = vision_client

    def extract_text(self, article: Article):
        """
        Updates the article.fuzzy_text with OCR extracted content.
        """
        if not article.local_image_path:
            logger.warning(f"No local image path found for article {article.code}. Skipping OCR.")
            return

        try:
            with open(article.local_image_path, 'rb') as img_file:
                content = img_file.read()

            image = {"content": content}
            response = self.vision_client.document_text_detection(image=image)

            if response.full_text_annotation:
                article.fuzzy_text = response.full_text_annotation.text
                logger.info(f"OCR complete for {article.code}.")
            else:
                article.fuzzy_text = ""
                logger.warning(f"No text detected for {article.code}.")
        except Exception as e:
            logger.error(f"Error processing article image with Google Vision OCR: {str(e)}")
            article.fuzzy_text = ""
