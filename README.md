elasticachepricing.py
=====================

Written by Evgeny Gridasov     

http://itoc.com.au

http://cloudedify.com


elasticachepricing.py is a quick & dirty library and a command line interface (CLI)
to get a list of all Amazon Web Services ElastiCache instances pricing (reserved/ondemand).

The data is based on a set of JSON files used in the ElastiCache page (http://aws.amazon.com/elasticache).

Data can be filtered by region and instance type.

Running this file will activate its CLI interface in which you can get output to your console in a CSV, JSON and table formats (default is table).

To run the command line interface, you need to install:
argparse - if you are running Python < 2.7
prettytable - to get a nice table output to your console

Both of these libraries can be installed using the 'pip install' command.

Original idea by Eran Sandler https://github.com/erans/ec2instancespricing
