from flask import Flask, render_template, request,jsonify
from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Subscription(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable =False)
    cost = db.Column(db.Float,nullable=False)

    def __repr__(self):
        return f"<Subscription {self.name} - ${self.cost}>"


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/add/',methods=['POST'])
def add_subscription():
    data = request.json
    sub_name=data.get('name')
    sub_cost=data.get('cost')
    new_sub = Subscription(name=sub_name,cost=sub_cost)
    db.session.add(new_sub)
    db.session.commit()
    return jsonify({"status": "success", 
        "message": f"{sub_name} saved to database!"}),201

@app.route('/api/subscriptions',methods=['GET'])
def get_subscriptions():
    subs = Subscription.query.all()

    subs_list = [{"id" : sub.id,"name": sub.name, "cost": sub.cost} for sub in subs]
    return jsonify(subs_list),200

@app.route('/api/delete/<int:sub_id>',methods=['DELETE'])
def delete_subscription(sub_id):
    sub_to_delete = db.session.get(Subscription, sub_id)
    if not sub_to_delete:
        return jsonify({"error":"Subscription not found"}), 404
    db.session.delete(sub_to_delete)
    db.session.commit()
    return jsonify({"message":"Deleted subscription successfully"}), 200

if __name__=="__main__":
    app.run(debug=True)