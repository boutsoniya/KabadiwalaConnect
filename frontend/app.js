const API_BASE_URL = window.API_BASE_URL || '';
const form = document.querySelector('#pickupForm');
const result = document.querySelector('#result');

async function loadImpact() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/impact`);
    if (!response.ok) return;
    const data = await response.json();
    document.querySelector('#totalPickups').textContent = data.total_pickups;
    document.querySelector('#completedPickups').textContent = data.completed_pickups;
    document.querySelector('#recycledKg').textContent = `${data.total_recycled_kg} kg`;
    document.querySelector('#valueInr').textContent = `₹${data.total_value_inr}`;
  } catch (_) {
    // Keep the dashboard usable if the API is temporarily sleeping on free hosting.
  }
}

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
    loadImpact();
  } catch (error) {
    result.textContent = `Error: ${error.message}. Please try again in a moment.`;
  }
});

loadImpact();