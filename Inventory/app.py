
from flask import Flask, flash, render_template, request, redirect, url_for
from models import db, Product, Location, ProductMovement
from datetime import datetime
import secrets

app = Flask(__name__)

app.config['SECRET_KEY'] = secrets.token_hex(16)  
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root123@localhost/inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():

    locations = Location.query.all()
    products = Product.query.all()
    product_balances = {}
    for location in locations:
        product_balances[location.name] = {}

    # Populate the product balances
    movements = ProductMovement.query.all()
    for movement in movements:
        location_id = movement.to_location if movement.to_location else movement.from_location
        product_id = movement.product_id
        qty = movement.qty

        product_name = Product.query.get(product_id).name

        if product_name not in product_balances[location_id]:
            product_balances[location_id][product_name] = qty
        else:
            product_balances[location_id][product_name] += qty

    return render_template('inventory.html', locations=locations, products=products, balances=product_balances)


@app.route('/product', methods=['GET', 'POST'])
def manage_product():
    if request.method == 'POST':
        product_id = request.form['product_id']
        product_name = request.form['product_name']
        product = Product(product_id=product_id, name=product_name)
        db.session.add(product)
        db.session.commit()
        return redirect(url_for('manage_product'))
    products = Product.query.all()
    return render_template('manage_product.html', products=products)

@app.route('/location', methods=['GET', 'POST'])
def manage_location():
    if request.method == 'POST':
        location_id = request.form['location_id']
        location_name = request.form['location_name']
        location = Location(location_id=location_id, name=location_name)
        db.session.add(location)
        db.session.commit()
        return redirect(url_for('manage_location'))
    locations = Location.query.all()
    return render_template('manage_location.html', locations=locations)


@app.route('/movement', methods=['GET', 'POST'])
def manage_movement():
    if request.method == 'POST':
        movement_id = request.form['movement_id']
        timestamp = datetime.utcnow()
        from_location = request.form['from_location']
        to_location = request.form['to_location']
        product_name = request.form['product_id'] 
        qty = int(request.form['qty'])

 
        product = Product.query.filter_by(name=product_name).first()
        if product:
            product_id = product.product_id

            movement = ProductMovement(
                movement_id=movement_id,
                timestamp=timestamp,
                from_location=from_location,
                to_location=to_location,
                product_id=product_id,
                qty=qty
            )

            db.session.add(movement)
            db.session.commit()
            return redirect(url_for('manage_movement'))

    movements = ProductMovement.query.all()
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('manage_movement.html', movements=movements, products=products, locations=locations)

@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get(product_id)
    if request.method == 'POST':
        product.name = request.form['product_name']
        db.session.commit()
        return redirect(url_for('manage_product'))
    return render_template('edit/edit_product.html', product=product)

@app.route('/edit_location/<location_id>', methods=['GET', 'POST'])
def edit_location(location_id):
    location = Location.query.get(location_id)
    if request.method == 'POST':
        location.name = request.form['location_name']
        db.session.commit()
        return redirect(url_for('manage_location'))
    return render_template('edit/edit_location.html', location=location)

@app.route('/edit_movement/<movement_id>', methods=['GET', 'POST'])
def edit_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)
    products = Product.query.all()
    locations = Location.query.all()

    if request.method == 'POST':
        movement.from_location = request.form['from_location']
        movement.to_location = request.form['to_location']
        movement.product_id = request.form['product_id']
        movement.qty = int(request.form['qty'])
        db.session.commit()
        return redirect(url_for('manage_movement'))

    return render_template('edit/edit_movement.html', movement=movement, products=products, locations=locations)


@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if product:
        # Manually delete associated movements
        ProductMovement.query.filter_by(product_id=product_id).delete()
        db.session.delete(product)
        db.session.commit()
        flash(f"Product with ID {product_id} deleted successfully", 'success')
    else:
        flash(f"Product with ID {product_id} not found", 'error')

    return redirect(url_for('manage_product'))


@app.route('/delete_location/<location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get(location_id)

    if location:
        ProductMovement.query.filter((ProductMovement.from_location == location.name) | (ProductMovement.to_location == location.name)).delete()
        db.session.delete(location)
        db.session.commit()
        flash(f"Location with ID {location_id} deleted successfully", 'success')
    else:
        flash(f"Location with ID {location_id} not found", 'error')

    return redirect(url_for('manage_location'))



@app.route('/delete_movement/<movement_id>', methods=['POST'])
def delete_movement(movement_id):
    movement = ProductMovement.query.get(movement_id)

    if movement:
        db.session.delete(movement)
        db.session.commit()
        flash(f"Movement with ID {movement_id} deleted successfully", 'success')
    else:
        flash(f"Movement with ID {movement_id} not found", 'error')

    return redirect(url_for('manage_movement'))



if __name__ == '__main__':
    app.run(debug=True)