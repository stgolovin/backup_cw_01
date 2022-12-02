import json
import os

import requests
from tqdm import tqdm


class Vk():

    def __init__(self, access_token, user_id, version='5.131'):
        self.token = access_token
        self.id = user_id
        self.version = version
        self.params = {'access_token': self.token, 'v': self.version}

    def users_info(self):
        url = 'https://api.vk.com/method/photos.get'
        params = {'users_id': self.id, 'album_id': 'profile', 'extended': 1}
        vk_response = requests.get(url, params={**self.params, **params})
        self.get_photo_names(vk_response.json())

    def get_photo_names(self, vk_response: dict):
        photo_dict = dict()
        photos_info = dict()
        max_size = 0
        photos_report = list()
        if not os.path.exists('images_vk'):
            os.mkdir('images_vk')
        for photo in tqdm(vk_response['response']['items'], desc='Перебираем фото'):
            for size in photo['sizes']:
                if size['height'] >= max_size:
                    max_size = size['height']
            if photo['likes']['count'] not in photo_dict.keys():
                photo_dict[photo['likes']['count']] = size['url']
                photos_info['file_name'] = f"{photo['likes']['count']}.jpg"
            else:
                photo_dict[f"{photo['likes']['count']}_{photo['date']}"] = size['url']
                photos_info['file_name'] = f"{photo['likes']['count']}+{photo['date']}.jpg"
            photos_info['size'] = size['type']
            photos_report.append(photos_info)
        for photo_name, photo_url in tqdm(photo_dict.items(), desc='Загружаем фото на локальный диск'):
            with open('images_vk/%s' % f'{photo_name}.jpg', 'wb') as file:
                img = requests.get(photo_url)
                file.write(img.content)
        with open('photos_report.json', 'w') as file:
            json.dump(photos_report, file, indent=4)
        print(f'На локальный диск загружено: {len(photos_report)} фотографий.')


class YaDisk:

    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def get_params(self):
        return {
            "path": f'{folder_name}/{filename}',
            "overwrite": "true"
        }

    def get_files_list(self):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        headers = self.get_headers()
        response = requests.get(files_url, headers=headers)
        return response.json()

    def create_folder(self):
        url = f'https://cloud-api.yandex.net/v1/disk/resources/'
        headers = self.get_headers()
        params = {'path': f'{folder_name}',
                  'overwrite': 'false'}
        try:
            response = requests.put(url=url, headers=headers, params=params)
            print(f'Папка "{folder_name}" создана.')
        except:
            print(f'Папку "{folder_name}" не удалось создать.')

    def _get_upload_link(self, path_to_file):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = self.get_params()
        response = requests.get(url=upload_url, headers=headers, params=params)
        return response.json()

    def upload_file_to_disk(self, path_to_file, filename):
        # href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")
        href = self._get_upload_link(path_to_file=path_to_file).get('href')
        response = requests.put(href, data=open(path_to_file, 'rb'))


# access_token = open('vk_token.txt').read()
access_token = input('Введите токен ВК:   ')
# user_id = '51476467'
user_id = int(input('Введите ID пользователя ВК:   '))
vk = Vk(access_token, user_id)

# ya_token = open('ya_token.txt').read()
ya_token = input('Введите токен Яндекс.Диск:   ')
uploader = YaDisk(ya_token)
folder_name = str(input('Введите имя папки на Яндекс диске, в которую необходимо сохранить фото:   =>'))

if __name__ == '__main__':
    vk.users_info()
    uploader.create_folder()
    photos_list = os.listdir('images_vk')
    count = 0
    count_limit = int(input("Сколько фотографий необходимо загрузить на Я.Диск?   =>"))
    for photo in tqdm(photos_list, desc='Загружаем фото на Я.Диск'):
        if count == count_limit:
            break
        else:
            filename = photo
            path_to_file = os.getcwd() + '/images_vk/' + photo
            uploader.upload_file_to_disk(path_to_file, filename)
            count += 1
            print(f'Загружено {count} фотографий.')
