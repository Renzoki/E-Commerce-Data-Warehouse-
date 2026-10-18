// ============================================================
// SITE CONFIG — the only file you need to edit to wire up the API.
//
// Every endpoint must return JSON in one of these shapes:
//   [ {col: value, ...}, ... ]                    (plain array of rows)
//   { "rows": [ ... ], "total": 1234 }            (for server-side paging)
//
// Leave `endpoint` as "" (or USE_MOCK = true) to show placeholder data
// from js/mock.js instead. No queries are defined here — every endpoint
// is for your group to write.
// ============================================================

const CONFIG = {
  // "" = same origin (when FastAPI serves this folder).
  // Set to "http://127.0.0.1:8000" if you open the HTML some other way.
  API_BASE: "",

  // true  -> every page uses js/mock.js (good for working on the UI)
  // false -> real endpoints are called; items with endpoint "" still use mock
  USE_MOCK: false,

  HEALTH_ENDPOINT: "/health",

  // ---------- Star schema (ecommerce_dw) — shown on the Schema page ----------
  // pk = primary key, fk = foreign key -> table
  schema: {
    fact: "fact_sales",
    tables: {
      fact_sales: [
        { name: "sales_id",     type: "BIGINT", pk: true },
        { name: "date_key",     type: "INT", fk: "dim_date" },
        { name: "customer_key", type: "INT", fk: "dim_customer" },
        { name: "product_key",  type: "INT", fk: "dim_product" },
        { name: "rider_key",    type: "INT", fk: "dim_rider" },
        { name: "order_id",     type: "INT" },
        { name: "order_number", type: "VARCHAR(255)" },
        { name: "quantity",     type: "INT" },
        { name: "unit_price",   type: "DECIMAL(10,2)" },
        { name: "line_amount",  type: "DECIMAL(12,2)" },
      ],
      dim_date: [
        { name: "date_key",   type: "INT", pk: true },
        { name: "full_date",  type: "DATE" },
        { name: "day",        type: "TINYINT" },
        { name: "day_name",   type: "VARCHAR(9)" },
        { name: "month",      type: "TINYINT" },
        { name: "month_name", type: "VARCHAR(9)" },
        { name: "quarter",    type: "TINYINT" },
        { name: "year",       type: "SMALLINT" },
        { name: "is_weekend", type: "BOOLEAN" },
      ],
      dim_customer: [
        { name: "customer_key", type: "INT", pk: true },
        { name: "user_id",      type: "INT" },
        { name: "username",     type: "VARCHAR(255)" },
        { name: "full_name",    type: "VARCHAR(255)" },
        { name: "gender",       type: "CHAR(1)" },
        { name: "birth_date",   type: "DATE" },
        { name: "age_group",    type: "VARCHAR(10)" },
        { name: "city",         type: "VARCHAR(255)" },
        { name: "country",      type: "VARCHAR(255)" },
        { name: "zip_code",     type: "CHAR(5)" },
      ],
      dim_product: [
        { name: "product_key",  type: "INT", pk: true },
        { name: "product_id",   type: "INT" },
        { name: "product_code", type: "VARCHAR(255)" },
        { name: "product_name", type: "VARCHAR(255)" },
        { name: "category",     type: "VARCHAR(50)" },
        { name: "unit_price",   type: "DECIMAL(10,2)" },
        { name: "price_range",  type: "VARCHAR(20)" },
      ],
      dim_rider: [
        { name: "rider_key",    type: "INT", pk: true },
        { name: "rider_id",     type: "INT" },
        { name: "full_name",    type: "VARCHAR(255)" },
        { name: "gender",       type: "CHAR(1)" },
        { name: "age",          type: "TINYINT" },
        { name: "age_group",    type: "VARCHAR(10)" },
        { name: "vehicle_type", type: "VARCHAR(20)" },
        { name: "courier_name", type: "VARCHAR(255)" },
      ],
    },
  },

  // ---------- Overview page: headline totals (LIVE) ----------
  // Served by app/controllers/overview_controller.py -> GET /api/overview
  // One request returns a single row; each tile reads one field from it.
  overview: { id: "overview", endpoint: "/api/overview" },
  kpis: [
    { label: "Total revenue",       field: "total_revenue",   format: "money" },
    { label: "Orders delivered",    field: "total_orders",    format: "int" },
    { label: "Avg. order value",    field: "avg_order_value", format: "money" },
    { label: "Units sold",          field: "units_sold",      format: "int" },
    { label: "Order lines (fact rows)", field: "order_lines", format: "int" },
    { label: "Customers",           field: "customers",       format: "int" },
    { label: "Products",            field: "products",        format: "int" },
    { label: "Riders",              field: "riders",          format: "int" },
    { label: "Couriers",            field: "couriers",        format: "int" },
  ],

  // ---------- Browse page: warehouse tables (LIVE) ----------
  // Served by app/controllers/table_controller.py -> GET /api/tables/{name}
  // The page sends ?q=&sort=&order=&limit=&offset= and gets {rows, total, columns}.
  datasets: [
    { id: "fact_sales", label: "fact_sales — order lines (fact)", endpoint: "/api/tables/fact_sales", server: true,
      description: "One row per product line in a delivered order. Measures: quantity, unit_price, line_amount (quantity × unit_price). order_id and order_number are degenerate dimensions." },
    { id: "dim_date", label: "dim_date — delivery dates", endpoint: "/api/tables/dim_date", server: true,
      description: "One row per calendar day between the first and last delivery date. Hierarchy: year → quarter → month → day. date_key is YYYYMMDD." },
    { id: "dim_customer", label: "dim_customer — customers", endpoint: "/api/tables/dim_customer", server: true,
      description: "One row per source user. Hierarchies: country → city → customer, and age_group → customer (age as of 2025-09-23)." },
    { id: "dim_product", label: "dim_product — products", endpoint: "/api/tables/dim_product", server: true,
      description: "One row per source product. Hierarchy: category → product. Categories are cleaned (e.g. BAG → Bags, Toy/TOYS → Toys); price_range bands the unit price." },
    { id: "dim_rider", label: "dim_rider — riders & couriers", endpoint: "/api/tables/dim_rider", server: true,
      description: "One row per delivery rider, with the courier denormalized in (no separate dim_courier). Hierarchies: courier → rider, and vehicle_type → rider." },
  ],

  // ---------- Reports page: one card per OLAP query (your queries) ----------
  // Titles/columns below are placeholders — rename them to match your queries.
  // chart: "bar" | "line" | "pie" | "doughnut" | "table"
  // x: label column, y: numeric column(s)
  // params: sent as query params; options come from dimension attributes.
  reports: [
    {
      id: "report_1",
      title: "Product Revenue - Category and Quarter",
      description: "Total revenue per product category in each quarter, with quarter subtotals and a grand total. Roll-up category → quarter.",
      endpoint: "/api/reports/category-quarterly",
      chart: "bar",
      x: "quarter",
      y: ["total_revenue"],
      chartRows: (rows) => rows.filter((row) => row.row_type === "quarter_total"),
      params: [
        { name: "year", label: "Year", type: "select", options: ["2024", "2025"], default: "2025" }
      ]
    },

    {
      id: "report_2",
      title: "Sales - City and Country",
      description: "Analyze which cities and countries contribute the most to total sales revenue. Roll-up city → country; dice by city and country. The chart shows the top 15 by revenue; the data table lists every row.",
      endpoint: "/api/reports/sales-by-location",
      chart: "bar",
      horizontal: true,
      // city rows also have country, so label them "City, Country" (same city name can exist in two countries)
      x: (row) => (row.city ? `${row.city}, ${row.country}` : row.country),
      y: ["total_revenue"],
      // rows already come sorted by revenue; chart the top 15 so labels stay readable (table keeps all rows)
      chartRows: (rows) => rows.slice(0, 15),
      params: [
        { name: "level", label: "Group By", type: "select", options: ["city", "country"], default: "city" }
      ]
    },

    {
      id: "report_3",
      title: "Top Customers — Monthly and Yearly",
      description: "View the top customers by total sales revenue, grouped by month and year. Roll-up month → year; dice by customer and year.",
      endpoint: "/api/reports/top-sales",
      chart: "table",
      params: [
        {name: "level", label: "View", type: "select", options: ["2024", "2025", "month"], default: "month"},
      ],
    },

    {
      id: "report_4",
      title: "Monthly Courier Deliveries and Revenue",
      description: "Orders delivered and revenue per courier per month. Roll-up rider → courier, day → month; dice by year, courier and vehicle type.",
      endpoint: "/api/reports/courier-monthly",
      chart: "bar",
      x: "month_name",
      y: ["total_deliveries"],
      params: [
        { name: "year", label: "Year", type: "select", options: ["", "2024", "2025"], default: "" },
        { name: "courier_name", label: "Courier", type: "select",
          options: ["", "JNT", "LBCD", "FEDEZ"], default: "" },
        { name: "vehicle_type", label: "Vehicle type", type: "select",
          options: ["", "Motorcycle", "Bicycle", "Tricycle", "Car"], default: "" },
      ],
    },
  ],
};