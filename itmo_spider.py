import scrapy
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from embeddings import encode_document
from data.ydb_adapter import YDBAdapter
from datetime import datetime


class ItmoSpider(scrapy.Spider):
    name = "itmo_spider"
    allowed_domains = ["ai.itmo.ru"]
    start_urls = ["https://ai.itmo.ru/"]

    custom_settings = {
        "DEPTH_LIMIT": 3,
    }

    def __init__(self, specialization_source: str = None, start_url = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if start_url:
            self.start_urls = [start_url]
        self.specialization_source = specialization_source
        self.db_adapter = YDBAdapter()
        self.db_adapter.create_table()
        self.visited_urls = set()  # Initialize visited_urls here

    def parse(self, response):
        # Check if URL has been visited
        if response.url in self.visited_urls:
            self.logger.info(f"Skipping already visited URL: {response.url}")
            return

        # Add current URL to visited set
        self.visited_urls.add(response.url)

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(response.body, "html.parser")

        # Remove scripts, styles, and images
        for script in soup.find_all("script"):
            script.decompose()
        for style in soup.find_all("style"):
            style.decompose()
        for img in soup.find_all("img"):
            img.decompose()

        # Convert the cleaned HTML body to markdown
        markdown_content = md(str(soup))

        # Print the markdown content to the console
        self.logger.info(f"--- Content from {response.url} ---")
        self.logger.info(markdown_content)
        self.logger.info(f"--- End of content from {response.url} ---")

        # Get current timestamp
        current_timestamp = datetime.now()

        embedding = encode_document(markdown_content)

        # Insert data into YDB
        try:
            self.db_adapter.insert_data(
                current_timestamp,
                embedding,
                response.url,
                markdown_content,
                self.specialization_source,
            )
        except Exception as e:
            self.logger.error(f"Error inserting data for {response.url}: {e}")

        # Follow links to other pages within the allowed domain
        for href in response.css("a::attr(href)").getall():
            full_url = response.urljoin(href)
            if (
                self.allowed_domains[0] in full_url
                and full_url not in self.visited_urls
            ):
                yield response.follow(href, self.parse)

    def closed(self, reason):
        self.db_adapter.close()
        self.logger.info(f"Spider closed: {reason}. YDB connection closed.")
