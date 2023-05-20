function highlightSaveButton() {
    $(this).closest('tr').find('.save').addClass('btn-info');
    $(this).closest('tr').find('.save').removeClass('btn-outline-secondary');
}

function successAlert(message) {
  const styledMessage = `${message}`;
  alert(styledMessage);
}

function saveSplitButton() {
    // Get the row id and new category value
    var id = $(this).closest('tr').find('.id').text();
    var value = $(this).closest('tr').find('.value input').val();
    var description= $(this).closest('tr').find('.description input').val();
    var category = $(this).closest('tr').find('.category-save').find('option:selected').text();

    if (!value) {
        alert("Must input a value!");
        return false;
    }

    $.getJSON(
        url='/save_split_transaction',
        data={
            "category": category,
            "description": description,
            "id": id,
            "value": value,
        }
    );

    // Remove save button highlight
    $(this).closest('tr').find('.save').addClass('btn-outline-secondary');
    $(this).closest('tr').find('.save').removeClass('btn-info');

    successAlert('Successfully split Transaction!\nGoing back to transaction page.');

    window.location.href = document.referrer;

    return true;
}

function setUpdateValue() {
    // Get original value by reading it from second row
    var originalValue = $('tr').eq(1).find("td").eq(4);

    function updateValue(e) {
        var prevValue = 0;
        if (e.target.hasAttribute("prevValue")) {
            prevValue = $(e.target).attr("prevValue");
        }

        var splitDelta = prevValue - e.target.value;

        // Calculate delta and round to nearest cent
        var newValue = Math.round(
            (
                (parseFloat(originalValue.text()) + splitDelta) 
                + Number.EPSILON
            ) 
            * 100) / 100;

        if (!isNaN(newValue)) {
            originalValue.text(newValue);
            $(e.target).attr("prevValue", e.target.value);
        } else {
            alert("Must input numbers only!");
        }
    }

    $(".value").on('change', updateValue);
}


function main() {
    $('.category-save').on('change', highlightSaveButton);
    $('.value').on('change', highlightSaveButton);
    $('.description').on('change', highlightSaveButton);
    $('.save').click(saveSplitButton);
    setUpdateValue()
}


$(document).ready(function() {
    main()
});

