function searchBarKeyPress(e) {
    //See notes about 'which' and 'key'
    if (e.keyCode == 13) {
        searchTransactions()
        return false;
    }
}

function highlightSaveButton() {
    $(this).closest('tr').find('.save').addClass('btn-info');
    $(this).closest('tr').find('.save').removeClass('btn-outline-secondary');
}

function saveCategoryButton() {
    // Get the row id and new category value
    var id = $(this).closest('tr').find('.id-value').text();
    var category = $(this).closest('tr').find('.category-save').find('option:selected').text();

    // Write it to DB
    $.getJSON(
        url='/save_new_category',
        data={"category": category, "id": id}
    );

    // Remove save button highlight
    $(this).closest('tr').find('.save').addClass('btn-outline-secondary');
    $(this).closest('tr').find('.save').removeClass('btn-info');

    return true;
}

function clearSearch() {
    $('#searchbar').find('input').val('');
    $('tbody').find('tr').show();
}

function searchTransactions() {
    const searchTerm = $('#searchbar').find('input').val().toLowerCase();
    $('tbody').find('tr').hide();
    $('tbody').find('tr').each(function (index, row) {
        // Only want to use specific columns for search terms
        if ($(row).find('td:nth-child(2)').text().toLowerCase().indexOf(searchTerm) != -1
            || $(row).find('td:nth-child(3)').text().toLowerCase().indexOf(searchTerm) != -1
            || $(row).find('td:nth-child(4)').text().toLowerCase().indexOf(searchTerm) != -1
            || $(row).find('td:nth-child(5)').text().toLowerCase().indexOf(searchTerm) != -1
            || $(row).find('td:nth-child(6)').find('option:selected').text().toLowerCase().indexOf(searchTerm) != -1
        ) {
            $(row).show();
        };
    });
}

function main() {

  $('.category-save').on('change', highlightSaveButton);
  $('.save').click(saveCategoryButton);
  $('#search').click(searchTransactions);
  $('#clear-search').click(clearSearch);
}

$(document).ready(function() {
    main()
});
