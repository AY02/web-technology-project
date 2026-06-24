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
  const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
  if (!csrfInput) {
    alert("Security Error: Token CSRF not found in the page.");
    checkboxElem.checked = !checkboxElem.checked;
    return;
  }
  const csrfToken = csrfInput.value;

  const entryId = checkboxElem.dataset.entryId;
  
  fetch(toggleTodoBaseUrl + entryId + "/", {
    method: 'POST',
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json',
    }
  }) // asynchronous fetch, returnes a Promise
  .then(response => response.json()) // convert the response in the JSON
  .then(data => { // the data is the json
    if (data.status === 'ok') {
      updateUIWithoutReload(entryId, data);
    } else {
      checkboxElem.checked = !checkboxElem.checked;
      alert("Error.");
    }
  })
  .catch(error => {
    checkboxElem.checked = !checkboxElem.checked;
    alert("Error.");
  });
}

function updateUIWithoutReload(id, data) {
  // Update the TODO List.
  const todoLabel = document.getElementById(`todo_label_${id}`);
  const todoBadges = document.getElementById(`todo_badges_${id}`);
  
  if (todoLabel) {
    if (data.is_completed) {
      todoLabel.classList.add('text-decoration-line-through');
    } else {
      todoLabel.classList.remove('text-decoration-line-through');
    }
  }

  if (todoBadges) {
    if (data.is_completed) {
      todoBadges.innerHTML = `<small class="badge bg-success fw-normal border">Completed: ${data.completion_date}</small>`;
    } else if (data.deadline) {
      const badgeClass = data.is_expired ? 'text-danger' : 'text-primary';
      const badgeText = data.is_expired ? 'Expired:' : 'Expiring:';
      todoBadges.innerHTML = `<small class="badge bg-light ${badgeClass} fw-normal border">${badgeText} ${data.deadline}</small>`;
    } else {
      todoBadges.innerHTML = '';
    }
  }

  // Update the Calendar Panel.
  const calendarItem = document.getElementById(`calendar_item_${id}`);
  const calendarBadge = document.getElementById(`calendar_badge_${id}`);

  if (calendarItem) {
    if (data.is_completed) {
      // Hide the calendar entry.
      calendarItem.classList.remove('d-flex');
      calendarItem.classList.add('d-none');
    } else {
      // Show the calendar entry.
      calendarItem.classList.remove('d-none');
      calendarItem.classList.add('d-flex');
      if (calendarBadge) {
        const badgeClass = data.is_expired ? 'bg-danger' : 'bg-primary';
        const badgeText = data.is_expired ? 'Expired' : 'Pending';
        calendarBadge.innerHTML = `<span class="badge ${badgeClass} py-1 px-2 small">${badgeText}</span>`;
      }
    }
  }
}