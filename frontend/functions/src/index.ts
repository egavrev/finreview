import { onRequest } from 'firebase-functions/v2/https';
import * as admin from 'firebase-admin';

// Initialize Firebase Admin
admin.initializeApp();

// OAuth Redirect Function (2nd Gen)
export const authCallback = onRequest({
  invoker: 'public'
}, async (req, res) => {
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
    // Extract the authorization code from query parameters
    const code = req.query.code as string;
    if (!code) {
      res.redirect('https://financial-apps-471615.web.app/auth/error?message=No authorization code received');
      return;
    }

    console.log('Received OAuth code, forwarding to backend...');

    // Get the backend URL from environment (Cloud Functions v2 supports dotenv)
    const backendUrl = process.env.BACKEND_URL || 'https://finreview-app-rq7lgavxwq-ew.a.run.app';
    
    // Forward the OAuth code to the backend with the stable Firebase redirect URI
    const backendResponse = await fetch(`${backendUrl}/auth/google/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        code: code,
        redirect_uri: 'https://financial-apps-471615.web.app/auth/google/callback'
      })
    });

    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('Backend authentication failed:', errorText);
      res.redirect('https://financial-apps-471615.web.app/auth/error?message=Authentication failed');
      return;
    }

    const authResult = await backendResponse.json();
    const token = authResult.access_token;

    if (!token) {
      console.error('No token received from backend');
      res.redirect('https://financial-apps-471615.web.app/auth/error?message=No token received');
      return;
    }

    // Redirect to frontend with the token
    console.log('Authentication successful, redirecting to frontend with token');
    res.redirect(`https://financial-apps-471615.web.app/auth/callback?token=${token}`);
    
  } catch (error) {
    console.error('Error in auth callback:', error);
    res.redirect('https://financial-apps-471615.web.app/auth/error?message=Authentication error');
  }
});
