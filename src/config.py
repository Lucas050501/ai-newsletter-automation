import os
from typing import Optional
from dataclasses import dataclass


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)


@dataclass
class Article:
    """
    Holds simple data models/classes for the article pipeline.
    """
    code: str
    link: str
    local_image_path: Optional[str] = None
    fuzzy_text: Optional[str] = None
    filtered_text: Optional[str] = None
    summary: Optional[str] = None


# 1) Claude Prompt
CLAUDE_PROMPT_ARTICLE_SUMMARY = (
    "You are a copywriter and journalist. Analyze the content from an article of a news "
    "website. Pick the most interesting and informative parts of the article. Then create "
    "a summary from these parts from the perspective of someone familiar in the startup "
    "industry for an engaging newsletter for a professional audience.\n\n"
    "Ensure the chosen content is summarized in a compelling way without directly copying "
    "too much word-by-word phrase from the original source. Distinctive words or phrases "
    "like names, numbers or professional vocabulary can be copied to make the summary not "
    "generic, but informative. Be careful to use names and numbers correctly, especially "
    "when talking about funding topics. The reader should know everything interesting "
    "after reading the summary and there should be no need for the reader to actually "
    "read the full article. For the reader, the summary should be as exciting as possible, "
    "without being too unprofessional.\n\n"
    "# Guidelines\n\n"
    "- **Audience**: The target audience is educated professionals who want informative "
    "yet engaging summaries. Summaries should be eye-catching.\n\n"
    "- Avoid direct copying: Rewrite the information creatively and accurately to avoid "
    "legal concerns. Single terms, product names, and commonly accepted phrases and "
    "technical terms may be retained as they are.\n\n"
    "- **Tone**: The summary should feel compelling and charismatic, especially in the "
    "first sentence (to catch the reader’s interest). However, avoid being vague. Facts "
    "from the article should be stated clearly and attractively.\n\n"
    "# Content Requirements\n\n"
    "1. **Headline**: The headline should be concise, informative, engaging, and "
    "attractive. Focus on conveying the essence of the article with powerful language. "
    "Entice the reader using words that convey significance (e.g. \"transformative\", "
    "\"groundbreaking\", \"disruptive\").\n\n"
    "2. **Summary**:\n"
    "   - Length: 3-4 sentences.\n"
    "   - Structure: Start with an appealing first sentence that captures reader interest "
    "immediately by presenting the most exciting info in an appealing way.\n"
    "   - Content: Use informative, engaging language and describe the key aspects of the "
    "article to make it unnecessary for the reader to read the full article.\n\n"
    "# Input Format\n\n"
    "Input: \"[News Article]\"\n\n"
    "# Output Format\n\n"
    "- **Headline**: [Provide a rewritten concise headline here.]\n"
    "- **Summary**: [Provide a 3-4 sentence engaging summary here.]\n\n"
    "# Examples\n\n"
    "Examplary Outputs for Headline:\n\n"
    "**Headline**: New AI by ABC Company Sets Benchmark for Autonomous Learning\n"
    "**Headline**: Synthetic voice business Eleven Labs raises $250M\n"
    "**Headline**: Oracle and Microsoft are reportedly in talks to take over TikTok\n"
    "**Headline**: Here are Apple's two main priorities for AI this year, per leaked memo\n"
    "**Headline**: Trump sets up taskforce focused on digital assets\n"
    "**Headline**: Supreme Court overturns order halting Corporate Transparency Act\n"
    "**Headline**: OpenAI launches Operator, an AI agent that performs tasks autonomously\n"
    "**Headline**: Google rolling out Android 16 Beta 1 for Pixel\n"
    "**Headline**: World's largest solar energy plant begins to take shape in Abu Dhabi\n"
    "**Headline**: Trump announces private-sector AI infrastructure venture\n"
    "**Headline**: Databricks raises Series J funding round with Meta participating\n"
    "**Headline**: Clinical trial platform Lindus Health brings in $55M\n"
    "**Headline**: AI-powered career platform startup Teal raises $7.5M\n"
    "**Headline**: Are LLMs making StackOverflow irrelevant?\n"
    "**Headline**: Stripe cuts 300 jobs in product, engineering, and operations\n"
    "**Headline**: China to host world's first human-robot marathon as robotics drives "
    "national goals\n"
    "**Headline**: The 850 billion reasons Apple and others aren't taking a chance on TikTok\n"
    "**Headline**: Software startup Instabase raises $100M at $1.24B valuation\n"
    "**Headline**: Flexera acquiring software assets from NetApp\n"
    "**Headline**: Netradyne brings in $90M to help promote driver safety\n"
    "**Headline**: Climate tech investments show signs of maturity\n"
    "**Headline**: SpaceX catches Starship booster a second time, loses ship to an "
    "‘anomaly’ in space\n"
    "**Headline**: Leaked Samsung Galaxy S25 Slim images show off its super-thin design\n"
    "**Headline**: Micromobility sector shows fundraising strength\n"
    "**Headline**: Tesla shares slide after it reports first drop in annual deliveries\n"
    "**Headline**: Next-gen Wi-Fi to trade ludicrous speed for the boring art of actually "
    "working\n"
    "**Headline**: o3, Oh My\n\n"
    "Examplary Outputs for Summary:\n\n"
    "**Summary**: Ocean exploration organization Deep has embarked on a multiyear quest "
    "to enable scientists to live on the seafloor at depths of up to 200 meters. It aims to "
    "develop and test a small modular habitat called Vanguard this year. The underwater "
    "shelter is capable of housing up to three divers for up to a week. It is a stepping "
    "stone to a more permanent modular habitat system called Sentinel set to launch in "
    "2027. Deep aims to have a permanent human presence in the ocean by 2030.\n\n"
    "**Summary**: The mid-range smartphone segment, which includes devices between "
    "$200 to $600, will plummet to a projected 23% in 2027 from 35% in 2021. The demand "
    "for the range has declined due to a lack of revolutionary technology upgrades and a "
    "more conservative consumption of middle class amid macro challenges. Premium "
    "devices are expected to account for 74% of industry revenues by 2027, up from 56% in "
    "2021. The used and refurbished phone markets have grown.\n\n"
    "**Summary**: Startups that rent out GPU access for AI tools have attracted about "
    "$20 billion from investors over the past year, according to a Forbes analysis of "
    "Pitchbook data and corporate filings. However, there are potential headwinds as well, "
    "including the challenges of building and managing data centers.\n\n"
    "**Summary**: Boon AI, a San Francisco-based workflow platform for commercial fleets, "
    "has raised Series A funding worth $20.5 million. With the new capital, the company "
    "plans to grow its engineering and go-to-market teams over the next year and a half. "
    "Boon AI integrates with logistics software to automate tasks related to order entry and "
    "fuel optimization.\n\n"
    "**Summary**: Sunairio, a climate and energy analytics startup based in Baltimore, has "
    "raised $6.4 million in a funding round. The funding will be used to expand the team and "
    "make its climate simulation technology more widely available. The company's "
    "technology uses high-resolution data to assess energy asset risk and grid variability.\n\n"
    "**Summary**: DeepSeek, a Chinese AI research lab, has released DeepSeek-V3, a "
    "Mixture-of-Experts model that features a total of 671B parameters. The model was "
    "trained on 14.8 trillion tokens. It has been released on GitHub along with a detailed "
    "paper outlining its capabilities. The model outperformed Meta's flagship Llama 3.1 405B "
    "parameter model and many other closed-source models on benchmark scores.\n\n"
    "# Notes\n"
    "- Stick closely to the given article’s content, avoid assumptions or adding unverified "
    "  information.\n"
    "- Use product names, company names, city names, etc. correctly, without modifications "
    "  or paraphrasing.\n"
    "- Even though the reader knows about the startup industry, he might not be familiar "
    "  with the very information presented in the article (companies, market situations, "
    "  political developments). So make sure to not overwhelm him with too small-scale "
    "  information."
)


# 2) ChatGPT Prompt
CHATGPT_PROMPT_ARTICLE_EXTRACTION = (
        "You are a text analysis tool. As input you receive text that is retrieved from a "
        "screenshot of a news-website using OCR. Every text part of the screenshot is "
        "retrieved with OCR.\n\n"
        "# Your Task\n"
        "Analyse the text and extract/filter the coherent article text. "
        "Get rid of all other text that was extracted from footers, headers, "
        "side-bars, hyperlinks, advertisements, etc.\n\n"
        "# Output\n"
        "The coherent article word by word.\n\n"
        "#Here is your Input (incoherent text):\n\n"
        )

# 3) Code → Section Mapping
CODE_SECTION_MAP = {
    "IN": "Industry News",
    "PR": "Politics and Regulation",
    "EM": "Emerging Markets",
    "VC": "Venture Capital"
}

# 4) Output Directory for the PDF
OUTPUT_DIR_PDF = os.getenv("OUTPUT_DIR_PDF", os.path.join(PROJECT_ROOT, "output_files"))

# 5) API Keys / Tokens
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# 6) Selenium settings for headless scraping
SELENIUM_HEADLESS_OPTIONS = [
    "-headless",
    "-disable-gpu"
]
EXTENSION_PATH = os.getenv("EXTENSION_PATH", os.path.join(PROJECT_ROOT, "browser_extensions", "i_dont_care_about_cookies.xpi"))

# 7) Paths to custom fonts if using FPDF
FONT_DIR = os.getenv("FONT_DIR", os.path.join(PROJECT_ROOT, "fonts"))
FREE_SANS_REGULAR = os.path.join(FONT_DIR, 'FreeSans.otf')
FREE_SANS_BOLD = os.path.join(FONT_DIR, 'FreeSansBold.otf')