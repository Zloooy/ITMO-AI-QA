import ydb
import os
from datetime import datetime

# YDB connection details from environment variables
ENDPOINT = os.getenv("YDB_ENDPOINT")
DATABASE = os.getenv("YDB_DATABASE")
SERVICE_ACCOUNT_KEY_FILE = os.getenv("YDB_SERVICE_ACCOUNT_KEY_FILE")

# Table name for articles
TABLE_NAME = "itmo_articles"


class YDBAdapter:
    def __init__(self):
        self.driver = None
        self.pool = None
        self._initialize_driver()

    def _initialize_driver(self):
        if not all([ENDPOINT, DATABASE, SERVICE_ACCOUNT_KEY_FILE]):
            raise ValueError(
                "YDB_ENDPOINT, YDB_DATABASE, and YDB_SERVICE_ACCOUNT_KEY_FILE environment variables must be set."
            )

        self.driver = ydb.Driver(
            endpoint=ENDPOINT,
            database=DATABASE,
            credentials=ydb.iam.ServiceAccountCredentials.from_file(
                SERVICE_ACCOUNT_KEY_FILE
            ),
        )

        self.driver.wait(fail_fast=True, timeout=5)
        self.pool = ydb.SessionPool(self.driver)

    def create_table(self):
        def callee(session):
            try:
                session.execute_scheme(
                    f"""
                    CREATE TABLE `{TABLE_NAME}` (
                        timestamp DateTime,
                        embedding String,
                        embedding_bit String,
                        url Text,
                        article_text Text,
                        specialization_source Text,
                        PRIMARY KEY (url)
                    )
                    """
                )
                print(f"Table '{TABLE_NAME}' created successfully.")
            except ydb.Error as e:
                if "already exists" in str(e):
                    print(f"Table '{TABLE_NAME}' already exists.")
                else:
                    print(f"Error creating table '{TABLE_NAME}': {e}")

        return self.pool.retry_operation_sync(callee)

    def insert_data(
        self,
        timestamp: datetime,
        embedding: list,
        url: str,
        article_text: str,
        specialization_source: str,
    ):
        def callee(session):
            try:
                prepared_query = session.prepare(
                    f"""
                    DECLARE $timestamp AS DateTime;
                    DECLARE $embedding AS List<Float>;
                    DECLARE $url AS Text;
                    DECLARE $article_text AS Text;
                    DECLARE $specialization_source AS Text;

                    INSERT INTO `{TABLE_NAME}` (
                        timestamp, embedding, embedding_bit, url, article_text, specialization_source
                    )
                    VALUES (
                        $timestamp,
                        Knn::ToBinaryStringFloat($embedding),
                        Knn::ToBinaryStringBit($embedding),
                        $url,
                        $article_text,
                        $specialization_source
                    );
                    """
                )
                session.transaction().execute(
                    prepared_query,
                    {
                        "$timestamp": int(timestamp.timestamp()) & 0xFFFFFFFF,
                        "$embedding": embedding,
                        "$url": url,
                        "$article_text": article_text,
                        "$specialization_source": specialization_source,
                    },
                    commit_tx=True,
                )
                print("Data inserted successfully.")
            except ydb.Error as e:
                print(f"Error inserting data: {e}")

        return self.pool.retry_operation_sync(callee)

    def extract_urls(self, page_size=1000):
        def callee(session):
            try:
                visited_urls = set()
                offset = 0
                while True:
                    result = session.transaction().execute(
                        f"""
                        SELECT url FROM `{TABLE_NAME}`
                        LIMIT {page_size}
                        OFFSET {offset}
                        """,
                        commit_tx=True,
                    )
                    if not result[0].rows:
                        break
                    visited_urls.update(row.url for row in result[0].rows)
                    offset += page_size
                return visited_urls
            except ydb.Error as e:
                print(f"Error extracting URLs: {e}")
                return set()

        return self.pool.retry_operation_sync(callee)

    def extract_top_simular(self, query_embedding, top_k=5):
        def callee(session):
            try:
                results = []
                prepared_query = session.prepare(
                    """
                DECLARE $query_embedding AS List<Float>;
                DECLARE $limit AS Int32;
                SELECT timestamp, article_text, url, embedding FROM `{}`
                ORDER BY Knn::CosineDistance(Knn::FromBinaryStringFloat(embedding), $query_embedding) ASC, timestamp DESC
                LIMIT $limit;
                """.format(
                        TABLE_NAME
                    )
                )
                # Fetch a page of URLs
                result = session.transaction().execute(
                    prepared_query,
                    {"$query_embedding": query_embedding, "$limit": top_k},
                )
                # Add the URLs from this page to the set
                results = result[0].rows
                # Move to the next page
                return results
            except ydb.Error as e:
                print(f"Error extracting URLs: {e}")
                return results

        return self.pool.retry_operation_sync(callee)
    def extract_top_simular_by_specialization(
        self, query_embedding, specialization_source, top_k=5
    ):
        def callee(session):
            try:
                results = []
                prepared_query = session.prepare(
                    """
                DECLARE $query_embedding AS List<Float>;
                DECLARE $specialization_source AS Text;
                DECLARE $limit AS Int32;
                SELECT timestamp, article_text, url, embedding FROM `{}`
                WHERE specialization_source = $specialization_source
                ORDER BY Knn::CosineDistance(Knn::FromBinaryStringFloat(embedding), $query_embedding) ASC, timestamp DESC
                LIMIT $limit;
                """.format(
                        TABLE_NAME
                    )
                )
                result = session.transaction().execute(
                    prepared_query,
                    {
                        "$query_embedding": query_embedding,
                        "$specialization_source": specialization_source,
                        "$limit": top_k,
                    },
                )
                results = result[0].rows
                return results
            except ydb.Error as e:
                print(f"Error extracting URLs by specialization: {e}")
                return results

        return self.pool.retry_operation_sync(callee)

    def close(self):
        if self.driver:
            self.driver.stop()
            print("YDB driver closed.")


if __name__ == "__main__":
    # Example usage (replace with actual values for testing)
    # Set environment variables before running this example
    # export YDB_ENDPOINT="grpcs://ydb.serverless.yandexcloud.net:2135"
    # export YDB_DATABASE="/ru-central1/b1g800d0000000000000/etv00000000000000000"
    # export YDB_SERVICE_ACCOUNT_KEY_FILE="/path/to/your/sa_key.json"

    try:
        adapter = YDBAdapter()
        adapter.create_table()

        # Example data insertion
        # from datetime import datetime
        # current_time = datetime.now()
        # example_embedding = [0.1, 0.2, 0.3] # Replace with actual embedding
        # example_url = "https://example.com/article1"
        # example_text = "This is an example article content."
        # adapter.insert_data(current_time, example_embedding, example_url, example_text)

        # Example URL extraction
        # urls = adapter.extract_urls()
        # print(f"Extracted URLs: {urls}")

    except ValueError as e:
        print(f"Configuration error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if "adapter" in locals():
            adapter.close()
