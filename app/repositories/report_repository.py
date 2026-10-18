from sqlalchemy import text
from sqlalchemy.engine import Connection


def top_sales(conn: Connection) -> list[dict]:
    sql = text("""
        WITH annual_top_customers AS (
            SELECT 'Yearly Top 10' AS report_type, '2025' AS time_period, c.full_name, c.customer_key, SUM(f.line_amount) AS yearly_spending
            FROM fact_sales f
            JOIN dim_date d ON d.date_key = f.date_key
            JOIN dim_customer c ON c.customer_key = f.customer_key
            WHERE d.year = 2025
            GROUP BY c.customer_key, c.full_name
            ORDER BY yearly_spending DESC
            LIMIT 10
        ),

        monthly_top_customers AS (
            SELECT 'Monthly Top 10' AS report_type, d.month_name AS time_period, c.full_name, c.customer_key, SUM(f.line_amount) AS monthly_spending
            FROM fact_sales f
            JOIN dim_date d ON d.date_key = f.date_key
            JOIN dim_customer c ON c.customer_key = f.customer_key
            WHERE d.year = 2025
            GROUP BY d.month, d.month_name, c.customer_key, c.full_name
            ORDER BY d.month ASC
            LIMIT 12
        )

        SELECT report_type, time_period, full_name, customer_key, yearly_spending FROM annual_top_customers
        UNION ALL 
        SELECT report_type, time_period, full_name, customer_key, monthly_spending FROM monthly_top_customers;

    """)
    return [dict(r._mapping) for r in conn.execute(sql)]