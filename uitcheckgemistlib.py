# -*- coding: utf-8 -*-

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
        """Gets initial page to retrieve session cookies.

        Returns:
            response (requests.response): The response object of the initial page.
        """
        response = self.session.get(self.url)
        return response

    def _submit_card_details(self, response):
        """Submits the card's details in the first form.

        Args:
            response (requests.response): The response object having the form.

        Returns:
            response (requests.response): The response object of the submitted form.
        """
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
        """Retrieves the hidden token from the form.

        Args:
            response (requests.response): The response object having the form.
            name (str): The name of the token to look for.

        Returns:
            token (str): The retrieved token.
        """
        soup = bfs(response.text, 'html.parser')
        token = soup.find('input', {'name': name}).attrs.get('value')
        return token 

    def _submit_data(self, url, data):
        """Helper method to post data to url.

        Args:
            url (str): The url to post to.
            data (dict): The data to post.

        Returns:
            response (requests.response): The response of the post.
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}        
        response = self.session.post(url, data=data, headers=headers)
        return response

    def _submit_information(self, response):
        """Submits the birth date of the card owner.

        Args:
            response (requests.response): The response object having the form.

        Returns:
            response (requests.response): The response object of the submitted form.
        """
        token = self._get_token(response, 'tls_person_information[_token]')
        data = {'tls_person_information[_token]': token,
                'tls_person_information[holderBirthDate]': self.birth_date}
        response = self._submit_data(response.url, data)
        return response

    def get_missed_checks(self):
        """Returns the html with the check-ins and check-outs.

        Returns:
            response.text (str): The html in string format.
        """
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
        """Validates the card number. 

        Validates that the card number has 16 numeric characters 
        and that the first four are '3528'. 
        After the validation is succeful, populates the attributes of the object 
        with the parts of the card number.

        Args:
            card_number (str): The card number.

        Raises: 
            ValueError if the card doesn't have 16 numeric characters 
            and the first four are not '3528'.

        Returns:
            None
        """
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


