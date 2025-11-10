from flask import Flask, request, jsonify, abort
import requests
import os

app = Flask(__name__)

# Configuration
ORIGINAL_API_BASE = "https://karobetahack.vercel.app/fetch"
VALID_TOKEN = "4DM1N3055"  # Hardcoded auth token

def is_browser_request():
    """Check if request is from browser - BLOCK browsers"""
    user_agent = request.headers.get('User-Agent', '').lower()
    
    # Browser indicators (BLOCK these)
    browser_keywords = ['mozilla', 'chrome', 'safari', 'firefox', 'edge', 'opera', 'webkit']
    
    # Allowed clients (ALLOW these)
    api_clients = ['python', 'requests', 'curl', 'postman', 'http-client', 'urllib']
    
    # Check for API clients first
    for client in api_clients:
        if client in user_agent:
            return False
    
    # Check for browsers
    for browser in browser_keywords:
        if browser in user_agent:
            return True
    
    # If no User-Agent or unknown, allow (for API clients)
    return False

@app.route('/')
def home():
    """Root path - always 404"""
    abort(404)

@app.route('/fetch')
def fetch_data():
    """
    Main API endpoint
    Only accessible via cURL, Python, etc.
    Browser access will be blocked
    """
    
    # BLOCK browser requests
    if is_browser_request():
        return jsonify({
            "success": False,
            "error": "Browser Access Denied",
            "message": "This API can only be accessed via cURL, Python requests, or other server-side tools. Browser access is not allowed.",
            "solution": "Use cURL command or create your own API with Python to access this service."
        }), 403

    # Check authentication token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({
            "success": False,
            "error": "Authentication Required",
            "message": "Bearer token is required in Authorization header",
            "example": 'curl -H "Authorization: Bearer 4DM1N3O55" "https://your-api.vercel.app/fetch?key=KEY&num=NUM"'
        }), 401
    
    token = auth_header.replace('Bearer ', '')
    if token != VALID_TOKEN:
        return jsonify({
            "success": False,
            "error": "Invalid Token",
            "message": "The provided authentication token is invalid",
            "valid_token": "4DM1N3O55"
        }), 401

    # Get parameters from request
    key = request.args.get('key')
    num = request.args.get('num')
    
    if not key:
        return jsonify({
            "success": False,
            "error": "Missing Parameter",
            "message": "'key' parameter is required"
        }), 400

    if not num:
        return jsonify({
            "success": False,
            "message": "'num' parameter is required"
        }), 400

    try:
        # Make request to original Karobetahack API
        original_url = f"{ORIGINAL_API_BASE}?key={key}&num={num}"
        response = requests.get(original_url, timeout=30)
        
        # Return raw JSON response from original API
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({
            "success": False,
            "error": "Timeout",
            "message": "Request to original API timed out"
        }), 504
    except requests.exceptions.RequestException as e:
        return jsonify({
            "success": False,
            "error": "API Connection Failed",
            "message": f"Could not connect to original API: {str(e)}"
        }), 502
    except Exception as e:
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404 Error Handler"""
    return jsonify({
        "success": False,
        "error": "Endpoint Not Found",
        "message": "This API endpoint does not exist. Use /fetch with proper authentication."
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """405 Error Handler"""
    return jsonify({
        "success": False,
        "error": "Method Not Allowed",
        "message": "This HTTP method is not supported for this endpoint"
    }), 405

# Health check endpoint (hidden from browsers)
@app.route('/health')
def health_check():
    if is_browser_request():
        abort(404)
    return jsonify({"status": "healthy", "service": "Protected API"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=3000)
