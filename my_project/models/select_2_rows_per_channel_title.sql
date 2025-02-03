WITH ranked_messages AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY channel_title ORDER BY id DESC) AS row_num  -- Replace 'created_at' with an actual column
    FROM {{ source('my_source', 'telegram_messages') }}  -- Referencing the source table
)
SELECT * 
FROM ranked_messages
WHERE row_num <= 2
