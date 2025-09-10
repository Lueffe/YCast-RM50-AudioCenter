import base64
import uuid
import logging
import urllib.parse
import json
import http.client
from urllib.parse import urlparse

from ycast import __version__
import ycast.vtuner as vtuner
import ycast.generic as generic
from ycast.generic import get_json_attr

API_ENDPOINT = "http://all.api.radio-browser.info"
ID_PREFIX = "RB"
MINIMUM_COUNT_GENRE = 5
MINIMUM_COUNT_COUNTRY = 5
MINIMUM_COUNT_LANGUAGE = 5
DEFAULT_STATION_LIMIT = 200
SHOW_BROKEN_STATIONS = False

station_cache = {}

class Station:
    def __init__(self, station_json):
        self.stationuuid = generic.get_json_attr(station_json, 'stationuuid')
        self.id = generic.generate_stationid_with_prefix(
            base64.urlsafe_b64encode(uuid.UUID(self.stationuuid).bytes).decode(), ID_PREFIX)
        self.name = generic.get_json_attr(station_json, 'name')

        # Use original URL instead of resolved URL to avoid HTTPS redirects
        self.url = generic.get_json_attr(station_json, 'url')
        if not self.url:
            self.url = generic.get_json_attr(station_json, 'url_resolved')

        self.icon = generic.get_json_attr(station_json, 'favicon')
        self.description = generic.get_json_attr(station_json, 'tags')
        self.tags = generic.get_json_attr(station_json, 'tags').split(',')
        self.countrycode = generic.get_json_attr(station_json, 'countrycode')
        self.language = generic.get_json_attr(station_json, 'language')
        self.languagecodes = generic.get_json_attr(station_json, 'languagecodes')
        self.votes = generic.get_json_attr(station_json, 'votes')
        self.codec = generic.get_json_attr(station_json, 'codec')
        self.bitrate = generic.get_json_attr(station_json, 'bitrate')

    def to_vtuner(self):
        return vtuner.Station(self.id, self.name,
                              self.description, self.url, self.icon,
                              self.tags[0], self.countrycode, self.codec, self.bitrate, None)

    def to_dict(self):
        return {'name': self.name , 'url': self.url, 'icon': self.icon, 'description': self.description }

    def get_playable_url(self):
        try:
            playable_url_json = request('url/' + str(self.stationuuid))
            self.url = playable_url_json['url']
        except (IndexError, KeyError):
            logging.error("Could not retrieve first playlist item for station with id '%s'", self.stationuuid)


def request(url):
    logging.debug("Radiobrowser API request: %s", url)
    headers = {'content-type': 'application/json', 'User-Agent': generic.USER_AGENT + '/' + __version__}

    try:
        # Parse the URL
        parsed_url = urlparse(API_ENDPOINT + '/json/' + url)
        connection = http.client.HTTPConnection(parsed_url.netloc, timeout=5)
        connection.request('GET', parsed_url.path + '?' + parsed_url.query, headers=headers)
        response = connection.getresponse()
        data = response.read()
        connection.close()
    except Exception as err:
        logging.error("Connection to Radiobrowser API failed (%s)", err)
        return {}

    if response.status != 200:
        logging.error("Could not fetch data from Radiobrowser API (HTML status %s)", response.status)
        return {}

    return json.loads(data)


def get_station_by_id(vtune_id):
    global station_cache
    # decode
    uidbase64 = generic.get_stationid_without_prefix(vtune_id)
    uid = str(uuid.UUID(base64.urlsafe_b64decode(uidbase64).hex()))
    if station_cache:
        station = station_cache.get(vtune_id)
        if station:
            return station
    # no item in cache, do request
    station_json = request('stations/byuuid?uuids=' + uid)
    if station_json and len(station_json):
        station = Station(station_json[0])
        if station:
            station_cache[station.id] = station
        return station
    return None


def get_country_directories():
    country_directories = []
    apicall = 'countries'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    countries_raw = request(apicall)
    for country_raw in countries_raw:
        if get_json_attr(country_raw, 'name') and get_json_attr(country_raw, 'stationcount') and \
                int(get_json_attr(country_raw, 'stationcount')) > MINIMUM_COUNT_COUNTRY:
            country_directories.append(generic.Directory(get_json_attr(country_raw, 'name'),
                                                         get_json_attr(country_raw, 'stationcount')))
    return country_directories


def get_language_directories():
    language_directories = []
    apicall = 'languages'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    languages_raw = request(apicall)
    for language_raw in languages_raw:
        if get_json_attr(language_raw, 'name') and get_json_attr(language_raw, 'stationcount') and \
                int(get_json_attr(language_raw, 'stationcount')) > MINIMUM_COUNT_LANGUAGE:
            language_directories.append(generic.Directory(get_json_attr(language_raw, 'name'),
                                                          get_json_attr(language_raw, 'stationcount'),
                                                          get_json_attr(language_raw, 'name').title()))
    return language_directories


def get_genre_directories():
    genre_directories = []
    apicall = 'tags'
    if not SHOW_BROKEN_STATIONS:
        apicall += '?hidebroken=true'
    genres_raw = request(apicall)
    for genre_raw in genres_raw:
        if get_json_attr(genre_raw, 'name') and get_json_attr(genre_raw, 'stationcount') and \
                int(get_json_attr(genre_raw, 'stationcount')) > MINIMUM_COUNT_GENRE:
            genre_directories.append(generic.Directory(get_json_attr(genre_raw, 'name'),
                                                       get_json_attr(genre_raw, 'stationcount'),
                                                       get_json_attr(genre_raw, 'name').capitalize()))
    return genre_directories


def get_stations_by_country(country):
    stations = []
    # URL-encode the country parameter to handle spaces and special characters
    encoded_country = urllib.parse.quote(str(country))
    stations_json = request('stations/search?order=name&reverse=false&country=' + encoded_country)
    logging.info(f'Radio-Browser API returned {len(stations_json)} stations for country {country}')
    
    filtered_count = 0
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            station_url = get_json_attr(station_json, 'url')
            station_name = get_json_attr(station_json, 'name')
            logging.debug(f'Station: {station_name} - URL: {station_url}')
            
            if station_url and station_url.startswith('http://'):
                stations.append(Station(station_json))
                logging.debug(f'✓ Added HTTP station: {station_name}')
            else:
                filtered_count += 1
                logging.debug(f'✗ Filtered out non-HTTP station: {station_name} - {station_url}')
    
    logging.info(f'Filtered out {filtered_count} non-HTTP stations, returning {len(stations)} HTTP stations')
    return stations


def get_stations_by_language(language):
    stations = []
    # Remove languageExact=true to allow partial matching
    stations_json = request('stations/search?codec=MP3&url=http&order=name&reverse=false&language=' + str(language))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            station_url = get_json_attr(station_json, 'url')
            if station_url and station_url.startswith('http://'):
                stations.append(Station(station_json))
    return stations


def get_stations_by_genre(genre):
    stations = []
    # Convert to lowercase and URL-encode the genre parameter
    encoded_genre = urllib.parse.quote(str(genre).lower())
    stations_json = request('stations/search?order=name&reverse=false&tag=' + encoded_genre)
    logging.info(f'Radio-Browser API returned {len(stations_json)} stations for genre {genre}')
    
    filtered_count = 0
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            station_url = get_json_attr(station_json, 'url')
            station_name = get_json_attr(station_json, 'name')
            logging.debug(f'Station: {station_name} - URL: {station_url}')
            
            if station_url and station_url.startswith('http://'):
                stations.append(Station(station_json))
                logging.debug(f'✓ Added HTTP station: {station_name}')
            else:
                filtered_count += 1
                logging.debug(f'✗ Filtered out non-HTTP station: {station_name} - {station_url}')
    
    logging.info(f'Filtered out {filtered_count} non-HTTP stations, returning {len(stations)} HTTP stations for genre {genre}')
    return stations


def get_stations_by_votes(limit=DEFAULT_STATION_LIMIT):
    stations = []
    stations_json = request('stations/search?codec=MP3&url=http&order=votes&reverse=true&limit=' + str(limit))
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            station_url = get_json_attr(station_json, 'url')
            if station_url and station_url.startswith('http://'):
                stations.append(Station(station_json))
    return stations


def search(name, limit=DEFAULT_STATION_LIMIT):
    stations = []
    # URL-encode the name parameter to handle spaces and special characters
    encoded_name = urllib.parse.quote(str(name))
    stations_json = request('stations/search?order=name&reverse=false&limit=' + str(limit) + '&name=' + encoded_name)
    for station_json in stations_json:
        if SHOW_BROKEN_STATIONS or get_json_attr(station_json, 'lastcheckok') == 1:
            station_url = get_json_attr(station_json, 'url')
            if station_url and station_url.startswith('http://'):
                stations.append(Station(station_json))
    return stations