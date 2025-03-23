# Scrapy settings for about_scraper project

BOT_NAME = 'about_scraper'

SPIDER_MODULES = ['about_scraper.spiders']
NEWSPIDER_MODULE = 'about_scraper.spiders'

# Obey robots.txt rules - set to False to ignore robots.txt
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 4

# Configure a delay for requests for the same website
DOWNLOAD_DELAY = 2

# Enable or disable cookies
COOKIES_ENABLED = True

# Configure item pipelines
ITEM_PIPELINES = {
   # 'about_scraper.pipelines.AboutScraperPipeline': 300,
}

# Set the User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'

# Enable and configure HTTP caching
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # 24 hours
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# Configure logging
LOG_LEVEL = 'INFO'