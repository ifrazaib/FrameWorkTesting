from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/echo', methods=['POST'])
def echo():
    """
    Example:
    Input JSON:  {"message": "Hello"}
    Output JSON: {"echo": "Hello"}
    """
    data = request.get_json(force=True)  # Parse JSON input
    message = data.get('message', '')    # Get "message" key from JSON
    return jsonify({"echo": message}), 200  # Return response

if __name__ == '__main__':
    app.run(debug=True)
