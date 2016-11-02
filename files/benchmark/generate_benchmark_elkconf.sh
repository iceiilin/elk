if [ $# -lt 3 ]; then
    echo "need an argument: -o [operation] -i [interval]"
    exit 0
fi

while getopts "p:t:" arg
do
    case $arg in
        p)
            path=`echo $OPTARG | sed -e "s#/#\\\\\/#g"`
            ;;
        t)
            time=$OPTARG
            ;;
        ?)
            echo "unknown argument"
            exit 1
            ;;
    esac
done

sed -e "s#TMP1#"$path"#g" -e "s/TMP2/$time/g" benchmark_logstash.template > benchmark.logstash
sed -e "s/TMP1/$time/g" benchmark_kibana.template > benchmark.kibana
