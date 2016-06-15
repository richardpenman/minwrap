# -*- coding: utf-8 -*-

__doc__ = 'Wrappers to interact with websites and trigger AJAX events'


class britishairways:
    def __init__(self):
        self.data = [
            ('lon', ['London, London (All Airports) (LON), United Kingdom', 'London, City Airport (LCY), United Kingdom', 'London, Gatwick (LGW), United Kingdom', 'London, Heathrow (LHR), United Kingdom', 'London, Luton (LTN), United Kingdom', 'London, Stansted (STN), United Kingdom', 'Londonderry, Londonderry (LDY), United Kingdom', 'Long Beach (CA), Long Beach (CA) (LGB), USA', 'Longview, East Texas Regional (TX) (GGG), USA', 'Longyearbyen, Svalbard (LYR), Norway', 'Changchun, Longjia Intl (CGQ), China', 'East London, East London (ELS), South Africa']),
            ('par', ['Paris, Paris (All) (PAR), France', 'Paris, Charles de Gaulle (CDG), France', 'Paris, Orly (ORY), France', 'Paramaribo, Paramaribo (PBM), Suriname', 'State College, University Park (PA) (SCE), USA']),
        ]

    def run(self, browser):
        # XXX why does not autofill properly when reload homepage for each input?
        browser.load('http://www.britishairways.com/travel/home/public/en_gb')
        for i, (input_value, output_values) in enumerate(self.data):
            if i == 0:
                browser.click('div#accept_ba_cookies a')
            browser.fill('input#planTripFlightDestination', input_value)
            browser.click('input#planTripFlightDestination')
            yield output_values


class delta:
    def __init__(self):
        self.data = [ 
            ('lon', ['London Area Airports, United Kingdom (LON)', 'London Metropolitan Area', 'London Area Airports', 'London-Heathrow, United Kingdom (LHR)', 'Heathrow Airport', 'London-Heathrow']),
            ('par', ['Paris Area Airports, France (PAR)', 'CDG/ORY', 'Paris Area Airports', 'CDG', 'Paris-De Gaulle, France (CDG)', 'Charles De Gaulle Intl Arpt', 'Paris-De Gaulle', 'Paraburdoo, Australia (PBO)', 'Paraburdoo,Orly Brazil (CKS)']),
            ('new', ['New York Area Airports, NY (NYC)', 'LGA/JFK/EWR/SWF', 'New York Area Airports', 'New York Area Airports, NY (NYC)', 'New York-Kennedy, NY (JFK)', 'John F Kennedy International']),
        ]

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load('http://www.delta.com/') # XXX each time loaded generates different session ID
            browser.keys('input#originCity', input_value)
            yield output_values


class lufthansa:
    def __init__(self):
        self.data = [
            ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
            ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
        ]

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load('http://www.lufthansa.com/uk/en/Homepage')
            browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
            browser.wait_load('div.rw-popup')
            yield output_values


class fiat:
    def __init__(self):
        self.data = [ 
            ('OX1', ['OXON', '0051422', 'HARTWELL ABINGDON', '01235522822', 'OX14 5JU', 'David Ebsworth', 'david.ebsworth@hartwell.co.uk', '3112', 'hartwell-auto.co.uk/fiat/?locationcode=00000013&bannerid=DL&source=WCOR', '08448548198', '51.66387', '0870 909 5214', '-1.297952', 'ABINGDON', '6870.98', 'DRAYTON ROAD', 'BUCKS', '0060169', 'PERRYS', '08433939305', 'HP19_8BY', 'Lee Jackson', 'aylesfiatcontrol@perrys.co.uk', 'perrys-auto.co.uk/fiat/?locationcode=00000034&bannerid=DL&source=WCOR']),
            ('CB2', ['10 WHITTON ROAD', 'SURREY', '0046500', 'MOTOR VILLAGE CROYDON', '02086831000', 'CR0 3HH', 'Simon Wright', 'tim.keatinge@fiat.com', 'croydon-motorvillage.co.uk/fiat/?locationcode=00000256&bannerid=DL&source=WCOR', '0208 6831222', '51.385291', '02086831222', 'CROYDON', '89491.75', '121 CANTERBURY ROAD', 'BERKS', '0065920', 'THAMES MOTOR GROUP (SLOUGH) LTD.', '01753 325063', 'SL1 6BB', 'Tim Fennell', 'ss@thamesmotorgroup.co.uk', 'thames-auto.co.uk/fiat/?locationcode=00000819&bannerid=DL&source=WCOR', '01628559669', '51.520652', '-0.647828', '01753788000', '01753325063', 'SLOUGH', '90276.94', '470 BATH ROAD', '0047239', 'DESIRA GROUP PLC - NORWICH', '01603633222', 'NR2_4TG']),
        ]

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load('http://www.fiat.co.uk/find-dealer')
            browser.fill('div.input_text input', input_value)
            browser.click('div.input_text button.search')
            yield output_values


class dacia:
    def __init__(self):
        self.data = [
            #('vienna', ['Ernst Karner GmbH', 'Radetzkyplatz 6', '1030 Wien', '+4317125572', 'Rembrandtstrasse 32-34', '1020 Wien', '01/3304443', '01/3304443-4']),
            ('linz', ['Sonnleitner Gmbh & Co KG', 'Linke Brückenstrasse 60', '4040 Linz', '+43732 9366', '+43732 9366111', 'Welserstraße 54', '4060 Leonding', '+43732672222', '+4373267222230']),
            ('salzburg', ['Herbert Peterbauer KG', 'Itzlinger Hauptstrasse 44', '5020 Salzburg', '+43662451087', '+43662451687', 'Sonnleitner Gmbh & Co KG', 'Landstrasse 2b', '5020 Salzburg']),
        ]

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load('http://dacia.at/')
            browser.fill('input#quicksearch-overnav', input_value)
            browser.click('button')
            yield output_values


class peugeot:
    def __init__(self):
        self.data = [ 
            ('amsterdam', ['Van Mossel Amsterdam Noord', 'Joh. van Hasseltweg 65', '1021 KN AMSTERDAM', '(088) 0014 200', '(088) 001 42 09', 'Van Mossel Amsterdam Zuidoost', 'Klokkenbergweg 29', '1101 AK AMSTERDAM', '(088) 0014 500', '(088) 001 45 09']),
            ('leiden', ['Van Mossel Leiderdorp', 'Van der Valk Boumanweg 2', '2352 JC LEIDERDORP', '(088) 0014 700', '(088) 0014 709', 'DAVO Leidschendam', 'Veurse Achterweg 22', '2264 SG LEIDSCHENDAM', '(070) 850 2400']),
        ]

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load('http://www.peugeot.nl/zoek-een-dealer/')
            #browser.wait_load('div.main_search')
            browser.fill('div.main_search input#dl_main_search', input_value)
            browser.click('div.main_search input[type=submit]')
            yield output_values
