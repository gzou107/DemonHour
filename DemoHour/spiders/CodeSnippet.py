class sample:		
	"""	
		links = hxs.select("//div[@class='ui-pagination']/ul/li/a/@href")
		for link in links:
			link_url = link.extract()
			self.log("I am in link %s" %link_url)
	
			if re.search('page=1$', link_url):
				self.log('match rule: %s' %link_url)
				print link_url
			else:
				yield Request(link_url, self.parse_one_page)
		"""
		
	"""
	def parse(self, response):
		self.log('hi, this is an item page! %s' %response.url)
		
		if response.meta['depth'] > 5:
			self.log('reach depth of 5 when at page %s' % response.url)
			
		hxs = HtmlXPathSelector(response)

		# firstly get the total backer count so that we know the pagination number
		count_str = hxs.select("//a[@class='ui-tab-current']/span[@id='backer_count']/text()").extract()
		print "total supporter count: ", count_str
		count = int(count_str[0])
		backer_per_page = 40
		
		current_page = hxs.select("//div[@class='ui-pagination']/ul/li[@class = 'ui-pagination-current']/a/@href").extract()
		for i in range(1, count/backer_per_page + 2):
			page_url_base = current_page[0].split('?')
			page_url_prefix = page_url_base[0]
			page_url = page_url_prefix + '?' + 'page='+ str(i)
			yield Request(page_url, self.parse_one_page)
		
		
		visited_page = set()
		for page in pages:
			if not page in visited_page:
				visited_page.add(page)
				yield Request(page, self.parse_one_page)
		
	"""	
	
	# loader = XPathItemLoader(item = Supporter(), response = response)
		
	"""
	for backer in backers:
			loader.add_xpath('supporter_name', ".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/text()")
			loader.add_xpath('supporter_url', ".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/a[@class='supportersmeta-t-a']/@href")
			loader.add_xpath('supporter_icon',".//div[@class='supportersmeta']/div[@class='supportersmeta-t']/div[@class='icon-sun-ms']/a/text()")
			loader.add_xpath('supporter_support_time', ".//div[@class='supportersmeta']/text()[2]")
			loader.add_xpath('supporter_total_support_proj', ".//div[@class='supportersmeta']/text()[4]")
			loader.add_xpath('supporter_support_amount', ".//div[@class='supportersmeta']/text()[3]")
			items.append(loader.load_item())
	return items
	"""