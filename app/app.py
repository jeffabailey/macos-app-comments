from flask import Flask, render_template, jsonify, request, Response
import json
import os
import sys
import subprocess

app = Flask(__name__)

def load_applications():
    """Load applications data from the JSON file"""
    json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'applications.json')
    with open(json_path, 'r') as f:
        return json.load(f)

@app.route('/')
def index():
    """Main page displaying all applications"""
    applications = load_applications()
    return render_template('index.html', applications=applications)

@app.route('/copy-description', methods=['POST'])
def copy_description():
    """HTMX endpoint to copy description to clipboard"""
    app_name = request.form.get('app_name')
    applications = load_applications()
    description = applications.get(app_name, '')
    
    return jsonify({
        'success': True,
        'message': f'Description for "{app_name}" copied to clipboard',
        'description': description
    })

@app.route('/refresh-applications', methods=['POST'])
def refresh_applications():
    """Refresh applications.json by running the metadata builder"""
    import subprocess
    import os
    
    try:
        # Get the path to the metadata builder script
        script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app_metadata_builder.py')
        
        # Run the metadata builder script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(script_path)
        )
        
        if result.returncode == 0:
            # Reload applications after successful update
            applications = load_applications()
            return jsonify({
                'success': True,
                'message': f'Successfully refreshed {len(applications)} applications',
                'count': len(applications)
            })
        else:
            return jsonify({
                'success': False,
                'message': f'Error running metadata builder: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error refreshing applications: {str(e)}'
        }), 500

def _stream_process_output(process):
    """Stream process output line by line."""
    import time
    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            yield f"data: {json.dumps({'type': 'output', 'message': line.strip()})}\n\n"
            time.sleep(0.01)

def _wait_for_process_completion(process):
    """Wait for process completion with timeout."""
    yield f"data: {json.dumps({'type': 'output', 'message': 'Waiting for process to complete...'})}\n\n"
    try:
        return_code = process.wait(timeout=300)  # 5 minute timeout
        yield f"data: {json.dumps({'type': 'output', 'message': f'Process completed with return code: {return_code}'})}\n\n"
        return return_code
    except subprocess.TimeoutExpired:
        process.kill()
        yield f"data: {json.dumps({'type': 'error', 'message': 'Process timed out after 5 minutes'})}\n\n"
        return None

def _handle_process_result(return_code):
    """Handle process completion result."""
    if return_code == 0:
        applications = load_applications()
        yield f"data: {json.dumps({'type': 'success', 'message': f'Successfully refreshed {len(applications)} applications', 'count': len(applications)})}\n\n"
    else:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Process failed with return code {return_code}'})}\n\n"

@app.route('/refresh-applications-stream')
def refresh_applications_stream():
    """Stream the refresh process with real-time output"""
    def generate():
        try:
            yield f"data: {json.dumps({'type': 'output', 'message': 'Starting metadata builder...'})}\n\n"
            
            script_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app_metadata_builder.py')
            yield f"data: {json.dumps({'type': 'output', 'message': f'Script path: {script_path}'})}\n\n"
            
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=0,
                universal_newlines=True,
                cwd=os.path.dirname(script_path),
                env=dict(os.environ, PYTHONUNBUFFERED='1')
            )
            
            yield f"data: {json.dumps({'type': 'output', 'message': 'Process started, streaming output...'})}\n\n"
            
            yield from _stream_process_output(process)
            return_code = yield from _wait_for_process_completion(process)
            
            if return_code is not None:
                yield from _handle_process_result(return_code)
                
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=1337) 