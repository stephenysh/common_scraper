from html.parser import HTMLParser
import urllib.parse

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        print("Encountered a start tag:", tag)

    def handle_endtag(self, tag):
        print("Encountered an end tag :", tag)

    def handle_data(self, data):
        print("Encountered some data  :", data)

parser = MyHTMLParser()
encodedStr = 'https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%84%D8%A9_%D8%A7%D9%84%D8%A8%D8%A7%D8%A8%D9%84%D9%8A%D8%A9_%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89'
parser.feed('https://ar.wikipedia.org/wiki/%D8%A7%D9%84%D8%B3%D9%84%D8%A7%D9%84%D8%A9_%D8%A7%D9%84%D8%A8%D8%A7%D8%A8%D9%84%D9%8A%D8%A9_%D8%A7%D9%84%D8%A3%D9%88%D9%84%D9%89')

decodedStr = urllib.parse.unquote(encodedStr)

a = 1