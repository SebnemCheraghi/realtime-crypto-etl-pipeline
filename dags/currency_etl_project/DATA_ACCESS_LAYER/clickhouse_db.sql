
CREATE DATABASE IF NOT EXISTS crypto_db;


USE crypto_db;


CREATE TABLE IF NOT EXISTS crypto_prices (
    timestamp DateTime CODEC(DoubleDelta, ZSTD),
    currency_id String,
    symbol LowCardinality(String),
    name String,
    current_price Float64,
    market_cap UInt64,
    total_volume UInt64,
    high_24h Float64,
    low_24h Float64,
    price_change_percentage_24h Float64
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (currency_id, timestamp)
SETTINGS index_granularity = 8192;