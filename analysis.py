import duckdb as ddb

pscp = ddb.sql(r"FROM read_csv('D:\pscp\search_contracts_edc2ddf18b65535f0363cb86c01c4eef3b78e083_en.csv')")

ddb.sql('DESCRIBE pscp')

ddb.sql('SELECT "Vendor Name", COUNT(DISTINCT "Procurement Identification Number") as cnt FROM pscp  WHERE "Contract Year" > 2019 GROUP BY "Vendor Name" ORDER BY cnt')



info = ddb.sql(
"""
SELECT DISTINCT 
"Procurement Identification Number" AS pin, 
UPPER("Vendor Name") AS "vendor_name"--,
--UPPER("Description of Work English") AS description,
--UPPER("Standing Offer") AS standing_offer
FROM pscp
""")

# for each PIN, keep the max total cost
contracts = ddb.sql("""
SELECT "Procurement Identification Number" as pin,
       MAX("Total Contract Value") as total_value
FROM pscp 
WHERE "Contract Year" > 2019 
GROUP BY pin
""")

total_contracts = ddb.sql(
"""
WITH cte AS
( SELECT b.vendor_name, a.total_value
FROM contracts a
LEFT JOIN info b
ON a.pin = b.pin )
SELECT vendor_name,
SUM(total_value) as sum_total_value 
FROM cte 
GROUP BY vendor_name
ORDER BY sum_total_value   
"""
)

ddb.sql(
"""SELECT 
"Vendor Name", 

"Contract Year", 
"Contract Period Start Date","Contract Period End Date or Delivery Date","Total Contract Value","Original Contract Value","Contract Amendment Value"
FROM pscp 
WHERE "Procurement Identification Number" = '000013769'
"""
)

