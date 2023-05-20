function uploadFile() {
  $.post(
    url='/file_upload',
  ).done();
}

function main() {
  $('#submit-csv').click(uploadFile);
}


$(document).ready(function() {
  main()
});
