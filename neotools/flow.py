"""Utilities for building the db deployment pipeline."""

from time import perf_counter
from common.logging import get_logger
from neotools import FLOW_BATCH_SIZE

Logger = get_logger(__name__)


def run_flow(db, tasks, description):
    """
    Run the given list of tasks that each run queries against the given database.

    Each task must have a `run_task()` method that accepts a database session as parameter.
    """
    with db._driver.session() as session:
        Logger.info('Running flow "%s" with %s tasks', description, len(tasks))
        start = perf_counter()
        for task in tasks:
            task.run_task(session)
        end = perf_counter()
        delta = end - start
        Logger.info('Flow "%s" took %.2f s', description, delta)


class DbTask:
    """
    Base class for tasks that run queries against the database.

    Subclasses must implement the `_run()` method that runs the actual queries.
    That method is called with a database transaction as parameter. Transaction commits are handled by this class.
    """

    def __init__(self, description):
        self.logger = Logger
        self.description = description

    def run_query_with_single_result(self, tx, query):
        """Run the given query and return the single result record."""
        self.logger.debug("Query: %s", query)
        result = tx.run(query)
        record = result.single()
        self.logger.debug("Result: %s", str(record))
        return record

    def run_task(self, db_session):
        """Runs the task in a new transaction within the given database session."""
        self.logger.info('Running task "%s"', self.description)
        start = perf_counter()
        with db_session.begin_transaction() as tx:
            self._run(tx)
            tx.commit()
        end = perf_counter()
        delta = end - start
        Logger.info('Task "%s" took %.2f s', self.description, delta)

    def _run(self, _):
        raise NotImplementedError("Subclasses must implement this method")


class SimpleDbTask(DbTask):
    """DbTask that runs a database query."""

    def __init__(self, description, query):
        super().__init__(description)
        self.query = query

    def _run(self, tx):
        self.run_query_with_single_result(tx, self.query)


class UpdateOrCreateTask(DbTask):
    """
    DbTask that runs a database query to update or create nodes and relationships.

    To limit memory consumption, the query is run in batches using the APOC library's apoc.periodic.iterate() function.
    To run a query like `MATCH (n) DETACH DELETE n`, pass the __init__ function a description of the task, an iterate query of the form `MATCH (n) RETURN n`, and an action query of the form `DETACH DELETE n`.
    The action query is then run in batches of 10000 nodes as returned by the iterate query.
    """

    default_batch_size = 10000  # Default batch size for APOC periodic iterate

    def __init__(self, description, iterate_query, action_query):
        super().__init__(description)
        self.iterate_query = iterate_query
        self.action_query = action_query

        try:
            batch_size = int(FLOW_BATCH_SIZE)
        except ValueError:
            self.logger.warning(
                "Provided FLOW_BATCH_SIZE '%s' is not an integer, using default value of %d",
                FLOW_BATCH_SIZE,
                self.default_batch_size,
            )
            batch_size = self.default_batch_size

        self.apoc_params = f"{{batchSize: {batch_size}}}"

    def _run(self, tx):
        self.logger.debug("Running update/create query")
        apoc_query = f'CALL apoc.periodic.iterate("{self.iterate_query}", "{self.action_query}", {self.apoc_params})'
        self.run_query_with_single_result(tx, apoc_query)


class DetachDeleteAll(UpdateOrCreateTask):
    def __init__(self, type):
        match_query = f"MATCH (n:{type}) RETURN n"
        super().__init__(
            f"Detach-Delete all {type}",
            f"{match_query}",
            f"DETACH DELETE n",
        )


class UpdateAttrIfNull(UpdateOrCreateTask):
    def __init__(self, type, attr):
        super().__init__(
            f"Replace NULL {type}.{attr} with empty string",
            f"MATCH (n:{type}) WHERE n.{attr} IS NULL RETURN n",
            f"SET n.{attr} = ''",
        )


class VerifyTask(DbTask):
    """
    DB task that runs a query to verify that the results are as expected.

    The expected result can be a value or a function that returns a value.
    To e.g. verify that all nodes without a certain attribute have been deleted, pass the __init__ function a description of the task, a query like `MATCH (n) WHERE n.prop IS NULL RETURN n`, and an expected result of 0.
    """

    def __init__(self, description, verify_query, expected_result, raise_error=False):
        super().__init__(description)
        self.verify_query = verify_query
        self.expected_result = expected_result
        self.raise_error = raise_error

    def _run(self, tx):
        self.logger.debug("Running query to verify results")
        verify_result = self.run_query_with_single_result(tx, self.verify_query)[0]

        try:
            expected_result = self.expected_result()
        except TypeError:
            expected_result = self.expected_result
        self.logger.debug("Expected: %s", expected_result)

        if not verify_result == self.expected_result:
            message = f'Task "{self.description}" failed to verify: {verify_result} != {self.expected_result}'
            if self.raise_error:
                raise Exception(message)
            else:
                self.logger.error(message)
