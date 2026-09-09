const API_BASE_URL = window.API_BASE_URL || 'https://kabadiwala-connect-api.onrender.com';
const form = document.querySelector('#pickupForm');
const result = document.querySelector('#result');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  result.textContent = 'Submitting…';
  try {
    const userResponse = await fetch(`${API_BASE_URL}/api/users`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name: document.querySelector('#name').value,
        phone: document.querySelector('#phone').value,
        role: 'citizen'
      })
    });
    const user = await userResponse.json();
    if (!userResponse.ok || !user.id) throw new Error(user.detail || 'Could not create user');

    const pickupResponse = await fetch(`${API_BASE_URL}/api/pickups`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        citizen_id: user.id,
        material: document.querySelector('#material').value,
        estimated_weight_kg: Number(document.querySelector('#weight').value),
        address: document.querySelector('#address').value
      })
    });
    const pickup = await pickupResponse.json();
    if (!pickupResponse.ok || !pickup.id) throw new Error(pickup.detail || 'Could not create pickup');

    result.textContent = `Pickup #${pickup.id} created successfully. Status: ${pickup.status}.`;
    form.reset();
  } catch (error) {
    result.textContent = `Error: ${error.message}. Please try again in a moment.`;
  }
});