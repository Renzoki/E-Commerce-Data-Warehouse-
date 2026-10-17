-- Star schema for ecommerce_dw
-- Grain of fact_sales: one product line in one order (one row per source OrderItems row)
-- Run: docker exec -i ecommerce-mysql sh -c 'mysql -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" ecommerce_dw' < sql/schema.sql

SET NAMES utf8mb4;

-- fact first, since it references the dimensions
DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_customer;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_rider;

-- hierarchy: year > quarter > month > day (one row per delivery date)
CREATE TABLE dim_date (
    date_key    INT         NOT NULL,   -- YYYYMMDD
    full_date   DATE        NOT NULL,
    day         TINYINT     NOT NULL,
    day_name    VARCHAR(9)  NOT NULL,
    month       TINYINT     NOT NULL,
    month_name  VARCHAR(9)  NOT NULL,
    quarter     TINYINT     NOT NULL,
    year        SMALLINT    NOT NULL,
    is_weekend  BOOLEAN     NOT NULL,
    PRIMARY KEY (date_key),
    UNIQUE KEY uq_dim_date_full_date (full_date)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- hierarchies: country > city > customer, age_group > customer
CREATE TABLE dim_customer (
    customer_key  INT          NOT NULL AUTO_INCREMENT,
    user_id       INT          NOT NULL,   -- source Users.id
    username      VARCHAR(255) NOT NULL,
    full_name     VARCHAR(255) NOT NULL,
    gender        CHAR(1),                 -- M / F
    birth_date    DATE,
    age_group     VARCHAR(10),
    city          VARCHAR(255),
    country       VARCHAR(255),
    zip_code      CHAR(5),
    PRIMARY KEY (customer_key),
    UNIQUE KEY uq_dim_customer_user_id (user_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- hierarchy: category > product
CREATE TABLE dim_product (
    product_key   INT           NOT NULL AUTO_INCREMENT,
    product_id    INT           NOT NULL,  -- source Products.id
    product_code  VARCHAR(255)  NOT NULL,
    product_name  VARCHAR(255)  NOT NULL,
    category      VARCHAR(50)   NOT NULL,  -- cleaned (BAG/Bags, Toy/TOYS, make up/Makeup merged)
    unit_price    DECIMAL(10,2) NOT NULL,
    price_range   VARCHAR(20)   NOT NULL,
    PRIMARY KEY (product_key),
    UNIQUE KEY uq_dim_product_product_id (product_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- hierarchies: courier > rider, vehicle_type > rider
-- courier is denormalized here instead of a separate dim_courier (keeps it a star, not a snowflake)
CREATE TABLE dim_rider (
    rider_key     INT          NOT NULL AUTO_INCREMENT,
    rider_id      INT          NOT NULL,   -- source Riders.id
    full_name     VARCHAR(255) NOT NULL,
    gender        CHAR(1),                 -- M / F
    age           TINYINT,
    age_group     VARCHAR(10),
    vehicle_type  VARCHAR(20),             -- cleaned (Bike/Bicycle, Motorbike/Motorcycle merged)
    courier_name  VARCHAR(255) NOT NULL,
    PRIMARY KEY (rider_key),
    UNIQUE KEY uq_dim_rider_rider_id (rider_id)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;

-- no secondary indexes yet: this is the baseline for the query optimization phase
-- (InnoDB still creates an index for each foreign key column)
CREATE TABLE fact_sales (
    sales_id      BIGINT        NOT NULL AUTO_INCREMENT,
    date_key      INT           NOT NULL,
    customer_key  INT           NOT NULL,
    product_key   INT           NOT NULL,
    rider_key     INT           NOT NULL,
    order_id      INT           NOT NULL,  -- degenerate dimension
    order_number  VARCHAR(255)  NOT NULL,  -- degenerate dimension
    quantity      INT           NOT NULL,
    unit_price    DECIMAL(10,2) NOT NULL,
    line_amount   DECIMAL(12,2) NOT NULL,  -- quantity * unit_price
    PRIMARY KEY (sales_id),
    CONSTRAINT fk_fact_sales_date     FOREIGN KEY (date_key)     REFERENCES dim_date (date_key),
    CONSTRAINT fk_fact_sales_customer FOREIGN KEY (customer_key) REFERENCES dim_customer (customer_key),
    CONSTRAINT fk_fact_sales_product  FOREIGN KEY (product_key)  REFERENCES dim_product (product_key),
    CONSTRAINT fk_fact_sales_rider    FOREIGN KEY (rider_key)    REFERENCES dim_rider (rider_key)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
