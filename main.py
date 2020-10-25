import settings

from vk_parser import VkParser
from vk_user import VkUser


def main(FRIEND_ID):
    my_vk = VkUser(settings.MY_ID)
    vk_friend = VkUser(FRIEND_ID)

    vk_parser = VkParser(FRIEND_ID)
    vk_parser.run()

    # Собирает статистику сообщений, передавая её в инстансы VkUser
    for message in vk_parser.all_json_messages:
        if message['from_id'] == FRIEND_ID:
            vk_friend.collect_statistics(message)
        else:
            my_vk.collect_statistics(message)


if __name__ == '__main__':
    FRIEND_ID = 123
    main(FRIEND_ID)
