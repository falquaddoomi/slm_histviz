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

    /*
    var labelTestData = [
        {label: "person a", times: [{"starting_time": 1355752800000, "ending_time": 1355759900000}, {"starting_time": 1355767900000, "ending_time": 1355774400000}]},
        {label: "person b", times: [{"starting_time": 1355759910000, "ending_time": 1355761900000}]},
        {label: "person c", times: [{"starting_time": 1355761910000, "ending_time": 1355763910000}]}
    ];

    var chart = d3.timeline().stack().showToday().labelFormat(function(label){ return label;});
    var svg = d3.select("#timeline")
        .append("svg")
        .attr("width", $("#timeline").parent().width())
        .datum(labelTestData).call(chart);
    */
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
}