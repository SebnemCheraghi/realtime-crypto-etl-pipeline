CREATE DATABASE IF NOT EXISTS sqlserver_monitoring;

-- 1. Server Level Metrics (CPU, RAM, Connections, Sessions, Uptime)
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_server
(
    server_name String,
    sql_cpu_utilization UInt8,
    other_cpu_utilization UInt8,
    sql_memory_mb UInt64,
    total_ram_mb UInt64,
    free_ram_mb UInt64,
    connection_count UInt32,
    active_session_count UInt32,
    uptime_seconds UInt64,
    database_count UInt16,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, created_at);

-- 2. Database Level Inventory & Sizes
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_database
(
    server_name String,
    database_name String,
    recovery_model_desc String,
    file_name String,
    file_type String,
    size_mb Float64,
    used_space_mb Float64,
    free_space_mb Float64,
    auto_growth_setting String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, database_name, created_at);

-- 3. Disk I/O Performance Metrics
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_disk_io
(
    server_name String,
    database_name String,
    logical_file_name String,
    file_type String,
    num_of_reads UInt64,
    num_of_bytes_read UInt64,
    io_stall_read_ms UInt64,
    num_of_writes UInt64,
    num_of_bytes_written UInt64,
    io_stall_write_ms UInt64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, database_name, created_at);

-- 4. Table & Index Health Metrics
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_table_index_health
(
    server_name String,
    database_name String,
    schema_name String,
    table_name String,
    index_name String,
    index_type String,
    row_count UInt64,
    user_seeks UInt64,
    user_scans UInt64,
    user_lookups UInt64,
    user_updates UInt64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, database_name, table_name, created_at);

-- 5. Missing Index Recommendations
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_missing_indexes
(
    server_name String,
    database_name String,
    table_name String,
    equality_columns Nullable(String),
    inequality_columns Nullable(String),
    included_columns Nullable(String),
    unique_compiles UInt64,
    user_seeks UInt64,
    user_scans UInt64,
    avg_total_user_cost Float64,
    avg_user_impact Float64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, database_name, created_at);

-- 6. Index Fragmentation Details
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_index_fragmentation
(
    server_name String,
    database_name String,
    table_name String,
    index_name String,
    avg_fragmentation_pct Float32,
    page_count UInt64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, database_name, created_at);

-- 7. Wait Statistics History
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_wait_stats
(
    server_name String,
    wait_type String,
    waiting_tasks_count UInt64,
    wait_time_ms UInt64,
    signal_wait_time_ms UInt64,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, created_at);

-- 8. Active Requests, Blocking, Deadlocks & Long Queries
CREATE TABLE IF NOT EXISTS sqlserver_monitoring.metrics_active_requests
(
    server_name String,
    session_id Int32,
    blocking_session_id Int32,
    database_name String,
    status String,
    command String,
    wait_type String,
    wait_time_ms UInt64,
    total_elapsed_time_ms UInt64,
    query_text String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (server_name, created_at);