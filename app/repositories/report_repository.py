from sqlalchemy import text
from sqlalchemy.engine import Connection

# level is "2024" / "2025" (that year's top 10) or "month" (top 5 per month)

def top_sales(conn: Connection, level: str = "month") -> list[dict]:
    sql = text("""
                WITH annual_top_customers AS (
                    SELECT d.year AS sort_year, 0 AS sort_key, 'Yearly Top 10' AS report_type,
                        CAST(d.year AS CHAR) AS time_period, f.customer_key,
                        SUM(f.line_amount) AS yearly_spending,
                        ROW_NUMBER() OVER (PARTITION BY d.year ORDER BY SUM(f.line_amount) DESC) AS rank_number
                    FROM fact_sales f
                    JOIN dim_date d ON d.date_key = f.date_key
                    WHERE 'Monthly Top 5' = 'Yearly Top 10'
                    AND d.year IN (2024, 2025)
                    AND (NULL IS NULL OR d.year = NULL)
                    GROUP BY d.year, f.customer_key
                ),

                monthly_top_customers AS (
                    SELECT d.year AS sort_year, d.month AS sort_key, 'Monthly Top 5' AS report_type,
                        CONCAT(d.month_name, ' ', d.year) AS time_period, f.customer_key,
                        SUM(f.line_amount) AS monthly_spending,
                        RANK() OVER (PARTITION BY d.year, d.month ORDER BY SUM(f.line_amount) DESC) AS rank_number
                    FROM fact_sales f
                    JOIN dim_date d ON d.date_key = f.date_key
                    WHERE 'Monthly Top 5' = 'Monthly Top 5'
                    AND d.year IN (2024, 2025)
                    GROUP BY d.year, d.month, d.month_name, f.customer_key
                )

                SELECT combined.report_type, combined.time_period, c.full_name,
                    combined.customer_key, combined.yearly_spending
                FROM (
                    SELECT sort_year, sort_key, report_type, time_period, customer_key, yearly_spending
                    FROM annual_top_customers WHERE rank_number <= 10
                    UNION ALL
                    SELECT sort_year, sort_key, report_type, time_period, customer_key, monthly_spending
                    FROM monthly_top_customers WHERE rank_number <= 5
                ) AS combined
                JOIN dim_customer c ON c.customer_key = combined.customer_key
                ORDER BY combined.sort_year, combined.sort_key, combined.yearly_spending DESC;
            """)
    if level == "month":
        params = {"report_type": "Monthly Top 5", "period": None}
    else:
        params = {"report_type": "Yearly Top 10", "period": level}
    return [dict(r._mapping) for r in conn.execute(sql, params)]



def sales_by_location(conn: Connection, level: str = "city") -> list[dict]:
    if level not in ("city", "country"):
        raise ValueError("Invalid level. Use 'city' or 'country'.")

    sql = text("""
        SELECT c.country,
               CASE WHEN GROUPING(c.city) = 1 THEN NULL
                    ELSE c.city END AS city,
               COUNT(*) AS total_customers,
               SUM(s.total_orders) AS total_orders,
               SUM(s.total_revenue) AS total_revenue
        FROM dim_customer c
        JOIN (
            SELECT customer_key,
                   COUNT(DISTINCT order_id) AS total_orders,
                   SUM(line_amount) AS total_revenue
            FROM fact_sales
            GROUP BY customer_key
        ) AS s ON c.customer_key = s.customer_key
        GROUP BY c.country, c.city WITH ROLLUP
        HAVING GROUPING(c.country) = 0
           AND (
               (:level = 'city' AND GROUPING(c.city) = 0)
               OR (:level = 'country' AND GROUPING(c.city) = 1)
           )
        ORDER BY total_revenue DESC;
    """)

    return [dict(r._mapping) for r in conn.execute(sql, {"level": level})]

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

