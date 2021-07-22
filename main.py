from vk_parser import VkParser


def main(friend_id):
    vk_parser = VkParser(friend_id)
    vk_parser.run()


if __name__ == '__main__':
    friend_id = 1  # int or str (1 or 'durov')
    main(friend_id)
