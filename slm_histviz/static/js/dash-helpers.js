/**
 * Created by faisal on 9/16/16.
 */


/*
* helper functions for grouping raw access logs in various ways
 */

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

var tagsToReplace = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;'
};

function replaceTag(tag) {
    return tagsToReplace[tag] || tag;
}

/**
 * Sanitizes a string containing html.
 * credit: http://stackoverflow.com/a/5499821/346905
 *
 * @param str input string in which to replace html brackets
 * @returns {string} sanitized string
 */
function safe_tags_replace(str) {
    return str.replace(/[&<>]/g, replaceTag);
}

/**
 * Translates seconds into human readable format of seconds, minutes, hours, days, and years
 * credit: http://stackoverflow.com/a/34270811/346905
 * (minor modifications for compactness' sake)
 *
 * @param  {number} seconds The number of seconds to be processed
 * @return {string}         The phrase describing the the amount of time
 */
function forHumans ( seconds ) {
    var levels = [
        [Math.floor(seconds / 31536000), 'y'],
        [Math.floor((seconds % 31536000) / 86400), 'd'],
        [Math.floor(((seconds % 31536000) % 86400) / 3600), 'h'],
        [Math.floor((((seconds % 31536000) % 86400) % 3600) / 60), 'm'],
        [Math.floor((((seconds % 31536000) % 86400) % 3600) % 60), 's'],
    ];
    var returntext = '';

    for (var i = 0, max = levels.length; i < max; i++) {
        if ( levels[i][0] === 0 ) continue;
        returntext += ' ' + levels[i][0] + (levels[i][0] === 1 ? levels[i][1].substr(0, levels[i][1].length-1): levels[i][1]);
    }
    return returntext.trim();
}