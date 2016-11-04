
This repo is designed to collect RackHD host performance, benchmarkand and logs for @Scale test.
All data will be stored in Elasticsearch and can be displayed in Kibana <br />

Here are steps to use this tool in the VM that is running ELK stack.

1. Enter ~/elk folder, edit information about RackHD and esxi server in the file named "hosts"

    [rackhd] - rackhd IP

    [esxi_server] - IPs about esxi server. one IP per line

    [elk:vars]

        benchmark/esxtop/rackhdlog - whether to collect benchmark/esxtop/rackhlog data. "true" to collect them.

        rackhd* - username/password/APIport information about rackhd

        esxi* - username/password information about esxi server. Currently these servers should have the same configurations

2. Run setup_env.yml to setup the environment
    It only needs to run once for the one set of @Scale environment
    ```
    ansible-playbook -i hosts setup_env.yml
    ```
3. Run start.yml to start collecting performance data

    ```
    ansible-playbook -i hosts start.yml
    ```
4. Run stop.yml to stop data collection and port data to elasticsearch and kibana

    ```
    ansible-playbook -i hosts stop.yml
    ```
5. View the dashboard for performance data in kibana
    Open an browser and type "<vm(ELK) ip>:5601", choose "dashboard" in the left bar, select "open" on top
    of the screen, and choose one dashboard from the drop down menu.
    The name of the dashboard is build as <data source>_<IP(only for esxi server)>_<day>_<time>

(Old for reference below)

Here are steps to use this tool:<br />
1. Configure username, password and IP address for RackHD OVA, ESXi host deployed with RackHD OVA and test server (localhost) in "hosts" file.<br />
2. Run rackhd_elk.py to collect data. Below are some command examples:<br />
    >a. ./rackhd_elk.py --start<br />
        >>Start RackHD ELK data collection<br />
    >b. ./rackhd_elk.py --stop<br />
        >>Stop RackHD ELK data collection and configure ELK<br />
    >c. ./rackhd_elk.py --start -d 3600 -a<br />
        >>Run test for one hour and automatically complete data colleciton and configure ELK<br />
    >d. ./rackhd_elk.py --kill --clear --start <br />
        >>Clear elasticsearch database and kill ELK processes before start test<br />
3. Open browser and enter <localhost_ip>:5601 to access kibana.<br />
    >a. 3 indexes will be created: rackhd_benchmark, esxtop, rackhd_log.<br />
    >b. Two dashboards are configured for RackHD ESXi host and benchmark performance to display CPU, network and memory performance.<br />
