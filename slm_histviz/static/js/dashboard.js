/**
 * Created by faisal on 9/2/16.
 */

/*
general flow of dashboard creation:
---

1) makeDashboard() grabs list of dates on which we have data and creates date choosers; it also fires off a request
   for the most recent date on which we have data via fetchOnDate()
2) fetchOnDate() grabs the raw access log from the server and feeds the data to bindComponentsToData()
3) bindComponentsToData() populates three components:
   - the table, which just gets the raw access log
   - the timeline, which requires some data massaging:
     * the log is partitioned by service
     * for each service's timeline, points within a threshold are merged into intervals
   - the donut chart, which displays aggregate time spent per service
     * uses the intervalized data from the timline and computes aggregate time per service

 4) changes to the selected date will return to step #2 to refresh the data, reusing existing DOM where possible
    (i.e. the pie.) (the timeline is completely recreated, unfortunately)
 */


function makeDashboard() {
    // grab list of dates on which we have data
    $.get("/api/data_dates").done(function(data) {
        var dates = data['dates'].map((d) => moment.utc(d[0]));

        // bind available dates to picker
        var predates = dates.map((d) => {
            var $div = $('<div class="date-choice" />');
            var df = d.local().format("MM/DD/YYYY");

            $('<a href="#' + df + '" />')
                .text(df)
                .click(function() {
                    fetchOnDate(d.toDate());
                }).appendTo($div);

            return $div;
        });

        $("#date-selector").empty().append(
            [ ...predates, $('<div class="date-choice"><input type="text" id="timeline-datepicker" /></div>') ]
        );

        // create datepicker, bind to refresh data, and highlight dates on which we have data
        var $dpick = $('#timeline-datepicker');

        $dpick.datepicker({
            autoclose: true,
            beforeShowDay: (d) => {
                md = moment.utc(d);
                // console.log(md);
                return dates.some((cand) => cand.format('YYYY MM DD') == md.format('YYYY MM DD'))?"has-data":"";
            }
        })
        .on('changeDate', function(e) {
            fetchOnDate(e.date);
        });

        // if we have a hash in the location, use that
        var hashed_loc = location.hash.substring(1);

        if (hashed_loc != "") {
            $dpick.datepicker('setUTCDate', moment.utc(hashed_loc).toDate());
        }
        else {
            // select the most recent date on which we have data
            $dpick.datepicker('setUTCDate', dates[dates.length-1].toDate());
        }
    });
}

function makePie(target, data) {
    var pie = new d3pie(target, {
        "header": {
            "title": {
                "text": "(duration)",
                "fontSize": 24,
                "font": "Lato"
            },
            "location": "pie-center",
            "subtitle": {
                "text": "(site)",
                "color": "#999999",
                "fontSize": 12,
                "font": "Lato"
            },
            "titleSubtitlePadding": 4
        },
        "size": {
            "canvasHeight": 300,
            "canvasWidth": 300,
            "pieInnerRadius": "50%",
            "pieOuterRadius": "100%"
        },
        "data": {
            "smallSegmentGrouping": {
                "enabled": true,
                "value": 10,
                "valueType": "value"
            },
            "sortOrder": "value-desc",
            "content": data.slice(0,30)
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
        },
        "callbacks": {
            "onClickSegment": (e) => {
                console.log(e);
                pie.updateProp('header.title.text', forHumans(e.data.value));
                pie.updateProp('header.subtitle.text', safe_tags_replace(e.data.label));
            }
        }
    });

    return pie;
}

// used by bindComponentsToData to update the pie chart if it exists
var pie = null;
var access_log_dtable = null;

function bindComponentsToData(data) {
    // ------------------------------------------------------------------------------------------------
    // --- STEP 1. bind the table
    // ------------------------------------------------------------------------------------------------

    // create rows to bind to the datatable
    var access_log_rows = data['objects'].map((row) => [
            moment.utc(row.created_at).local().format("ll, LTS"),
            row.hostname,
            safe_tags_replace((row.sni != '<unknown>')?row.sni:row.sni_or_reverse_ip + "*"),
            row.protocol
    ]);

    // create new datatable if it doesn't exist, or reuse it if it does
    if (!access_log_dtable) {
        access_log_dtable = $("#access_table").DataTable({
            data: access_log_rows,
            columns: [
                { title: "Date" },
                { title: "Hostname" },
                { title: "Server Name Indicator" },
                { title: "Protocol "}
            ]
        });
    }
    else {
        access_log_dtable.clear();
        access_log_dtable.rows.add(access_log_rows);
        access_log_dtable.draw();
    }

    // ------------------------------------------------------------------------------------------------
    // --- STEP 2. produce data for d3-timeline
    // ------------------------------------------------------------------------------------------------

    // calculate extents
    var extents = d3.extent(data['objects'], (d) => new Date(d.created_at));
    var interval_width = moment.duration(moment.utc(extents[1]).diff(moment.utc(extents[0])));
    // group by service and coalesce contiguous timepoints
    var access_by_service = groupByService(data['objects']);
    access_by_service = intervalizeAccesses(access_by_service, 10, 'seconds');

    console.log(access_by_service);

    var $timeline = $("#timeline");

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
        .showTimeAxisTick()
        .margin({left: 150, top: 0, right: 5, bottom: 0})
        .labelFormat(function(label){ return label; });

    if (interval_width.asMinutes() > 5) {
        chart.tickFormat({
            format: d3.time.format("%I:%M %p"),
            tickTime: d3.time.minutes,
            tickInterval: 3,
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

    // ------------------------------------------------------------------------------------------------
    // --- STEP 3. produce data for d3pie
    // ------------------------------------------------------------------------------------------------

    var colors = d3.scale.category20();
    var service_aggregate_data = aggregatedServiceUsage(access_by_service).map((entry, idx) => {
        return {
            "label": entry.service,
            "value": parseFloat(entry.time.toFixed(2)),
            "color": colors(idx)
        }
    });

    if (pie) {
        pie.updateProp('header.title.text', "(duration)");
        pie.updateProp('header.subtitle.text', "(site)");
        pie.updateProp('data.content', service_aggregate_data);
    }
    else {
        pie = makePie('time_usage_chart', service_aggregate_data);
    }
}

/**
 * Fetches data and updates components for the given date.
 *
 * @param get_date js Date for which to fetch data
 */
function fetchOnDate(get_date) {
    var utc_moment = moment.utc(get_date);
    console.log("Fetching for day ", utc_moment);

    // bind up the controls on the page
    getAccessOnDate(get_date).done(function(data) {
        // populate the bits on the page
        bindComponentsToData(data);
    });

    // highlight the date selector whose date is selected (if any)
    var $date_selector = $("#date-selector");
    var $selected = $date_selector.find("a:contains('" + utc_moment.local().format("MM/DD/YYYY") + "')");
    $date_selector.find("a")
        .filter($selected).addClass("selected").end()
        .not($selected).removeClass("selected");

}

function getAccessOnDate(start_date) {
    var tomorrow = d3.time.day.offset(start_date, 1);
    return getAccessBetweenDates(start_date, tomorrow);
}

function getAccessBetweenDates(start_date, end_date) {
    var start_txt = moment.utc(start_date).format("YYYY-MM-DD");
    var end_txt = moment.utc(end_date).format("YYYY-MM-DD");

    var filters = {filters: [
        {and: [
            {name: "created_at", op: "gte", val: start_txt},
            {name: "created_at", op: "lt", val: end_txt},
        ]}
    ]};

    return $.get("/api/access_log", {results_per_page: 10000, q: JSON.stringify(filters)})
        .fail(function() {
            console.error("Couldn't get access log data!");
        });
}