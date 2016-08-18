ELK Configuration for RackHD

This repo is to store RackHD ELK configure files

./benchmark_elk includes logstash configure and kibana configure files

./esxtop_elk contains all documents required for ESXi performance data collection
To collect ESXi performance data and display in kibana:
    run ./rackhd_esxtop_csv_collector.py on ESXi host
rackhd_esxtop60rc, rackhd_esxtop_template.json and configure_file_generator.py are required to run this script.
    rackhd_esxtop60rc: esxtop configure file
    rackhd_esxtop_template.json: kibana configure file template, this is required to generate new kibana configure file
    configure_file_generator.py: provide libraries for rackhd_esxtop_csv_collector.py

3 files will be generated after above operation:
    rackhd_esxtop.csv: store CPU, memory, network for all virtuals machines
    rackhd_esxtop.logstash: required logstash file to import rackhd_esxtop.csv to ELK
    rackhd_esxtop_kibana.json: required kibana configure file to display collected performance data in ELK
Anther file will be generated is:
    rackhd_esxtop.entity: this file shows VMs and NICs that there performance data are collected

