# from scrapy.selector import Selector
# from scrapy.http import HtmlResponse
#
# url = 'https://dumps.wikimedia.org/enwiki/latest/'
#
#
# response = HtmlResponse(url=url)
# selector = Selector(response=response).xpath('//pre/a/@href')
#
# a = 1
#
# f= open('wikidumps.json','w')
# href_list = response.xpath('//pre/a/@href').getall()
# text_list = response.xpath('//pre/a/text()').getall()
# info_list = response.xpath('//pre/text()').getall()
#
# import itertools
# dict_list = [dict(href=href, text=text, info=info) for href,text,info in itertools.itertools.zip_longest(href_list, text_list, info_list)]
#
# json_str_list = [json.dumps(d) for d in dict_list]
#
#
# f.writelines([line + '\n' for line in json_str_list])

import pandas as pd

# f = open('wikidumps.json')
# json_data = json.load(f)
print(pd.read_json('wikidumps.json'))
