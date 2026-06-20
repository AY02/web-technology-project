// Functions for error messages for the owner acceptance / rejection.
function openRejectModal(btnElem) {
  document.getElementById('rejectForm').action = btnElem.dataset.rejectUrl;
  new bootstrap.Modal(document.getElementById('rejectModal')).show();
}

function openAcceptModal(btnElem) {
  document.getElementById('acceptForm').action = btnElem.dataset.acceptUrl;
  new bootstrap.Modal(document.getElementById('acceptModal')).show();
}