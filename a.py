from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup (default localhost)
client = MongoClient('mongodb://localhost:27017/')
db = client['demo_db']
users_collection = db['users']
invoices_collection = db['invoices']

users_collection.insert_one({'name': 'John Doe', 'gmail': 'john.doe@example.com'})

@app.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user with their name and Gmail.
    
    Expected JSON payload:
    {
        "name": "string",
        "gmail": "string"
    }
    
    Returns:
        201: User registered successfully
        400: Invalid/missing data
        409: User already exists with provided Gmail
    """
    data = request.get_json()
    
    # Validate request data
    if not data:
        return jsonify({'error': 'No data provided'}), 400
        
    name = data.get('name', '').strip()
    gmail = data.get('gmail', '').strip().lower()
    
    # Validate required fields
    if not name or not gmail:
        return jsonify({'error': 'Name and Gmail are required.'}), 400
        
    # Validate email format
    if not '@' in gmail:
        return jsonify({'error': 'Invalid Gmail format'}), 400
        
    # Check if user already exists
    existing_user = users_collection.find_one({'gmail': gmail})
    if existing_user:
        return jsonify({'error': 'User with this Gmail already exists'}), 409
        
    # Create and insert new user
    user = {
        'name': name,
        'gmail': gmail,
        'created_at': datetime.utcnow()
    }
    users_collection.insert_one(user)
    return jsonify({'message': 'User registered successfully.'}), 201

@app.route('/invoice', methods=['GET'])
def get_invoice():
    gmail = request.args.get('gmail')
    if not gmail:
        return jsonify({'error': 'Gmail is required as a query parameter.'}), 400
    invoice = invoices_collection.find_one({'gmail': gmail}, {'_id': 0})
    if not invoice:
        return jsonify({'error': 'Invoice not found for this Gmail.'}), 404
    return jsonify(invoice)

if __name__ == '__main__':
    app.run(debug=True)
