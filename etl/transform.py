import pandas as pd

GENDER_MAP = {
    "Male" : 'M',
    "M" : 'M',
    "Female" : 'F',
    "F" : 'F',
}

CATEGORY_MAP = {
    "BAG" : 'Bags',
    "GADGETS" : 'Gadgets',
    "make up" : 'Makeup',
    "TOYS" : 'Toys',
    "Toy" : 'Toys'
}
VEHICLE_MAP = {
    "Motorbike" : 'Motorcycle',
    "Bike" : 'Bicycle',
    "Trike" : 'Tricycle',
}

def parse_dates(s: pd.Series) -> pd.Series:
    dash = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")
    slash = pd.to_datetime(s, format="%m/%d/%Y", errors="coerce")
    return dash.fillna(slash)

def clean_gender(s: pd.Series) -> pd.Series:
    return s.map(GENDER_MAP).fillna(s)

def clean_category(s: pd.Series) -> pd.Series:
    return s.map(CATEGORY_MAP).fillna(s)
    
def clean_vehicle(s: pd.Series) -> pd.Series:
    return s.map(VEHICLE_MAP).fillna(s)

### TEST DATA ###
if __name__ == "__main__":
    from etl.extract import extract_all, extract_table

    # dates
    orders = next(extract_table("Orders"))
    print("deliveryDate unparsed:", parse_dates(orders["deliveryDate"]).isna().sum())

    users = next(extract_table("Users"))
    print("dateOfBirth unparsed:", parse_dates(users["dateOfBirth"]).isna().sum())

    # gender
    print("\nUsers gender:")
    print(clean_gender(users["gender"]).value_counts(dropna=False))

    riders = extract_all("Riders")
    print("\nRiders gender:")
    print(clean_gender(riders["gender"]).value_counts(dropna=False))

    # vehicle
    print("\nRiders vehicleType:")
    print(clean_vehicle(riders["vehicleType"]).value_counts(dropna=False))

    # category
    products = extract_all("Products")
    print("\nProducts category:")
    print(clean_category(products["category"]).value_counts(dropna=False))