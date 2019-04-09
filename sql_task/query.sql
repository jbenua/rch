SELECT a.user_id, SUM(a.amount)
FROM (
    SELECT
        m.user_id as user_id,
        m.amount * exchange_rates.rate as amount
    FROM (
        SELECT
            transactions.ts ts,
            user_id,
            currency,
            amount,
            MAX(exchange_rates.ts) mer,
            from_currency,
            to_currency
        FROM transactions INNER JOIN exchange_rates ON currency = from_currency
        WHERE
            transactions.ts >= exchange_rates.ts
        GROUP BY
            transactions.ts,
            user_id,
            currency,
            amount,
            from_currency,
            to_currency
    ) m INNER JOIN exchange_rates ON
        m.mer = exchange_rates.ts AND
        m.from_currency = exchange_rates.from_currency AND
        m.to_currency = exchange_rates.to_currency
    UNION
    SELECT
        user_id,
        amount
    FROM transactions
    WHERE currency = 'GBP'
) a
GROUP BY a.user_id
