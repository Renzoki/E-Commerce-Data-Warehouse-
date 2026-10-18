from sqlalchemy import text
from sqlalchemy.engine import Connection


def top_sales(conn: Connection) -> list[dict]:
    sql = text("""
        WITH annual_top_customers AS (
            SELECT 0 AS sort_key, 'Yearly Top 10' AS report_type, '2025' AS time_period, c.full_name, c.customer_key, SUM(f.line_amount) AS yearly_spending
            FROM fact_sales f
            JOIN dim_date d ON d.date_key = f.date_key
            JOIN dim_customer c ON c.customer_key = f.customer_key
            WHERE d.year = 2025
            GROUP BY c.customer_key, c.full_name
            ORDER BY yearly_spending DESC
            LIMIT 10
        ),

        monthly_top_customers AS (
            SELECT d.month AS sort_key, 'Monthly Top 5' AS report_type, d.month_name AS time_period, c.full_name, c.customer_key, SUM(f.line_amount) AS monthly_spending,
            RANK() OVER (PARTITION BY d.month ORDER BY SUM(f.line_amount) DESC) AS rank_number
            FROM fact_sales f
            JOIN dim_date d ON d.date_key = f.date_key
            JOIN dim_customer c ON c.customer_key = f.customer_key
            WHERE d.year = 2025
            GROUP BY d.month, d.month_name, c.customer_key, c.full_name
        )

        SELECT report_type, time_period, full_name, customer_key, yearly_spending
        FROM (
            SELECT sort_key, report_type, time_period, full_name, customer_key, yearly_spending FROM annual_top_customers
            UNION ALL
            SELECT sort_key, report_type, time_period, full_name, customer_key, monthly_spending FROM monthly_top_customers WHERE rank_number <= 5
        ) AS combined
        ORDER BY sort_key, yearly_spending DESC;

    """)
    return [dict(r._mapping) for r in conn.execute(sql)]



def sales_by_location(conn: Connection, level: str = "city") -> list[dict]:

    if level == "city":
        sql = text("""
            SELECT
                c.country,
                c.city,
                COUNT(DISTINCT f.customer_key) AS total_customers,
                COUNT(DISTINCT f.order_id) AS total_orders,
                SUM(f.line_amount) AS total_revenue

            FROM fact_sales f

            JOIN dim_customer c
                ON f.customer_key = c.customer_key

            GROUP BY
                c.country,
                c.city

            ORDER BY
                total_revenue DESC;
        """)

    elif level == "country":
        sql = text("""
            SELECT
                c.country,
                COUNT(DISTINCT f.customer_key) AS total_customers,
                COUNT(DISTINCT f.order_id) AS total_orders,
                SUM(f.line_amount) AS total_revenue

            FROM fact_sales f

            JOIN dim_customer c
                ON f.customer_key = c.customer_key

            GROUP BY
                c.country

            ORDER BY
                total_revenue DESC;
        """)

    else:
        raise ValueError("Invalid level. Use 'city' or 'country'.")

    return [dict(row._mapping) for row in conn.execute(sql)]


def courier_monthly(conn: Connection, year: int | None = None,
                    courier_name: str | None = None, vehicle_type: str | None = None) -> list[dict]:
    # deliveries = distinct orders, since one order can have several product lines
    sql = text("""
        SELECT r.courier_name, d.year, d.month, d.month_name,
               COUNT(DISTINCT f.order_id) AS total_deliveries,
               SUM(f.line_amount)         AS total_revenue
        FROM fact_sales f
        JOIN dim_rider r ON r.rider_key = f.rider_key
        JOIN dim_date d ON d.date_key = f.date_key
        WHERE (:year IS NULL OR d.year = :year)
          AND (:courier_name IS NULL OR r.courier_name = :courier_name)
          AND (:vehicle_type IS NULL OR r.vehicle_type = :vehicle_type)
        GROUP BY r.courier_name, d.year, d.month, d.month_name
        ORDER BY r.courier_name, d.year, d.month;
    """)
    params = {"year": year, "courier_name": courier_name, "vehicle_type": vehicle_type}
    return [dict(r._mapping) for r in conn.execute(sql, params)]


def category_quarterly(conn: Connection, year: int) -> list[dict]:
    sql = text("""
        SELECT CASE WHEN GROUPING(d.quarter) = 1 THEN 'All quarters'
                    ELSE CONCAT('Q', d.quarter) END       AS quarter,
               CASE WHEN GROUPING(p.category) = 1 THEN 'All categories'
                    ELSE p.category END                   AS category,
               SUM(f.line_amount)                         AS total_revenue,
               CASE WHEN GROUPING(d.quarter) = 1 THEN 'grand_total'
                    WHEN GROUPING(p.category) = 1 THEN 'quarter_total'
                    ELSE 'detail' END                     AS row_type
        FROM fact_sales f
        JOIN dim_date d    ON d.date_key = f.date_key
        JOIN dim_product p ON p.product_key = f.product_key
        WHERE d.year = :year
        GROUP BY d.quarter, p.category WITH ROLLUP
        ORDER BY GROUPING(d.quarter), d.quarter, GROUPING(p.category), p.category
    """)
    return [dict(r._mapping) for r in conn.execute(sql, {"year": year})]

