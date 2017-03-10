from requests import Session
from bs4 import BeautifulSoup as bfs


class Server(object):

    def __init__(self, card_number, valid_until, birth_date):
        self.url = 'https://www.uitcheckgemist.nl/'
        # When OvChipCard class is complete, card number attribute 
        # and valid_until attribute will be part of a card object.
        self.card_number = card_number
        self.valid_until = valid_until
        self.birth_date = birth_date
        self.session = Session()
        response = self._get_initial_page()
        response = self._submit_card_details(response)
        self.response = self._submit_information(response)

    def _get_initial_page(self):
        response = self.session.get(self.url)
        return response

    def _submit_card_details(self, response):
        token = self._get_token(response, 'tls_card_information[_token]')
        data = {'tls_card_information[_token]': token,
                'tls_card_information[engravedId][0]': self.card_number.split('-')[0],
                'tls_card_information[engravedId][1]': self.card_number.split('-')[1],
                'tls_card_information[engravedId][2]': self.card_number.split('-')[2],
                'tls_card_information[engravedId][3]': self.card_number.split('-')[3],
                'tls_card_information[expirationDate]': self.valid_until,
                'tls_card_information[optIn]': 1 }
        response = self._submit_data(self.url, data)
        return response

    def _get_token(self, response, name):
        soup = bfs(response.text, 'html.parser')
        token = soup.find('input', {'name': name}).attrs.get('value')
        return token 

    def _submit_data(self, url, data):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}        
        response = self.session.post(url, data=data, headers=headers)
        return response

    def _submit_information(self, response):
        token = self._get_token(response, 'tls_person_information[_token]')
        data = {'tls_person_information[_token]': token,
                'tls_person_information[holderBirthDate]': self.birth_date}
        response = self._submit_data(response.url, data)
        return response

    def get_missed_checks(self):
        # When check-ins and check-outs are modeled as classes 
        # this will return a list of the appropriate objects
        # and not dump the html content as it does now.
        return self.response.text



class OvChipCard(object):

    def __init__(self, card_number):
        self.first_part = None
        self.second_part = None
        self.third_part = None
        self.fourth_part = None
        self.number = None
        self._validate_number(card_number)

    def _validate_number(self, card_number):
        card_number = ''.join([character for character in card_number 
                               if character.isdigit()])
        if not len(card_number) == 16:
            raise ValueError('Invalid card number :{}'.format(card_number))
        if not card_number[:4] == '3528':
            raise ValueError('Invalid card number :{}'.format(card_number))
        self.first_part = card_number[:4]
        self.second_part = card_number[4:8]
        self.third_part = card_number[8:12]
        self.fourth_part = card_number[12:]
        self.number = '-'.join([self.first_part, 
                                self.second_part, 
                                self.third_part, 
                                self.fourth_part])

    def __str__(self):
        return self.number


