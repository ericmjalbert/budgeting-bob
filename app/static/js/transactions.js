function main() {
  $('.save').click(function () {
    // Get the row id and new category value
    var id = $(this).closest('tr').find('.id-value').text();
    var category = $(this).closest('.category-save').find('option:selected').text();
    
    // Write it to DB
    $.getJSON(
      url='/save_new_category',
      data={"category": category, "id": id}
    ); 

    // Overwrite the displayed category
    $(this).closest('tr').find('.category').text(category);

    return true;
  });
}


$(document).ready(function() {
  main()
});
