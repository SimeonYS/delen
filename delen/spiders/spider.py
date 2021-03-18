import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import DelenItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.delen.be/api/news/overview?includeapp=false&includeweb=true&includeprospects=false&category=&page={}'
class DelenSpider(scrapy.Spider):
	name = 'delen'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['Articles'])):
			links = data['Articles'][index]['Url']
			yield response.follow(links,self.parse_post)
		if data['HasMore']:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response):
		date = response.xpath('(//p[@class="c-metabox"]/span)[1]/text()').get()
		title = response.xpath('//h1/text()').get()
		content = response.xpath('(//div[@class="o-editable"])[last()]//text() | //div[@class="u-grid__cell u-12-12 u-8-12@tablet "]//text()[not (ancestor::p[@class="c-metabox"] or ancestor::h1)]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=DelenItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
