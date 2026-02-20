#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from urllib.parse import urlencode, quote
from urllib.request import urlopen, Request, HTTPError, URLError


class RadioBrowserError(Exception):
    pass


class RadioBrowserClient:

    BASE_URL = 'https://de1.api.radio-browser.info/json'

    def __init__(self, user_agent='Kodi Radio Addon'):
        self.user_agent = user_agent

    def get_tags(self, limit=500):
        return self._call('tags', {
            'order': 'stationcount',
            'reverse': 'true',
            'hidebroken': 'true',
            'limit': limit,
        })

    def get_languages(self, limit=500):
        return self._call('languages', {
            'order': 'stationcount',
            'reverse': 'true',
            'hidebroken': 'true',
            'limit': limit,
        })

    def get_countries(self, limit=500):
        return self._call('countries', {
            'order': 'stationcount',
            'reverse': 'true',
            'hidebroken': 'true',
            'limit': limit,
        })

    def get_states(self, country=None, limit=1000):
        params = {
            'order': 'stationcount',
            'reverse': 'true',
            'hidebroken': 'true',
            'limit': limit,
        }
        if country:
            params['country'] = country
        return self._call('states', params)

    def get_station_by_uuid(self, station_uuid):
        stations = self._call('stations/byuuid/%s' % quote(str(station_uuid)), {
            'hidebroken': 'true',
        })
        if not stations:
            return None
        return stations[0]

    def search_stations(self, sizeperpage, pageindex, order='clickcount', **criteria):
        offset = (int(pageindex) - 1) * int(sizeperpage)
        params = {
            'hidebroken': 'true',
            'order': order,
            'reverse': 'true' if order != 'name' else 'false',
            'offset': offset,
            'limit': int(sizeperpage) + 1,
        }
        params.update({k: v for k, v in criteria.items() if v})

        stations = self._call('stations/search', params)
        has_more = len(stations) > int(sizeperpage)
        return has_more, stations[:int(sizeperpage)]

    def list_stations(self, sizeperpage, pageindex, endpoint, order='clickcount'):
        offset = (int(pageindex) - 1) * int(sizeperpage)
        stations = self._call(endpoint, {
            'hidebroken': 'true',
            'order': order,
            'reverse': 'true' if order != 'name' else 'false',
            'offset': offset,
            'limit': int(sizeperpage) + 1,
        })
        has_more = len(stations) > int(sizeperpage)
        return has_more, stations[:int(sizeperpage)]

    def _call(self, path, params=None):
        url = '%s/%s' % (self.BASE_URL, path)
        if params:
            url += '?%s' % urlencode(params)

        req = Request(url)
        req.add_header('User-Agent', self.user_agent)
        try:
            response = urlopen(req).read()
        except HTTPError as error:
            raise RadioBrowserError('HTTPError: %s' % error)
        except URLError as error:
            raise RadioBrowserError('URLError: %s' % error)

        try:
            return json.loads(response)
        except Exception as error:
            raise RadioBrowserError('Invalid JSON response: %s' % error)
