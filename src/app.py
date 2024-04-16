from flask import Flask, jsonify, request
from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from config import config
from validatePassword import validate
import re


app=Flask(__name__)
CORS(app)

conexion = MySQL(app)

@app.route('/register', methods = ['POST'])
def register():
    try:
        cursor = conexion.connection.cursor()
        sql = """ INSERT INTO usuario (user_id, username, password) 
        VALUES ('{0}', '{1}', '{2}')""".format(request.json['user_id'], request.json['username'], request.json['password'])

        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'message': 'Usuario registrado'})
    except Exception as ex:
         return  jsonify({'message': 'Error al crear el usuario'})
    

@app.route('/login', methods = ['POST'])
def login():
    data = request.json
    print(data)
    if not data.get('username') or not data.get('password'):
        return jsonify({'message': 'Todos los campos son requeridos'}), 400
    
    try:
        username = data['username']
        password = data['password']
            
        cursor = conexion.connection.cursor()

        sql = "SELECT * FROM usuario WHERE username = '{0}' ".format(username)
        cursor.execute(sql)
        user = cursor.fetchone()
        if user:

            isValid, errorMessage = validate(request.json['password'])

            if not isValid:
                return jsonify({'message': errorMessage}), 400
            
            password_db = user[2]
            

            if password_db == password:
                return jsonify({'username': user[1]})
            else:
                return jsonify({'message': 'Contraseña incorrecta'}), 401
        else:
            return jsonify({'message': 'Usuario no encontrado'}), 404
    
    except Exception as ex:
        print(ex)
        return jsonify({'message': 'Error al iniciar sesión'}), 500
    

@app.route('/customer/search/<identifier>', methods=['GET'])
def getCustomer(identifier):
    try:
        if len(identifier) == 10 and identifier.isdigit(): 
            return getCustomerByPhone(identifier)
        elif '@' in identifier:
            return getCustomerByEmail(identifier)
        elif identifier.isdigit():
            return getCustomerByCode(identifier)
        else:
            return getCustomerByName(identifier)
    except Exception as ex:
        return jsonify({'message': 'Error al obtener el cliente'})

@app.route('/customer/code/<code>', methods=['GET'])
def getCustomerByCode(code):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM clientes WHERE clave = '{0}' ".format(code)
        cursor.execute(sql)
        data = cursor.fetchall()
        customers = []
        for fila in data:
            customer = {'clave': fila[0], 'nombre': fila[1], 'correo': fila[2], 'telefono': fila[3]}
            customers.append(customer)
        return jsonify({'clientes': customers})
    except Exception as ex:
        return jsonify({'message': 'Error al obtener el cliente'})

@app.route('/customer/name/<name>', methods=['GET'])
def getCustomerByName(name):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM clientes WHERE CONCAT(' ', nombre, ' ') LIKE '% {0} %' ".format(name)
        cursor.execute(sql)
        data = cursor.fetchall()
        customers = []
        for fila in data:
            customer = {'clave': fila[0], 'nombre': fila[1], 'correo': fila[2], 'telefono': fila[3]}
            customers.append(customer)
        return jsonify({'clientes': customers})
    except Exception as ex:
        return jsonify({'message': 'Error al obtener el cliente'}) 

@app.route('/customer/email/<email>', methods=['GET'])
def getCustomerByEmail(email):
    try:
        # Validar el formato del correo electrónico
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({'message': 'El formato del correo electrónico es inválido'}), 400

        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM clientes WHERE correo LIKE '%{0}%' ".format(email)
        cursor.execute(sql)
        data = cursor.fetchall()
        customers = []
        for fila in data:
            customer = {'clave': fila[0], 'nombre': fila[1], 'correo': fila[2], 'telefono': fila[3]}
            customers.append(customer)
        return jsonify({'clientes': customers})
    except Exception as ex:
        return jsonify({'message': 'Error al obtener el cliente'}), 500


@app.route('/customer/phone/<phone>', methods=['GET'])
def getCustomerByPhone(phone):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT * FROM clientes WHERE telefono LIKE '%{0}%' ".format(phone)
        cursor.execute(sql)
        data = cursor.fetchall()
        customers = []
        for fila in data:
            customer = {'clave': fila[0], 'nombre': fila[1], 'correo': fila[2], 'telefono': fila[3]}
            customers.append(customer)
        return jsonify({'clientes': customers})
    except Exception as ex:
        return jsonify({'message': 'Error al obtener el cliente'}) 

def customers():
    try:
        cursor = conexion.connection.cursor()
        sql = 'SELECT * FROM clientes'
        cursor.execute(sql)
        data = cursor.fetchall()
        customers = []
        for fila in data:
            customer = {'clave': fila[0], 'nombre': fila[1], 'correo': fila[2], 'telefono': fila[3]}
            customers.append(customer)
        return jsonify({'clientes': customers})
    except Exception as ex:
        return  jsonify({'message': 'Error al obtener los clientes'})

@app.route('/customer/<code>', methods=['DELETE'])
def deleteCustomer(code):
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM clientes WHERE clave = '{0}'".format(code)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'message': 'Cliente eliminado correctamente'})
    except Exception as ex:
        return jsonify({'message': 'Error al eliminar el cliente'})

@app.route('/customer/<code>', methods=['PUT'])
def updateCustomer(code):
    try:
        cursor = conexion.connection.cursor()
        data = request.json

        if data['clave'] != code:
            cursor.execute("SELECT * FROM clientes WHERE clave = %s", (data['clave'],))
            existing_customer = cursor.fetchone()

            if existing_customer and existing_customer[0] != code:
                return jsonify({'message': 'Ya existe un cliente con la misma clave'}), 409

        sql = """UPDATE clientes SET clave = %s, nombre = %s, correo = %s, telefono = %s WHERE clave = %s"""
        cursor.execute(sql, (data['clave'], data['nombre'], data['correo'], data['telefono'], code))
        conexion.connection.commit()

        updated_code = data['clave'] if 'clave' in data else code

        cursor.execute("SELECT * FROM clientes WHERE clave = %s", (updated_code,))
        updated_customer = cursor.fetchone()

        if updated_customer:
            customer = {
                'clave': updated_customer[0],
                'nombre': updated_customer[1],
                'correo': updated_customer[2],
                'telefono': updated_customer[3]
            }

            return jsonify({'cliente': customer, 'message': 'Información actualizada'})

    except Exception as ex:
        return jsonify({'message': 'Error al actualizar el cliente'}), 500


@app.route('/customer', methods=['POST'])
def createCustomer():
    try:
        required_fields = ['clave', 'nombre', 'correo', 'telefono']
        if not all(field in request.json for field in required_fields):
            return jsonify({'message': 'Todos los campos son requeridos'}), 400

        cursor = conexion.connection.cursor()
        data = request.json

        cursor.execute("SELECT * FROM clientes WHERE clave = %s", (data['clave'],))
        existing_customer = cursor.fetchone()

        if existing_customer:
            return jsonify({'message': 'Ya existe un cliente con la misma clave'}), 409

        sql = """INSERT INTO clientes (clave, nombre, correo, telefono) 
                 VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (data['clave'], data['nombre'], data['correo'], data['telefono']))
        conexion.connection.commit()
        new_customer = {
            'clave': data['clave'],
            'nombre': data['nombre'],
            'correo': data['correo'],
            'telefono': data['telefono']
        }
        return jsonify({"cliente": [ new_customer]}), 201

    except Exception as ex:
        return jsonify({'message': 'Error al crear el cliente'}), 500



if(__name__ == '__main__'):
    app.config.from_object(config['development'])
    app.run()