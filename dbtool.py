from database import Database


def main():
    db = Database('user.db')
    print('nickname\t\tpassword')
    for nickname, password in db.dump():
        print('{}\t\t{}'.format(nickname, password))


if __name__ == '__main__':
    main()
    input('Press Enter to exit...')
