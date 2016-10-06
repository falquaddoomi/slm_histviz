/**
 * Created by faisal on 9/21/16.
 */

var align_moment = moment("9/10/2016 12:00am", "M/DD/YYYY h:mma");

// statically-defined ground truth (offset is in minutes)
var ground_truth = [
    {offset: 0,  desc: "wake phone, connect to VPN", svc: 'awake'},
    {offset: 3,  desc: "open facebook, browse", svc: 'facebook'},
    {offset: 7,  desc: "stop browsing by locking phone", svc: 'sleeping'},
    {offset: 10, desc: "unlock phone", svc: 'awake'},
    {offset: 12, desc: "open instagram, browse", svc: 'instagram'},
    {offset: 15, desc: "return to home, leave phone idle but unlocked", svc: 'awake'},
    {offset: 16, desc: "lock phone", svc: 'sleeping'}
];

var svc_colors = {
    'awake': '#ccc',
    'sleeping': '#555',
    'facebook': '#3B5998',
    'instagram': '#e1306c'
};

// var svc_color_map = d3.scale.category20().domain(Object.keys(svc_colors));

// data describing our participants
var users = [
    {username: 'faisal', span: ["9/21/2016 10:31am", "9/21/2016 10:48am"]},
    {username: 'fabian', span: ["9/20/2016 11:15pm", "9/20/2016 11:32pm"]},
    {username: 'hongyi', span: ["9/20/2016 10:56pm", "9/21/2016 11:13pm"]}
];

function getAccessBetweenDateTimes(username, start_date, end_date) {
    var start_txt = moment.utc(start_date).format();
    var end_txt = moment.utc(end_date).format();

    var filters = {filters: [
        {and: [
            {name: "username", op: "==", val: username},
            {name: "created_at", op: "gte", val: start_txt},
            {name: "created_at", op: "lt", val: end_txt},
        ]}
    ]};

    return $.get("/api/access_log", {results_per_page: 10000, nofilter: 'abbaz', q: JSON.stringify(filters)})
        .fail(function() {
            console.warn("Couldn't get access log data!");
        });
}

function makeAnalysis() {
    users.map((entry) => {
        console.log("Username: ", entry.username, "Span: ", entry.span.map((t) => moment(t, "M/DD/YYYY h:mma").local().toDate()));
    });

    // actually grab the data using the access log API
    console.log("Initiating request for a ton of data...");

    var promises = users.map((entry) => {
        var span = entry.span.map((t) => moment(t, "M/DD/YYYY h:mma").toDate());
        return getAccessBetweenDateTimes(entry.username, span[0], span[1]);
    });

    // we need to wait for an array of promises to complete here
    $.when.apply($, promises)
        .done(function(...reqs) {
            console.log("...complete!");

            reqs.map((req, idx) => {
                console.log("username: ", users[idx].username, "data: ", req[0]);
            });

            bindResultsToTimeline(reqs.map((req, idx) => { return {
                user: users[idx].username,
                start_date: moment(users[idx].span[0], "M/DD/YYYY h:mma"),
                data: req[0]};
            }));
        })
        .fail(function(e) {
            console.log("Requests failed: ", e);
        });
}

function bindResultsToTimeline(user_data) {
    // user_data consists of {username, data} objects
    // we use ground_truth, user_data, and users to create a d3 timeline object

    // each result needs to be grouped by service, intervalized, then normalized to align to all the rest
    console.log("About to do some expensive aggregation....");
    var user_timelines = user_data.map((entry, user_id) => {
        var grouped_data = groupByService(entry.data.objects);

        // reduce grouped_data down to only the items of interest
        var filtered_data = {};
        ['Facebook', 'Instagram'].map((svc) => {
            if (grouped_data[svc]) {
                filtered_data[svc] = grouped_data[svc];
            }
        });
        var intervalized_data = intervalizeAccesses(filtered_data, 1, 'seconds');

        var user_align_offset = entry.start_date.diff(align_moment);

        return Object.keys(intervalized_data).map((service) => {
            var ret = {
                label: "user #" + user_id + " - " + service,
                times: intervalized_data[service].map((row) => {
                    return {
                        color: svc_colors[service.toLowerCase()],
                        starting_time: row.start_date.subtract(user_align_offset, 'ms').toDate(),
                        ending_time: row.end_date.subtract(user_align_offset, 'ms').toDate()
                    };
                })
            };

            console.log(ret);

            return ret;
        });
    });
    console.log("...done!");

    // create a single array from all our little ones
    var results = [];
    for (let entry of user_timelines) {
        // console.log(entry);
        results = results.concat(entry);
    }

    // add ground-truth series
    results.push(
        {
            label: 'test protocol',
            times: ground_truth.map((entry, idx, entries) => {
                var next = entries[idx + 1];
                var start_time = align_moment.clone().add(moment.duration(entry.offset, 'minutes'));
                var end_time = (next) ? align_moment.clone().add(moment.duration(next.offset, 'minutes')) : align_moment.clone().add(moment.duration(entry.offset + 1, 'minutes'));

                return {
                    starting_time: start_time.toDate(),
                    ending_time: end_time.toDate(),
                    color: svc_colors[entry.svc],
                    // label: entry.desc
                }
            })
        }
    );

    console.log(results);

    var $timeline = $("#timeline");

    $timeline.empty();
    var chart = d3.timeline()
        .stack()
        .margin({left: 120, top: 0, right: 0, bottom: 10})
        .showTimeAxisTick()
        // .relativeTime()
        .labelFormat(function(label){ return label; });

    chart.tickFormat({
        format: d3.time.format("%I:%M %p"),
        tickTime: d3.time.minutes,
        tickInterval: 2,
        tickSize: 6
    });

    var timeline_svg = d3.select("#timeline")
        .append("svg")
        .attr("width", $timeline.parent().width())
        .datum(results)
        .call(chart);

    console.log("Completed chart render!");

    // create a legend for the activities
    var legend_entries = Object.keys(svc_colors).map((activity) => {
        var $box = $("<div />").addClass("legend-entry");
        var $tile = $("<div />").addClass("tile " + activity);
        var $txt = $("<div />").text(activity);
        $box.append($tile);
        $box.append($txt);
        return $box;
    });

    $("#legend").append(legend_entries);
}