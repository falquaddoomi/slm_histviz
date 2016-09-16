/**
 * Created by faisal on 9/2/16.
 */

function hello() {
    console.log("this is a test of the emergency dddd system");

    return (d) => {
        console.log(d);
    };
}

function makeDashboard() {
    console.log("Making the dashboard...");

    var $dpick = $('#timeline-datepicker');

    // create the visualization components with nothing in them
    var $timeline = $("#timeline");
    // create aggregates of the usage data and bind that to the donut
    var pie = null;

    function getAccessBetweenDates(start_date, end_date) {
        var filters = {filters: [
            {and: [
                {name: "created_at", op: "gte", val: start_date},
                {name: "created_at", op: "lt", val: end_date},
            ]}
        ]};

        return $.get("/api/access_log", {results_per_page: 10000, q: JSON.stringify(filters)})
            .fail(function() {
                console.error("Couldn't get access log data!");
            });
    }

    function bindComponentsToData(data) {
        //
        // STEP 1. bind the table
        //

        $("#access_table").find("tbody").empty().append(
            data['objects'].reduce((acc, row) => {
                var last = acc[acc.length - 1];

                if (!last || last.hostname != row.hostname) {
                    var $tr = $("<tr />");

                    $("<td />").text(row.created_at).appendTo($tr);
                    $("<td />").text(row.hostname).appendTo($tr);
                    $("<td />").text(row.sni).appendTo($tr);
                    $("<td />").text(row.protocol).appendTo($tr);

                    acc.push($tr);
                }

                return acc;
            }, [])
        );

        // calculate extents
        var extents = d3.extent(data['objects'], (d) => new Date(d.created_at));
        var interval_width = moment.duration(moment.utc(extents[1]).diff(moment.utc(extents[0])));
        console.log(interval_width);

        // pre-step: group by service and coalesce contiguous timepoints
        var access_by_service = groupByService(data['objects']);
        access_by_service = intervalizeAccesses(access_by_service, 5, 'seconds');

        console.log(access_by_service);

        //
        // STEP 2. produce data for d3-timeline
        //

        var timelineData = Object.keys(access_by_service).map(function (service) {
            return {
                label: service,
                times: access_by_service[service].map((span) => {
                    return {
                        starting_time: span.start_date.toDate().valueOf(),
                        ending_time: span.end_date.toDate().valueOf(),
                    }
                })
            }
        });

        $timeline.empty();
        var chart = d3.timeline()
            .stack()
            .showToday()
            .labelFormat(function(label){ return label; });

        if (interval_width.asMinutes() > 5) {
            chart.tickFormat({
                format: d3.time.format("%I:%M %p"),
                tickTime: d3.time.minutes,
                tickInterval: 10,
                tickSize: 6
            });
        }
        else {
            chart.tickFormat({
                format: d3.time.format("%I:%M %p"),
                tickTime: d3.time.minutes,
                tickInterval: 1,
                tickSize: 6
            });
        }

        var timeline_svg = d3.select("#timeline")
            .append("svg")
            .attr("width", $timeline.parent().width())
            .datum(timelineData)
            .call(chart);

        //
        // STEP 3. produce data for d3pie
        //

        var colors = d3.scale.category20();
        var service_aggregate_data = aggregatedServiceUsage(access_by_service).map((entry, idx) => {
            return {
                "label": entry.service,
                "value": parseFloat(entry.time.toFixed(2)),
                "color": colors(idx)
            }
        });

        if (pie) {
            pie.updateProp('data.content', service_aggregate_data);
        }
        else {
            pie = makePie('time_usage_chart', service_aggregate_data);
        }
    }

    var dates = [];

    // mask out dates in the datepicker for which we don't have data
    $.get("/api/data_dates").done(function(data) {
        dates = data['dates'].map((d) => moment.utc(d[0]));
        console.log("Dates: ", dates);
        // $dpick.datepicker('update');

        $dpick.datepicker({
            beforeShowDay: (d) => {
                md = moment.utc(d);
                // console.log(md);
                return dates.some((cand) => cand.format('YYYY MM DD') == md.format('YYYY MM DD'))?"has-data":"";
            }
        })
        .on('changeDate', function(e) {
            console.log("Fetching for day ", moment.utc(e.date));

            var tomorrow = d3.time.day.offset(e.date, 1);
            // bind up the controls on the page
            getAccessBetweenDates(moment.utc(e.date).format("YYYY-MM-DD"), moment.utc(tomorrow).format("YYYY-MM-DD")).done(function(data) {
                // populate the bits on the page
                bindComponentsToData(data);
            })
        });

        // select the most recent date on which we have data
        $dpick.datepicker('setUTCDate', dates[dates.length-1].local().toDate());
    });
}

function makePie(target, data) {
    var pie = new d3pie(target, {
        "header": {
            /*
            "title": {
                "text": "Lots of Programming Languages",
                "fontSize": 24,
                "font": "open sans"
            },
            "subtitle": {
                "text": "A full pie chart to show off label collision detection and resolution.",
                "color": "#999999",
                "fontSize": 12,
                "font": "open sans"
            },
            */
            "titleSubtitlePadding": 9
        },
        /*
        "footer": {
            "color": "#999999",
            "fontSize": 10,
            "font": "open sans",
            "location": "bottom-left"
        },
        */
        "size": {
            "canvasHeight": 300,
            "canvasWidth": 300,
            "pieInnerRadius": "50%",
            "pieOuterRadius": "100%"
        },
        "data": {
            "sortOrder": "value-desc",
            "content": data
        },
        "labels": {
            "outer": {
                "format": "none",
                "pieDistance": 32
            },
            "inner": {
                "hideWhenLessThanPercentage": 3
            },
            "mainLabel": {
                "fontSize": 11
            },
            "percentage": {
                "color": "#ffffff",
                "decimalPlaces": 0
            },
            "value": {
                "color": "#adadad",
                "fontSize": 11
            },
            "truncation": {
                "enabled": true
            }
        },
        "tooltips": {
            "enabled": true,
            "type": "placeholder",
            "string": "{label}: {value}, {percentage}%"
        },
        "effects": {
            "pullOutSegmentOnClick": {
                "effect": "linear",
                "speed": 400,
                "size": 8
            }
        }
    });

    return pie;
}

function groupByService(data) {
    return data.reduce((acc, cur) => {
        if (acc.hasOwnProperty(cur.sni)) {
            acc[cur.sni].push(cur);
        } else {
            acc[cur.sni] = [cur];
        }

        return acc;
    }, {});
}

function intervalizeAccesses(access_by_service, interval, unit) {
    var intervaled_access = {};

    // for each service, we now coalesce the points into contiguous intervals within some threshold
    Object.keys(access_by_service).map(function (service) {
        var logs = access_by_service[service];

        intervaled_access[service] = logs.reduce((acc, cur) => {
            // for each point, extend the span if the previous point + 5sec <= current point
            // if not, append this as a new entry
            var last_entry = acc[acc.length - 1];
            if (!last_entry || moment(cur.created_at) > moment(last_entry.end_date)) {
                // it's outside the previous span, create a mini-span of (time, time + 5sec)
                acc.push({
                    start_date: moment(cur.created_at),
                    end_date: moment(cur.created_at).add(interval, unit)
                })
            }
            else {
                // it's within the previous span, so extend the last one
                last_entry.end_date = moment(cur.created_at).add(interval, unit);
            }

            return acc;
        }, []);
    });

    return intervaled_access;
}

function aggregatedServiceUsage(access_by_service) {
    return Object.keys(access_by_service).map((service, idx) => {
        var total_time = access_by_service[service].reduce((running_total, cur) => {
            return moment.duration(cur.end_date.diff(cur.start_date)).asSeconds() + running_total;
        }, 0);

        return {
            "service": service,
            "time": total_time
        }
    });
}
