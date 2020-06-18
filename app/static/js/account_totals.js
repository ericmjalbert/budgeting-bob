function getCumulativeValues(values) {
    const cumulativeValues = []

    values.forEach(function(item, index) {
        if (index == 0) {
            currentTotal = 0;
        } else {
            currentTotal = cumulativeValues[index-1];
        }
        cumulativeValues.push(item + currentTotal);
    });

    return cumulativeValues
}


function renderChart(dates, values) {
    const ctx = $('#myChart');

    const data = {
        // Labels should be Date objects
        labels: dates,
        datasets: [{
            fill: false,
            data: values,
            borderColor: '#2299dd',
            backgroundColor: '#2299dd',
            lineTension: 0,
        }]
    }

    const options = {
        type: 'line',
        data: data,
        options: {
            fill: false,
            responsive: true,
            scales: {
                xAxes: [{
                    type: 'time',
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: "Date",
                    }
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                    },
                    display: true,
                    scaleLabel: {
                        display: true,
                        labelString: "Account Total CAD",
                    }
                }]
            }
        }
    }

    Chart.defaults.global.legend.display = false;
    const chart = new Chart(ctx, options);
}


function main() {
    var dates = []
    var values = []

    $.getJSON(
        url="/get_account_daily_totals",
        function( data ) {
            $.each( data, function( key, value ) {
                dates.push(value.day);
                values.push(value.total);
            });

            cumulativeValues = getCumulativeValues(values);
            
            renderChart(dates, cumulativeValues);
        }
    );
}

$(document).ready(function() {
    main()
});
