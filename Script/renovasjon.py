#!/usr/bin/env python3

#
# Adapted from https://github.com/eyesoft/home-assistant-custom-components for use outside home assistant
#
###
#
# MIT License
#
# Copyright (c) 2018 eyesoft
# Copyright (c) 2021 mboehn
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
###


import argparse
import urllib.parse
import requests
import json
from datetime import date
from datetime import datetime
import logging

_LOGGER = logging.getLogger(__name__)


CONST_KOMMUNE_NUMMER = "Kommunenr"
CONST_APP_KEY = "RenovasjonAppKey"
CONST_URL_FRAKSJONER = 'https://komteksky.norkart.no/komtek.renovasjonwebapi/api/fraksjoner'
CONST_URL_TOMMEKALENDER = 'https://komteksky.norkart.no/komtek.renovasjonwebapi/api/tommekalender?' \
                          'gatenavn=[gatenavn]&gatekode=[gatekode]&husnr=[husnr]'
CONST_APP_KEY_VALUE = "AE13DEEC-804F-4615-A74E-B4FAC11F0A30"


class MinRenovasjon:
    def __init__(self, gatenavn, gatekode, husnr, kommunenr, date_format):
        self.gatenavn = self._url_encode(gatenavn)
        self.gatekode = gatekode
        self.husnr = husnr
        self._kommunenr = kommunenr
        self._date_format = date_format
        self._kalender_list = self._get_calendar_list()

    @staticmethod
    def _url_encode(string):
        string_decoded_encoded = urllib.parse.quote(
            urllib.parse.unquote(string))
        if string_decoded_encoded != string:
            string = string_decoded_encoded
        return string

    def refresh_calendar(self):
        do_refresh = self._check_for_refresh_of_data(self._kalender_list)
        if do_refresh:
            self._kalender_list = self._get_calendar_list()

    def _get_tommekalender_from_web_api(self):
        header = {CONST_KOMMUNE_NUMMER: self._kommunenr,
                  CONST_APP_KEY: CONST_APP_KEY_VALUE}

        url = CONST_URL_TOMMEKALENDER
        url = url.replace('[gatenavn]', self.gatenavn)
        url = url.replace('[gatekode]', self.gatekode)
        url = url.replace('[husnr]', self.husnr)

        response = requests.get(url, headers=header)
        if response.status_code == requests.codes.ok:
            data = response.text
            return data
        else:
            _LOGGER.error("GET Tommekalender returned: %s",
                          response.status_code)
            return None

    def _get_fraksjoner_from_web_api(self):
        header = {CONST_KOMMUNE_NUMMER: self._kommunenr,
                  CONST_APP_KEY: CONST_APP_KEY_VALUE}
        url = CONST_URL_FRAKSJONER

        response = requests.get(url, headers=header)
        if response.status_code == requests.codes.ok:
            data = response.text
            return data
        else:
            _LOGGER.error("GET Fraksjoner returned: %s", response.status_code)
            return None

    def _get_from_web_api(self):
        tommekalender = self._get_tommekalender_from_web_api()
        fraksjoner = self._get_fraksjoner_from_web_api()

        _LOGGER.debug(f"Tommekalender: {tommekalender}")
        _LOGGER.debug(f"Fraksjoner: {fraksjoner}")

        return tommekalender, fraksjoner

    def _get_calendar_list(self, refresh=False):
        data = None

        if refresh or data is None:
            _LOGGER.info("Refresh or no data. Fetching from API.")
            tommekalender, fraksjoner = self._get_from_web_api()
        else:
            tommekalender, fraksjoner = data

        kalender_list = self._parse_calendar_list(tommekalender, fraksjoner)

        if kalender_list is None:
            return None

        check_for_refresh = False
        if not refresh:
            check_for_refresh = self._check_for_refresh_of_data(kalender_list)

        if check_for_refresh:
            kalender_list = self._get_calendar_list(refresh=True)

        _LOGGER.info("Returning calendar list")
        return kalender_list

    @staticmethod
    def _parse_calendar_list(tommekalender, fraksjoner):
        kalender_list = []

        if tommekalender is None or fraksjoner is None:
            _LOGGER.error(
                "Could not fetch calendar. Check configuration parameters.")
            return None

        tommekalender_json = json.loads(tommekalender)
        fraksjoner_json = json.loads(fraksjoner)

        for calender_entry in tommekalender_json:
            fraksjon_id = calender_entry['FraksjonId']
            tommedato_forste = None
            tommedato_neste = None

            if len(calender_entry['Tommedatoer']) == 1:
                tommedato_forste = calender_entry['Tommedatoer'][0]
            else:
                tommedato_forste, tommedato_neste = calender_entry['Tommedatoer']

            if tommedato_forste is not None:
                tommedato_forste = datetime.strptime(
                    tommedato_forste, "%Y-%m-%dT%H:%M:%S")
            if tommedato_neste is not None:
                tommedato_neste = datetime.strptime(
                    tommedato_neste, "%Y-%m-%dT%H:%M:%S")

            for fraksjon in fraksjoner_json:
                if fraksjon['Id'] == fraksjon_id:
                    fraksjon_navn = fraksjon['Navn']
                    fraksjon_ikon = fraksjon['Ikon']

                    kalender_list.append(
                        (fraksjon_id, fraksjon_navn, fraksjon_ikon, tommedato_forste, tommedato_neste))
                    continue

        return kalender_list

    @staticmethod
    def _check_for_refresh_of_data(kalender_list):
        if kalender_list is None:
            _LOGGER.info("Calendar is empty, forcing refresh")
            return True

        for entry in kalender_list:
            _, _, _, tommedato_forste, tommedato_neste = entry

            if tommedato_forste.date() < date.today() or tommedato_neste.date() < date.today():
                _LOGGER.info("Data needs refresh")
                return True

        return False

    def get_calender_for_fraction(self, fraksjon_id):
        if self._kalender_list is None:
            return None

        for entry in self._kalender_list:
            entry_fraksjon_id, _, _, _, _ = entry
            if fraksjon_id == entry_fraksjon_id:
                return entry

    @property
    def calender_list(self):
        return self._kalender_list

    def format_date(self, date):
        if self._date_format == "None":
            return date
        return date.strftime(self._date_format)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('gatenavn', type=str)
    parser.add_argument('gatekode', type=str, help='sjekk NVDB eller geonorge')
    parser.add_argument('husnr', type=str)
    parser.add_argument('kommunenr', type=str)
    parser.add_argument('--fraksjon', type=int,
                        dest='fraksjon', help='1=rest, 2=papp osv.')
    args = parser.parse_args()

    mr = MinRenovasjon(gatenavn=args.gatenavn, gatekode=args.gatekode,
                       husnr=args.husnr, kommunenr=args.kommunenr, date_format='%d/%m/%Y')

    if args.fraksjon:
        print(json.dumps(mr.get_calender_for_fraction(
            args.fraksjon), default=str, indent=4))
    else:
        print(json.dumps(mr.calender_list, default=str, indent=4))
