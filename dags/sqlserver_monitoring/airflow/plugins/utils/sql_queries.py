# plugins/utils/sql_queries.py

SERVER_LEVEL_QUERIES = {
    # 1. Server Performance & Resources (CPU, Memory, Connections, Sessions, Uptime)
    "server_metrics": """
        WITH SystemIdle AS (
            SELECT 
                record.value('(./Record/SchedulerMonitorEvent/SystemHealth/SystemIdle)[1]', 'int') AS system_idle,
                record.value('(./Record/SchedulerMonitorEvent/SystemHealth/ProcessUtilization)[1]', 'int') AS sql_cpu
            FROM (
                SELECT CAST(record AS xml) AS record 
                FROM sys.dm_os_ring_buffers 
                WHERE ring_buffer_type = N'RING_BUFFER_SCHEDULER_MONITOR' 
                  AND record LIKE '%<SystemHealth>%'
            ) AS x
        )
        SELECT 
            (SELECT TOP 1 sql_cpu FROM SystemIdle) AS sql_cpu_utilization,
            (SELECT TOP 1 (100 - system_idle - sql_cpu) FROM SystemIdle) AS other_cpu_utilization,
            (SELECT physical_memory_in_use_kb / 1024 FROM sys.dm_os_process_memory) AS sql_memory_mb,
            (SELECT total_physical_memory_kb / 1024 FROM sys.dm_os_sys_memory) AS total_ram_mb,
            (SELECT available_physical_memory_kb / 1024 FROM sys.dm_os_sys_memory) AS free_ram_mb,
            (SELECT COUNT(*) FROM sys.dm_exec_connections) AS connection_count,
            (SELECT COUNT(*) FROM sys.dm_exec_sessions WHERE is_user_process = 1) AS active_session_count,
            (SELECT DATEDIFF(SECOND, create_date, GETDATE()) FROM sys.databases WHERE database_id = 2) AS uptime_seconds,
            (SELECT COUNT(*) FROM sys.databases) AS database_count;
    """,

    # 2. Disk I/O Per File
    "disk_io_metrics": """
        SELECT 
            DB_NAME(vfs.database_id) AS database_name,
            mf.name AS logical_file_name,
            mf.type_desc AS file_type,
            vfs.num_of_reads,
            vfs.num_of_bytes_read,
            vfs.io_stall_read_ms,
            vfs.num_of_writes,
            vfs.num_of_bytes_written,
            vfs.io_stall_write_ms
        FROM sys.dm_io_virtual_file_stats(NULL, NULL) vfs
        JOIN sys.master_files mf ON vfs.database_id = mf.database_id AND vfs.file_id = mf.file_id;
    """
}

DATABASE_LEVEL_QUERIES = {
    # 3. Database Sizes, Auto Growth & Recovery Model
    "database_inventory": """
        SELECT 
            d.name AS database_name,
            d.recovery_model_desc,
            mf.name AS file_name,
            mf.type_desc AS file_type,
            CAST(mf.size * 8.0 / 1024 AS DECIMAL(18,2)) AS size_mb,
            CAST(FILEPROPERTY(mf.name, 'SpaceUsed') * 8.0 / 1024 AS DECIMAL(18,2)) AS used_space_mb,
            CAST((mf.size - FILEPROPERTY(mf.name, 'SpaceUsed')) * 8.0 / 1024 AS DECIMAL(18,2)) AS free_space_mb,
            CASE WHEN mf.is_percent_growth = 1 
                 THEN CAST(mf.growth AS VARCHAR) + '%' 
                 ELSE CAST(mf.growth * 8 / 1024 AS VARCHAR) + ' MB' 
            END AS auto_growth_setting
        FROM sys.databases d
        JOIN sys.master_files mf ON d.database_id = mf.database_id;
    """,

    # 4. Table & Index Metrics (Counts, Rows, Unused, Missing, Usage)
    "table_and_index_health": """
        SELECT 
            DB_NAME() AS database_name,
            s.name AS schema_name,
            t.name AS table_name,
            i.name AS index_name,
            i.type_desc AS index_type,
            p.rows AS row_count,
            COALESCE(us.user_seeks, 0) AS user_seeks,
            COALESCE(us.user_scans, 0) AS user_scans,
            COALESCE(us.user_lookups, 0) AS user_lookups,
            COALESCE(us.user_updates, 0) AS user_updates
        FROM sys.tables t
        INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
        INNER JOIN sys.indexes i ON t.object_id = i.object_id
        INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
        LEFT JOIN sys.dm_db_index_usage_stats us ON i.object_id = us.object_id AND i.index_id = us.index_id AND us.database_id = DB_ID()
        WHERE t.is_ms_shipped = 0 AND p.index_id < 2;
    """,

    # 5. Missing Indexes
    "missing_indexes": """
        SELECT 
            DB_NAME(d.database_id) AS database_name,
            d.statement AS table_name,
            d.equality_columns,
            d.inequality_columns,
            d.included_columns,
            s.unique_compiles,
            s.user_seeks,
            s.user_scans,
            s.avg_total_user_cost,
            s.avg_user_impact
        FROM sys.dm_db_missing_index_details d
        JOIN sys.dm_db_missing_index_groups g ON d.index_handle = g.index_handle
        JOIN sys.dm_db_missing_index_group_stats s ON g.index_group_handle = s.group_handle;
    """,

    # 6. Fragmentation
    "index_fragmentation": """
        SELECT 
            DB_NAME() AS database_name,
            OBJECT_NAME(ps.object_id) AS table_name,
            i.name AS index_name,
            CAST(ps.avg_fragmentation_in_percent AS DECIMAL(5,2)) AS avg_fragmentation_pct,
            ps.page_count
        FROM sys.dm_db_index_physical_stats(DB_ID(), NULL, NULL, NULL, 'LIMITED') ps
        INNER JOIN sys.indexes i ON ps.object_id = i.object_id AND ps.index_id = i.index_id
        WHERE ps.avg_fragmentation_in_percent > 10 AND ps.page_count > 100;
    """
}

PERFORMANCE_QUERIES = {
    # 7. Wait Statistics
    "wait_statistics": """
        SELECT TOP 20
            wait_type,
            waiting_tasks_count,
            wait_time_ms,
            signal_wait_time_ms
        FROM sys.dm_os_wait_stats
        WHERE wait_type NOT IN (
            'CLR_SEMAPHORE', 'LAZYWRITER_SLEEP', 'RESOURCE_QUEUE', 'SLEEP_TASK',
            'SLEEP_SYSTEMTASK', 'SQLTRACE_BUFFER_FLUSH', 'WAITFOR', 'LOGMGR_QUEUE',
            'CHECKPOINT_QUEUE', 'REQUEST_FOR_DEADLOCK_SEARCH', 'XE_TIMER_EVENT'
        ) AND wait_time_ms > 0
        ORDER BY wait_time_ms DESC;
    """,

    # 8. Blocking, Deadlocks, Long Running Queries
    "active_requests": """
        SELECT 
            r.session_id,
            r.blocking_session_id,
            DB_NAME(r.database_id) AS database_name,
            r.status,
            r.command,
            r.wait_type,
            r.wait_time AS wait_time_ms,
            r.total_elapsed_time AS total_elapsed_time_ms,
            CAST(t.text AS VARCHAR(MAX)) AS query_text
        FROM sys.dm_exec_requests r
        CROSS APPLY sys.dm_exec_sql_text(r.sql_handle) t
        WHERE r.session_id > 50 AND (r.blocking_session_id <> 0 OR r.total_elapsed_time > 3000);
    """
}