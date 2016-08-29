This repo is designed to collect RackHD host, processes performance data and RackHD logs for @Scale test.
All data will be stored in Elasticsearch and can be displayed in Kibana
You can use scripts in this repo to collect RackHD services performance data, ESXi host performance data and RackHD logs.
Data will be stored in elasticsearch. Performance data can be displayed in Kibana with pre-set dashboard.

Here are steps to use this tool:
1. Configure username, password and IP address for RackHD OVA, ESXi host deployed with RackHD OVA and test server (localhost).
2. Run rackhd_elk.py to collect data. Below are some command examples:
    a. ./rackhd_elk.py --start
        Start RackHD ELK data collection
    b. ./rackhd_elk.py --stop
        Stop RackHD ELK data collection and configure ELK
    c. ./rackhd_elk.py --start -d 3600 -a
        Run test for one hour and automatically complete data colleciton and display in Kibana
    d. ./rackhd_elk.py --kill --clear --start 
        Clear elasticsearch database and kill ELK processes before start test
3. Open browser and enter <localhost_ip>:5601 to access kibana.
    a. 3 indexes will be created: rackhd_benchmark, esxtop, rackhd_log. 
    b. Two dashboards are configured for RackHD ESXi host and benchmark performance to display CPU, network and memory performance. 
