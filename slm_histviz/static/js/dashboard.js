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

    // insert the d3pie donut chart
    makePie('time_usage_chart');
}

function makePie(target) {
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
            "content": [
                {
                    "label": "JavaScript",
                    "value": 264131,
                    "color": "#2383c1"
                },
                {
                    "label": "Ruby",
                    "value": 218812,
                    "color": "#64a61f"
                },
                {
                    "label": "Java",
                    "value": 157618,
                    "color": "#7b6788"
                },
                {
                    "label": "PHP",
                    "value": 114384,
                    "color": "#a05c56"
                },
                {
                    "label": "Python",
                    "value": 95002,
                    "color": "#961919"
                },
                {
                    "label": "C+",
                    "value": 78327,
                    "color": "#d8d239"
                },
                {
                    "label": "C",
                    "value": 67706,
                    "color": "#e98125"
                },
                {
                    "label": "Objective-C",
                    "value": 36344,
                    "color": "#d0743c"
                },
                {
                    "label": "Shell",
                    "value": 28561,
                    "color": "#635122"
                },
                {
                    "label": "Cobol",
                    "value": 24131,
                    "color": "#6ada6a"
                },
                {
                    "label": "C#",
                    "value": 100,
                    "color": "#0b6197"
                },
                {
                    "label": "Coldfusion",
                    "value": 68,
                    "color": "#7c9058"
                },
                {
                    "label": "Fortran",
                    "value": 218812,
                    "color": "#207f32"
                },
                {
                    "label": "Coffeescript",
                    "value": 157618,
                    "color": "#44b9af"
                },
                {
                    "label": "Node",
                    "value": 114384,
                    "color": "#bca349"
                },
                {
                    "label": "Basic",
                    "value": 95002,
                    "color": "#e4a14a"
                },
                {
                    "label": "Cola",
                    "value": 36344,
                    "color": "#a3acb2"
                },
                {
                    "label": "Perl",
                    "value": 32170,
                    "color": "#8cc2e9"
                },
                {
                    "label": "Dart",
                    "value": 28561,
                    "color": "#69a5f9"
                },
                {
                    "label": "Go",
                    "value": 264131,
                    "color": "#5a378f"
                },
                {
                    "label": "Groovy",
                    "value": 218812,
                    "color": "#546e91"
                },
                {
                    "label": "Processing",
                    "value": 157618,
                    "color": "#8bde94"
                },
                {
                    "label": "Smalltalk",
                    "value": 114384,
                    "color": "#d2ab58"
                },
                {
                    "label": "Scala",
                    "value": 95002,
                    "color": "#273c71"
                },
                {
                    "label": "Visual Basic",
                    "value": 78327,
                    "color": "#98bf6e"
                },
                {
                    "label": "Scheme",
                    "value": 67706,
                    "color": "#4caa4a"
                },
                {
                    "label": "Rust",
                    "value": 36344,
                    "color": "#98aac5"
                },
                {
                    "label": "FoxPro",
                    "value": 32170,
                    "color": "#cc0f0f"
                }
            ]
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