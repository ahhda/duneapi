import unittest

from tests.db.pg_client import connect


class TestMockDB(unittest.TestCase):
    def test_db_connect(self):
        db_conn = connect()
        cur = db_conn.cursor()

        table = """
        CREATE TABLE student(
            id SERIAL PRIMARY KEY, 
            firstName VARCHAR(40) NOT NULL, 
            lastName VARCHAR(40) NOT NULL, 
            age INT, 
            address VARCHAR(80), 
            email VARCHAR(40)
        )
        """
        values = [
            "Mona the",
            "Octocat",
            9,
            "88 Colin P Kelly Jr St, San Francisco, CA 94107, United States",
            "octocat@github.com",
        ]

        text = """
        INSERT INTO student(firstname, lastname, age, address, email) 
        VALUES(%s, %s, %s, %s, %s) RETURNING *
        """.format(
            values
        )

        cur.execute(table)
        cur.execute(text, values)
        cur.execute("SELECT * FROM student")
        x = cur.fetchall()
        self.assertEqual(1, len(x))


if __name__ == "__main__":
    unittest.main()
