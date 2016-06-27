# -*- coding: utf-8 -*-

__doc__ = """Wrappers to interact with websites and trigger AJAX events

A wrapper defines a run() method that takes a browser instance. 
yield is used to give execution back to the main event loop. 
A list of strings can be passed to define what the reply of interest should contain.
"""



class british_airways:
    def __init__(self):
        self.data = [
            ('lon', ['London, London (All Airports) (LON), United Kingdom', 'London, City Airport (LCY), United Kingdom', 'London, Gatwick (LGW), United Kingdom', 'London, Heathrow (LHR), United Kingdom', 'London, Luton (LTN), United Kingdom', 'London, Stansted (STN), United Kingdom', 'Londonderry, Londonderry (LDY), United Kingdom', 'Long Beach (CA), Long Beach (CA) (LGB), USA', 'Longview, East Texas Regional (TX) (GGG), USA', 'Longyearbyen, Svalbard (LYR), Norway', 'Changchun, Longjia Intl (CGQ), China', 'East London, East London (ELS), South Africa']),
            ('par', ['Paris, Paris (All) (PAR), France', 'Paris, Charles de Gaulle (CDG), France', 'Paris, Orly (ORY), France', 'Paramaribo, Paramaribo (PBM), Suriname', 'State College, University Park (PA) (SCE), USA']),
        ]
        self.website = 'http://www.britishairways.com/travel/home/public/en_gb'
        self.category = 'autocomplete'
        self.http_method = 'GET'
        self.response_format = 'JavaScript'
        self.notes = 'JavaScript results use content-type text/plain and then modified before being inserted into document'

    def run(self, browser):
        # XXX why does not autofill properly when reload homepage for each input?
        browser.load(self.website)
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
        self.website = 'http://www.delta.com/'
        self.category = 'autocomplete'
        self.http_method = 'POST'
        self.response_format = 'JavaScript'
        self.notes = 'Request has 2 parameters - the prefix and a query counter'

    def run(self, browser):
        browser.load(self.website) # XXX each time loaded generates different session ID
        for input_value, output_values in self.data:
            browser.keys('input#originCity', input_value)
            yield output_values


class lufthansa:
    def __init__(self):
        self.data = [
            ('lon', ['United Kingdom', 'London, all airports', 'London City Airport', 'London Gatwick', 'London Heathrow', 'London-Stansted', 'Southampton', 'London, Canada', 'Sarnia', 'Windsor', 'Londrina', 'Long Beach', 'Burbank', 'Oxnard/Ventura', 'Norway', 'Longyearbyen']),
            ('par', ['France', 'Paris - Charles De Gaulle', 'Parkersburg/Marietta', 'Clarksburg']),
        ]
        self.website = 'http://www.lufthansa.com/uk/en/Homepage'
        self.category = 'autocomplete'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'AJAX callback triggered on KeyUp event'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.keys('input#flightmanagerFlightsFormOrigin', input_value)
            browser.wait_load('div.rw-popup')
            yield output_values


class fiat:
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


class audi:
    def __init__(self):
        self.data = [
            ('Antwerpen', ['Auto Natie', 'info@autonatie.audi.be', '+32 3 231 59 30', 'Groenendaallaan, 397 ANTWERPEN 3', 'Garage Thuy n.v.', 'Lakborslei, 81 DEURNE (ANTWERPEN)', '+32 3 326 11 22', 'info@thuy.audi.be']),
            ('Bruxelles', ['D\'Ieteren Mail', 'Rue Du Mail, 50 IXELLES', '+32 2 536 55 11', 'info@dmail.audi.be', 'Audi Center Brussels', 'Bemptstraat, 38 DROGENBOS', '+32 2 371 27 11', 'info@ddrogenbos.audi.be']),
        ]
        self.website = 'http://www.dealerlocator.audi.be/default.aspx'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'All data pre-loaded in single AJAX request'
    
    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.keys('input#addressinput', input_value)
            browser.click('span#lnk_search')
            yield output_values

        
class dacia:
    def __init__(self):
        self.data = [
            ('linz', ['Sonnleitner Gmbh & Co KG', 'Linke Brückenstrasse 60', '4040 Linz', '+43732 9366', '+43732 9366111', 'Welserstraße 54', '4060 Leonding', '+43732672222', '+4373267222230']),
            ('salzburg', ['Herbert Peterbauer KG', 'Itzlinger Hauptstrasse 44', '5020 Salzburg', '+43662451087', '+43662451687', 'Sonnleitner Gmbh & Co KG', 'Landstrasse 2b', '5020 Salzburg']),
        ]
        self.website = 'http://dacia.at/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = 'Includes redundant parameters <i>_sourcePage</i> and <i>__fp</i>'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('input#quicksearch-overnav', input_value)
            browser.click('button')
            yield output_values


"""
class hyundai:
    def __init__(self):
        self.data = [
            ('linz', ['Lietz Linz GmbH', 'St. Peter Straße 21', '4020 Linz', '0732307665', 'Lietz-Urfahr GmbH', 'Mostnystraße 8', '4040 Linz-Urfahr', '0732757272']),
            ('salzburg', ['AUTO&MOTORRAD HOLZMEISTER GmbH&Co.KG', 'http://holzmeister.hyundai.at/', 'Almerstraße 36', '5760 Saalfelden', '0658273891', 'info@autobike.eu']),
        ]
        self.website = 'http://www.hyundai.at/Beratung/Beratung/Handler-finden.aspx'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.keys('input#dealerAutocomplete', input_value) # XXX why is text not inserted?
            browser.click('a#ctl00_cphContent_ctl01_ctlSearchBox_lbSearch')
            yield output_values
"""


class kia:
    def __init__(self):
        self.data = [
            ('madrid', ['Calle Sinesio Delgado 36', '28029', 'San Francisco de Sales 34', '28003', 'kiturmadrid@kia.es', 'http://www.kiturmadrid.com', '911108878', 'autosselikar@kia.es', '914811535']),
            ('granada', ['Polígono Industrial de Guadix, M2, P11', '18500', 'Guadix', 'C/ Comercio (P.Ind El Florío)', '18015', 'Granada', 'armmotor@kia.es', 'http://www.dealershipdomain.com', '958126211']),
        ]
        self.website = 'http://www.kia.com/es/dealerfinder2011/'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'XML'
        self.notes = 'All dealers are fetched in a single XML AJAX call'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('input#ds-searchinput', input_value) # XXX why not inserted
            browser.keys('input#ds-searchinput', input_value) # XXX why not inserted
            browser.wait(5)
            yield output_values


class landrover:
    def __init__(self):
        self.data = [
            ('Lisboa', ['Avenida Marechal Gomes Costa, 33, Lisboa, 1800-255', 'Carclasse', '211 901 000', '211 901 099', 'miguel.igrejas@carclasse.pt', 'http://carclasse.landrover.pt/']),
            ('Alcafaz', ['M. Coutinho Porto', 'Av. Dr. Francisco Sá Carneiro, Apartado 149, Paredes, Porto, 4580-104', '255 780 100', '255 780 111', 'mcoutinhoporto@mcoutinho.pt', 'http://mcoutinho.landrover.pt/']),
        ]
        self.website = 'http://www.landrover.pt/national-dealer-locator.html'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'HTML'
        self.notes = ''

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.fill('input[name=placeName]', input_value)
            browser.click('input[type=submit]')
            yield output_values



class lexus:
    def __init__(self):
        self.data = [
            ('paris', ['58, Boulevard Saint Marcel', '75005', '01 55 43 55 00', '3, rue des Ardennes', '75019', '01 40 03 16 00', '4, avenue de la Grande Armée', '75017', '01 40 55 40 00']),
            ('toulouse', ['123, Rue Nicolas', 'Vauquelin', '31100', '05 61 61 84 29', '4 rue Pierre-Gilles de Gennes', '64140', '05 59 72 29 00']),
            ('marseille', ['36 Boulevard Jean Moulin', '13005', '04 91 229 229', 'ZAC Aix La Pioline', 'Les Milles', '13290', '04 42 95 28 78', 'Rue Charles Valente', 'ZAC de la Castelette', 'Montfavet', '84143', '04 90 87 47 00']),
        ]
        self.website = 'http://www.lexus.fr/forms/find-a-retailer'
        self.category = 'car dealer'
        self.http_method = 'GET'
        self.response_format = 'JSON'
        self.notes = 'Uses variables in the URL path and requires a geocoding intermediary step'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            browser.click('span[class="icon icon--base icon-close"]')
            browser.wait_load('div.form-control__item__postcode')
            browser.fill('div.form-control__item__postcode input', input_value)
            browser.click('div.form-control__item__postcode button')
            yield output_values



class peugeot:
    def __init__(self):
        self.data = [ 
            ('amsterdam', ['Van Mossel Amsterdam Noord', 'Joh. van Hasseltweg 65', '1021 KN AMSTERDAM', '(088) 0014 200', '(088) 001 42 09', 'Van Mossel Amsterdam Zuidoost', 'Klokkenbergweg 29', '1101 AK AMSTERDAM', '(088) 0014 500', '(088) 001 45 09']),
            ('leiden', ['Van Mossel Leiderdorp', 'Van der Valk Boumanweg 2', '2352 JC LEIDERDORP', '(088) 0014 700', '(088) 0014 709', 'DAVO Leidschendam', 'Veurse Achterweg 22', '2264 SG LEIDSCHENDAM', '(070) 850 2400']),
        ]
        self.website = 'http://www.peugeot.nl/zoek-een-dealer/'
        self.category = 'car dealer'
        self.http_method = 'POST'
        self.response_format = 'JSON'
        self.notes = 'Output is JSON but then bulk of this is a HTML block, so parsing is less useful'

    def run(self, browser):
        for input_value, output_values in self.data:
            browser.load(self.website)
            #browser.wait_load('div.main_search')
            browser.fill('div.main_search input#dl_main_search', input_value)
            browser.click('div.main_search input[type=submit]')
            yield output_values
