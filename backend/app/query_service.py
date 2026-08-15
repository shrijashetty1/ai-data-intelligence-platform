from langchain_ollama import ChatOllama
from app.database import get_connection
import re


# ============================================================
# OLLAMA MODEL
# ============================================================

llm = ChatOllama(
    model="qwen3:1.7b",
    temperature=0
)


# ============================================================
# DATABASE SCHEMA
# ============================================================

DATABASE_SCHEMA = """
Tables:

customers(
    customer_id,
    name,
    email,
    city,
    signup_date
)

products(
    product_id,
    product_name,
    category,
    price
)

orders(
    order_id,
    customer_id,
    product_id,
    quantity,
    order_date,
    total_amount
)

Relationships:
orders.customer_id -> customers.customer_id
orders.product_id -> products.product_id
"""


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(question: str) -> str:

    prompt = f"""
You are a PostgreSQL SQL expert.

Convert the user's natural language question into ONE PostgreSQL
SELECT query.

Database schema:
{DATABASE_SCHEMA}

Rules:

- Return ONLY SQL.
- Return exactly ONE SELECT statement.
- Do not use markdown.
- Do not use ```sql.
- Do not use INSERT.
- Do not use UPDATE.
- Do not use DELETE.
- Do not use DROP.
- Do not use ALTER.
- Do not use CREATE.
- Do not use TRUNCATE.
- Do not use GRANT.
- Do not use REVOKE.
- Use only the tables and columns provided in the schema.
- Never invent a table or column.
- Use PostgreSQL syntax.
- Use clear aliases for calculated columns.
- For sales or revenue questions, use orders.total_amount.
- For product sales questions, JOIN orders with products.
- When calculating sales by product, use:
  SUM(orders.total_amount) AS total_sales
- When the question asks for "top N", use ORDER BY the relevant
  metric DESC and LIMIT N.
- When the question asks for "highest", "most", or "best",
  order the relevant metric DESC.
- Do not calculate units from total_amount.
- If the question asks for quantity sold, use SUM(orders.quantity).
- If the question asks for revenue or sales, use SUM(orders.total_amount).

User question:
{question}
"""

    response = llm.invoke(prompt)

    sql = response.content.strip()

    # Remove markdown code fences if Ollama adds them
    sql = re.sub(
        r"```sql\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```\s*",
        "",
        sql
    )

    sql = sql.strip()

    return sql


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql: str) -> bool:

    if not sql:
        return False

    normalized = sql.strip().lower()

    # Must start with SELECT
    if not normalized.startswith("select"):
        return False

    # Prevent multiple SQL statements
    # A single trailing semicolon is allowed.
    sql_without_trailing_semicolon = normalized.rstrip(";").strip()

    if ";" in sql_without_trailing_semicolon:
        return False

    # Prevent SQL comments
    if "--" in normalized:
        return False

    if "/*" in normalized:
        return False

    if "*/" in normalized:
        return False

    # Block dangerous SQL operations
    forbidden_keywords = [
        "insert",
        "update",
        "delete",
        "drop",
        "alter",
        "create",
        "truncate",
        "grant",
        "revoke",
        "replace",
        "merge",
        "execute",
        "call",
        "copy",
    ]

    for keyword in forbidden_keywords:

        if re.search(
            rf"\b{keyword}\b",
            normalized
        ):
            return False

    return True


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql: str):

    if not validate_sql(sql):
        raise ValueError(
            "Unsafe or invalid SQL query."
        )

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute(sql)

        # SELECT queries should have cursor.description
        if cursor.description is None:
            return []

        columns = [
            description[0]
            for description in cursor.description
        ]

        rows = cursor.fetchall()

        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        return results

    finally:

        cursor.close()
        connection.close()


# ============================================================
# GENERATE BUSINESS INSIGHT
# ============================================================

def generate_insight(
    question: str,
    results: list
) -> str:

    # If there are no results, don't waste another Ollama call.
    if not results:
        return (
            "The query completed successfully, but no records "
            "matched the requested criteria."
        )

    prompt = f"""
You are a concise business data analyst.

User question:
{question}

Database results:
{results}

Write ONE short business insight based ONLY on these results.

IMPORTANT:

- Use only the information in the database results.
- Never invent information.
- Never invent dates.
- Never invent percentages.
- Never invent trends.
- Never invent historical comparisons.
- Never mention previous periods unless present in the results.
- Do not use Markdown.
- Do not use **.
- Do not use bullet points.
- Do not use headings.
- Do not use the word "units" unless the database result
  actually represents quantity.
- If a column is named total_sales, describe it as sales.
- If a column is named total_revenue, describe it as revenue.
- If a column is named quantity, describe it as quantity or units.
- Monetary values must be described as money/sales/revenue.
- Preserve the exact product/customer/city names from the results.
- Mention the most important result first.
- Compare results only when the comparison is directly supported.
- Keep the response to 1 or 2 sentences.
- Return ONLY the insight.

Example:

Laptop Pro generated the highest sales at $150,000, followed by
Standing Desk at $54,000 and Wireless Headphones at $15,000.

Do not use the example unless those values actually appear
in the database results.
"""

    try:

        response = llm.invoke(prompt)

        insight = response.content.strip()

        # Remove accidental markdown formatting
        insight = re.sub(
            r"\*\*",
            "",
            insight
        )

        insight = re.sub(
            r"```",
            "",
            insight
        )

        return insight.strip()

    except Exception as error:

        print(
            f"Insight generation failed: {error}"
        )

        # The SQL/database result is still valid,
        # so return a safe fallback instead of failing
        # the entire analysis.
        return build_fallback_insight(results)


# ============================================================
# FALLBACK INSIGHT
# ============================================================

def build_fallback_insight(results: list) -> str:

    if not results:
        return (
            "The query completed successfully, "
            "but no results were found."
        )

    first_row = results[0]

    # --------------------------------------------------------
    # Product sales
    # --------------------------------------------------------

    if (
        "product_name" in first_row
        and "total_sales" in first_row
    ):

        product = first_row["product_name"]
        sales = first_row["total_sales"]

        try:
            formatted_sales = (
                f"${float(sales):,.0f}"
            )
        except (TypeError, ValueError):
            formatted_sales = str(sales)

        return (
            f"{product} has the highest sales among "
            f"the returned products at {formatted_sales}."
        )

    # --------------------------------------------------------
    # Revenue
    # --------------------------------------------------------

    if "total_revenue" in first_row:

        revenue = first_row["total_revenue"]

        try:
            formatted_revenue = (
                f"${float(revenue):,.0f}"
            )
        except (TypeError, ValueError):
            formatted_revenue = str(revenue)

        return (
            f"The total revenue is {formatted_revenue}."
        )

    # --------------------------------------------------------
    # Total sales
    # --------------------------------------------------------

    if "total_sales" in first_row:

        sales = first_row["total_sales"]

        try:
            formatted_sales = (
                f"${float(sales):,.0f}"
            )
        except (TypeError, ValueError):
            formatted_sales = str(sales)

        return (
            f"The total sales are {formatted_sales}."
        )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    if "total_quantity" in first_row:

        quantity = first_row["total_quantity"]

        return (
            f"The total quantity is {quantity}."
        )

    # --------------------------------------------------------
    # Generic fallback
    # --------------------------------------------------------

    return (
        f"The query returned {len(results)} "
        f"result{'s' if len(results) != 1 else ''}."
    )