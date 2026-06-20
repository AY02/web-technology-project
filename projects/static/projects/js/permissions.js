// Function to handle the revoke permission modal
function openRevokeModal(btnElem) {
  // Extract data from the clicked button's dataset attributes
  const revokeUrl = btnElem.dataset.revokeUrl;
  const username = btnElem.dataset.username;

  // Inject the data into the modal's form and text
  document.getElementById('revokePermissionForm').action = revokeUrl;
  document.getElementById('revokeUsernameDisplay').textContent = username;

  const revokeModal = new bootstrap.Modal(document.getElementById('revokePermissionModal'));
  revokeModal.show();
}

// Function to handle the Grant/Update permission modal
function openConfirmGrantModal() {
  const form = document.getElementById('grantPermissionForm');
  
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }
  // Values entered by the users
  const username = document.querySelector('[name="username"]').value;
  const roleSelect = document.querySelector('[name="role"]');
  const roleText = roleSelect.options[roleSelect.selectedIndex].text;

  document.getElementById('confirmUsernameDisplay').textContent = username;
  document.getElementById('confirmRoleDisplay').textContent = roleText;

  // Showing this modal on top of the other
  const confirmModal = new bootstrap.Modal(document.getElementById('confirmGrantModal'));
  confirmModal.show();
}

// Function to submit the form after confirmation
function submitGrantForm() {
  document.getElementById('grantPermissionForm').submit();
}

// Function to autofill the form when clicking on a user in the list
function fillPermissionForm(elem) {
  const username = elem.dataset.username;
  const roleValue = elem.dataset.role;

  // Find the form inputs by their name attributes
  const usernameInput = document.querySelector('[name="username"]');
  const roleSelect = document.querySelector('[name="role"]');

  if (usernameInput && roleSelect) {
    // Fill the fields
    usernameInput.value = username;
    roleSelect.value = roleValue;

    // Brief visual change to the form so the user notices the change
    usernameInput.classList.add('bg-warning', 'bg-opacity-10');
    setTimeout(() => {
      usernameInput.classList.remove('bg-warning', 'bg-opacity-10');
    }, 500);
  }
}