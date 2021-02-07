// Mostly just magic to store the user's declared name in local storage and pull
// it back out quickly.

const local_storage = window.localStorage;

function storeValues(event) {
  local_storage.setItem('hunter-name', event.target.elements.name.value);
  local_storage.setItem('hunter-email', event.target.elements.email.value);
  local_storage.setItem('hunter-sailing-7', event.target.elements['slot-7'].checked);
  local_storage.setItem('hunter-sailing-8', event.target.elements['slot-8'].checked);
  local_storage.setItem('hunter-sailing-9', event.target.elements['slot-9'].checked);
}

function recallValues() {
  document.querySelector('#reg-form').addEventListener('submit', storeValues);
  document.querySelector('#name').value = local_storage.getItem('hunter-name');
  document.querySelector('#email').value = local_storage.getItem('hunter-email');
  document.querySelector('#slot-7').checked = (
    local_storage.getItem('hunter-sailing-7', false) == 'true');
  document.querySelector('#slot-8').checked = (
    local_storage.getItem('hunter-sailing-8', false) == 'true');
  document.querySelector('#slot-9').checked = (
    local_storage.getItem('hunter-sailing-9', false) == 'true');
}

window.onload = recallValues;
