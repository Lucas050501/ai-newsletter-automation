import sys
from datetime import datetime
from loguru import logger

# Import your own modules
from google_processes import GoogleAuthenticator, GoogleMailManager, GoogleDriveManager
from web_scraping import WebScraper
from ocr_processing import OCRProcessor
from ai_processing import ArticleCleaner, ArticleSummarizer
from pdf_generator import PDFGenerator
from beehiiv_renderer import BeehiivRenderer
from helper_functions import send_telegram, cleanup_local_files, add_source_link


def main():
    logger.info("=== Article Processing pipeline starting ===")
    send_telegram("=== Article Processing running ===")

    current_date = datetime.now().strftime("%Y-%m-%d")

    # 1) Google Authentication
    try:
        auth_gd = GoogleAuthenticator()
        auth_gd.authenticate()
        gmail_service = auth_gd.get_gmail_service()
        drive_service = auth_gd.get_drive_service()
        vision_client = auth_gd.get_vision_client()

        logger.success("Google authentication completed.")
    except Exception as e:
        logger.error(f"Error authenticating Google services: {str(e)}")
        send_telegram(f"Error in Google authentication: {str(e)}")
        send_telegram("Script terminated ❌")
        sys.exit(1)

    # 2) Fetch article links from Gmail
    mail_manager = GoogleMailManager(gmail_service)
    try:
        article_links = mail_manager.fetch_article_links(label_name="Article Links")
        if not article_links:
            logger.error("No article links fetched from Gmail.")
            send_telegram("No article links fetched from Gmail.")
            send_telegram("Script terminated ❌")
            sys.exit(1)
        else:
            logger.success(f"Fetched {len(article_links)} articles from Gmail.")
    except Exception as e:
        logger.error(f"Error fetching articles from Gmail: {str(e)}")
        send_telegram(f"Gmail fetch error: {str(e)}")
        sys.exit(1)

    # 3) Create Google Drive folders
    drive_manager = GoogleDriveManager(drive_service)
    try:
        main_folder_id = drive_manager.create_folder(current_date)
        article_images_folder_id = drive_manager.create_folder("Article_Images", parent_id=main_folder_id)
        preprod_folder_id = drive_manager.create_folder("PreProduction_PDFs", parent_id=main_folder_id)
        logger.success("Google Drive folders created.")
    except Exception as e:
        logger.error(f"Error creating GDrive folders: {str(e)}")
        send_telegram(f"Google Drive folder creation error: {str(e)}")
        send_telegram("Script terminated ❌")
        sys.exit(1)

    # 4) Web Scraper: take screenshots, upload, create Article objects
    scraper = WebScraper(drive_manager=drive_manager)
    articles = scraper.take_screenshots(article_links, article_images_folder_id)
    if not articles:
        logger.error("No articles processed from web scraping.")
        send_telegram("Script terminated ❌")
        sys.exit(1)

    logger.success("Screenshots captured and uploaded.")

    # 5) OCR on each article
    ocr_processor = OCRProcessor(vision_client)
    for art in articles:
        ocr_processor.extract_text(art)

    logger.success("OCR completed for all articles.")

    # 6) ChatGPT cleaning (ArticleCleaner)
    cleaner = ArticleCleaner()
    for art in articles:
        cleaner.filter_article_text(art)

    logger.success("ChatGPT cleaning done.")

    # 7) Claude summarizing (ArticleSummarizer)
    summarizer = ArticleSummarizer()
    for art in articles:
        summarizer.summarize_article(art)

    logger.success("Claude summarization done.")

    # 8) Adding source link to summary
    for art in articles:
        add_source_link(art)

    logger.success("Source Links added to summary.")

    # 9) Generate PDF
    pdf_gen = PDFGenerator()
    pdf_path = pdf_gen.create_summary_pdf(articles, output_filename="Summary_Report.pdf")
    try:
        drive_manager.upload_file(pdf_path, preprod_folder_id)
        logger.success("Summary PDF uploaded to GDrive.")
    except Exception as e:
        logger.error(f"Error uploading Summary PDF: {str(e)}")

    # 10) Beehiiv template: generate JS
    beehiiv = BeehiivRenderer()
    beehiiv.generate_javascript_code(articles)
    logger.success("Beehiiv template JS code generated & copied to clipboard.")

    # 11) Cleanup local files
    cleanup_local_files(articles, pdf_path)
    logger.info("Temporary images deleted.")

    send_telegram("=== ✅SUCCESS✅ ===")
    logger.success("=== Article Processing finished successfully ===")


if __name__ == "__main__":
    main()