#!/usr/bin/env python3
"""
EU eTranslation Web Application
A Flask web app that provides a simple interface for the EU eTranslation API
Based on the official EU documentation examples
"""

from flask import Flask, render_template, request, jsonify, url_for
import requests
from requests.auth import HTTPDigestAuth
import json
import threading
import time
from datetime import datetime
import os
from config import config

app = Flask(__name__)

# Load configuration from environment variables
try:
    if not config.validate():
        print("❌ Missing required environment variables. Please create a .env file with your credentials.")
        print("📄 Copy .env.example to .env and fill in your actual values.")
        exit(1)
except Exception as e:
    print(f"❌ Configuration error: {e}")
    exit(1)

# Global correlation map to store translation results
correlation_map = {}

def get_callback_url():
    """Get the appropriate callback URL for production or development"""
    
    # Check for production environment variables first
    production_url = os.getenv('PRODUCTION_URL')
    if production_url:
        callback_url = f"{production_url.rstrip('/')}/callback"
        print(f"🌍 Using production callback URL: {callback_url}")
        return callback_url
    
    # Fallback to local URL (for local development)
    callback_url = url_for('callback', _external=True)
    print(f"⚠️  Using local callback URL: {callback_url}")
    print("   Note: EU eTranslation may not be able to reach this URL!")
    return callback_url

# Supported languages (based on common EU languages)
SUPPORTED_LANGUAGES = {
    'BG': 'Bulgarian',
    'CS': 'Czech',
    'DA': 'Danish',
    'DE': 'German',
    'EL': 'Greek',
    'EN': 'English',
    'ES': 'Spanish',
    'ET': 'Estonian',
    'FI': 'Finnish',
    'FR': 'French',
    'GA': 'Irish',
    'HR': 'Croatian',
    'HU': 'Hungarian',
    'IT': 'Italian',
    'LT': 'Lithuanian',
    'LV': 'Latvian',
    'MT': 'Maltese',
    'NL': 'Dutch',
    'PL': 'Polish',
    'PT': 'Portuguese',
    'RO': 'Romanian',
    'SK': 'Slovak',
    'SL': 'Slovenian',
    'SV': 'Swedish'
}

@app.route('/')
def index():
    """Main page with translation interface"""
    return render_template('index.html', languages=SUPPORTED_LANGUAGES)

@app.route('/receiveRequest', methods=['POST'])
def receive_request():
    """
    Handle translation request from the frontend
    Based on PART 2 of the official documentation
    """
    try:
        # Get form data
        text_to_translate = request.form.get('textToTranslate', '').strip()
        source_language = request.form.get('sourceLanguage', '').strip()
        target_language = request.form.get('targetLanguage', '').strip()
        
        # Validation
        if not text_to_translate:
            return "-1001", 400  # Custom error code for empty text
        
        if not source_language or not target_language:
            return "-1002", 400  # Custom error code for missing languages
            
        if source_language == target_language:
            return "-1003", 400  # Custom error code for same source/target
        
        print(f"Translation request: {source_language} -> {target_language}")
        print(f"Text: {text_to_translate[:100]}{'...' if len(text_to_translate) > 100 else ''}")
        
        # Get the callback URL dynamically
        callback_url = get_callback_url()
        
        # Build translation request (based on official example)
        translation_request = {
            'sourceLanguage': source_language,
            'targetLanguages': [target_language],
            'callerInformation': {
                "application": config.application_name,
                "username": config.email
            },
            'textToTranslate': text_to_translate,
            'requesterCallback': callback_url
        }
        
        # Convert to JSON
        json_request = json.dumps(translation_request)
        
        # Set headers
        headers = {'Content-Type': 'application/json'}
        
        # Send request to eTranslation API
        response = requests.post(
            config.rest_url,
            auth=HTTPDigestAuth(config.application_name, config.api_password),
            headers=headers,
            data=json_request,
            timeout=30
        )
        
        request_id = response.text.strip()
        print(f"eTranslation API response: {response.status_code}, ID: {request_id}")
        
        if response.status_code == 200:
            try:
                # Check if it's a positive integer (success) or negative (error)
                id_num = int(request_id)
                if id_num > 0:
                    # Store the request ID with empty translation (will be filled by callback)
                    correlation_map[request_id] = {
                        'status': 'pending',
                        'translation': None,
                        'timestamp': datetime.now().isoformat(),
                        'source_language': source_language,
                        'target_language': target_language,
                        'original_text': text_to_translate
                    }
                    print(f"Request stored with ID: {request_id} at {datetime.now()}")
                    print(f"Translation: {source_language} -> {target_language}, {len(text_to_translate)} characters")
                    return request_id
                else:
                    print(f"Error code from eTranslation: {id_num}")
                    return str(id_num)
            except ValueError:
                print(f"Invalid response format: {request_id}")
                return "-1004"  # Custom error for invalid response
        else:
            print(f"HTTP error: {response.status_code}")
            return f"-{response.status_code}"
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return "-1005"  # Custom error for network issues
    except Exception as e:
        print(f"Unexpected error: {e}")
        return "-1006"  # Custom error for other issues

@app.route('/checkResult', methods=['POST'])
def check_result():
    """
    Check if translation is ready
    Based on PART 3 and PART 5 of the official documentation
    """
    try:
        request_id = request.form.get('idRequest', '').strip()
        
        if not request_id:
            return "", 400
        
        # Check if translation is available
        if request_id in correlation_map:
            translation_data = correlation_map[request_id]
            if translation_data['status'] == 'completed' and translation_data['translation']:
                print(f"Translation ready for ID: {request_id}")
                return translation_data['translation']
            else:
                # Still pending - log occasionally for debugging
                elapsed_time = datetime.now() - datetime.fromisoformat(translation_data['timestamp'])
                elapsed_seconds = int(elapsed_time.total_seconds())
                
                if elapsed_seconds > 0 and elapsed_seconds % 30 == 0:  # Log every 30 seconds
                    print(f"Translation still pending for ID: {request_id} (waiting {elapsed_seconds}s)")
                    print(f"  Status: {translation_data['status']}")
                    print(f"  From {translation_data.get('source_language', 'unknown')} to {translation_data.get('target_language', 'unknown')}")
                
                return ""
        else:
            # Request ID not found
            print(f"Request ID not found: {request_id}")
            return ""
            
    except Exception as e:
        print(f"Error checking result: {e}")
        return "", 500

@app.route('/test-callback', methods=['GET', 'POST'])
def test_callback_endpoint():
    """Test endpoint to verify callback functionality"""
    print("🧪 TEST CALLBACK ENDPOINT CALLED")
    print(f"⏰ Timestamp: {datetime.now().isoformat()}")
    print(f"🔗 Method: {request.method}")
    print(f"🌐 Source IP: {request.environ.get('REMOTE_ADDR', 'unknown')}")
    print(f"🔗 User Agent: {request.headers.get('User-Agent', 'unknown')}")
    
    if request.method == 'POST':
        print("📋 POST data received:")
        for key, value in request.form.items():
            print(f"  {key}: {value}")
    
    return jsonify({
        "status": "success", 
        "message": "Test callback endpoint is working",
        "timestamp": datetime.now().isoformat(),
        "method": request.method
    }), 200

@app.route('/callback', methods=['GET', 'POST'])
def callback():
    """
    Receive translation result from eTranslation
    Based on PART 4 of the official documentation
    """
    try:
        if request.method == 'GET':
            # Handle browser/GET requests for testing
            print("🌐 GET request to callback endpoint (probably from browser)")
            return jsonify({
                "status": "callback_endpoint_working",
                "message": "This is the EU eTranslation callback endpoint",
                "method": "GET",
                "note": "EU eTranslation will send POST requests here",
                "timestamp": datetime.now().isoformat()
            }), 200
        
        # Handle POST requests (from EU eTranslation)
        print("=" * 60)
        print("🎉 CALLBACK RECEIVED FROM ETRANSLATION!")
        print(f"⏰ Timestamp: {datetime.now().isoformat()}")
        print(f"🌐 Source IP: {request.environ.get('REMOTE_ADDR', 'unknown')}")
        print(f"🔗 User Agent: {request.headers.get('User-Agent', 'unknown')}")
        
        # Log all form data for debugging
        print("📋 All callback data received:")
        for key, value in request.form.items():
            if len(value) > 100:
                print(f"  {key}: {value[:100]}... (truncated)")
            else:
                print(f"  {key}: {value}")
        
        # Get callback data
        request_id = request.form.get('request-id', '').strip()
        target_language = request.form.get('target-language', '').strip()
        translated_text = request.form.get('translated-text', '').strip()
        
        print(f"🆔 Request ID: {request_id}")
        print(f"🌍 Target Language: {target_language}")
        print(f"📝 Translation: {translated_text[:100]}{'...' if len(translated_text) > 100 else ''}")
        
        # Store the translation result
        if request_id in correlation_map:
            correlation_map[request_id]['status'] = 'completed'
            correlation_map[request_id]['translation'] = translated_text
            correlation_map[request_id]['completed_at'] = datetime.now().isoformat()
            
            # Calculate how long it took
            try:
                start_time = datetime.fromisoformat(correlation_map[request_id]['timestamp'])
                duration = datetime.now() - start_time
                print(f"⏱️  Translation completed in {duration.total_seconds():.1f} seconds")
                correlation_map[request_id]['duration_seconds'] = duration.total_seconds()
            except:
                pass
                
            print(f"✅ Translation stored for ID: {request_id}")
        else:
            print(f"⚠️  Warning: Received callback for unknown request ID: {request_id}")
            print("   This might be from an earlier session or timing issue")
            # Store it anyway in case of timing issues
            correlation_map[request_id] = {
                'status': 'completed',
                'translation': translated_text,
                'timestamp': datetime.now().isoformat(),
                'target_language': target_language,
                'completed_at': datetime.now().isoformat()
            }
            print(f"📥 Stored unknown callback for ID: {request_id}")
        
        print("✅ Callback processed successfully!")
        print("=" * 60)
        return "OK", 200
        
    except Exception as e:
        print(f"❌ Error in callback: {e}")
        print("=" * 60)
        return "ERROR", 500

@app.route('/status')
def status():
    """Debug endpoint to check correlation map status and connection info"""
    callback_url = get_callback_url()
    
    return jsonify({
        'callback_url': callback_url,
        'deployment_mode': 'production' if os.getenv('PRODUCTION_URL') else 'local',
        'callback_reachable': bool(os.getenv('PRODUCTION_URL')),
        'active_translations': len(correlation_map),
        'translations': {k: {
            'status': v['status'],
            'has_translation': bool(v.get('translation')),
            'timestamp': v.get('timestamp'),
            'source_language': v.get('source_language'),
            'target_language': v.get('target_language')
        } for k, v in correlation_map.items()}
    })

@app.route('/test')
def test():
    """Test page to verify the API connection"""
    return render_template('test.html')

@app.route('/api/test', methods=['POST'])
def api_test():
    """Test API endpoint connectivity"""
    try:
        # Simple test request
        test_request = {
            'sourceLanguage': 'EN',
            'targetLanguages': ['DE'],
            'callerInformation': {
                "application": config.application_name,
                "username": config.email
            },
            'textToTranslate': 'Hello World!',
            'requesterCallback': url_for('callback', _external=True)
        }
        
        headers = {'Content-Type': 'application/json'}
        json_request = json.dumps(test_request)
        
        response = requests.post(
            config.rest_url,
            auth=HTTPDigestAuth(config.application_name, config.api_password),
            headers=headers,
            data=json_request,
            timeout=30
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response': response.text,
            'success': response.status_code == 200,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/debug/<request_id>')
def debug_translation(request_id):
    """Debug endpoint to check a specific translation by ID"""
    if request_id in correlation_map:
        translation_data = correlation_map[request_id]
        return jsonify({
            'request_id': request_id,
            'status': translation_data['status'],
            'has_translation': bool(translation_data.get('translation')),
            'translation_length': len(translation_data.get('translation', '')),
            'timestamp': translation_data.get('timestamp'),
            'completed_at': translation_data.get('completed_at'),
            'source_language': translation_data.get('source_language'),
            'target_language': translation_data.get('target_language'),
            'original_text_length': len(translation_data.get('original_text', ''))
        })
    else:
        return jsonify({
            'error': f'Request ID {request_id} not found',
            'active_requests': list(correlation_map.keys())
        }), 404

@app.route('/diagnose')
def diagnose_service():
    """Comprehensive diagnostic endpoint to check eTranslation service health"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'active_translations': len(correlation_map),
        'service_tests': [],
        'recommendations': []
    }
    
    # Test 1: Simple connectivity test
    try:
        test_request = {
            'sourceLanguage': 'EN',
            'targetLanguages': ['FR'],
            'callerInformation': {
                "application": config.application_name,
                "username": config.email
            },
            'textToTranslate': 'Test',
            'requesterCallback': url_for('callback', _external=True)
        }
        
        headers = {'Content-Type': 'application/json'}
        json_request = json.dumps(test_request)
        
        response = requests.post(
            config.rest_url,
            auth=HTTPDigestAuth(config.application_name, config.api_password),
            headers=headers,
            data=json_request,
            timeout=10
        )
        
        test_result = {
            'test': 'Quick connectivity test',
            'status_code': response.status_code,
            'response': response.text.strip(),
            'success': response.status_code == 200,
            'response_time_ms': response.elapsed.total_seconds() * 1000
        }
        
        if response.status_code == 200:
            try:
                request_id = int(response.text.strip())
                if request_id > 0:
                    test_result['interpretation'] = 'Service is accepting requests normally'
                    results['recommendations'].append('Service appears healthy - longer wait times may be due to high demand')
                elif request_id == -20028:
                    test_result['interpretation'] = 'Service is experiencing high load (concurrency quota exceeded)'
                    results['recommendations'].append('Service is very busy - try again in 10-15 minutes')
                else:
                    test_result['interpretation'] = f'Service returned error code: {request_id}'
                    results['recommendations'].append('Service may be experiencing issues - check EU service status')
            except ValueError:
                test_result['interpretation'] = 'Unexpected response format'
        else:
            test_result['interpretation'] = f'HTTP error {response.status_code} - service may be down'
            results['recommendations'].append('Service connectivity issues - check EU service status')
            
        results['service_tests'].append(test_result)
        
    except requests.exceptions.Timeout:
        results['service_tests'].append({
            'test': 'Quick connectivity test',
            'success': False,
            'error': 'Timeout after 10 seconds',
            'interpretation': 'Service is very slow or unresponsive'
        })
        results['recommendations'].append('Service is very slow - likely experiencing high load')
        
    except Exception as e:
        results['service_tests'].append({
            'test': 'Quick connectivity test',
            'success': False,
            'error': str(e),
            'interpretation': 'Network or service error'
        })
    
    # Test 2: Check if callbacks are being received
    recent_callbacks = 0
    completed_translations = 0
    for req_id, data in correlation_map.items():
        if data['status'] == 'completed':
            completed_translations += 1
            if 'completed_at' in data:
                try:
                    completed_time = datetime.fromisoformat(data['completed_at'])
                    if (datetime.now() - completed_time).total_seconds() < 3600:  # Last hour
                        recent_callbacks += 1
                except:
                    pass
    
    results['callback_analysis'] = {
        'total_completed_translations': completed_translations,
        'recent_callbacks_last_hour': recent_callbacks,
        'interpretation': 'Callbacks working normally' if recent_callbacks > 0 or completed_translations > 0 else 'No recent callbacks received'
    }
    
    if recent_callbacks == 0 and len(correlation_map) > 0:
        results['recommendations'].append('No recent callbacks received - service may be experiencing callback delivery issues')
    
    # Test 3: Analyze pending translations
    pending_translations = []
    for req_id, data in correlation_map.items():
        if data['status'] == 'pending':
            try:
                wait_time = (datetime.now() - datetime.fromisoformat(data['timestamp'])).total_seconds()
                pending_translations.append({
                    'request_id': req_id,
                    'wait_time_seconds': int(wait_time),
                    'wait_time_minutes': round(wait_time / 60, 1),
                    'language_pair': f"{data.get('source_language', '?')} -> {data.get('target_language', '?')}"
                })
            except:
                pass
    
    results['pending_analysis'] = {
        'count': len(pending_translations),
        'longest_wait_minutes': max([t['wait_time_minutes'] for t in pending_translations]) if pending_translations else 0,
        'details': pending_translations[:5]  # Show first 5
    }
    
    if pending_translations:
        avg_wait = sum([t['wait_time_minutes'] for t in pending_translations]) / len(pending_translations)
        if avg_wait > 3:
            results['recommendations'].append(f'Average wait time is {avg_wait:.1f} minutes - service is experiencing delays')
        
    # Overall assessment
    if not results['recommendations']:
        results['recommendations'].append('Service appears to be operating normally')
    
    return jsonify(results)

@app.route('/test-quick', methods=['POST'])
def test_quick_translation():
    """Quick test with a simple word to check service responsiveness"""
    try:
        # Simple test with just one word
        test_request = {
            'sourceLanguage': 'EN',
            'targetLanguages': ['FR'],
            'callerInformation': {
                "application": config.application_name,
                "username": config.email
            },
            'textToTranslate': 'Hello',
            'requesterCallback': url_for('callback', _external=True)
        }
        
        headers = {'Content-Type': 'application/json'}
        json_request = json.dumps(test_request)
        
        start_time = datetime.now()
        response = requests.post(
            config.rest_url,
            auth=HTTPDigestAuth(config.application_name, config.api_password),
            headers=headers,
            data=json_request,
            timeout=30
        )
        end_time = datetime.now()
        
        return jsonify({
            'status_code': response.status_code,
            'response': response.text.strip(),
            'response_time_ms': (end_time - start_time).total_seconds() * 1000,
            'success': response.status_code == 200,
            'timestamp': start_time.isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/test-callback', methods=['GET', 'POST'])
def test_callback():
    """Test endpoint to verify callback functionality"""
    if request.method == 'GET':
        # Display a simple form to test callback manually
        return '''
        <!DOCTYPE html>
        <html>
        <head><title>Callback Test</title></head>
        <body>
            <h2>Test Callback Endpoint</h2>
            <p>This form simulates what the EU eTranslation service sends to your callback URL.</p>
            <form method="POST">
                <label>Request ID: <input name="request-id" value="test-123" /></label><br><br>
                <label>Target Language: <input name="target-language" value="DE" /></label><br><br>
                <label>Translated Text: <textarea name="translated-text">Hallo Welt!</textarea></label><br><br>
                <button type="submit">Send Test Callback</button>
            </form>
            <br>
            <a href="/status">Check Status</a> | <a href="/">Back to Main</a>
        </body>
        </html>
        '''
    else:
        # Process the test callback (same logic as real callback)
        return callback()

@app.route('/callback-log')
def callback_log():
    """Show recent callback attempts and logs"""
    # Check if we have any callback attempts logged
    callback_attempts = []
    
    return jsonify({
        'callback_url': get_callback_url(),
        'deployment_status': 'production' if os.getenv('PRODUCTION_URL') else 'local',
        'callback_test_url': url_for('test_callback', _external=True),
        'total_requests_stored': len(correlation_map),
        'completed_translations': len([v for v in correlation_map.values() if v['status'] == 'completed']),
        'pending_translations': len([v for v in correlation_map.values() if v['status'] == 'pending']),
        'recent_activity': list(correlation_map.keys())[-5:] if correlation_map else [],
        'instructions': {
            'manual_test': f"Visit {url_for('test_callback', _external=True)} to manually test the callback",
            'check_logs': "Check your deployment logs for 'Callback received from eTranslation!' messages",
            'verify_deployment': "Ensure your production URL is correctly set and accessible"
        }
    })

if __name__ == '__main__':
    print("Starting EU eTranslation Web Application")
    print("=" * 50)
    print(f"Application Name: {config.application_name}")
    print(f"Email: {config.email}")
    print(f"REST Endpoint: {config.rest_url}")
    print()
    print("Starting Flask server...")
    
    # Production-ready server configuration
    # Use PORT environment variable for cloud deployments (Heroku, Railway, etc.)
    port = int(os.environ.get('PORT', config.flask_port))
    host = '0.0.0.0'  # Required for cloud deployments
    debug = config.flask_debug and os.environ.get('FLASK_ENV') != 'production'
    
    print(f"Server will start on {host}:{port}")
    app.run(host=host, port=port, debug=debug)
