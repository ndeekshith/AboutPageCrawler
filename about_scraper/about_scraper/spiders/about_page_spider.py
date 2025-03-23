import scrapy
from scrapy import Request
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re
import time
import os
from urllib.parse import urlparse, urljoin

class AboutPageSpider(scrapy.Spider):
    name = 'about_page_spider'
    
    # Add your start URLs here
    start_urls = {'https://www.abhiruchiprobiotics.in/',
                  'https://cloq.app/'
                  }  # Replace with your target website
    
    # Custom settings
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'DOWNLOAD_DELAY': 2,  # Be polite to the websites
        'FEEDS': {
            'about_pages.json': {
                'format': 'json',
                'encoding': 'utf8',
                'indent': 4,
            }
        }
    }

    def __init__(self, *args, **kwargs):
        super(AboutPageSpider, self).__init__(*args, **kwargs)
        
        # Set up Firefox options
        firefox_options = Options()
        firefox_options.add_argument("--headless")  # Run Firefox in headless mode
        firefox_options.add_argument("--disable-gpu")
        firefox_options.add_argument("--window-size=1920,1080")
        
        # Add User-Agent to avoid bot detection
        firefox_options.set_preference(
            "general.useragent.override",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        )
        
        # Initialize Selenium WebDriver
        self.driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()), 
            options=firefox_options
        )
        
        # Track visited URLs to avoid duplicates
        self.visited_urls = set()
        
        # Define patterns to find about pages
        self.about_patterns = [
            r'about\s*us', 
            r'about', 
            r'know\s*us', 
            r'who\s*we\s*are',
            r'our\s*story',
            r'about\s*company',
            r'company\s*profile'
        ]
        
        # Compile patterns for efficiency
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.about_patterns]

    def parse(self, response):
        """Initial parse method that finds and visits about pages"""
        self.logger.info(f"Visiting main page: {response.url}")
        
        # Visit the page with Selenium
        self.driver.get(response.url)
        
        try:
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Allow JavaScript to render properly
            time.sleep(3)
            
            # Find all links on the page
            links = self.driver.find_elements(By.TAG_NAME, "a")
            
            about_links = []
            domain = urlparse(response.url).netloc
            
            # Find all about links
            for link in links:
                try:
                    href = link.get_attribute('href')
                    link_text = link.text.strip()
                    
                    # Skip if link is None or invalid
                    if not href or href.startswith('javascript:') or href.startswith('#'):
                        continue
                        
                    # Check if href or link text matches any about pattern
                    if any(pattern.search(href) for pattern in self.patterns) or any(pattern.search(link_text) for pattern in self.patterns):
                        # Ensure it's an absolute URL
                        if not href.startswith(('http://', 'https://')):
                            href = urljoin(response.url, href)
                            
                        # Only follow links to the same domain
                        if urlparse(href).netloc == domain and href not in self.visited_urls:
                            about_links.append(href)
                            self.logger.info(f"Found about link: {href} (text: {link_text})")
                        
                except Exception as e:
                    self.logger.error(f"Error processing link: {e}")
                    continue
            
            # If about links found, visit them
            if about_links:
                self.logger.info(f"Found {len(about_links)} about page links")
                for about_url in about_links:
                    self.visited_urls.add(about_url)
                    yield Request(about_url, callback=self.parse_about_page)
            else:
                # If no about links found, try to extract company information from the main page
                self.logger.warning("No about links found on the main page. Attempting to extract info from main page.")
                yield self.extract_page_info(response.url)
                
        except Exception as e:
            self.logger.error(f"Error processing main page {response.url}: {e}")
        
    def parse_about_page(self, response):
        """Parse the about us page and extract all text content"""
        self.logger.info(f"Processing about page: {response.url}")
        
        # Visit the page with Selenium
        self.driver.get(response.url)
        
        try:
            # Wait for the page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Allow JavaScript to render properly
            time.sleep(3)
            
            # Extract detailed information from the about page
            yield self.extract_page_info(response.url)
            
        except Exception as e:
            self.logger.error(f"Error processing about page {response.url}: {e}")
    
    def extract_page_info(self, url):
        """Extract all text content from the page with emphasis on readability"""
        try:
            # Get page title
            title = self.driver.title
            
            # Get the complete body text
            body = self.driver.find_element(By.TAG_NAME, "body")
            
            # First, try to exclude navigation, footer, header, etc. to get cleaner content
            # This attempts to mark elements to ignore for cleaner text extraction
            try:
                # These are common elements we want to ignore for cleaner text
                ignore_selectors = [
                    "nav", ".nav", ".navbar", ".navigation", 
                    "header", ".header", "#header", 
                    "footer", ".footer", "#footer",
                    ".menu", "#menu", ".sidebar", "#sidebar",
                    ".copyright", ".social-media", ".social-links",
                    ".cookie-notice", ".privacy-notice", ".advertisement",
                    ".cart", ".shopping-cart"
                ]
                
                for selector in ignore_selectors:
                    for element in self.driver.find_elements(By.CSS_SELECTOR, selector):
                        # Mark these elements to be ignored
                        self.driver.execute_script("arguments[0].setAttribute('data-scrapy-ignore', 'true')", element)
            except Exception as e:
                self.logger.warning(f"Error while trying to exclude non-content elements: {e}")
            
            # Get main content using common content container selectors first
            main_content_text = ""
            content_selectors = [
                "article", "main", "#main", "#content", ".content", ".main-content",
                ".about-content", ".about-us", ".about", "#about", 
                ".company-info", ".company-profile"
            ]
            
            for selector in content_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        element_text = element.text.strip()
                        if element_text and len(element_text) > 100:  # Only accept if substantial content found
                            main_content_text = element_text
                            self.logger.info(f"Found main content using selector: {selector}")
                            break
                    if main_content_text:
                        break
                except Exception:
                    continue
            
            # If no specific content containers found, get text from the body excluding marked elements
            if not main_content_text:
                # Try to get all text not in ignored sections
                all_text = []
                for element in self.driver.find_elements(By.XPATH, "//body//*[not(ancestor-or-self::*[@data-scrapy-ignore='true'])]"):
                    try:
                        element_text = element.text.strip()
                        if element_text and not any(child.get_attribute("data-scrapy-ignore") == "true" for child in element.find_elements(By.XPATH, ".//*")):
                            all_text.append(element_text)
                    except Exception:
                        continue
                
                # Join all text with proper spacing
                main_content_text = "\n".join(all_text)
            
            # As a fallback, if still no substantial content, just get the entire body text
            if not main_content_text or len(main_content_text) < 100:
                main_content_text = body.text
            
            # Clean up the text
            # Split by newlines and filter out empty lines
            lines = [line.strip() for line in main_content_text.split('\n') if line.strip()]
            
            # Remove duplicate adjacent lines
            cleaned_lines = []
            prev_line = None
            for line in lines:
                if line != prev_line:
                    cleaned_lines.append(line)
                    prev_line = line
            
            # Join back with proper spacing
            cleaned_text = '\n'.join(cleaned_lines)
            
            # Create final result
            return {
                'url': url,
                'page_title': title,
                'content': cleaned_text,
                'page_type': 'about_page',
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            self.logger.error(f"Error extracting content from {url}: {e}")
            return {
                'url': url,
                'error': str(e),
                'page_type': 'about_page',
                'scraped_at': time.strftime("%Y-%m-%d %H:%M:%S")
            }
    
    def closed(self, reason):
        """Clean up resources when spider is closed"""
        self.logger.info("Spider closed: %s", reason)
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()