"""MoexClient for security fetching."""
from decimal import Decimal

import requests
import xml.etree.ElementTree as ET


class MoexClient:

    MOEX_DOMAIN = 'http://iss.moex.com'
    CURRENCY_PATH = '/iss/statistics/engines/currency/markets/selt/rates/'
    MARKETS_PATH = '/iss/engines/stock/markets/'
    SECURITIES_LIST_PATH = '/iss/history/engines/stock/markets/{}/securities/'
    SECURITIES_DETAIL_PATH = '/iss/securities/{}/'
    USD_MARKETS = ['foreignshares', 'foreignndm', 'mamc']
    ALLOWED_CURRENCY = ['USD', 'RUB']

    def __init__(self):
        self.market = None
        self.security = None
        self.currency = None
        self.cost_of_security = None

    def init_fetching_security(self):
        """Get security with detail info depending on user choice."""
        markets = self.get_markets()
        market_options = self.make_options(markets)

        print(f'Select market by its key.\n{market_options}')
        self.market = self.get_validated_input(markets.keys())

        securities = self.get_security_list_by_market()
        security_options = self.make_options(securities)

        print(f'Select market by its key.\n{security_options}')
        self.security = self.get_validated_input(securities.keys())

        security_info = self.get_security_info()
        self.cost_of_security = Decimal(
            securities[self.security]['yesterday_price'] or 0)

        print(f'Chose currency to display: RUB, USD.')
        self.currency = self.get_validated_input(self.ALLOWED_CURRENCY)
        security_info.update(
            {'yesterday_price': {
                'cost': self.calculate_cost(),
                'currency': self.currency
            }}
        )
        print(security_info)

    def get_markets(self):
        """Make request to MOEX markets endpoint and return slags and
        titles of markets.

        :return: dict of markets, type {str: str}
        """
        market_url = self.MOEX_DOMAIN + self.MARKETS_PATH
        response = requests.get(market_url)
        root = ET.fromstring(response.content)
        markets = root.findall('./data/rows/')
        return {market.attrib['NAME']: market.attrib['title'] for market in
                markets}

    def get_usd_currency_quote(self):
        """Make request to MOEX currency endpoint and return USD quotes.

        :return: dict of currencies, type: Decimal
        """
        currency_url = self.MOEX_DOMAIN + self.CURRENCY_PATH
        response = requests.get(currency_url)
        root = ET.fromstring(response.content)
        currency_data = root.find('./data/rows/').attrib
        usd = currency_data['CBRF_USD_LAST']
        return Decimal(usd)

    def get_security_list_by_market(self):
        """Make request to MOEX security list endpoint
        and return list of security.

        :return: dict of securities, type {str: dict}
        """
        security_list_url = self.MOEX_DOMAIN + \
            self.SECURITIES_LIST_PATH.format(self.market) + '?limit=10'
        # we don't need too mach items for now, that is why limit is 10
        response = requests.get(security_list_url)
        root = ET.fromstring(response.content)
        securities_data = root.findall('./data[@id="history"]/rows/')
        securities_result_dict = {}
        for security in securities_data:
            securities_result_dict.update(
                {security.attrib['SECID']:
                    {'title': security.attrib['SHORTNAME'],
                     'yesterday_price': security.attrib['CLOSE']}})
        return securities_result_dict

    def get_security_info(self):
        """Make request to MOEX security detail endpoint and
        return list of security.

        :return: dict of rich data about selected security, type {str, str}
        """
        security_detail_url = self.MOEX_DOMAIN + \
            self.SECURITIES_DETAIL_PATH.format(self.security)
        response = requests.get(security_detail_url)
        root = ET.fromstring(response.content)
        description = root.findall('./data[@id="description"]/rows/')
        return {elem.attrib['title']: elem.attrib['value'] for elem in
                description}

    def calculate_cost(self):
        """Calculates cost in chosen currency, depending on market type.

        :return: cost in chosen currency, type: Decimal
        """
        if self.market in self.USD_MARKETS and self.currency == 'USD' or \
                self.market not in self.USD_MARKETS and self.currency == 'RUB':
            return self.cost_of_security
        else:
            usd_quote = self.get_usd_currency_quote()
            if self.market in self.USD_MARKETS and self.currency == 'RUB':
                self.cost_of_security = self.cost_of_security * usd_quote
            else:
                self.cost_of_security = self.cost_of_security / usd_quote
            return self.cost_of_security.quantize(Decimal('0.001'))
            # purpose is only to represent
            # 3 points after dot like in broker terminals

    def make_options(self, dict_of_items):
        """Make string of options from dict of items.

        :param dict_of_items: key - value data to represent, type: dict
        :return: 'Key: key, Title: value,\n...' type: Str
        """
        options = ''
        for key, value in dict_of_items.items():
            options += f'Key: {key}, Title: {value}\n'
        return options

    def get_validated_input(self, validation_items):
        """Perform input and validate it by given list.
        Question should be announced before method.

        :param validation_items: list of possible options, type List[str]
        :return: chosen item, type: Str
        """
        while True:
            item = input('Enter key:   ')
            if item in validation_items:
                break
            print('Invalid key')
        return item


if __name__ == '__main__':
    client = MoexClient()
    while True:
        client.init_fetching_security()
        answer_to_continue = input('Continue search? y/n:   ')
        if answer_to_continue == 'n':
            break
