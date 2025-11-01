CREATE DATABASE IF NOT EXISTS mi_base;

CREATE EXTERNAL TABLE IF NOT EXISTS mi_base.personas (
  id INT,
  nombre STRING,
  edad INT
)
PARTITIONED BY (pais STRING)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
  'separatorChar' = ',',
  'quoteChar' = '"'
)
STORED AS TEXTFILE
LOCATION 's3://pechel-use1-lake/datasets/personas/'
TBLPROPERTIES ('skip.header.line.count'='1');

MSCK REPAIR TABLE `personas`;

select * from personas;
