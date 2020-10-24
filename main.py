import settings

from vk_parser import VkParser
from vk_user import VkUser

if __name__ == '__main__':
    friend_id = 183145350
    my_vk = VkUser(settings.my_id)
    vk_friend = VkUser(friend_id)

    vk_parser = VkParser(friend_id)
    vk_parser.run()
    for message in vk_parser.all_json_messages:
        if message['from_id'] == friend_id:
            vk_friend.collect_statistics(message)
        else:
            my_vk.collect_statistics(message)
