import { v4 as uuidv4 } from 'uuid';

// Assuming an existing async logging function
async function logUserAction(actionType, additionalData = {}) {
  const uuid = uuidv4();
  const payload = {
    uuid,
    actionType,
    timestamp: new Date().toISOString(),
    ...additionalData
  };

  try {
    await fetch('/api/log-action', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
  } catch (error) {
    console.error('Failed to log action:', error);
  }
}

export { logUserAction };
