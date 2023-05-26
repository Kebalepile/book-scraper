import scrapy


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css("article.product_pod")

        for book in books:
            book_page_path = book.css("h3 a").attrib['href']
            if "catalogue/" in book_page_path:
                book_page_url = f'{self.start_urls[0]}/{book_page_path}'
            else:
                book_page_url = f'{self.start_urls[0]}/catalogue/{book_page_path}'

            yield response.follow(book_page_url, callback=self.parse_book_page)

        next_page_path = response.css("li.next a::attr(href)").get()

        if "catalogue/" in next_page_path:
            next_page_url = f'{self.start_urls[0]}/{next_page_path}'
        else:
            next_page_url = f'{self.start_urls[0]}/catalogue/{next_page_path}'

        yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):
        table_rows = response.css("table tr")
        yield {
            "url": response.url,
            "title": response.css("*.product_main h1::text").get(),
            "product_type": table_rows[1].css("td::text").get(),
            "price_excl_tax": table_rows[2].css("td::text").get(),
            "price_incl_tax": table_rows[3].css("td::text").get(),
            "tax": table_rows[4].css("td::text").get(),
            "availability": table_rows[5].css("td::text").get(),
            "num_of_reviews": table_rows[6].css("td::text").get(),
            "stars": response.css("p.star-rating").attrib["class"],
            "category": response.xpath('//*[@id="default"]/div/div/ul/li[3]/a/text()').get(),
            "description": response.xpath('//*[@id="content_inner"]/article/p/text()').get(),
            "price": response.css("p.price_color::text").get()
        }
