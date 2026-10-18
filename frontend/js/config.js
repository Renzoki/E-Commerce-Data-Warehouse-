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

  // ---------- Overview page: single-number tiles (your queries) ----------
  // Endpoint returns one row: [{ "value": 12345 }]  (or set `field`)
  kpis: [
    { id: "kpi_sales",     label: "Total sales (line_amount)", endpoint: "", field: "value", format: "money" },
    { id: "kpi_orders",    label: "Orders",                    endpoint: "", field: "value", format: "int" },
    { id: "kpi_customers", label: "Customers",                 endpoint: "", field: "value", format: "int" },
    { id: "kpi_riders",    label: "Riders",                    endpoint: "", field: "value", format: "int" },
  ],

  // ---------- Browse page: warehouse tables (LIVE) ----------
  // Served by app/controllers/table_controller.py -> GET /api/tables/{name}
  // The page sends ?q=&sort=&order=&limit=&offset= and gets {rows, total, columns}.
  datasets: [
    { id: "fact_sales",   label: "fact_sales",   endpoint: "/api/tables/fact_sales",   server: true },
    { id: "dim_date",     label: "dim_date",     endpoint: "/api/tables/dim_date",     server: true },
    { id: "dim_customer", label: "dim_customer", endpoint: "/api/tables/dim_customer", server: true },
    { id: "dim_product",  label: "dim_product",  endpoint: "/api/tables/dim_product",  server: true },
    { id: "dim_rider",    label: "dim_rider",    endpoint: "/api/tables/dim_rider",    server: true },
  ],

  // ---------- Reports page: one card per OLAP query (your queries) ----------
  // Titles/columns below are placeholders — rename them to match your queries.
  // chart: "bar" | "line" | "pie" | "doughnut" | "table"
  // x: label column, y: numeric column(s)
  // params: sent as query params; options come from dimension attributes.
  reports: [
    {
      id: "report_1",
      title: "Top Customers — yearly and monthly",
      description: "Top 10 customers of 2025, then top 5 per month.",
      endpoint: "/api/reports/top-sales",
      chart: "table",
    },
    {
      id: "report_2",
      title: "Report 2 — slice on dim_product",
      description: "Placeholder. Grouped by category, sliced by year and price_range.",
      endpoint: "",
      chart: "bar",
      x: "category",
      y: ["total_sales"],
      params: [
        { name: "year", label: "Year", type: "select", options: ["", "2024", "2025"], default: "" },
        { name: "price_range", label: "Price range", type: "select",
          options: ["", "Budget", "Mid", "Premium"], default: "" },
      ],
    },
    {
      id: "report_3",
      title: "Report 3 — dice on dim_customer",
      description: "Placeholder. Grouped by age_group, diced by gender and city.",
      endpoint: "",
      chart: "bar",
      x: "age_group",
      y: ["total_sales", "total_quantity"],
      params: [
        { name: "gender", label: "Gender", type: "select", options: ["", "M", "F"], default: "" },
        { name: "city", label: "City", type: "text", default: "" },
      ],
    },
    {
      id: "report_4",
      title: "Monthly Courier Deliveries and Revenue",
      description: "Orders delivered and revenue per courier per month. Roll-up rider → courier, day → month; dice by year, courier and vehicle type.",
      endpoint: "/api/reports/courier-monthly",
      chart: "table",
      params: [
        { name: "year", label: "Year", type: "select", options: ["", "2024", "2025"], default: "" },
        { name: "courier_name", label: "Courier", type: "select",
          options: ["", "JNT", "LBCD", "FEDEZ"], default: "" },
        { name: "vehicle_type", label: "Vehicle type", type: "select",
          options: ["", "Motorcycle", "Bicycle", "Tricycle", "Car"], default: "" },
      ],
    },
    {
      id: "report_5",
      title: "Sales by City and Country",
      description: "Analyze which cities and countries contribute the most to total sales revenue using OLAP roll-up.",
      endpoint: "/api/reports/sales-by-location",
      chart: "table",
      params: [
    { name: "level", label: "Group By", type: "select", options: ["city", "country"], default: "city"}
  ]
  },
  ],
};