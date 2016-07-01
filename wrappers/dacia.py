# -*- coding: utf-8 -*-

class Wrapper:
    def __init__(self):
        self.data = [
            ('linz', ['Sonnleitner Gmbh & Co KG', 'Linke Brückenstrasse 60', '4040 Linz', '+43732 9366', '+43732 9366111', 'Welserstraße 54', '4060 Leonding', '+43732672222', '+4373267222230']),
            ('salzburg', ['Herbert Peterbauer KG', 'Itzlinger Hauptstrasse 44', '5020 Salzburg', '+43662451087', '+43662451687', 'Sonnleitner Gmbh & Co KG', 'Landstrasse 2b', '5020 Salzburg']),
            ('graz', ['Vogl + Co AutoverkaufsgmbH', 'Schießstattgasse 65', '8010 Graz', '0316/8080', '0316/8080-1009', 'Vogl Auto Nord GmbH', 'Wiener Strasse 306', '+43316686808', '+4331668680817']),
            ('Klagenfurt', ['K&P FahrzeughandelsgesmbH', 'Flatschacherstrasse 68', '0463/33210', '0463/332102', 'Alois Paintner', 'Villacher Straße 139', '0463/261162', '0463/239147']), 
        ]
        self.website = 'http://dacia.at/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Includes redundant parameters _sourcePage and __fp. Final response is HTML and scraping this is not yet supported.'

    def run(self, browser, input_value):
        browser.get(self.website)
        browser.fill('input#quicksearch-overnav', input_value)
        browser.click('button')
