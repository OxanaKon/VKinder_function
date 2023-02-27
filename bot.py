from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from token_2 import token_group , access_token, V

# from database import create_table_seen_users, insert_data_seen_users


vk_session = vk_api.VkApi(token = token_group)
session_api = vk_session.get_api()

longpoll = VkLongPoll(vk_session)



def write_msg(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


def paste_foto(user_id, attachment):
    vk_session.method('messages.send', {'user_id':user_id, 'attachment':attachment, 'random_id':randrange(10 ** 7),})


def search_users(birth_year, sex, hometown, status):
    all_persons = []
    link_profile = 'https://vk.com/id'
    vk = vk_api.VkApi(token=access_token)
    response = vk.method('users.get',
                          {'birth_year': birth_year,
                          'sex': sex,
                          'hometown': hometown,
                          'status': status,
                          'count': 10,
                          'sort': 1,
                          'online': 1,
                           })
    for element in response['items']:
        person = [
            element['first_name'],
            element['last_name'],
            link_profile + str(element['id']),
            element['id']
        ]
        all_persons.append(person)
    return all_persons


# Ищем фото
def get_photos(owner_id):
    vk = vk_api.VkApi(token=access_token)

    params = {    'access_token': access_token,
                  'v': V,
                  'owner_id': owner_id,
                  'album_id': 'profile',
                  'count': 10,
                  'extended': 1}

    result = vk.method('photos.get', params)

    photos = [(item['likes']['count'], f"photo{item['owner_id']}_{item['id']}")
              for item in result ['items']]
    photos = sorted(photos)
    photos = [item[1] for item in photos][:3]
    return photos


def find_user(birth_year, sex, hometown, status):
    vk = vk_api.VkApi(token=access_token)

    params = {'birth_year': birth_year,
              'sex': sex,
              'hometown': hometown,
              'status': status,
              'count': 10,

              }

    result = vk.method('users.search', params)
    return result


if __name__ == '__main__':
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text


                if request == 'привет':
                    write_msg(event.user_id, 'Привет! Хочешь найти себе пару?')

                elif request == 'да':

                    write_msg(event.user_id, 'Начинаю поиск...')

                    result = find_user(1990, 1, 'Москва', 6)


                    for user in result['items']:
                       if user['is_closed'] == True:
                            continue



                       photos = get_photos(user['id'])


                       write_msg(event.user_id,
                                      f"{user['first_name']} {user['last_name']} \n https://vk.com/id{user['id']}")
                       paste_foto(event.user_id, photos)


                elif request == 'пока':
                    write_msg(event.user_id, 'Пока((')


                else:
                    write_msg(event.user_id, 'Не понял вашего ответа')

