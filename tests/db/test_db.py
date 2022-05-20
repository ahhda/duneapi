import csv
import os
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
            "Ben",
            "Smith",
            37,
            "Berlin, Germany",
            "bh2smith@gmail.com",
        ]

        insert = """
            INSERT INTO student(firstname, lastname, age, address, email) 
            VALUES(%s, %s, %s, %s, %s) RETURNING *
        """.format(
            values
        )

        cur.execute(table)
        cur.execute(insert, values)
        # Its weird the way values is used twice here!

        cur.execute("SELECT * FROM student")
        x = cur.fetchall()
        self.assertEqual(1, len(x))

    def test_db_connect(self):
        db_conn = connect()
        cur = db_conn.cursor()

        with open("tests/build_schema.sql", "r", encoding="utf-8") as file:
            populate_query = file.read()

        cur.execute(populate_query)

        data_dir = "tests/data"
        for filename in os.listdir(data_dir):
            schema, table_name = filename.replace(".csv", "").split(".")
            table = f'{schema}."{table_name}"'

            with open(os.path.join(data_dir, filename), "r") as dat_file:
                reader = dat_file.readlines()
                fields = reader[0]
                values = []
                for row in reader[1:]:
                    row_string = ",".join([f"'{str(item)}'" if item else None for item in row.split(",")])
                    values.append(f"({row_string})")

                insert_query = (
                    f"INSERT INTO {table} ({fields}) VALUES {','.join(values[:5])};"
                )
            print("Inserting data", insert_query)
            cur.execute(insert_query)

        cur.execute("SELECT * FROM erc20.tokens;")
        x = cur.fetchall()
        self.assertEqual(5, len(x))
        print(x)
        self.assertEqual(1, 0)


if __name__ == "__main__":
    unittest.main()
