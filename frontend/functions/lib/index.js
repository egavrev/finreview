"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.authCallback = void 0;
const https_1 = require("firebase-functions/v2/https");
const admin = __importStar(require("firebase-admin"));
// Initialize Firebase Admin
admin.initializeApp();
// OAuth Redirect Function (2nd Gen)
exports.authCallback = (0, https_1.onRequest)({
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
        const code = req.query.code;
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
    }
    catch (error) {
        console.error('Error in auth callback:', error);
        res.redirect('https://financial-apps-471615.web.app/auth/error?message=Authentication error');
    }
});
//# sourceMappingURL=index.js.map