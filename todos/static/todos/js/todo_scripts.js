function openEditTodoModal(btnElem) {
  var id = btnElem.dataset.entryId;
  var content = btnElem.dataset.entryContent;
  var deadline = btnElem.dataset.entryDeadline;

  document.getElementById('editTodoForm').action = editTodoBaseUrl + id + "/";
  document.getElementById('editTodoContent').value = content;
  document.getElementById('editTodoDeadline').value = deadline;
  
  // We open the bootstrap modal only with the data from the todo entry the user wants to edit.
  var editModal = new bootstrap.Modal(document.getElementById('editTodoModal'));
  editModal.show();
}

function openDeleteTodoModal(btnElem) {
  var id = btnElem.dataset.entryId;
  document.getElementById('deleteTodoForm').action = deleteTodoBaseUrl + id + "/";
  var deleteModal = new bootstrap.Modal(document.getElementById('deleteTodoModal'));
  deleteModal.show();
}

function toggleTask(checkboxElem) {
  var entryId = checkboxElem.dataset.entryId;
  // Label to be checked.
  var label = checkboxElem.nextElementSibling;
  const xhttp = new XMLHttpRequest();
  
  xhttp.onload = function() {
    if (xhttp.status == 200) {
      window.location.reload();
    } else {
      // If it's not okay, we use the checkbox as before.
      checkboxElem.checked = !checkboxElem.checked;
      alert("Error while updating the task.");
    }
  };
  
  xhttp.open("GET", toggleTodoBaseUrl + entryId + "/");
  xhttp.send();
}