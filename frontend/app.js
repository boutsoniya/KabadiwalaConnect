const API_BASE_URL = window.API_BASE_URL || 'http://127.0.0.1:8000';
const form = document.querySelector('#pickupForm');
const result = document.querySelector('#result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.textContent = 'Submitting…';
  try {
    const user = await fetch(`${API_BASE_URL}/api/users`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name:document.querySelector('#name').value, phone:document.querySelector('#phone').value, role:'citizen'})}).then(r => r.json());
    if (!user.id) throw new Error(user.detail || 'Could not create user');
    const pickup = await fetch(`${API_BASE_URL}/api/pickups`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({citizen_id:user.id, material:document.querySelector('#material').value, estimated_weight_kg:Number(document.querySelector('#weight').value), address:document.querySelector('#address').value})}).then(r => r.json());
    if (!pickup.id) throw new Error(pickup.detail || 'Could not create pickup');
    result.textContent = `Pickup #${pickup.id} created successfully. Status: ${pickup.status}.`;
    form.reset();
  } catch (error) {
    result.textContent = `Error: ${error.message}. Start the backend and try again.`;
  }
});