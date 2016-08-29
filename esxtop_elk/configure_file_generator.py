#!/usr/bin/env python
"""
This script is used to auto-generate kibana configure file for esxtop performance charts
"""
import re
import copy
import json

# pylint: disable=line-too-long, anomalous-backslash-in-string, too-many-locals
HEADINGS = [
    '_timestamp',
    'Memory_Memory-Overcommit-(1-Minute-Avg)',
    'Physical-Cpu-Load_Cpu-Load-(1-Minute-Avg)',
    'Physical-Cpu-Load_Cpu-Load-(5-Minute-Avg)',
    'Physical-Cpu(_Total)_%-Processor-Time',
    'Physical-Cpu(_Total)_%-Util-Time',
    'Physical-Cpu(_Total)_%-Core-Util-Time',
    'Group-Cpu(19299:Krein)_%-Used',
    'Group-Cpu(28868:Ted_DEV_ORA)_%-Used',
    'Group-Cpu(29116:C6320)_%-Used',
    'Group-Cpu(3404747:quanta_t41)_%-Used',
    'Group-Memory(19299:Krein)_Memory-Consumed-Size-MBytes',
    'Group-Memory(19299:Krein)_Touched-MBytes',
    'Group-Memory(28868:Ted_DEV_ORA)_Memory-Consumed-Size-MBytes',
    'Group-Memory(28868:Ted_DEV_ORA)_Touched-MBytes',
    'Group-Memory(29116:C6320)_Memory-Consumed-Size-MBytes',
    'Group-Memory(29116:C6320)_Touched-MBytes',
    'Group-Memory(3404747:quanta_t41)_Memory-Consumed-Size-MBytes',
    'Group-Memory(3404747:quanta_t41)_Touched-MBytes',
    'Network-Port(vSwitch0:33554434:vmnic2)_MBits-Transmitted/sec',
    'Network-Port(vSwitch0:33554434:vmnic2)_MBits-Received/sec',
    'Network-Port(vSwitch0:33554437:36139:Krein)_MBits-Transmitted/sec',
    'Network-Port(vSwitch0:33554437:36139:Krein)_MBits-Received/sec',
    'Network-Port(vSwitch0:33554438:37496:Ted_DEV_ORA)_MBits-Transmitted/sec',
    'Network-Port(vSwitch0:33554438:37496:Ted_DEV_ORA)_MBits-Received/sec',
    'Network-Port(vSwitch1:50331650:vmnic5)_MBits-Transmitted/sec',
    'Network-Port(vSwitch1:50331650:vmnic5)_MBits-Received/sec',
    'Network-Port(vSwitch6:134217730:36139:Krein)_MBits-Transmitted/sec',
    'Network-Port(vSwitch6:134217730:36139:Krein)_MBits-Received/sec',
    'Network-Port(vSwitch6:134217731:506106:quanta_t41)_MBits-Transmitted/sec',
    'Network-Port(vSwitch6:134217731:506106:quanta_t41)_MBits-Received/sec',
    'Network-Port(vSwitch7:150994946:37496:Ted_DEV_ORA)_MBits-Transmitted/sec',
    'Network-Port(vSwitch7:150994946:37496:Ted_DEV_ORA)_MBits-Received/sec',
    'Network-Port(vSwitch7:150994947:37511:C6320)_MBits-Transmitted/sec',
    'Network-Port(vSwitch7:150994947:37511:C6320)_MBits-Received/sec',
    'Network-Port(vSwitch8:167772162:vmnic3)_MBits-Transmitted/sec',
    'Network-Port(vSwitch8:167772162:vmnic3)_MBits-Received/sec',
    'Network-Port(vSwitch8:167772164:36139:Krein)_MBits-Transmitted/sec',
    'Network-Port(vSwitch8:167772164:36139:Krein)_MBits-Received/sec',
    'Network-Port(vSwitch8:167772165:36139:Krein)_MBits-Transmitted/sec',
    'Network-Port(vSwitch8:167772165:36139:Krein)_MBits-Received/sec',
    'Network-Port(vSwitch8:167772166:37496:Ted_DEV_ORA)_MBits-Transmitted/sec',
    'Network-Port(vSwitch8:167772166:37496:Ted_DEV_ORA)_MBits-Received/sec',
    'Network-Port(vSwitch8:167772167:37496:Ted_DEV_ORA)_MBits-Transmitted/sec',
    'Network-Port(vSwitch8:167772167:37496:Ted_DEV_ORA)_MBits-Received/sec'
]
######################################kibana dashboard json file#############################################
"""
{
    "_id": "rack_hd_normal_dashboard",
    "_type": "dashboard",
    "_source": {
      "title": "rack_hd_normal_dashboard",
      "hits": 0,
      "description": "",
      "panelsJSON": "[
          {\"id\":\"physical_network_usage\",\"type\":\"visualization\",\"panelIndex\":1,\"size_x\":7,\"size_y\":3,\"col\":1,\"row\":1},
          {\"id\":\"cpu_usage\",\"type\":\"visualization\",\"panelIndex\":2,\"size_x\":7,\"size_y\":3,\"col\":1,\"row\":4},
          {\"id\":\"memory_usage\",\"type\":\"visualization\",\"panelIndex\":3,\"size_x\":5,\"size_y\":6,\"col\":8,\"row\":1}
        ]",
      "optionsJSON": "{\"darkTheme\":false}",
      "uiStateJSON": "{}",
      "version": 1,
      "timeRestore": false,
      "kibanaSavedObjectMeta": {
        "searchSourceJSON": "{\"filter\":[{\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}]}"
      }
    }
    }
"""
##################################kibana visualization json file#############################################
"""
{
    "_id": "cpu_usage",
    "_type": "visualization",
    "_source": {
        "title": "cpu_usage",
        "visState": "{
            \"title\":\"cpu_usage\",
            \"type\":\"line\",
            \"params\":
                {\"shareYAxis\":true,\"addTooltip\":true,
                 \"addLegend\":true,\"showCircles\":true,\"smoothLines\":false,\"interpolate\":\"linear\",\"scale\":\"linear\",
                 \"drawLinesBetweenPoints\":true,\"radiusRatio\":9,\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,
                 \"setYExtents\":false,\"yAxis\":{}},
            \"aggs\":[
                {\"id\":\"1\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"Group-Cpu(19299:Krein)_%-Used\"}},
                {\"id\":\"2\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"Group-Cpu(28868:Ted_DEV_ORA)_%-Used\"}},
                {\"id\":\"3\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"Group-Cpu(29116:C6320)_%-Used\"}},
                {\"id\":\"4\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"Group-Cpu(3404747:quanta_t41)_%-Used\"}},
                {\"id\":\"5\",\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"timestamp\",\"interval\":\"custom\",\"customInterval\":\"20s\",\"min_doc_count\":1,\"extended_bounds\":{}}},
                {\"id\":\"6\",\"type\":\"avg\",\"schema\":\"metric\",\"params\":{\"field\":\"Physical-Cpu(_Total)_%-Core-Util-Time\"}}],
            \"listeners\":{}}",
        "uiStateJSON": "{}",
        "description": "",
        "version": 1,
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": "{\"filter\":[],\"index\":\"esxtop\",\"highlight\":{\"pre_tags\":[\"@kibana-highlighted-field@\"],\"post_tags\":[\"@/kibana-highlighted-field@\"],\"fields\":{\"*\":{}},\"require_field_match\":false,\"fragment_size\":2147483647},\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}"
        }
    }
}
"""

def create_kibana(heading_list, template, configure_file):
    """
    :param heading_list: headings_list includes headings in elasticsearchs
    :param template: template is a kibana configure json template. Dashboard configure is hard-coded and visualization
        can increase as needed
    :param configure_file: Generated kibana configure json file name
    :return:
    """
    f_old_kibana = open(template, "r")
    kibana_json_example = json.load(f_old_kibana)
    kibana_json = []
    visualization_json_list = []
    for configure in kibana_json_example:
        if configure["_type"] == "visualization":
            visualization_json_list.append(configure)
        elif configure["_type"] == "dashboard":
            ## All dashboard items are fixed, nothing should be changed
            kibana_json.append(configure)
    #######################below items is working on visualization#############################
    vis_json_example = visualization_json_list[0]
    vis_state_example = json.loads(vis_json_example["_source"]["visState"])
    aggregate_metric = {
        "schema": "metric",
        "id": "0",
        "type": "avg", ## "max" should be used for network, "median" is more real
        "params": {
            "field": ""
        }
    }
    aggregate_bullet = {
        "schema": "segment",
        "id": "0",
        "type": "date_histogram",
        "params": {
            "min_doc_count": 1,
            "extended_bounds": {},
            "interval": "custom",
            "field": "timestamp",
            "customInterval": "20s"
        }
    }

    vis_aggregates = [[], [], []] ## aggregate list for each visualization
    vis_indexes = [1, 1, 1] ## index of metrics/bullets for each visualization
    vis_metric_type = ["median", "avg", "max"] ## define metric type for each visualizations
    vis_titles = ["cpu_usage", "memory_usage", "physical_network_usage"] ## visualization names
    vis_pattens = [
        re.compile("(Group-Cpu\(\d+\:[\w_-]+\)_\%-Used|Physical-Cpu\(_Total\)_\%-Core-Util-Time)", re.I),
        re.compile("Group-Memory\(\d+\:[\w_-]+\)_(Memory-Consumed-Size|Touched)-MBytes", re.I),
        re.compile("Network-Port\(vSwitch\d+:\d+\:vmnic\d+\)_MBits-(Transmitted|Received)\/sec", re.I)
    ]

    #### Filter CPU, Memory and network headings and create relative aggregates list
    for heading in heading_list:
        for (index, patten) in enumerate(vis_pattens):
            if patten.match(heading):
                metric_copy = copy.deepcopy(aggregate_metric)
                metric_copy["id"] = str(vis_indexes[index])
                ## metric type will be cpu => median, memory => avg, network => max
                metric_copy["type"] = vis_metric_type[index]
                vis_indexes[index] += 1
                metric_copy["params"]["field"] = heading
                vis_aggregates[index].append(metric_copy)
                break
    #### Generate Kibana configure list for visualization

    for (index, value) in enumerate(vis_indexes):
        vis_title = vis_titles[index]
        ## Add bullet description
        bullet_copy = aggregate_bullet.copy()
        bullet_copy["id"] = str(value)
        ## Update visState attribute
        vis_aggregates[index].append(bullet_copy)

        ## Update title, id for each visualization
        vis_json = copy.deepcopy(vis_json_example)
        vis_json["_id"] = vis_title
        vis_json["title"] = vis_title
        vis_json["_source"]["title"] = vis_title
        vi_state_copy = vis_state_example.copy()
        vi_state_copy["title"] = vis_title
        vi_state_copy["aggs"] = vis_aggregates[index]
        vis_json["_source"]["visState"] = json.dumps(vi_state_copy)
        kibana_json.append(vis_json)
    f_new_kibana = open(configure_file, "w")
    json.dump(kibana_json, f_new_kibana)
    f_new_kibana.close()
    f_old_kibana.close()

def create_logstash(heading_list, convert_list, config_file_name):
    """
    :param heading_list: headings_list filtered to be delivered to logstash
    :param convert_list: columns that should be transfer from string to number
    :param configure_file_name: Generated logstash configure file name
    :return:
    """
    f_logstash = open(config_file_name, "w")
    heading_list[0] = "_timestamp"
    del convert_list[0]
    converting_list = "\n            ".join(convert_list)
    headings = str(heading_list)
    logstash_string = \
        'input {\n' \
        '    file {\n' \
        '        path => ["/tmp/rackhd_esxtop.csv"]\n' \
        '        start_position => "beginning"\n' \
        '        ignore_older => 0\n' \
        '        sincedb_path => "/dev/null"\n' \
        '        type => esxtop_csv \n' \
        '    }\n' \
        '}\n' \
        '\n' \
        'filter {\n' \
        '    if [type] == "esxtop_csv" {\n'\
        '        csv {\n' \
        '            columns => ' + headings + '\n' \
        '            separator => ","\n' \
        '            convert => {\n            ' + converting_list + '}\n' \
        '        }\n' \
        '        date {\n' \
        '            locale => "en"\n' \
        '            timezone => "Asia/Hong_Kong"\n' \
        '            match => [ "_timestamp", "MM/dd/yyyy HH:mm:ss" ]\n' \
        '            target => ["timestamp"]\n' \
        '            remove_field => ["_timestamp"]\n' \
        '        }\n' \
        '    }\n' \
        '}\n' \
        '\n' \
        'output{\n' \
        '    elasticsearch\n' \
        '    {\n' \
        '       hosts => ["localhost:9200"]\n' \
        '       codec => "json"\n' \
        '       index => "esxtop"\n' \
        '    }\n' \
        '}'
    f_logstash.write(logstash_string)
    f_logstash.close()


if __name__ == "__main__":
    create_kibana(HEADINGS, "rackhd_esxtop_template.json", "rackhd_esxtop_debug.json")
