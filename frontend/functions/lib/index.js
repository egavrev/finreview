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
exports.authCallback = functions.https.onRequest((req, res) => {
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
        // Get the backend URL from Firebase config
        const backendUrl = ((_a = functions.config().backend) === null || _a === void 0 ? void 0 : _a.url) || 'https://finreview-app-rq7lgavxwq-ew.a.run.app';
        const callbackPath = '/auth/google/callback';
        // Build the redirect URL with all query parameters
        const queryString = req.url.split('?')[1] || '';
        const redirectUrl = queryString
            ? `${backendUrl}${callbackPath}?${queryString}`
            : `${backendUrl}${callbackPath}`;
        console.log('Redirecting OAuth callback to:', redirectUrl);
        // Redirect to the backend
        res.redirect(302, redirectUrl);
    }
    catch (error) {
        console.error('Error in auth callback:', error);
        res.status(500).send('Internal Server Error');
    }
});
//# sourceMappingURL=index.js.map