from django.http import HttpResponse
from django.views.generic import TemplateView
import requests
from django.shortcuts import render

_URL_API = 'https://rickandmortyapi.com/api/'
_EPISODE_URL = _URL_API + 'episode/'
_CHARACTER_URL = _URL_API + 'character/'
_LOCATION_URL = _URL_API + 'location/'


def index(request):
    # SOURCE: https://docs.djangoproject.com/en/3.0/intro/tutorial03/
    try:
        response = requests.get(_EPISODE_URL).json()
    except:
        return HttpResponse("Lo sentimos, tuvimos problemas conectandonos a la API! No pudimos encontrar los episodios!")

    if response:
        episodes = []
        results = response['results']

        # Agregando los resultados para render
        for epi in results:
            _dic_aux = {}
            _dic_aux['id'] = epi['id']
            _dic_aux['name'] = epi['name']
            _dic_aux['air_date'] = epi['air_date']
            _dic_aux['episode'] = epi['episode']
            episodes.append(_dic_aux)

        # caso de que sean mas pages... hacer otro request
        while True:
            _next_url = response['info']['next']
            if _next_url == "":
                break
            else:
                response = requests.get(_next_url).json()
                if response:
                    results = response['results']
                    for epi in results:
                        _dic_aux = {}
                        _dic_aux['id'] = epi['id']
                        _dic_aux['name'] = epi['name']
                        _dic_aux['air_date'] = epi['air_date']
                        _dic_aux['episode'] = epi['episode']
                        episodes.append(_dic_aux)
                else: pass

            return render(request, 'index.html', {'episodes': episodes})


def episode(request, episode_id):
    try:
        response = requests.get(_EPISODE_URL + str(episode_id)).json()
    except:
            return HttpResponse("Lo sentimos, problemas conectandose a la API")

    try: 
        response['error'] == 'Episode not found'
        return HttpResponse("Lo sentimos, Episodio no encontrado en la API")

    except:
        # personajes
        urls_characters = response['characters']
        characters_ids = ""
        
        for ur in urls_characters:
            characters_ids += str(ur.rsplit('/', 1)[-1])
            characters_ids += ','
        characters_ids = characters_ids[:-1]

        if len(urls_characters) > 1:
            response_char=requests.get(_CHARACTER_URL + characters_ids).json()
            if response_char:
                characters=[]

                # Agregando los resultados para render
                for char in response_char:
                    _dic_aux={}
                    _dic_aux['id'] = char['id']
                    _dic_aux['name'] = char['name']
                    characters.append(_dic_aux)

        elif len(urls_characters) == 1:
            response_char = requests.get(_CHARACTER_URL + characters_ids).json()
            characters = [{'id': response_char['id'],
                         'name': response_char['name']}]

        else:
            characters = [{'id': "",
                         'name': ""}]

        return render(request, 'episode.html', 
            {'name': response['name'],
            'id': response['id'],
            'air_date': response['air_date'],
            'episode': response['episode'],
            'characters': characters})


def character(request, character_id):
    try:
        response = requests.get(_CHARACTER_URL + str(character_id)).json()
    except:
        return HttpResponse("Lo sentimos, problemas conectandose a la API")

    try: 
        response['error'] == "Character not found"
        return HttpResponse("Lo sentimos, Personaje no encontrado en la API")
    except:

        # Get episodios
        urls_episodes = response['episode']
        episodes_ids = ""

        for ur in urls_episodes:
            episodes_ids += str(ur.rsplit('/', 1)[-1])
            episodes_ids += ','
        episodes_ids = episodes_ids[:-1]

        if len(urls_episodes) > 1:
            response_epi = requests.get(_EPISODE_URL + episodes_ids).json()
            if response_epi:
                episodes = []

                # Agregando los resultados para render
                for epi in response_epi:
                    _dic_aux = {}
                    _dic_aux['id'] = epi['id']
                    _dic_aux['name'] = epi['name']
                    episodes.append(_dic_aux)

        elif len(urls_episodes) == 1:
            response_epi = requests.get(_EPISODE_URL + episodes_ids).json()
            episodes = [{'id': response_epi['id'], 
            'name': response_epi['name']}]

        else:
            episodes = [{'id': "", 
            'name': ""}]

        # origin
        origin = {
            'id' : str(response['origin']['url'].rsplit('/', 1)[-1]),
            'name' : response['origin']['name']
        }

        #location
        location = {
            'id': str(response['location']['url'].rsplit('/', 1)[-1]),
            'name': response['location']['name']
        }
        return render(request, 'character.html',
                    {
                        'id': response['id'],
                        'name': response['name'],
                        'status': response['status'],
                        'species': response['species'],
                        'type': response['type'],
                        'gender': response['gender'],
                        'image': response['image'],
                        'episodes': episodes,
                        'origin': origin,
                        'location': location
                        }
                    )
        



def location(request, location_id):

    try:
        response = requests.get(_LOCATION_URL + str(location_id)).json()
    except:
        return HttpResponse("Lo sentimos, problemas conectandose a la API")

    try:
        response['error'] == "Location not found"
        return HttpResponse("Lo sentimos, Lugar no encontrado en la API")
    except:

        # Get residentes
        urls_residents = response['residents']
        residents_ids = ""

        for ur in urls_residents:
            residents_ids += str(ur.rsplit('/', 1)[-1])
            residents_ids += ','
        residents_ids = residents_ids[:-1]

        if len(urls_residents) > 1:
            response_char = requests.get(_CHARACTER_URL + residents_ids).json()
            if response_char:
                characters = []

                # Agregando los resultados para render
                for char in response_char:
                    _dic_aux = {}
                    if char['id'] != "":
                        _dic_aux['id'] = char['id']
                    else:
                        _dic_aux['id'] = "No id"

                    if char['name'] != "":
                        _dic_aux['name'] = char['name']
                    else:
                        _dic_aux['name'] = "No Name"

                    characters.append(_dic_aux)

        elif len(urls_residents) == 1:
            response_char=requests.get(_CHARACTER_URL + residents_ids).json()
            characters = [{'id': response_char['id'], 'name': response_char['name']}]

        else:
            characters=[{'id': "",
                         'name': ""}]

        return render(request, 'location.html',
                      {
                          'id': response['id'],
                          'name': response['name'],
                          'type': response['type'],
                          'dimension': response['dimension'],
                          'characters': characters
   
                      }
                      )


def search(request):
    '''
    SOURCE : https: // stackoverflow.com/questions/54678389/search-bar-in-django
    SOURCE : https: // stackoverflow.com/questions/17716624/django-csrf-cookie-not-set
    SOURCE : https://docs.djangoproject.com/en/3.0/ref/request-response/
    '''
    search_url = '?name='
    search_term = request.POST.get('search', '')

    # episodes
    string = _EPISODE_URL + '?name=' + search_term
    response = requests.get(string).json()
    try:
        episodes_results = response['results']

        episodes = []
        if len(episodes_results) > 0:
            # Agregando los resultados para render
            for epi in episodes_results:
                _dic_aux = {}
                _dic_aux['id'] = epi['id']
                _dic_aux['name'] = epi['name']
                episodes.append(_dic_aux)
            
            # caso de que sean mas pages... hacer otro request
            while True:
                _next_url = response['info']['next']

                if _next_url == "":
                    break
                else:
                    response = requests.get(_next_url).json()
                    if response:
                        results = response['results']
                        for epi in results:
                            _dic_aux = {}
                            _dic_aux['id'] = epi['id']
                            _dic_aux['name'] = epi['name']
                            episodes.append(_dic_aux)
                    else:
                        pass
        else:
            episodes = [{'id': "",
                        'name': ""}]
    except:
        episodes = [{'id': "",
                     'name': ""}]



    # characters
    string = _CHARACTER_URL + '?name=' + search_term
    response = requests.get(string).json()
    try:
        character_results = response['results']
        characters = []
        if len(character_results) > 0:

            # Agregando los resultados para render
            for char in character_results:
                _dic_aux = {}
                _dic_aux['id'] = char['id']
                _dic_aux['name'] = char['name']
                characters.append(_dic_aux)
            
            # caso de que sean mas pages... hacer otro request
            while True:
                _next_url = response['info']['next']

                if _next_url == "":
                    break
                else:
                    response = requests.get(_next_url).json()
                    if response:
                        results = response['results']
                        for epi in results:
                            _dic_aux = {}
                            _dic_aux['id'] = epi['id']
                            _dic_aux['name'] = epi['name']
                            characters.append(_dic_aux)
                    else:
                        pass
        else:
            characters = [{'id': "",
                        'name': ""}]
    except:
        characters = [{'id': "",
                       'name': ""}]

    # lugares
    string = _LOCATION_URL + '?name=' + search_term
    response = requests.get(string).json()
    try:
        location_results = response['results']
        locations = []
        if len(location_results) > 0:

            # Agregando los resultados para render
            for char in location_results:
                _dic_aux = {}
                _dic_aux['id'] = char['id']
                _dic_aux['name'] = char['name']
                locations.append(_dic_aux)

            # caso de que sean mas pages... hacer otro request
            while True:
                _next_url = response['info']['next']

                if _next_url == "":
                    break
                else:
                    response = requests.get(_next_url).json()
                    if response:
                        results = response['results']
                        for epi in results:
                            _dic_aux = {}
                            _dic_aux['id'] = epi['id']
                            _dic_aux['name'] = epi['name']
                            locations.append(_dic_aux)
                    else:
                        pass
        else:
            locations = [{'id': "",
                           'name': ""}]
    except:
        locations = [{'id': "",
                       'name': ""}]
    return render(request, 'search.html',
                      {'episodes': episodes,
                      'characters': characters,
                      'locations': locations})
