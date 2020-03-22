function main() {
  $('#month-selector').change(function(){
    // Get the month value that's is selected
    var month = $(this).val()

    // show budgets of selected month
    location.href = '/budgets?selected_month=' + month
  });
}

$(document).ready(function() {
  main()
});
