import pandas as pd
import pytest

from etl import transform as t


def test_parse_dates_both_formats():
    out = t.parse_dates(pd.Series(["2025-01-31", "01/31/2025", "garbage"]))
    assert out.iloc[0] == pd.Timestamp("2025-01-31")
    assert out.iloc[1] == pd.Timestamp("2025-01-31")
    assert pd.isna(out.iloc[2])


def test_slash_dates_are_month_first():
    out = t.parse_dates(pd.Series(["03/04/2025"]))
    assert out.iloc[0] == pd.Timestamp("2025-03-04")


def test_clean_gender():
    out = t.clean_gender(pd.Series(["Male", "F", " Female ", "M"]))
    assert out.tolist() == ["M", "F", "F", "M"]
    with pytest.raises(ValueError):
        t.clean_gender(pd.Series(["X"]))


def test_clean_category():
    out = t.clean_category(pd.Series(["BAG", "Toy", "TOYS", "make up", "Laptops"]))
    assert out.tolist() == ["Bags", "Toys", "Toys", "Makeup", "Laptops"]


def test_clean_vehicle():
    out = t.clean_vehicle(pd.Series(["Motorbike", "Bike", "Trike", "Car"]))
    assert out.tolist() == ["Motorcycle", "Bicycle", "Tricycle", "Car"]


def test_clean_zip():
    assert t.clean_zip(pd.Series(["12345", "12345-6789"])).tolist() == ["12345", "12345"]
    with pytest.raises(ValueError):
        t.clean_zip(pd.Series(["12"]))


def test_clean_price():
    assert t.clean_price(pd.Series([1.77046, 9999.42])).tolist() == [1.77, 9999.42]
    with pytest.raises(ValueError):
        t.clean_price(pd.Series([0.0]))


def test_age_on_counts_birthdays_correctly():
    birth = pd.Series(pd.to_datetime(["2006-09-29", "2007-09-23", "2007-09-24"]))
    assert t.age_on(birth).tolist() == [18, 18, 17]


def test_age_group_boundaries():
    out = t.age_group(pd.Series([17, 18, 24, 25, 60]))
    assert out.tolist() == ["Under 18", "18-24", "18-24", "25-34", "55+"]


def test_price_range_boundaries():
    out = t.price_range(pd.Series([100.0, 2500.0, 7500.0]))
    assert out.tolist() == ["Under 2500", "2500-4999.99", "7500 and up"]


def test_dim_date():
    dim = t.build_dim_date(pd.Series(pd.to_datetime(["2025-01-30", "2025-02-02"])))
    assert dim["date_key"].tolist() == [20250130, 20250131, 20250201, 20250202]
    assert dim["is_weekend"].tolist() == [False, False, True, True]
    assert set(dim["quarter"]) == {1}


def test_dim_customer():
    users = pd.DataFrame({
        "id": [2, 1], "username": ["b", "a"],
        "firstName": ["Bea", "Al"], "lastName": ["Cruz", "Diaz"],
        "gender": ["Female", "M"], "dateOfBirth": ["01/15/2007", "2006-10-01"],
        "city": [" Parma", "Edmond"], "country": ["Spain", "Peru"],
        "zipCode": ["12345-6789", "00000"],
    })
    dim = t.build_dim_customer(users)
    assert dim["customer_key"].tolist() == [1, 2]
    assert dim["user_id"].tolist() == [1, 2]
    assert dim["full_name"].tolist() == ["Al Diaz", "Bea Cruz"]
    assert dim["gender"].tolist() == ["M", "F"]
    assert dim["zip_code"].tolist() == ["00000", "12345"]
    assert dim["city"].tolist() == ["Edmond", "Parma"]


def test_fact_sales_keeps_good_rows_and_rejects_unmatched_keys():
    dim_product = pd.DataFrame({"product_id": [10], "product_key": [1], "unit_price": [2.50]})
    orders = pd.DataFrame(
        {"order_number": ["A1"], "date_key": [20250101], "customer_key": [1], "rider_key": [1]},
        index=pd.Index([100], name="order_id"),
    )
    items = pd.DataFrame({"OrderId": [100, 100, 999], "ProductId": [10, 77, 10], "quantity": [3, 1, 2]})

    fact, rejected = t.build_fact_sales(items, orders, dim_product)

    assert len(fact) == 1
    assert fact.iloc[0]["line_amount"] == 7.5
    assert fact.iloc[0]["order_number"] == "A1"
    assert len(rejected) == 2          # unknown product 77, unknown order 999