import requests
import json
from time import sleep
from tqdm import tqdm

# GET_URL_API_VK = 'https://api.vk.com/method/users.get' #Получить ID
# params = {
#     'user_ids': 'begemot_korovin',
#     'access_token': token_vk,
#     'v': '5.131'
# }

class VK: #Получить ВК_ID человека, запись данных в json файл
    def __init__(self, token: str):
        self.token_vk = token
        self.url_photo_api_vk = 'https://api.vk.com/method/photos.get'
        self.params_korovin = {
            'owner_id': 552934290,
            'album_id': 'profile',
            'access_token': self.token_vk,
            'v': '5.131',
            'extended': '1'
        }

    def get_photo(self):
        self.all_photo_vk = requests.get(self.url_photo_api_vk, params=self.params_korovin) #Получить ID
        self.all_photo_vk_json = self.all_photo_vk.json() #Получить ID json
        self.photo_korovin = []
        self.photo_dict = {}
        self.photo_korovin_id = []
        for i in self.all_photo_vk_json['response']['items']: #Получаем фото с максимальными парам и лайками.
            id = i['id']
            likes_photo = i['likes']['count']
            sizes = i['sizes'][-1]['type']
            url = i['sizes'][-1]['url']
            date_1 = i['date']
            likes_date = f'{likes_photo}_{date_1}'
            self.photo_korovin_id.append(id)
            self.photo_korovin.append([likes_date, sizes, url])
            self.photo_dict[likes_date] = [sizes, url]
        return self.photo_dict

    def save_json(self): #Создаём json файл
        with open("save_json.json", 'w', encoding='utf-8') as f:
            output = {self.params_korovin['owner_id']: self.photo_dict}
            json.dump(output, f)

class YA: #Загрузка фото на я.диск
    def __init__(self, token: str, get_photo):
        self.token_ya = token
        self.photo_dict = get_photo #Из класса ВК получаем список данных

    def photo_upload(self): #Загрузка фото на я.диск
        self.pbar_photo_dict = tqdm(self.photo_dict)
        for photo in (self.pbar_photo_dict):
            headers = {
                "Accept": "application/json",
                "Authorization": f"OAuth {self.token_ya}"
            }  # Получить авторизацию

            params = {
                'path': f'net/{photo}',
                'url': self.photo_dict[photo][1]
            }

            url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            r = requests.post(url=url, params=params, headers=headers) #Отправить файл...
            #res = r.json()
            # print(r.status_code)
            if r.status_code == 202:
                print('Успешно')
            else:
                print('Ошибка')

            self.pbar_photo_dict.set_description("Processing")
            sleep(1)


if __name__ == '__main__':
    token_vk = '008'
    token_ya = "GOGIA"
    vk = VK(token_vk)
    vk_get_photo = vk.get_photo()
    vk.save_json()
    ya = YA(token_ya, vk_get_photo)
    ya.photo_upload()

