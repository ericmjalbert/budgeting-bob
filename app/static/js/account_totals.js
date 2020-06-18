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


function createAm4coreChart(dates, values) {
    // Themes begin
    am4core.useTheme(am4themes_animated);
    // Themes end

    // Create chart instance
    var chart = am4core.create("myChart", am4charts.XYChart);

    // Add data
    chart.data = dates.map(function(date, i) {
        return {"date": date, "value": values[i]}
    });

    // Create axes
    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
    dateAxis.renderer.minGridDistance = 50;

    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
    valueAxis.title.text = "Account Total CAD";
    valueAxis.min = 0

    // Create series
    var series = chart.series.push(new am4charts.LineSeries());
    series.dataFields.valueY = "value";
    series.dataFields.dateX = "date";
    series.strokeWidth = 2;
    series.fillOpacity = 0.6;
    series.minBulletDistance = 10;
    series.tooltipText = "{valueY}";
    series.tooltip.pointerOrientation = "vertical";
    series.tooltip.background.cornerRadius = 20;
    series.tooltip.background.fillOpacity = 0.5;
    series.tooltip.label.padding(12,12,12,12)

    // Add scrollbar
    chart.scrollbarX = new am4charts.XYChartScrollbar();
    chart.scrollbarX.series.push(series);

    // Add cursor
    chart.cursor = new am4charts.XYCursor();
    chart.cursor.xAxis = dateAxis;
    chart.cursor.snapToSeries = series;
}


function generateChartData() {
    var chartData = [];
    var firstDate = new Date();
    firstDate.setDate(firstDate.getDate() - 1000);
    var visits = 1200;
    for (var i = 0; i < 500; i++) {
        // we create date objects here. In your data, you can have date strings
        // and then set format of your dates using chart.dataDateFormat property,
        // however when possible, use date objects, as this will speed up chart rendering.
        var newDate = new Date(firstDate);
        newDate.setDate(newDate.getDate() + i);
        
        visits += Math.round((Math.random()<0.5?1:-1)*Math.random()*10);

        chartData.push({
            date: newDate,
            visits: visits
        });
    }
    return chartData;
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

    //         
    //         renderChart(dates, cumulativeValues);
            createAm4coreChart(dates, cumulativeValues);
        }
    );

}

$(document).ready(function() {
    main()
});
