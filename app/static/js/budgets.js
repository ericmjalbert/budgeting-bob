function monthSelector() {
  // Get the month value that's is selected
  var month = $(this).val()

  // show budgets of selected month
  location.href = '/budgets?selected_month=' + month
}


function getBudgetValue(thisButton) {
  var budgetText = thisButton.siblings('.budget-text')

  if (thisButton.hasClass('btn-outline-secondary')) {
    var budgetValue = parseInt(budgetText.text());
  } else if (thisButton.hasClass('btn-info')) {
    var budgetValue = budgetText.find('input').attr("value");
  }
  return budgetValue
}


function toggleEditButtonColor(thisButton) {
  if (thisButton.hasClass('btn-outline-secondary')) {
    thisButton.addClass('btn-info');
    thisButton.removeClass('btn-outline-secondary');
  } else if (thisButton.hasClass('btn-info')) {
    thisButton.addClass('btn-outline-secondary');
    thisButton.removeClass('btn-info');
  }
}


function toggleEditBudgetInput(thisButton) {
  var currentBudget = getBudgetValue(thisButton);
  var budgetText = thisButton.siblings('.budget-text')

  if (thisButton.hasClass('btn-outline-secondary')) {
    budgetText[0].innerHTML = `
    <div class="input-group">
      <input type="number" value="` + currentBudget + `">
      <div class="input-group-append">
        <button class="btn btn-secondary save" type="button">Save</button>
      </div>
    </div>
    `;
  } else if (thisButton.hasClass('btn-info')) {
    budgetText[0].innerHTML = currentBudget;
  }
}

function updateBudgetRow(row, newData) {
  row.find('td').eq(1).find('.budget-text').text(newData["budget"]); 
  row.find('td').eq(2).text(newData["remaining"]); 
  row.find('td').eq(3).text(newData["overage"]); 
  row.find('td').eq(4).text(newData["status"]); 
  row.attr('class', newData["status-class"]);
}

function saveBudgetEdit() {
  // Get the row id and new category value
  var currentRow = $(this).parents('tr');
  var category = $(this).closest('tr').find('.category-name').text();
  var newBudgetValue = $(this).parents('.row').find('input')[0].value;

  // Write it to DB
  var month = $('#month-selector').val()
  $.getJSON(
    url='/save_new_budget',
    data={"category": category, "new_value": newBudgetValue, "selected_month": month},
  ).done(function(data) {
    var totalsRow = currentRow.parents('tbody').find('.totals');

    updateBudgetRow(currentRow, data["budget_rows"][category.toLowerCase()]);
    updateBudgetRow(totalsRow, data["total"]);
  });

  var editButton = $(this).parents('.row').find('.budget');
  toggleEditBudgetInput(editButton);
  toggleEditButtonColor(editButton);

  return true;
}


function editBudgetMode() {
  toggleEditBudgetInput($(this));
  toggleEditButtonColor($(this));
  $('.save').click(saveBudgetEdit);
}


function main() {
  $('#month-selector').change(monthSelector);
  $('.budget').click(editBudgetMode);
}


$(document).ready(function() {
  main()
});
