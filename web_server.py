from flask import Flask, request, jsonify

def create_app(explorer):
    app = Flask(__name__)

    @app.route('/webhook', methods=['POST'])
    def webhook():
        """
        Endpoint to handle webhook notifications.
        """
        payload = request.json
        explorer.handle_webhook(payload)
        return jsonify({'status': 'received'}), 200

    return app

def run_flask_app(app):
    """
    Runs the Flask app.
    """
    app.run(host='0.0.0.0', port=5000, debug=False)
