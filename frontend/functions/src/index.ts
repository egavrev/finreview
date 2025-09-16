import * as functions from 'firebase-functions';
import * as admin from 'firebase-admin';

// Initialize Firebase Admin
admin.initializeApp();

// OAuth Redirect Function
export const authCallback = functions.https.onRequest((req, res) => {
  // Set CORS headers
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(204).send('');
    return;
  }

  // Only handle GET requests
  if (req.method !== 'GET') {
    res.status(405).send('Method Not Allowed');
    return;
  }

  try {
    // Get the backend URL from Firebase config
    const backendUrl = functions.config().backend?.url || 'https://finreview-app-rq7lgavxwq-ew.a.run.app';
    const callbackPath = '/auth/google/callback';
    
    // Build the redirect URL with all query parameters
    const queryString = req.url.split('?')[1] || '';
    const redirectUrl = queryString 
      ? `${backendUrl}${callbackPath}?${queryString}` 
      : `${backendUrl}${callbackPath}`;
    
    console.log('Redirecting OAuth callback to:', redirectUrl);
    
    // Redirect to the backend
    res.redirect(302, redirectUrl);
    
  } catch (error) {
    console.error('Error in auth callback:', error);
    res.status(500).send('Internal Server Error');
  }
});
