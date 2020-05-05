from lxml import etree


class Parser():

    def parse_html(self, html, xpath):
        selector = etree.HTML(html)

        return selector.xpath(xpath)
