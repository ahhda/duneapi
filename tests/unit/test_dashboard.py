import json
import unittest

from src.duneapi.api import DuneAPI
from src.duneapi.dashboard import DuneDashboard, DuplicateQueryError
from src.duneapi.types import DashboardTile, DuneQuery


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.user = "TestUser"
        self.dune = DuneAPI(username=self.user, password="")
        self.queries = [
            {
                "id": 1,
                "name": "Example 1",
                "query_file": "./example/dashboard/query1.sql",
                "network": "mainnet",
                "requires": "./example/dashboard/base_query.sql",
            },
            {
                "id": 2,
                "name": "Example 2",
                "query_file": "./example/dashboard/query2.sql",
                "network": "gchain",
            },
        ]
        self.valid_input = json.loads(
            json.dumps(
                {
                    "meta": {
                        "name": "Demo Dashboard",
                        "user": self.user,
                    },
                    "queries": self.queries,
                }
            )
        )

    def test_constructor(self):
        dashboard = DuneDashboard.from_json(self.dune, self.valid_input)
        expected_tiles = [DashboardTile.from_dict(q) for q in self.queries]
        expected_queries = [DuneQuery.from_tile(t) for t in expected_tiles]

        self.assertEqual(dashboard.name, "Demo Dashboard")
        self.assertEqual(dashboard.url, f"https://dune.xyz/{self.user}/Demo-Dashboard")
        self.assertEqual(dashboard.queries, expected_queries)

    def test_user_assertion(self):
        minimal_input = {
            "meta": {
                "name": "Demo Dashboard",
                "user": "WrongUser",
            },
            "queries": [],
        }
        # TODO - figure out how to use self.assertLogs
        with self.assertRaises(ValueError) as err:
            DuneDashboard.from_json(self.dune, minimal_input)
        self.assertEqual(
            str(err.exception),
            f"Attempt to load dashboard queries for invalid user WrongUser != {self.user}.",
        )

    def test_duplicate_query(self):
        query_file = "./tests/queries/test_query.sql"
        minimal_input = {
            "meta": {
                "name": "Demo Dashboard",
                "user": self.user,
            },
            "queries": [
                {
                    "id": 1,
                    "name": "Example 1",
                    "query_file": query_file,
                    "network": "mainnet",
                },
                {
                    "id": 2,
                    "name": "Example 2",
                    "query_file": query_file,
                    "network": "gchain",
                },
            ],
        }

        with self.assertRaises(DuplicateQueryError) as err:
            DuneDashboard.from_json(self.dune, minimal_input)
        self.assertEqual(
            str(err.exception), "[\"select 10 - '{{IntParameter}}' as value\"]"
        )


if __name__ == "__main__":
    unittest.main()