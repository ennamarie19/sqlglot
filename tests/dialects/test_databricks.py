from tests.dialects.test_dialect import Validator


class TestDatabricks(Validator):
    dialect = "databricks"

    def test_datediff(self):
        self.validate_all(
            "SELECT DATEDIFF(year, 'start', 'end')",
            write={
                "tsql": "SELECT DATEDIFF(year, 'start', 'end')",
                "databricks": "SELECT DATEDIFF(year, 'start', 'end')",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(microsecond, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(microsecond, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) * 1000000 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(millisecond, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(millisecond, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) * 1000 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(second, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(second, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(minute, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(minute, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) / 60 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(hour, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(hour, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) / 3600 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(day, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(day, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(epoch FROM CAST('end' AS TIMESTAMP) - CAST('start' AS TIMESTAMP)) / 86400 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(week, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(week, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(year FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) * 48 + EXTRACT(month FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) * 4 + EXTRACT(day FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) / 7 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(month, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(month, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(year FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) * 12 + EXTRACT(month FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(quarter, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(quarter, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(year FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) * 4 + EXTRACT(month FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) / 3 AS BIGINT)",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF(year, 'start', 'end')",
            write={
                "databricks": "SELECT DATEDIFF(year, 'start', 'end')",
                "postgres": "SELECT CAST(EXTRACT(year FROM AGE(CAST('end' AS TIMESTAMP), CAST('start' AS TIMESTAMP))) AS BIGINT)",
            },
        )

    def test_add_date(self):
        self.validate_all(
            "SELECT DATEADD(year, 1, '2020-01-01')",
            write={
                "tsql": "SELECT DATEADD(year, 1, '2020-01-01')",
                "databricks": "SELECT DATEADD(year, 1, '2020-01-01')",
            },
        )
        self.validate_all(
            "SELECT DATEDIFF('end', 'start')",
            write={"databricks": "SELECT DATEDIFF(DAY, 'start', 'end')"},
        )
        self.validate_all(
            "SELECT DATE_ADD('2020-01-01', 1)",
            write={
                "tsql": "SELECT DATEADD(DAY, 1, '2020-01-01')",
                "databricks": "SELECT DATEADD(DAY, 1, '2020-01-01')",
            },
        )

    def test_without_as(self):
        self.validate_all(
            "CREATE TABLE x (SELECT 1)",
            write={
                "databricks": "CREATE TABLE x AS (SELECT 1)",
            },
        )

        self.validate_all(
            "WITH x (select 1) SELECT * FROM x",
            write={
                "databricks": "WITH x AS (SELECT 1) SELECT * FROM x",
            },
        )
