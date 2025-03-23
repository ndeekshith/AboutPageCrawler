# About Page Scraper

This is a Scrapy-based web scraper that uses Selenium to extract 'About Us' page content from given websites.


## Usage
Run the Scrapy spider using:
```bash
scrapy crawl about_page_spider
```

The extracted data will be saved in `items.csv` see in items.csv file.

## Configuration
- Modify `start_urls` in `AboutPageSpider` to specify target websites.
- Adjust patterns in `self.about_patterns` to refine detection of 'About Us' pages.

## Notes
- Ensure Firefox is installed for Selenium to function correctly.
- Running in headless mode; remove `firefox_options.add_argument("--headless")` if you want to see the browser.


