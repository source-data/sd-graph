from os import getenv
from unittest import TestCase

from neotools.db import Instance, Query


class DbTestCase(TestCase):
    """
    Base class for tests that need to interact with the database.

    Provides a setUp method verifying that the database is empty before each test and a
    tearDown method deleting all nodes in the database after each test.
    A neotools.db.Instance database interface is available as `self.db`.
    """

    class DeleteAll(Query):
        code = "MATCH (n) DETACH DELETE n"

    class NumNodesInDatabase(Query):
        code = "MATCH (n) RETURN COUNT(n) AS N"
        returns = ["N"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Instance(
            getenv("NEO_URI"), getenv("NEO_USERNAME"), getenv("NEO_PASSWORD")
        )

    def setUp(self):
        self.verify_database_empty()

    def tearDown(self):
        self.db.query(self.__class__.DeleteAll())

    def verify_database_empty(self):
        num_nodes_in_database = self.db.query(self.__class__.NumNodesInDatabase())[0][0]
        self.assertEqual(
            0,
            num_nodes_in_database,
            msg="The database must empty before running tests.",
        )
