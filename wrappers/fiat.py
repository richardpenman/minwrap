# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('OX1', ['OXON', '0051422', 'HARTWELL ABINGDON', '01235522822', 'OX14 5JU', 'David Ebsworth', 'david.ebsworth@hartwell.co.uk', '3112', 'hartwell-auto.co.uk/fiat/?locationcode=00000013&bannerid=DL&source=WCOR', '08448548198', '51.66387', '0870 909 5214', '-1.297952', 'ABINGDON', '6870.98', 'DRAYTON ROAD', 'BUCKS', '0060169', 'PERRYS', '08433939305', 'HP19_8BY', 'Lee Jackson', 'aylesfiatcontrol@perrys.co.uk', 'perrys-auto.co.uk/fiat/?locationcode=00000034&bannerid=DL&source=WCOR']),
            ('CB2', ['10 WHITTON ROAD', 'SURREY', '0046500', 'MOTOR VILLAGE CROYDON', '02086831000', 'CR0 3HH', 'Simon Wright', 'tim.keatinge@fiat.com', 'croydon-motorvillage.co.uk/fiat/?locationcode=00000256&bannerid=DL&source=WCOR', '0208 6831222', '51.385291', '02086831222', 'CROYDON', '89491.75', '121 CANTERBURY ROAD', 'BERKS', '0065920', 'THAMES MOTOR GROUP (SLOUGH) LTD.', '01753 325063', 'SL1 6BB', 'Tim Fennell', 'ss@thamesmotorgroup.co.uk', 'thames-auto.co.uk/fiat/?locationcode=00000819&bannerid=DL&source=WCOR', '01628559669', '51.520652', '-0.647828', '01753788000', '01753325063', 'SLOUGH', '90276.94', '470 BATH ROAD', '0047239', 'DESIRA GROUP PLC - NORWICH', '01603633222', 'NR2_4TG']),
        ]
        self.website = 'http://www.fiat.co.uk/find-dealer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSONP'
        self.notes = 'Two potential AJAX requests by postcode and sales type'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('div.input_text input', input_value)
            browser.click('div.input_text button.search')
            yield output_values
