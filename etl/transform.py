"""DataFrame in, DataFrame out, no database calls"""
import pandas as pd

AS_OF = pd.Timestamp("2025-09-23")   # ages are computed on this date (last delivery date in the data)

GENDER_MAP = {
    "Male" : 'M',
    "Female" : 'F',
}

CATEGORY_MAP = {
    "BAG": "Bags",
    "GADGETS": "Gadgets",
    "make up": "Makeup",
    "TOYS": "Toys",
    "Toy": "Toys",
}

VEHICLE_MAP = {
    "Motorbike": "Motorcycle",
    "Bike": "Bicycle",
    "Trike": "Tricycle",
}

# what each column should contain after cleaning
GENDERS = {"M", "F"}
VEHICLES = {"Motorcycle", "Bicycle", "Tricycle", "Car"}
CATEGORIES = {"Toys", "Clothes", "Gadgets", "Bags", "Men's Apparel",
              "Makeup", "Electronics", "Appliances", "Laptops"}

# bands for the derived columns, defined once here
AGE_BINS = [-1, 17, 24, 34, 44, 54, 200]
AGE_LABELS = ["Under 18", "18-24", "25-34", "35-44", "45-54", "55+"]
PRICE_BINS = [0, 2500, 5000, 7500, float("inf")]
PRICE_LABELS = ["Under 2500", "2500-4999.99", "5000-7499.99", "7500 and up"]

FACT_COLUMNS = ["date_key", "customer_key", "product_key", "rider_key", "order_id",
                "order_number", "quantity", "unit_price", "line_amount"]


def parse_dates(s: pd.Series) -> pd.Series:
    dash = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    slash = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    return dash.fillna(slash)


def _check_values(s: pd.Series, allowed: set, name: str) -> None:
    unexpected = set(s.dropna().unique()) - allowed
    if unexpected:
        raise ValueError(f"{name}: unexpected values {sorted(unexpected)}")


def _standardize(s: pd.Series, mapping: dict, allowed: set, name: str) -> pd.Series:
    s = s.str.strip()
    s = s.map(mapping).fillna(s)        # known variants are renamed, everything else is kept
    _check_values(s, allowed, name)
    return s


def clean_gender(s: pd.Series) -> pd.Series:
    return _standardize(s, GENDER_MAP, GENDERS, "gender")


def clean_category(s: pd.Series) -> pd.Series:
    return _standardize(s, CATEGORY_MAP, CATEGORIES, "category")


def clean_vehicle(s: pd.Series) -> pd.Series:
    return _standardize(s, VEHICLE_MAP, VEHICLES, "vehicle type")


def clean_zip(s: pd.Series) -> pd.Series:
    z = s.str.strip().str[:5]           # ZIP+4 becomes the 5-digit ZIP
    if not z.dropna().str.fullmatch(r"\d{5}").all():
        raise ValueError("zip code: value is not 5 digits after trimming")
    return z


def clean_price(s: pd.Series) -> pd.Series:
    p = pd.to_numeric(s).round(2)
    if p.isna().any() or (p <= 0).any():
        raise ValueError("price: missing or non-positive values")
    return p


def full_name(first: pd.Series, last: pd.Series) -> pd.Series:
    return (first.str.strip() + " " + last.str.strip()).str.strip()


def age_on(birth: pd.Series, on: pd.Timestamp = AS_OF) -> pd.Series:
    had_birthday = (birth.dt.month < on.month) | ((birth.dt.month == on.month) & (birth.dt.day <= on.day))
    return on.year - birth.dt.year - (~had_birthday).astype(int)


def age_group(age: pd.Series) -> pd.Series:
    return pd.cut(age, AGE_BINS, labels=AGE_LABELS).astype(object)


def price_range(price: pd.Series) -> pd.Series:
    return pd.cut(price, PRICE_BINS, labels=PRICE_LABELS, right=False).astype(object)


def to_date_key(d: pd.Series) -> pd.Series:
    return d.dt.year * 10000 + d.dt.month * 100 + d.dt.day      # 2025-09-23 -> 20250923


# ---------- dimensions ----------

def _with_key(df: pd.DataFrame, key: str, sort_by: str) -> pd.DataFrame:
    """Surrogate keys are 1..n in natural-id order, so the same data always gets the same keys."""
    df = df.sort_values(sort_by).reset_index(drop=True)
    df.insert(0, key, df.index + 1)
    return df


def build_dim_date(dates: pd.Series) -> pd.DataFrame:
    days = pd.Series(pd.date_range(dates.min(), dates.max(), freq="D"))
    return pd.DataFrame({
        "date_key": to_date_key(days).astype("int64"),
        "full_date": days.dt.date,
        "day": days.dt.day,
        "day_name": days.dt.day_name(),
        "month": days.dt.month,
        "month_name": days.dt.month_name(),
        "quarter": days.dt.quarter,
        "year": days.dt.year,
        "is_weekend": days.dt.dayofweek >= 5,
    })


def build_dim_customer(users: pd.DataFrame) -> pd.DataFrame:
    birth = parse_dates(users["dateOfBirth"])
    df = pd.DataFrame({
        "user_id": users["id"],
        "username": users["username"].str.strip(),
        "full_name": full_name(users["firstName"], users["lastName"]),
        "gender": clean_gender(users["gender"]),
        "birth_date": birth.dt.date,
        "age_group": age_group(age_on(birth)),
        "city": users["city"].str.strip(),
        "country": users["country"].str.strip(),
        "zip_code": clean_zip(users["zipCode"]),
    })
    return _with_key(df, "customer_key", "user_id")


def build_dim_product(products: pd.DataFrame) -> pd.DataFrame:
    price = clean_price(products["price"])
    df = pd.DataFrame({
        "product_id": products["id"],
        "product_code": products["productCode"].str.strip(),
        "product_name": products["name"].str.strip(),
        "category": clean_category(products["category"]),
        "unit_price": price,
        "price_range": price_range(price),
    })
    return _with_key(df, "product_key", "product_id")


def build_dim_rider(riders: pd.DataFrame, couriers: pd.DataFrame) -> pd.DataFrame:
    courier = couriers.rename(columns={"id": "courierId", "name": "courier_name"})
    riders = riders.merge(courier[["courierId", "courier_name"]], on="courierId", how="left")
    df = pd.DataFrame({
        "rider_id": riders["id"],
        "full_name": full_name(riders["firstName"], riders["lastName"]),
        "gender": clean_gender(riders["gender"]),
        "age": riders["age"],
        "age_group": age_group(riders["age"]),
        "vehicle_type": clean_vehicle(riders["vehicleType"]),
        "courier_name": riders["courier_name"].fillna("Unknown"),
    })
    return _with_key(df, "rider_key", "rider_id")


def prepare_orders(orders: pd.DataFrame, dim_customer: pd.DataFrame,
                   dim_rider: pd.DataFrame) -> pd.DataFrame:
    """One row per order with its keys already looked up. Build it once, reuse it for every OrderItems chunk."""
    prepared = pd.DataFrame({
        "order_id": orders["id"],
        "order_number": orders["orderNumber"].str.strip(),
        "date_key": to_date_key(parse_dates(orders["deliveryDate"])),
        "customer_key": orders["userId"].map(dim_customer.set_index("user_id")["customer_key"]),
        "rider_key": orders["deliveryRiderId"].map(dim_rider.set_index("rider_id")["rider_key"]),
    })
    return prepared.set_index("order_id")


def build_fact_sales(items: pd.DataFrame, orders: pd.DataFrame,
                     dim_product: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (fact rows, rejected rows). A row is rejected if any key can't be found."""
    products = dim_product.set_index("product_id")
    order_ids, product_ids = items["OrderId"], items["ProductId"]
    df = pd.DataFrame({
        "date_key": order_ids.map(orders["date_key"]),
        "customer_key": order_ids.map(orders["customer_key"]),
        "product_key": product_ids.map(products["product_key"]),
        "rider_key": order_ids.map(orders["rider_key"]),
        "order_id": order_ids,
        "order_number": order_ids.map(orders["order_number"]),
        "quantity": items["quantity"],
        "unit_price": product_ids.map(products["unit_price"]),
    })

    required = ["date_key", "customer_key", "product_key", "rider_key", "quantity"]
    bad = df[required].isna().any(axis=1) | (df["quantity"] <= 0)

    fact = df[~bad].copy()
    fact["line_amount"] = (fact["quantity"] * fact["unit_price"]).round(2)
    int_cols = ["date_key", "customer_key", "product_key", "rider_key", "order_id", "quantity"]
    fact = fact.astype({c: "int64" for c in int_cols})
    return fact[FACT_COLUMNS], df[bad]


### TEST DATA ###
if __name__ == "__main__":
    from etl.extract import extract_all, extract_table

    users = extract_all("Users")
    products = extract_all("Products")
    riders = extract_all("Riders")
    couriers = extract_all("Couriers")
    orders = next(extract_table("Orders"))          # first 50,000 orders only
    items = next(extract_table("OrderItems"))       # first 50,000 items

    print("deliveryDate unparsed:", parse_dates(orders["deliveryDate"]).isna().sum())
    print("dateOfBirth unparsed:", parse_dates(users["dateOfBirth"]).isna().sum())
    dims = {
        "dim_customer": build_dim_customer(users),
        "dim_product": build_dim_product(products),
        "dim_rider": build_dim_rider(riders, couriers),
        "dim_date": build_dim_date(parse_dates(orders["deliveryDate"])),
    }
    for name, df in dims.items():
        print(f"{name}: {len(df)} rows, {int(df.isna().sum().sum())} missing values")
        print(df.head(3).to_string(index=False), "\n")

    print(dims["dim_customer"]["age_group"].value_counts(dropna=False), "\n")
    print(dims["dim_product"]["category"].value_counts(), "\n")
    print(dims["dim_product"]["price_range"].value_counts(), "\n")
    print(dims["dim_rider"]["vehicle_type"].value_counts(), "\n")

    prepared = prepare_orders(orders, dims["dim_customer"], dims["dim_rider"])
    fact, rejected = build_fact_sales(items, prepared, dims["dim_product"])
    print(f"fact rows: {len(fact)}, rejected: {len(rejected)}")
    print(fact.head().to_string(index=False))