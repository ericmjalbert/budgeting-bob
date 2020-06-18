function saveCategoryButton() {
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
}

function clearSearch() {
    $('#searchbar').find('input').val('');
    $('tbody').find('tr').show();
}

function setupSearchWhenDoneTyping() {
    //setup before functions
    var typingTimer;               //timer identifier
    var doneTypingInterval = 500;  //time in ms, 0.5 second
    var $input = $('#searchbar').find('input');

    //on keyup, start the countdown
    $input.on('keyup', function () {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(searchTransactions, doneTypingInterval);
    });

    //on keydown, clear the countdown
    $input.on('keydown', function () {
        clearTimeout(typingTimer);
    });
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
            || $(row).find('td:nth-child(6)').text().toLowerCase().indexOf(searchTerm) != -1
        ) {
            $(row).show();
        };
    });
}

function main() {
    $('.save').click(saveCategoryButton);
    $('#clear-search').click(clearSearch);
    setupSearchWhenDoneTyping();
}

$(document).ready(function() {
    main()
});
