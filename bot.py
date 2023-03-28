import psycopg2
from random import randrange
import vk_api
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from token_2 import token_group , access_token, V
from database import insert_data_seen_users, check_user, create_db, create_table_seen_users

vk_session = vk_api.VkApi(token = token_group)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

def write_msg(user_id, message):
    vk_session.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })

def paste_foto(user_id, attachment):
    vk_session.method('messages.send', {'user_id':user_id, 'attachment':attachment, 'random_id':randrange(10 ** 7),})

def search_users(age_from, age_to, sex, city, status):
    all_persons = []
    link_profile = 'https://vk.com/id'
    vk = vk_api.VkApi(token=access_token)
    response = vk.method('users.search',
                          {'age_from': age_from,
                           'age_to': age_to,
                          'sex': sex,
                          'hometown': city,
                          'status': status,
                          'count': 100,
                           })
    try:
        response = response['items']
    except KeyError:
        return None

    for element in response:
        if element['is_closed'] == False:
            all_persons.append({'first_name': element['first_name'],
                                'last_name': element['last_name'],
                                'id': element['id']
                                }
                            )
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


def get_profile_info(user_id):
    vk = vk_api.VkApi(token=access_token)
    try:
        info, = vk.method('users.get',
                          {'user_id': user_id,
                           'fields': 'bdate,sex,city'
                           }
                          )
    except ApiError:
        return None

    year = datetime.datetime.now().year
    
    if 'bdate' not in info:
       write_msg(user_id, 'Введите Ваш возраст')

    else:
        b_year = int(info['bdate'].split('.')[2])
        age_from = year - b_year - 5
        age_to = year - b_year + 5

    if 'city' in info:
        city = info['city']['title']
    else:
        write_msg(event.user_id, 'введите город')
        return None

    return {'id': info['id'],
            'city': city,
            'age_from': age_from,
            'age_to': age_to,
            'sex': info['sex']
            }


if __name__ == '__main__':
    connections = psycopg2.connect(database='database_db', user='postgres', password='lkjh9874')
    create_table_seen_users(connections)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            vk_id = event.user_id

            if event.to_me:
                request = event.text

                if request == 'привет':
                    write_msg(event.user_id, 'Привет! Хочешь найти себе пару?')

                elif request == 'да':

                    write_msg(event.user_id, 'Начинаю поиск...')

                    info = get_profile_info(event.user_id)
                  
                    result = search_users(info['age_from'],
                                      info['age_to'],
                                      1 if info['sex'] == 2 else 2,
                                      info['city'],
                                      6)

                    if result:
                        user = result.pop()
                    else:
                        write_msg(event.user_id, 'У нас проблемы, пользователи не найдены, попробуйте позже')

                        try:
                            if not check_user(vk_id, connections):
                                # добавляем пользователя в базу данных
                                insert_data_seen_users(vk_id, connections)
                        except psycopg2.errors.UniqueViolation:
                            continue

                    photos = ','.join(get_photos(user['id']))

                    write_msg(event.user_id,
                              f"{user['first_name']} {user['last_name']} \n https://vk.com/id{user['id']}")
                    paste_foto(event.user_id, photos)

                elif request == 'дальше':
                    if result:
                        user = result.pop()
                    else:
                        result = search_users(25, 30, sex, city, status)
                        user = result.pop()

                    photos = ','.join(get_photos(user['id']))
                    write_msg(event.user_id,
                              f"{user['first_name']} {user['last_name']} \n https://vk.com/id{user['id']}")
                    paste_foto(event.user_id, photos)

                elif request == 'пока':
                    write_msg(event.user_id, 'Пока((')

                else:
                    write_msg(event.user_id, 'Не понял вашего ответа')



