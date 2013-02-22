#!/usr/bin/python
#
# Copyright (c) 2013 Evgeny Gridasov (evgeny.gridasov@gmail.com)
# Copyright (c) 2013 ITOC Australia  http://itoc.com.au
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
import urllib2
import argparse
import re
try:
	import simplejson as json
except ImportError:
	import json

ELC_REGIONS = [
	"us-east-1",
	"us-west-1",
	"us-west-2",
	"eu-west-1",
	"ap-southeast-1",
	"ap-southeast-2",
	"ap-northeast-1",
	"sa-east-1"
]

ELC_INSTANCE_TYPES = [
	"cache.t1.micro",
	"cache.m1.small",
	"cache.m1.medium",
	"cache.m1.large",
	"cache.m1.xlarge",
	"cache.m2.xlarge",
	"cache.m2.2xlarge",
	"cache.m2.4xlarge",
	"cache.c1.xlarge",
	"cache.m3.xlarge",
	"cache.m3.2xlarge"
]

JSON_NAME_TO_ELC_REGIONS_API = {
	"us-east" : "us-east-1",
	"us-east-1" : "us-east-1",
	"us-west" : "us-west-1",
	"us-west-1" : "us-west-1",
	"us-west-2" : "us-west-2",
	"eu-ireland" : "eu-west-1",
	"eu-west-1" : "eu-west-1",
	"apac-sin" : "ap-southeast-1",
	"ap-southeast-1" : "ap-southeast-1",
	"ap-southeast-2" : "ap-southeast-2",
	"apac-syd" : "ap-southeast-2",
	"apac-tokyo" : "ap-northeast-1",
	"ap-northeast-1" : "ap-northeast-1",
	"sa-east-1" : "sa-east-1"
}

INSTANCES_ON_DEMAND_URL="http://aws.amazon.com/elasticache/pricing/pricing-standard-deployments.json"
INSTANCES_RESERVED_LIGHT_UTILIZATION_URL="http://aws.amazon.com/elasticache/pricing/pricing-elasticache-light-standard-deployments.json"
INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL="http://aws.amazon.com/elasticache/pricing/pricing-elasticache-medium-standard-deployments.json"
INSTANCES_RESERVED_HEAVY_UTILIZATION_URL="http://aws.amazon.com/elasticache/pricing/pricing-elasticache-heavy-standard-deployments.json"

INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL = {
	INSTANCES_RESERVED_LIGHT_UTILIZATION_URL : "light",
	INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL : "medium",
	INSTANCES_RESERVED_HEAVY_UTILIZATION_URL : "heavy",
}

DEFAULT_CURRENCY = "USD"

INSTANCE_TYPE_MAPPING = {
	"microInstClass.microInst": "cache.t1.micro",
	"dbInstClass.smDBInst" : "cache.m1.small",
	"dbInstClass.medInst" : "cache.m1.medium",
	"dbInstClass.lgDBInst" : "cache.m1.large",
	"dbInstClass.xlDBInst" : "cache.m1.xlarge",
	"hiMemDBInstClass.xlDBInst" : "cache.m2.xlarge",
	"hiMemDBInstClass.xxlDBInst" : "cache.m2.2xlarge",
	"hiMemDBInstClass.xxxxDBInst" : "cache.m2.4xlarge",
	"hiCPUDBInstClass.hiCPUxlDBInst" : "cache.c1.xlarge",
	"enInstClass.xlDBInst" : "cache.m3.xlarge",
	"enInstClass.xxlDBInst" : "cache.m3.2xlarge",
	
	#Reserved
	"stdDeployRes.mic" : "cache.t1.micro",
	"stdDeployRes.sm" : "cache.m1.small",
	"stdDeployRes.medInst" : "cache.m1.medium",
	"stdDeployRes.lg" : "cache.m1.large",
	"stdDeployRes.xl" : "cache.m1.xlarge",
	"stdDeployRes.xlHiMem" : "cache.m2.xlarge",
	"stdDeployRes.xxlHiMem" : "cache.m2.2xlarge",
	"stdDeployRes.xxxxlHiMem" : "cache.m2.4xlarge",
	"stdDeployRes.xlHiCPU" : "cache.c1.xlarge",
	"stdDeployRes.xlEn" : "cache.m3.xlarge",
	"stdDeployRes.xxlEn" : "cache.m3.2xlarge",
}

def _load_data(url):
	f = urllib2.urlopen(url)
	return json.loads(f.read())

def get_elc_reserved_instances_prices(filter_region=None, filter_instance_type=None):
	""" Get Elasticache reserved instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	get_specific_instance_type = (filter_instance_type is not None)

	currency = DEFAULT_CURRENCY

	urls = [
		INSTANCES_RESERVED_LIGHT_UTILIZATION_URL,
		INSTANCES_RESERVED_MEDIUM_UTILIZATION_URL,
		INSTANCES_RESERVED_HEAVY_UTILIZATION_URL
	]

	result_regions = []
	result_regions_index = {}
	result = {
		"config" : {
			"currency" : currency,
		},
		"regions" : result_regions
	}

	for u in urls:
		utilization_type = INSTANCES_RESERVED_UTILIZATION_TYPE_BY_URL[u]
		data = _load_data(u)
		if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
			for r in data["config"]["regions"]:
				if "region" in r and r["region"]:

					region_name = JSON_NAME_TO_ELC_REGIONS_API[r["region"]]
					if get_specific_region and filter_region != region_name:
						continue
					if region_name in result_regions_index:
						instance_types = result_regions_index[region_name]["instanceTypes"]
					else:
						instance_types = []
						result_regions.append({
							"region" : region_name,
							"instanceTypes" : instance_types
						})
						result_regions_index[region_name] = result_regions[-1]
						
					if "instanceTypes" in r:
						for it in r["instanceTypes"]:
							instance_class = it["type"]
							if "tiers" in it:
								for s in it["tiers"]:
									_type = INSTANCE_TYPE_MAPPING[instance_class + "." + s["size"] ]
	
									if get_specific_instance_type and _type != filter_instance_type:
										continue
	
									prices = {
										"1year" : {
											"hourly" : None,
											"upfront" : None
										},
										"3year" : {
											"hourly" : None,
											"upfront" : None
										}
									}

									instance_types.append({
										"type" : _type,
										"utilization" : utilization_type,
										"prices" : prices
									})
	
									for price_data in s["valueColumns"]:
										price = None
										try:
											price = float(re.sub("[^0-9\\.]", "", price_data["prices"][currency]))
										except ValueError:
											price = None
	
										if price_data["name"] == "yrTerm1":
											prices["1year"]["upfront"] = price
										elif price_data["name"] == "yearTerm1Hourly":
											prices["1year"]["hourly"] = price
										elif price_data["name"] == "yrTerm3":
											prices["3year"]["upfront"] = price
										elif price_data["name"] == "yearTerm3Hourly":
											prices["3year"]["hourly"] = price			

	return result

def get_elc_ondemand_instances_prices(filter_region=None, filter_instance_type=None):
	""" Get Elasticache on-demand instances prices. Results can be filtered by region """

	get_specific_region = (filter_region is not None)
	get_specific_instance_type = (filter_instance_type is not None)

	currency = DEFAULT_CURRENCY

	result_regions = []
	result = {
		"config" : {
			"currency" : currency,
			"unit" : "perhr"
		},
		"regions" : result_regions
	}

	data = _load_data(INSTANCES_ON_DEMAND_URL)
	if "config" in data and data["config"] and "regions" in data["config"] and data["config"]["regions"]:
		for r in data["config"]["regions"]:
			if "region" in r and r["region"]:
				region_name = JSON_NAME_TO_ELC_REGIONS_API[r["region"]]
				if get_specific_region and filter_region != region_name:
					continue
				instance_types = []
				if "types" in r:
					for it in r["types"]:
						instance_class = it["name"]
						if "tiers" in it:
							for s in it["tiers"]:
								_type = INSTANCE_TYPE_MAPPING[instance_class + "." + s["name"] ]

								if get_specific_instance_type and _type != filter_instance_type:
									continue
								
								price = None
								try:
									price = float(re.sub("[^0-9\\.]", "", s["prices"][currency]))
								except ValueError:
									price = None

								instance_types.append({
									"type" : _type,
									"price" : price
								})

					result_regions.append({
						"region" : region_name,
						"instanceTypes" : instance_types
					})

		return result

	return None

if __name__ == "__main__":
	def none_as_string(v):
		if not v:
			return ""
		else:
			return v

	try:
		import argparse 
	except ImportError:
		print "ERROR: You are running Python < 2.7. Please use pip to install argparse:   pip install argparse"


	parser = argparse.ArgumentParser(add_help=True, description="Print out the current prices of Elasticache instances")
	parser.add_argument("--type", "-t", help="Show ondemand or reserved instances", choices=["ondemand", "reserved"], required=True)
	parser.add_argument("--filter-region", "-fr", help="Filter results to a specific region", choices=ELC_REGIONS, default=None)
	parser.add_argument("--filter-type", "-ft", help="Filter results to a specific instance type", choices=ELC_INSTANCE_TYPES, default=None)
	parser.add_argument("--format", "-f", choices=["json", "table", "csv"], help="Output format", default="table")

	args = parser.parse_args()

	if args.format == "table":
		try:
			from prettytable import PrettyTable
		except ImportError:
			print "ERROR: Please install 'prettytable' using pip:    pip install prettytable"

	data = None
	if args.type == "ondemand":
		data = get_elc_ondemand_instances_prices(args.filter_region, args.filter_type)
	elif args.type == "reserved":
		data = get_elc_reserved_instances_prices(args.filter_region, args.filter_type)

	if args.format == "json":
		print json.dumps(data)
	elif args.format == "table":
		x = PrettyTable()

		if args.type == "ondemand":
			try:			
				x.set_field_names(["region", "type", "price"])
			except AttributeError:
				x.field_names = ["region", "type", "price"]

			try:
				x.aligns[-1] = "l"
			except AttributeError:
				x.align["price"] = "l"

			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					x.add_row([region_name, it["type"], none_as_string(it["price"])])
		elif args.type == "reserved":
			try:
				x.set_field_names(["region", "type", "utilization", "term", "price", "upfront"])
			except AttributeError:
				x.field_names = ["region", "type", "utilization", "term", "price", "upfront"]

			try:
				x.aligns[-1] = "l"
				x.aligns[-2] = "l"
			except AttributeError:
				x.align["price"] = "l"
				x.align["upfront"] = "l"
			
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					for term in it["prices"]:
						x.add_row([region_name, it["type"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"])])

		print x
	elif args.format == "csv":
		if args.type == "ondemand":
			print "region,type,os,price"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					print "%s,%s,%s" % (region_name, it["type"], none_as_string(it["price"]))
		elif args.type == "reserved":
			print "region,type,utilization,term,price,upfront"
			for r in data["regions"]:
				region_name = r["region"]
				for it in r["instanceTypes"]:
					for term in it["prices"]:
						print "%s,%s,%s,%s,%s,%s" % (region_name, it["type"], it["utilization"], term, none_as_string(it["prices"][term]["hourly"]), none_as_string(it["prices"][term]["upfront"]))
