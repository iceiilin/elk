This repo is designed to collect RackHD host performance, benchmarkand and logs for @Scale test.
All data will be stored in Elasticsearch and can be displayed in Kibana <br />
Here are steps to use this tool:<br />
1. Configure username, password and IP address for RackHD OVA, ESXi host deployed with RackHD OVA and test server (localhost) in "hosts" file.<br />
2. Run rackhd_elk.py to collect data. Below are some command examples:<br />
    a. ./rackhd_elk.py --start<br />
        Start RackHD ELK data collection<br />
    b. ./rackhd_elk.py --stop<br />
        Stop RackHD ELK data collection and configure ELK<br />
    c. ./rackhd_elk.py --start -d 3600 -a<br />
        Run test for one hour and automatically complete data colleciton and configure ELK<br />
    d. ./rackhd_elk.py --kill --clear --start <br />
        Clear elasticsearch database and kill ELK processes before start test<br />
3. Open browser and enter <localhost_ip>:5601 to access kibana.<br />
    a. 3 indexes will be created: rackhd_benchmark, esxtop, rackhd_log.<br />
    b. Two dashboards are configured for RackHD ESXi host and benchmark performance to display CPU, network and memory performance.<br />
