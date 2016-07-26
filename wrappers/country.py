# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ({'country': 'Australia'}, ['Adelaide', 'Adelaide Hills', 'Albany', 'Albury', 'Alice Springs', 'Altona Meadows', 'Armadale', 'Armidale', 'Ashfield', 'Auburn', 'Ballarat', 'Balwyn North', 'Bankstown', 'Banora Point', 'Bathurst', 'Baulkham Hills']),
            ({'country': 'Finland'}, ['Anjala', 'Espoo', 'Forssa', 'Haemeenlinna', 'Hamina', 'Haukipudas', 'Heinola', 'Helsinki', 'Hollola', 'Hyvinge', 'Iisalmi', 'Imatra', 'Jaemsae', 'Jaervenpaeae', 'Jakobstad']),
            ({'country': 'Greece'}, ['Acharnes', 'Agia Paraskevi', 'Agia Varvara', 'Agioi Anargyroi', 'Agios Dimitrios', 'Agios Ioannis Rentis', 'Agrinio', 'Aigaleo', 'Aigio', 'Alexandroupoli', 'Alimos', 'Amaliada', 'Ano Liosia', 'Argos', 'Argyroupoli', 'Arta', 'Artemida', 'Aspropyrgos', 'Athens']),
        ]
        self.website = 'http://localhost:8000/examples/country/'
        self.category = ''
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses local custom website to demonstrate a multi-step wrapper'

    def run(self, browser, inputs):
        browser.get(self.website)
        browser.wait_steady()
        browser.fill('input#country', inputs['country'])
        browser.click('button')
