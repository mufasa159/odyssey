import sqlite3


def main():
    conn = sqlite3.connect('database/odyssey.db')
    conn.row_factory = sqlite3.Row

    with open('database/seed.sql') as f:
        sql = f.read()
        conn.executescript(sql)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
