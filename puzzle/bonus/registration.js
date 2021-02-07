// Mostly just magic to store the user's declared name in local storage and pull
// it back out quickly.

const local_storage = window.localStorage;

function storeValues(event) {
  local_storage.setItem('hunter-name', event.target.elements.name.value);
  local_storage.setItem('hunter-email', event.target.elements.email.value);
}

function recallValues() {
  document.querySelector('#reg-form').addEventListener('submit', storeValues);
  document.querySelector('#name').value = local_storage.getItem('hunter-name');
  document.querySelector('#email').value = local_storage.getItem('hunter-email');
}

window.onload = recallValues;
