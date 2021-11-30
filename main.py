import requests
import json
import datetime
from time import sleep
from tqdm import tqdm


def time_convert(time_unix):
    time_bc = datetime.datetime.fromtimestamp(time_unix)
    str_time = time_bc.strftime('%Y-%m-%d time %H-%M-%S')
    return str_time

def get_id(token_vk, id):  #Функция получения ID_VK человек
    GET_URL_API_VK = 'https://api.vk.com/method/users.get'  # Получить ID
    if type(id) == int:
        return id
    elif type(id) == str:
        params_1 = {
            'user_ids': id,   #'begemot_korovin',
            'access_token': token_vk,
            'v': '5.131'
        }
        id_get = requests.get(GET_URL_API_VK, params=params_1)
        id_json = id_get.json()
        id_vk = id_json['response'][0]['id']
        return id_vk


class VK: #Получить ВК_ID человека, запись данных в json файл
    def __init__(self, token: str, id_vk):
        self.token_vk = token
        self.url_photo_api_vk = 'https://api.vk.com/method/photos.get'
        self.id_vk = id_vk
        self.params_korovin = {
            'owner_id': self.id_vk,              #552934290,
            'album_id': 'profile',
            'access_token': self.token_vk,
            'v': '5.131',
            'extended': '1'
        }
        self.photo_dict = {}


    def get_photo(self):
        all_photo_vk = requests.get(self.url_photo_api_vk, params=self.params_korovin)  # Получить все фотографии из ВК
        all_photo_vk_json = all_photo_vk.json()  # Преобразовать в джейсон

        for i in all_photo_vk_json['response']['items']:  # Получаем фото с максимальными парам и лайками.
            likes_photo = i['likes']['count']
            sizes = i['sizes'][-1]['type']
            url = i['sizes'][-1]['url']
            date_1 = time_convert(i['date'])
            if likes_photo in self.photo_dict:
                likes_photo = f'{likes_photo}_{date_1}'
            self.photo_dict[likes_photo] = [sizes, url]
        return self.photo_dict


    def save_json(self): #Создаём json файл
        with open("save_json.json", 'w', encoding='utf-8') as f:
            output = {self.params_korovin['owner_id']: self.photo_dict}
            json.dump(output, f)


class YA: #Загрузка фото на я.диск
    def __init__(self, token: str, get_photo):
        self.token_ya = token
        self.photo_dict = get_photo  #Из класса ВК получаем список данны
        self.pbar_photo_dictt = tqdm(self.photo_dict)
        self.headers = {
                "Accept": "application/json",
                "Authorization": f"OAuth {self.token_ya}"
            }  # Получить авторизацию
        self.file_name = 'Михаил Афанасьевич'
        self.params = {
                'path': self.file_name
        }
        self.url_file_name = f"https://cloud-api.yandex.net/v1/disk/resources?path=disk%3A%2F{self.file_name}"


    def photo_upload(self): #Загрузка фото на я.диск
        if requests.get(self.url_file_name, headers=self.headers, params=self.params).status_code != 200:
            requests.put(self.url_file_name, headers=self.headers, params=self.params)
            print(f'\nПапка {self.file_name} успешно создана в корневом каталоге Яндекс диска\n')
        else:
            print(f'\nПапка {self.file_name} уже существует. \n')

        for photo in self.pbar_photo_dictt:
            self.params = {
                'path': f'{self.file_name}/{photo}',
                'url': self.photo_dict[photo][1]
            }
            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            r = requests.post(url=url, params=self.params, headers=self.headers) #Отправить файл...
            #res = r.json()
            # print(r.status_code)
            if r.status_code == 202:
                print('Успешно')
            else:
                print('Ошибка')
            self.pbar_photo_dictt.set_description("Processing")
            sleep(1)


if __name__ == '__main__':
    token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
    token_ya = "AQAAAAAWGc4EAADLW2yBrRRXYEaXl075mlGOGIA"
    get_id_vk = get_id(token_vk, 552934290)  #Получить id вк, можно как id так и username
    vk = VK(token_vk, get_id_vk)
    vk_get_photo = vk.get_photo()
    vk.save_json()
    ya = YA(token_ya, vk_get_photo)
    ya.photo_upload()

