import psycopg2
from random import randrange
import vk_api
import datetime
from vk_api.longpoll import VkLongPoll, VkEventType
from token_2 import token_group, access_token, V
from database import insert_data_seen_users, check_user, create_table_seen_users
from vk_api.exceptions import ApiError

vk_session = vk_api.VkApi(token=token_group)
session_api = vk_session.get_api()
longpoll = VkLongPoll(vk_session)

ALIASE = {'city': 'город',
          'sex': 'пол партнёра',
          'bdate': 'свой возраст'
          }


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

    params = {'access_token': access_token,
              'v': V,
              'owner_id': owner_id,
              'album_id': 'profile',
              'count': 10,
              'extended': 1}
    result = vk.method('photos.get', params)

    photos = [(item['likes']['count'], f"photo{item['owner_id']}_{item['id']}")
              for item in result['items']]
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
        print(info)
    except ApiError:
        return None

    store = ['city', 'sex', 'bdate']
    out = {}
    for fields, value in info.items():
        if fields in store:
            if fields == 'sex':
                out[fields] = 1 if value == 2 else 2
                store.remove('sex')
            if fields == 'bdate':
                year = datetime.datetime.now().year
                b_year = int(info['bdate'].split('.')[2])
                age_from = year - b_year - 5
                age_to = year - b_year + 5
                out['age_from'] = age_from
                out['age_to'] = age_to
                store.remove('bdate')
            if fields == 'city':
                out['city'] = value['title']
                store.remove('city')

    return out, store


def get_city(input):
    if input.isdigit():
        return None
    else:
        return input.strip()

    pass


def get_sex(input):
    sex = 1
    if input.isdigit():
        return None
    else:
        if input[0].lower() == 'ж':
            sex = 2
    return sex


def get_bdate(input):
    if input.isdigit():
        return (int(input) - 5, int(input) + 5)
    else:
        return None


SWITH = {'city': get_city,
         'sex': get_sex,
         'bdate': get_bdate
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

                    info, fall_filds = get_profile_info(event.user_id)
                    print(info)
                    print(fall_filds)

                    if fall_filds:

                        for filds in fall_filds:
                            good_value = None
                            while good_value is None:
                                write_msg(event.user_id,
                                          f'В вашем профиле недостаточно данных, введите {ALIASE[filds]}')
                                longpoll.update_longpoll_server()
                                for fall_event in longpoll.listen():
                                    if fall_event.type == VkEventType.MESSAGE_NEW and event.to_me:
                                        if fall_event.user_id == vk_id:
                                            fall_value = fall_event.text
                                            good_value = SWITH[filds](fall_value)
                                            break
                            if filds == 'bdate':
                                info['age_from'] = good_value[0]
                                info['age_to'] = good_value[1]
                            else:
                                info[filds] = good_value

                    print(info)

                    result = search_users(info['age_from'],
                                          info['age_to'],
                                          info['sex'],
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



