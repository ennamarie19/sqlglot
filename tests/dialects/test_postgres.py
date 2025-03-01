from sqlglot import ParseError, transpile
from tests.dialects.test_dialect import Validator


class TestPostgres(Validator):
    maxDiff = None
    dialect = "postgres"

    def test_ddl(self):
        self.validate_identity("CREATE TABLE test (foo HSTORE)")
        self.validate_identity("CREATE TABLE test (foo JSONB)")
        self.validate_identity("CREATE TABLE test (foo VARCHAR(64)[])")
        self.validate_all(
            "CREATE TABLE products (product_no INT UNIQUE, name TEXT, price DECIMAL)",
            write={
                "postgres": "CREATE TABLE products (product_no INT UNIQUE, name TEXT, price DECIMAL)"
            },
        )
        self.validate_all(
            "CREATE TABLE products (product_no INT CONSTRAINT must_be_different UNIQUE, name TEXT CONSTRAINT present NOT NULL, price DECIMAL)",
            write={
                "postgres": "CREATE TABLE products (product_no INT CONSTRAINT must_be_different UNIQUE, name TEXT CONSTRAINT present NOT NULL, price DECIMAL)"
            },
        )
        self.validate_all(
            "CREATE TABLE products (product_no INT, name TEXT, price DECIMAL, UNIQUE (product_no, name))",
            write={
                "postgres": "CREATE TABLE products (product_no INT, name TEXT, price DECIMAL, UNIQUE (product_no, name))"
            },
        )
        self.validate_all(
            "CREATE TABLE products ("
            "product_no INT UNIQUE,"
            " name TEXT,"
            " price DECIMAL CHECK (price > 0),"
            " discounted_price DECIMAL CONSTRAINT positive_discount CHECK (discounted_price > 0),"
            " CHECK (product_no > 1),"
            " CONSTRAINT valid_discount CHECK (price > discounted_price))",
            write={
                "postgres": "CREATE TABLE products ("
                "product_no INT UNIQUE,"
                " name TEXT,"
                " price DECIMAL CHECK (price > 0),"
                " discounted_price DECIMAL CONSTRAINT positive_discount CHECK (discounted_price > 0),"
                " CHECK (product_no > 1),"
                " CONSTRAINT valid_discount CHECK (price > discounted_price))"
            },
        )

        with self.assertRaises(ParseError):
            transpile("CREATE TABLE products (price DECIMAL CHECK price > 0)", read="postgres")
        with self.assertRaises(ParseError):
            transpile(
                "CREATE TABLE products (price DECIMAL, CHECK price > 1)",
                read="postgres",
            )

    def test_postgres(self):
        self.validate_identity("SELECT ARRAY[1, 2, 3]")
        self.validate_identity("SELECT ARRAY_LENGTH(ARRAY[1, 2, 3], 1)")
        self.validate_identity("STRING_AGG(x, y)")
        self.validate_identity("STRING_AGG(x, ',' ORDER BY y)")
        self.validate_identity("STRING_AGG(x, ',' ORDER BY y DESC)")
        self.validate_identity("STRING_AGG(DISTINCT x, ',' ORDER BY y DESC)")
        self.validate_identity("SELECT CASE WHEN SUBSTRING('abcdefg') IN ('ab') THEN 1 ELSE 0 END")
        self.validate_identity(
            "SELECT CASE WHEN SUBSTRING('abcdefg' FROM 1) IN ('ab') THEN 1 ELSE 0 END"
        )
        self.validate_identity(
            "SELECT CASE WHEN SUBSTRING('abcdefg' FROM 1 FOR 2) IN ('ab') THEN 1 ELSE 0 END"
        )
        self.validate_identity(
            'SELECT * FROM "x" WHERE SUBSTRING("x"."foo" FROM 1 FOR 2) IN (\'mas\')'
        )
        self.validate_identity("SELECT * FROM x WHERE SUBSTRING('Thomas' FROM '...$') IN ('mas')")
        self.validate_identity(
            "SELECT * FROM x WHERE SUBSTRING('Thomas' FROM '%#\"o_a#\"_' FOR '#') IN ('mas')"
        )
        self.validate_identity(
            "SELECT SUBSTRING('bla' + 'foo' || 'bar' FROM 3 - 1 + 5 FOR 4 + SOME_FUNC(arg1, arg2))"
        )
        self.validate_identity("SELECT TRIM(' X' FROM ' XXX ')")
        self.validate_identity("SELECT TRIM(LEADING 'bla' FROM ' XXX ' COLLATE utf8_bin)")
        self.validate_identity(
            "SELECT TO_TIMESTAMP(1284352323.5), TO_TIMESTAMP('05 Dec 2000', 'DD Mon YYYY')"
        )
        self.validate_identity("COMMENT ON TABLE mytable IS 'this'")
        self.validate_identity("SELECT e'\\xDEADBEEF'")
        self.validate_identity("SELECT CAST(e'\\176' AS BYTEA)")
        self.validate_identity("""SELECT * FROM JSON_TO_RECORDSET(z) AS y("rank" INT)""")

        self.validate_all(
            "END WORK AND NO CHAIN",
            write={"postgres": "COMMIT AND NO CHAIN"},
        )
        self.validate_all(
            "END AND CHAIN",
            write={"postgres": "COMMIT AND CHAIN"},
        )
        self.validate_all(
            "CREATE TABLE x (a UUID, b BYTEA)",
            write={
                "duckdb": "CREATE TABLE x (a UUID, b VARBINARY)",
                "presto": "CREATE TABLE x (a UUID, b VARBINARY)",
                "hive": "CREATE TABLE x (a UUID, b BINARY)",
                "spark": "CREATE TABLE x (a UUID, b BINARY)",
            },
        )
        self.validate_all(
            "123::CHARACTER VARYING",
            write={"postgres": "CAST(123 AS VARCHAR)"},
        )
        self.validate_all(
            "TO_TIMESTAMP(123::DOUBLE PRECISION)",
            write={"postgres": "TO_TIMESTAMP(CAST(123 AS DOUBLE PRECISION))"},
        )
        self.validate_all(
            "SELECT to_timestamp(123)::time without time zone",
            write={"postgres": "SELECT CAST(TO_TIMESTAMP(123) AS TIME)"},
        )

        self.validate_identity(
            "CREATE TABLE A (LIKE B INCLUDING CONSTRAINT INCLUDING COMPRESSION EXCLUDING COMMENTS)"
        )
        self.validate_all(
            "SELECT SUM(x) OVER (PARTITION BY a ORDER BY d ROWS 1 PRECEDING)",
            write={
                "postgres": "SELECT SUM(x) OVER (PARTITION BY a ORDER BY d ROWS BETWEEN 1 PRECEDING AND CURRENT ROW)",
            },
        )
        self.validate_all(
            "SELECT * FROM x FETCH 1 ROW",
            write={
                "postgres": "SELECT * FROM x FETCH FIRST 1 ROWS ONLY",
                "presto": "SELECT * FROM x FETCH FIRST 1 ROWS ONLY",
                "hive": "SELECT * FROM x FETCH FIRST 1 ROWS ONLY",
                "spark": "SELECT * FROM x FETCH FIRST 1 ROWS ONLY",
            },
        )
        self.validate_all(
            "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname ASC NULLS LAST, lname",
            write={
                "postgres": "SELECT fname, lname, age FROM person ORDER BY age DESC, fname, lname",
                "presto": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname, lname",
                "hive": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname NULLS LAST, lname NULLS LAST",
                "spark": "SELECT fname, lname, age FROM person ORDER BY age DESC NULLS FIRST, fname NULLS LAST, lname NULLS LAST",
            },
        )
        self.validate_all(
            "SELECT CASE WHEN SUBSTRING('abcdefg' FROM 1 FOR 2) IN ('ab') THEN 1 ELSE 0 END",
            write={
                "hive": "SELECT CASE WHEN SUBSTRING('abcdefg', 1, 2) IN ('ab') THEN 1 ELSE 0 END",
                "spark": "SELECT CASE WHEN SUBSTRING('abcdefg', 1, 2) IN ('ab') THEN 1 ELSE 0 END",
            },
        )
        self.validate_all(
            "SELECT * FROM x WHERE SUBSTRING(col1 FROM 3 + LENGTH(col1) - 10 FOR 10) IN (col2)",
            write={
                "hive": "SELECT * FROM x WHERE SUBSTRING(col1, 3 + LENGTH(col1) - 10, 10) IN (col2)",
                "spark": "SELECT * FROM x WHERE SUBSTRING(col1, 3 + LENGTH(col1) - 10, 10) IN (col2)",
            },
        )
        self.validate_all(
            "SELECT SUBSTRING(CAST(2022 AS CHAR(4)) || LPAD(CAST(3 AS CHAR(2)), 2, '0') FROM 3 FOR 4)",
            read={
                "postgres": "SELECT SUBSTRING(2022::CHAR(4) || LPAD(3::CHAR(2), 2, '0') FROM 3 FOR 4)",
            },
        )
        self.validate_all(
            "SELECT TRIM(BOTH ' XXX ')",
            write={
                "mysql": "SELECT TRIM(' XXX ')",
                "postgres": "SELECT TRIM(' XXX ')",
                "hive": "SELECT TRIM(' XXX ')",
            },
        )
        self.validate_all(
            "TRIM(LEADING FROM ' XXX ')",
            write={
                "mysql": "LTRIM(' XXX ')",
                "postgres": "LTRIM(' XXX ')",
                "hive": "LTRIM(' XXX ')",
                "presto": "LTRIM(' XXX ')",
            },
        )
        self.validate_all(
            "TRIM(TRAILING FROM ' XXX ')",
            write={
                "mysql": "RTRIM(' XXX ')",
                "postgres": "RTRIM(' XXX ')",
                "hive": "RTRIM(' XXX ')",
                "presto": "RTRIM(' XXX ')",
            },
        )
        self.validate_all(
            "SELECT * FROM foo, LATERAL (SELECT * FROM bar WHERE bar.id = foo.bar_id) AS ss",
            read={
                "postgres": "SELECT * FROM foo, LATERAL (SELECT * FROM bar WHERE bar.id = foo.bar_id) AS ss"
            },
        )
        self.validate_all(
            "SELECT m.name FROM manufacturers AS m LEFT JOIN LATERAL GET_PRODUCT_NAMES(m.id) pname ON TRUE WHERE pname IS NULL",
            write={
                "postgres": "SELECT m.name FROM manufacturers AS m LEFT JOIN LATERAL GET_PRODUCT_NAMES(m.id) AS pname ON TRUE WHERE pname IS NULL",
            },
        )
        self.validate_all(
            "SELECT p1.id, p2.id, v1, v2 FROM polygons AS p1, polygons AS p2, LATERAL VERTICES(p1.poly) v1, LATERAL VERTICES(p2.poly) v2 WHERE (v1 <-> v2) < 10 AND p1.id <> p2.id",
            write={
                "postgres": "SELECT p1.id, p2.id, v1, v2 FROM polygons AS p1, polygons AS p2, LATERAL VERTICES(p1.poly) AS v1, LATERAL VERTICES(p2.poly) AS v2 WHERE (v1 <-> v2) < 10 AND p1.id <> p2.id",
            },
        )
        self.validate_all(
            "SELECT * FROM r CROSS JOIN LATERAL unnest(array(1)) AS s(location)",
            write={
                "postgres": "SELECT * FROM r CROSS JOIN LATERAL UNNEST(ARRAY[1]) AS s(location)",
            },
        )
        self.validate_all(
            "SELECT id, email, CAST(deleted AS TEXT) FROM users WHERE NOT deleted IS NULL",
            read={
                "postgres": "SELECT id, email, CAST(deleted AS TEXT) FROM users WHERE deleted NOTNULL"
            },
        )
        self.validate_all(
            "SELECT id, email, CAST(deleted AS TEXT) FROM users WHERE NOT deleted IS NULL",
            read={
                "postgres": "SELECT id, email, CAST(deleted AS TEXT) FROM users WHERE NOT deleted ISNULL"
            },
        )
        self.validate_all(
            "'[1,2,3]'::json->2",
            write={"postgres": "CAST('[1,2,3]' AS JSON) -> '2'"},
        )
        self.validate_all(
            """'{"a":1,"b":2}'::json->'b'""",
            write={"postgres": """CAST('{"a":1,"b":2}' AS JSON) -> 'b'"""},
        )
        self.validate_all(
            """'{"x": {"y": 1}}'::json->'x'->'y'""",
            write={"postgres": """CAST('{"x": {"y": 1}}' AS JSON) -> 'x' -> 'y'"""},
        )
        self.validate_all(
            """'{"x": {"y": 1}}'::json->'x'::json->'y'""",
            write={"postgres": """CAST(CAST('{"x": {"y": 1}}' AS JSON) -> 'x' AS JSON) -> 'y'"""},
        )
        self.validate_all(
            """'[1,2,3]'::json->>2""",
            write={"postgres": "CAST('[1,2,3]' AS JSON) ->> '2'"},
        )
        self.validate_all(
            """'{"a":1,"b":2}'::json->>'b'""",
            write={"postgres": """CAST('{"a":1,"b":2}' AS JSON) ->> 'b'"""},
        )
        self.validate_all(
            """'{"a":[1,2,3],"b":[4,5,6]}'::json#>'{a,2}'""",
            write={"postgres": """CAST('{"a":[1,2,3],"b":[4,5,6]}' AS JSON) #> '{a,2}'"""},
        )
        self.validate_all(
            """'{"a":[1,2,3],"b":[4,5,6]}'::json#>>'{a,2}'""",
            write={"postgres": """CAST('{"a":[1,2,3],"b":[4,5,6]}' AS JSON) #>> '{a,2}'"""},
        )
        self.validate_all(
            """SELECT JSON_ARRAY_ELEMENTS((foo->'sections')::JSON) AS sections""",
            write={
                "postgres": """SELECT JSON_ARRAY_ELEMENTS(CAST((foo -> 'sections') AS JSON)) AS sections""",
                "presto": """SELECT JSON_ARRAY_ELEMENTS(CAST((JSON_EXTRACT(foo, 'sections')) AS JSON)) AS sections""",
            },
        )
        self.validate_all(
            """x ? 'x'""",
            write={"postgres": "x ? 'x'"},
        )
        self.validate_all(
            "SELECT $$a$$",
            write={"postgres": "SELECT 'a'"},
        )
        self.validate_all(
            "SELECT $$Dianne's horse$$",
            write={"postgres": "SELECT 'Dianne''s horse'"},
        )
        self.validate_all(
            "UPDATE MYTABLE T1 SET T1.COL = 13",
            write={"postgres": "UPDATE MYTABLE AS T1 SET T1.COL = 13"},
        )

        self.validate_identity("x ~ 'y'")
        self.validate_identity("x ~* 'y'")
        self.validate_all(
            "x !~ 'y'",
            write={"postgres": "NOT x ~ 'y'"},
        )
        self.validate_all(
            "x !~* 'y'",
            write={"postgres": "NOT x ~* 'y'"},
        )

        self.validate_all(
            "x ~~ 'y'",
            write={"postgres": "x LIKE 'y'"},
        )
        self.validate_all(
            "x ~~* 'y'",
            write={"postgres": "x ILIKE 'y'"},
        )
        self.validate_all(
            "x !~~ 'y'",
            write={"postgres": "NOT x LIKE 'y'"},
        )
        self.validate_all(
            "x !~~* 'y'",
            write={"postgres": "NOT x ILIKE 'y'"},
        )
        self.validate_all(
            "'45 days'::interval day",
            write={"postgres": "CAST('45 days' AS INTERVAL day)"},
        )
        self.validate_all(
            "'x' 'y' 'z'",
            write={"postgres": "CONCAT('x', 'y', 'z')"},
        )
        self.validate_identity("SELECT ARRAY(SELECT 1)")

        self.validate_all(
            "x::cstring",
            write={"postgres": "CAST(x AS CSTRING)"},
        )

        self.validate_identity(
            "SELECT SUM(x) OVER a, SUM(y) OVER b FROM c WINDOW a AS (PARTITION BY d), b AS (PARTITION BY e)"
        )

    def test_bool_or(self):
        self.validate_all(
            "SELECT a, LOGICAL_OR(b) FROM table GROUP BY a",
            write={"postgres": "SELECT a, BOOL_OR(b) FROM table GROUP BY a"},
        )
