import duckdb as ddb

pscp = ddb.sql(r"FROM read_csv('D:\pscp\search_contracts_edc2ddf18b65535f0363cb86c01c4eef3b78e083_en.csv')")

ddb.sql('DESCRIBE pscp')

ddb.sql('SELECT "Vendor Name", COUNT(DISTINCT "Procurement Identification Number") as cnt FROM pscp  WHERE "Contract Year" > 2019 GROUP BY "Vendor Name" ORDER BY cnt')

# for each PIN, keep the max total cost
ddb.sql(
"""
WITH cte AS
( SELECT b."Vendor Name", a.Total_Value
FROM
(SELECT "Procurement Identification Number",
       MAX("Total Contract Value") as Total_Value
FROM pscp 
WHERE "Contract Year" > 2019 
GROUP BY "Procurement Identification Number") a
LEFT JOIN 
(SELECT DISTINCT "Procurement Identification Number", UPPER("Vendor Name") as "Vendor Name" from pscp) b
ON a."Procurement Identification Number" = b."Procurement Identification Number" )
SELECT "Vendor Name",
SUM(Total_Value) as Sum_Total_Value 
FROM cte 
GROUP BY "Vendor Name"
ORDER BY Sum_Total_Value   
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

