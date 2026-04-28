import time
import random
from datetime import datetime, timezone
import os

from influxdb_client import InfluxDBClient, Point, WritePrecision

# --- CONFIG ---
url = "http://localhost:8086"
token = os.getenv("INFLUX_TOKEN")
org = "afspace"
bucket = "test_data"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

def simulate_tvac():
	return {
		"temp": random.uniform(20, 120),
		"pressure": random.uniform(0.8, 1.2),
		"vibration": random.uniform(0, 5)
	}

while True:
	data = simulate_tvac()
	now = datetime.now(timezone.utc)

	points = []

	for key, value in data.items():
		p = (
			Point("tvac")
			.tag("system", key)
			.field("value", value)
			.time(now, WritePrecision.NS)
		)
		points.append(p)

	write_api.write(bucket=bucket, org=org, record=points)

	print(data)
	time.sleep(1)
