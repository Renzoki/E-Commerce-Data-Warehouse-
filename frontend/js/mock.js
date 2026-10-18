// Placeholder data shaped like the ecommerce_dw star schema, so the UI
// renders before the API exists. Keyed by the `id` in config.js; each
// function gets the query params. Values are fake.
// Delete entries as your real endpoints come online.

const MOCK = (() => {
  // seeded RNG so mock numbers stay the same on reload
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
  const pick = (arr) => arr[Math.floor(rnd() * arr.length)];
  const int = (lo, hi) => lo + Math.floor(rnd() * (hi - lo + 1));
  const pad = (n, w = 2) => String(n).padStart(w, "0");
  const ageGroup = (a) => (a < 25 ? "18-24" : a < 35 ? "25-34" : a < 45 ? "35-44" : a < 55 ? "45-54" : "55+");

  const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const MONTHS = ["January", "February", "March", "April", "May", "June", "July",
                  "August", "September", "October", "November", "December"];

  // ---------- dim_date: every day of 2024–2025 ----------
  const dim_date = [];
  for (let d = new Date(Date.UTC(2024, 0, 1)); d.getUTCFullYear() < 2026; d.setUTCDate(d.getUTCDate() + 1)) {
    const y = d.getUTCFullYear(), m = d.getUTCMonth() + 1, day = d.getUTCDate(), wd = d.getUTCDay();
    dim_date.push({
      date_key: +`${y}${pad(m)}${pad(day)}`,
      full_date: `${y}-${pad(m)}-${pad(day)}`,
      day,
      day_name: DAYS[wd],
      month: m,
      month_name: MONTHS[m - 1],
      quarter: Math.ceil(m / 3),
      year: y,
      is_weekend: wd === 0 || wd === 6,
    });
  }

  // ---------- dim_product ----------
  const categories = ["Electronics", "Fashion", "Home", "Beauty", "Sports", "Toys"];
  const dim_product = Array.from({ length: 40 }, (_, i) => {
    const price = +(50 + rnd() * 4950).toFixed(2);
    return {
      product_key: i + 1,
      product_id: 1000 + i,
      product_code: `PRD-${pad(i + 1, 4)}`,
      product_name: `Sample product ${i + 1}`,
      category: pick(categories),
      unit_price: price,
      price_range: price < 500 ? "Budget" : price < 2000 ? "Mid" : "Premium",
    };
  });

  // ---------- dim_customer ----------
  const cities = ["Manila", "Quezon City", "Makati", "Pasig", "Cebu City", "Davao City"];
  const dim_customer = Array.from({ length: 60 }, (_, i) => {
    const by = int(1960, 2006);
    return {
      customer_key: i + 1,
      user_id: 5000 + i,
      username: `user${i + 1}`,
      full_name: `Customer ${i + 1}`,
      gender: pick(["M", "F"]),
      birth_date: `${by}-${pad(int(1, 12))}-${pad(int(1, 28))}`,
      age_group: ageGroup(2026 - by),
      city: pick(cities),
      country: "Philippines",
      zip_code: pad(int(1000, 9999), 5),
    };
  });

  // ---------- dim_rider ----------
  const couriers = ["Courier A", "Courier B", "Courier C"];
  const dim_rider = Array.from({ length: 25 }, (_, i) => {
    const age = int(19, 58);
    return {
      rider_key: i + 1,
      rider_id: 200 + i,
      full_name: `Rider ${i + 1}`,
      gender: pick(["M", "F"]),
      age,
      age_group: ageGroup(age),
      vehicle_type: pick(["Motorcycle", "Motorcycle", "Bicycle", "Car", "Truck"]),
      courier_name: pick(couriers),
    };
  });

  // ---------- fact_sales: order lines ----------
  const fact_sales = [];
  for (let o = 1; o <= 400; o++) {
    const date = pick(dim_date), cust = pick(dim_customer), rider = pick(dim_rider);
    for (let l = 0, n = int(1, 3); l < n; l++) {
      const p = pick(dim_product), qty = int(1, 4);
      fact_sales.push({
        sales_id: fact_sales.length + 1,
        date_key: date.date_key,
        customer_key: cust.customer_key,
        product_key: p.product_key,
        rider_key: rider.rider_key,
        order_id: o,
        order_number: `ORD-${pad(o, 6)}`,
        quantity: qty,
        unit_price: p.unit_price,
        line_amount: +(p.unit_price * qty).toFixed(2),
      });
    }
  }

  // lookups for the placeholder report shapes
  const byKey = (rows, k) => Object.fromEntries(rows.map((r) => [r[k], r]));
  const D = byKey(dim_date, "date_key"), P = byKey(dim_product, "product_key"),
        C = byKey(dim_customer, "customer_key"), R = byKey(dim_rider, "rider_key");
  const sum = (rows, f) => +rows.reduce((s, r) => s + r[f], 0).toFixed(2);
  const group = (rows, keyFn) => rows.reduce((g, r) => ((g[keyFn(r)] ??= []).push(r), g), {});

  return {
    kpi_sales:     () => [{ value: sum(fact_sales, "line_amount") }],
    kpi_orders:    () => [{ value: new Set(fact_sales.map((f) => f.order_id)).size }],
    kpi_customers: () => [{ value: dim_customer.length }],
    kpi_riders:    () => [{ value: dim_rider.length }],

    fact_sales:   () => fact_sales,
    dim_date:     () => dim_date,
    dim_customer: () => dim_customer,
    dim_product:  () => dim_product,
    dim_rider:    () => dim_rider,

    // Fake output shapes only — just enough for the charts to draw.
    report_1: ({ level = "year" }) => {
      const key = (f) => {
        const d = D[f.date_key];
        return level === "year" ? `${d.year}`
          : level === "quarter" ? `${d.year}-Q${d.quarter}`
          : `${d.year}-${pad(d.month)}`;
      };
      const g = group(fact_sales, key);
      return Object.keys(g).sort().map((k) => ({ period: k, total_sales: sum(g[k], "line_amount") }));
    },
    report_2: ({ year = "", price_range = "" }) => {
      const rows = fact_sales.filter((f) =>
        (!year || D[f.date_key].year === +year) && (!price_range || P[f.product_key].price_range === price_range));
      const g = group(rows, (f) => P[f.product_key].category);
      return Object.keys(g).sort().map((k) => ({ category: k, total_sales: sum(g[k], "line_amount") }));
    },
    report_3: ({ gender = "", city = "" }) => {
      const rows = fact_sales.filter((f) => {
        const c = C[f.customer_key];
        return (!gender || c.gender === gender) && (!city || c.city.toLowerCase().includes(city.toLowerCase()));
      });
      const g = group(rows, (f) => C[f.customer_key].age_group);
      return Object.keys(g).sort().map((k) => ({
        age_group: k, total_sales: sum(g[k], "line_amount"), total_quantity: sum(g[k], "quantity"),
      }));
    },
    report_4: ({ courier_name = "" }) => {
      const rows = fact_sales.filter((f) =>
        !courier_name || R[f.rider_key].courier_name.toLowerCase().includes(courier_name.toLowerCase()));
      const g = group(rows, (f) => R[f.rider_key].vehicle_type);
      return Object.keys(g).sort().map((k) => ({
        vehicle_type: k, total_orders: new Set(g[k].map((f) => f.order_id)).size,
      }));
    },
  };
})();
