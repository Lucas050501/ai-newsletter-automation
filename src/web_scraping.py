import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from loguru import logger
from config import SELENIUM_HEADLESS_OPTIONS, EXTENSION_PATH, Article


class WebScraper:
    """
    Uses Selenium to open links, take screenshots, and store them in local paths + Google Drive.
    """
    def __init__(self, drive_manager):
        """
        drive_manager: instance of GoogleDriveManager (for uploading screenshots)
        """
        self.drive_manager = drive_manager

        options = Options()
        for arg in SELENIUM_HEADLESS_OPTIONS:
            options.add_argument(arg)
        self.driver = webdriver.Firefox(options=options)

    def take_screenshots(self, article_links_dict, images_folder_id):
        """
        article_links_dict: dict of { code: link }
        images_folder_id: Google Drive folder ID for screenshots
        returns: list of Article objects
        """
        articles = []
        screenshots_dir = os.path.join(os.getcwd(), "temp_screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        try:
            # Install cookie extension, if needed
            if EXTENSION_PATH and os.path.exists(EXTENSION_PATH):
                self.driver.install_addon(EXTENSION_PATH, temporary=True)
                time.sleep(3)
            else:
                logger.warning("Browser extension not found. Continuing without cookie extension.")

            for code, link in article_links_dict.items():
                try:
                    self.driver.get(link)
                    logger.info(f"Searching for {code} link...")
                    time.sleep(5)  # wait for page to load

                    domain = link.split('/')[2]
                    filename = f"{code}_{domain}.png"
                    local_path = os.path.join(screenshots_dir, filename)

                    # Full-page screenshot as bytes
                    screenshot_bytes = self.driver.get_full_page_screenshot_as_png()

                    # Save locally
                    with open(local_path, 'wb') as img_file:
                        img_file.write(screenshot_bytes)

                    # Upload to Drive
                    self.drive_manager.upload_screenshot_bytes(screenshot_bytes, filename, images_folder_id)
                    logger.info(f"Screenshot for {code} uploaded to Drive as {filename}.")

                    article = Article(
                        code=code,
                        link=link,
                        local_image_path=local_path
                    )
                    articles.append(article)

                except Exception as e:
                    logger.error(f"Error screenshotting link {link}: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Error in Selenium scraping process: {str(e)}")
        finally:
            self.driver.quit()

        return articles