import settings

from vk_parser import VkParser
from vk_user import VkUser


def main(FRIEND_ID):
    my_vk = VkUser(settings.MY_VK_ID)
    vk_friend = VkUser(FRIEND_ID)
    vk_parser = VkParser(FRIEND_ID)
    vk_parser.run()
    # Передаёт каждое сообщение в конкретный инстанс VkUser, собирая статистику
    for message in vk_parser.all_json_messages:
        if message['from_id'] == FRIEND_ID:
            vk_friend.collect_statistics(message)
        else:
            my_vk.collect_statistics(message)

    # Раскомментируй необходимый код
    # vk_friend.print_statistics_to_console()
    # vk_friend.print_most_popular_words(15)
    # vk_friend.write_statistics_to_files()
    # my_vk.print_statistics_to_console()
    # my_vk.print_most_popular_words(20)
    # my_vk.write_statistics_to_files()


if __name__ == '__main__':
    FRIEND_ID = 123  # int
    main(FRIEND_ID)
