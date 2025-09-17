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
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.authCallback = void 0;
const functions = __importStar(require("firebase-functions"));
const admin = __importStar(require("firebase-admin"));
// Initialize Firebase Admin
admin.initializeApp();
// OAuth Redirect Function
exports.authCallback = functions.https.onRequest(async (req, res) => {
    var _a;
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
        // Get the backend URL from Firebase config
        const backendUrl = ((_a = functions.config().backend) === null || _a === void 0 ? void 0 : _a.url) || 'https://finreview-app-rq7lgavxwq-ew.a.run.app';
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