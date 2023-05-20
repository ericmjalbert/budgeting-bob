function monthSelector() {
    // Get the month value that's is selected
    var month = $(this).val()

    // show budgets of selected month
    location.href = '/transactions?selected_month=' + month
}

function searchBarKeyPress(e) {
    //See notes about 'which' and 'key'
    if (e.keyCode == 13) {
        searchTransactions();
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
    // remove search bar and use month selector instead
    $('#searchbar').find('input').val('');

    $('#month-selector').each(monthSelector)
}

function searchTransactions() {
    const searchTerm = $('#searchbar').find('input').val().toLowerCase();

    // show only transactions that match searchterms
    location.href = '/transactions?search=' + encodeURIComponent(searchTerm);
}

function deleteSplitTransaction() {
    var thisRow = $(this).closest('tr');
    var id = thisRow.find('.id-value').text();

    $.getJSON(
        url='/delete_split_transaction',
        data={"id": id}
    );

    thisRow.css("text-decoration", "line-through");
    thisRow.find('.customSelect').addClass("disabled");
    thisRow.find('.save').prop("disabled", true);
}

function main() {
    $('#month-selector').change(monthSelector);
    $('.category-save').on('change', highlightSaveButton);
    $('.save').click(saveCategoryButton);
    $('#search').click(searchTransactions);
    $('#clear-search').click(clearSearch);
    $('.delete').click(deleteSplitTransaction);
}

$(document).ready(function() {
    main()
});
