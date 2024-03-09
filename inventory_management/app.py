from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to initialize the database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS items
                 (id INTEGER PRIMARY KEY, name TEXT, quantity INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS custom_parameters
                 (id INTEGER PRIMARY KEY, item_id INTEGER, param_name TEXT, param_value TEXT)''')
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items')
    items = c.fetchall()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('INSERT INTO items (name, quantity) VALUES (?, ?)', (name, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add_item.html')
    
@app.route('/remove/<int:item_id>', methods=['POST'])
def remove_item(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/increase/<int:item_id>', methods=['POST'])
def increase_quantity(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE items SET quantity = quantity + 1 WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/decrease/<int:item_id>', methods=['POST'])
def decrease_quantity(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('UPDATE items SET quantity = quantity - 1 WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))
    
@app.route('/product_info/<int:item_id>', methods=['GET', 'POST'])
def product_info(item_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
    item = c.fetchone()

    if request.method == 'POST':
        param_name = request.form['param_name']
        param_value = request.form['param_value']
        c.execute('INSERT INTO custom_parameters (item_id, param_name, param_value) VALUES (?, ?, ?)', (item_id, param_name, param_value))
        conn.commit()

    c.execute('SELECT param_name, param_value FROM custom_parameters WHERE item_id = ?', (item_id,))
    custom_parameters = dict(c.fetchall())
    
    conn.close()

    return render_template('product_info.html', item=item, custom_parameters=custom_parameters)
    
@app.route('/remove_parameter/<int:item_id>/<param_name>', methods=['POST'])
def remove_parameter(item_id, param_name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('DELETE FROM custom_parameters WHERE item_id = ? AND param_name = ?', (item_id, param_name))
    conn.commit()
    conn.close()
    return redirect(url_for('product_info', item_id=item_id))

@app.route('/edit_parameter/<int:item_id>/<param_name>', methods=['GET', 'POST'])
def edit_parameter(item_id, param_name):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    if request.method == 'POST':
        new_value = request.form['new_value']
        c.execute('UPDATE custom_parameters SET param_value = ? WHERE item_id = ? AND param_name = ?', (new_value, item_id, param_name))
        conn.commit()
        conn.close()
        return redirect(url_for('product_info', item_id=item_id))
    else:
        c.execute('SELECT param_value FROM custom_parameters WHERE item_id = ? AND param_name = ?', (item_id, param_name))
        param_value = c.fetchone()[0]
        conn.close()
        return render_template('edit_parameter.html', item_id=item_id, param_name=param_name, param_value=param_value)


if __name__ == '__main__':
    app.run(debug=True)