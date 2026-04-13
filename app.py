from flask import Flask, render_template, request,jsonify, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)

app.secret_key='mastersecretkey'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    # We store the scrambled hash, NOT the real password
    password_hash = db.Column(db.String(256), nullable=False) 
    
    # This creates the "One-to-Many" relationship link!
    # It tells SQLAlchemy that this user owns multiple subscriptions.
    subscriptions = db.relationship('Subscription', backref='owner', lazy=True)

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Float, nullable=False)

    # THE FOREIGN KEY: This integer matches the ID of the User who created it
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)



@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/add/',methods=['POST'])
def add_subscription():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    new_sub = Subscription(
        name=data.get('name'), 
        cost=data.get('cost'),
        user_id=session['user_id']
    )
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"message": "Saved!"}), 201

@app.route('/api/subscriptions',methods=['GET'])
def get_subscriptions():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_subs = Subscription.query.filter_by(user_id=session['user_id']).all()
    sub_list = [{"id": sub.id, "name": sub.name, "cost": sub.cost} for sub in user_subs]
    return jsonify(sub_list),200

@app.route('/api/delete/<int:sub_id>',methods=['DELETE'])
def delete_subscription(sub_id):
    if 'user_id' not in session:
        return jsonify({"error":"Unauthorized"}),401
    
    sub_to_delete = db.session.get(Subscription, sub_id)
    if not sub_to_delete:
        return jsonify({"error":"Subscription not found"}), 404
    db.session.delete(sub_to_delete)
    db.session.commit()
    return jsonify({"message":"Deleted subscription successfully"}), 200

@app.route('/api/register',methods=['POST'])
def register():
    data=request.json
    username=data.get('username')
    password=data.get('password')
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error":"Username already exists"}), 400
    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message":"User registered successfully"}), 201




@app.route('/api/login',methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/logout',methods=['POST'])
def logout():
    session.pop('user_id',None)
    return jsonify({"message":"Logged out successfully"}),200






if __name__=="__main__":
    app.run(debug=True)