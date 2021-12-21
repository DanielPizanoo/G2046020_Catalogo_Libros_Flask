import re
from sys import meta_path
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy

# from flask_bcrypt import Bcrypt
import json

from werkzeug.utils import redirect

app = Flask(__name__)
db = SQLAlchemy(app)
app.config[
    "SQLALCHEMY_DATABASE_URI"
] = "postgresql+psycopg2://postgres:12345@localhost:5432/libros_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
# bcrypt = Bcrypt(app)

# Creacion de tablas de BD
class Usuarios(db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80))
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password


class Editorial(db.Model):
    __tablename__ = "editorial"
    id_editorial = db.Column(db.Integer, primary_key=True)
    nombre_editorial = db.Column(db.String(80))

    def __ini__(self, nombre_editorial):
        self.nombre_editorial = nombre_editorial


class Genero(db.Model):
    __tablename__ = "genero"
    id_genero = db.Column(db.Integer, primary_key=True)
    nombre_genero = db.Column(db.String(80))

    def __init__(self, nombre_genero):
        self.nombre_genero = nombre_genero


class Autor(db.Model):
    __tablename__ = "autor"
    id_autor = db.Column(db.Integer, primary_key=True)
    nombre_autor = db.Column(db.String(120))
    fecha_nac = db.Column(db.Date)
    nacionalidad = db.Column(db.String(80))

    def __init__(self, nombre_autor, fecha_nac, nacionalidad):
        self.nombre_autor = nombre_autor
        self.fecha_nac = fecha_nac
        self.nacionalidad = nacionalidad


class Libro(db.Model):
    __tablename__ = "libro"
    id_libro = db.Column(db.Integer, primary_key=True)
    titulo_libro = db.Column(db.String(255))
    fecha_publicacion = db.Column(db.Date)
    numero_paginas = db.Column(db.Integer)
    formato = db.Column(db.String(30))
    id_editorial = db.Column(db.Integer, db.ForeignKey("editorial.id_editorial"))
    id_genero = db.Column(db.Integer, db.ForeignKey("genero.id_genero"))
    id_autor = db.Column(db.Integer, db.ForeignKey("autor.id_autor"))

    def __init__(
        self,
        titulo_libro,
        fecha_publicacion,
        numero_paginas,
        formato,
        id_editorial,
        id_genero,
        id_autor,
    ):
        self.titulo_libro = titulo_libro
        self.fecha_publicacion = fecha_publicacion
        self.numero_paginas = numero_paginas
        self.formato = formato
        self.id_editorial = id_editorial
        self.id_genero = id_genero
        self.id_autor = id_autor


class Favorito(db.Model):
    __tablename__ = "favorito"
    id_favorito = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    id_libro = db.Column(db.Integer, db.ForeignKey("libro.id_libro"))

    def __init__(self, id_usuario, id_libro):
        self.id_usuario = id_usuario
        self.id_libro = id_libro


# Metodo para consultar cada tabla de base de datos
@app.route("/consulta")
def consulta():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_usuarios = Usuarios.query.all()
    consulta_editoriales = Editorial.query.all()
    consulta_generos = Genero.query.all()
    consulta_autores = Autor.query.all()
    consulta_libros = Libro.query.all()
    consulta_favoritos = Favorito.query.all()

    # Convertir en diccionario
    dict_consultas["usuarios"] = list_usuario(consulta_usuarios)
    dict_consultas["editoriales"] = list_editorial(consulta_editoriales)
    dict_consultas["generos"] = list_genero(consulta_generos)
    dict_consultas["autores"] = list_autor(consulta_autores)
    dict_consultas["libros"] = list_libro(consulta_libros)
    dict_consultas["favoritos"] = list_favorito(consulta_favoritos)

    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False, default=str)
    return json_string, 200


def list_usuario(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {"id": data.id, "email": data.email, "password": data.password}
    return new_dict


def list_editorial(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_editorial": data.id_editorial,
            "nombre_editorial": data.nombre_editorial,
        }
    return new_dict


def list_genero(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_genero": data.id_genero,
            "nombre_genero": data.nombre_genero,
        }
    return new_dict


def list_autor(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {"id_autor": data.id_autor, "nombre_autor": data.nombre_autor}
    return new_dict


def list_libro(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_libro": data.id_libro,
            "titulo_libro": data.titulo_libro,
            "fecha_publicacion": data.fecha_publicacion,
            "numero_paginas": data.numero_paginas,
            "formato": data.formato,
            "id_editorial": data.id_editorial,
            "id_genero": data.id_genero,
            "id_autor": data.id_autor,
        }
    return new_dict


def list_favorito(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_favorito": data.id_favorito,
            "id_usuario": data.id_usuario,
            "id_libro": data.id_libro,
        }
    return new_dict


# Creacion de pagina inicial
@app.route("/")
def index():
    return render_template("index.html")


# --------------------------------------------------------------------
# Metodo para iniciar sesion
@app.route("/login", methods=["POST"])
def login():
    request_data = request.get_json()
    email = request_data["email"]
    password = request_data["password"]

    # email = request.form["email"]
    # password = request.form["password"]
    consulta_usuario = Usuarios.query.filter_by(email=email).first()
    if consulta_usuario.email == email and consulta_usuario.password == password:
        return "Inicio de sesión exitoso"
    else:
        return "El usuario y contraseña incorrecto"


# --------------------------------------------------------------------
# Metodo para registrar usuarios
@app.route("/registrarUsuario", methods=["POST"])
def registrarUsuario():
    request_data = request.get_json()
    email = request_data["email"]
    password = request_data["password"]

    usuario_nuevo = Usuarios(email=email, password=password)
    db.session.add(usuario_nuevo)
    db.session.commit()
    return "Usuario registrado"


@app.route("/registrar")
def registrar():
    return render_template("registro.html")


# --------------------------------------------------------------------
# Metodo para mostrar editoriales
@app.route("/consultaEditoriales")
def consultaEditorial():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_editoriales = Editorial.query.all()
    # Convertir en diccionario
    dict_consultas["editoriales"] = list_editorial(consulta_editoriales)
    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False)
    return json_string, 200


def list_editorial(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_editorial": data.id_editorial,
            "nombre_editorial": data.nombre_editorial,
        }
    return new_dict


# --------------------------------------------------------------------
# Metodo para registrar editoriales
@app.route("/registrarEditorial", methods=["POST"])
def registrarEditorial():
    request_data = request.get_json()
    nombre_editorial = request_data["nombre_editorial"]

    editorial_nuevo = Editorial(nombre_editorial=nombre_editorial)
    db.session.add(editorial_nuevo)
    db.session.commit()
    return "Editorial registrado"


@app.route("/crearEditorial", methods=["POST"])
def crearEditorial():
    return "Editorial registrado"


# --------------------------------------------------------------------
# Metodo para mostrar generos
@app.route("/consultaGeneros")
def consultaGenero():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_generos = Genero.query.all()
    # Convertir en diccionario
    dict_consultas["generos"] = list_genero(consulta_generos)
    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False)
    return json_string, 200


def list_genero(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_genero": data.id_genero,
            "nombre_genero": data.nombre_genero,
        }
    return new_dict


# --------------------------------------------------------------------
# Metodo para registrar generos
@app.route("/registrarGenero", methods=["POST"])
def registrarGenero():
    request_data = request.get_json()
    nombre_genero = request_data["nombre_genero"]

    genero_nuevo = Genero(nombre_genero=nombre_genero)
    db.session.add(genero_nuevo)
    db.session.commit()
    return "Genero registrado"


@app.route("/crearGenero", methods=["POST"])
def crearGenero():
    return "Genero registrado"


# --------------------------------------------------------------------
# Metodo para mostrar autores
@app.route("/consultaAutores")
def consultaAutor():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_autores = Autor.query.all()
    # Convertir en diccionario
    dict_consultas["autores"] = list_autor(consulta_autores)
    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False, default=str)
    return json_string, 200


def list_autor(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_autor": data.id_autor,
            "nombre_autor": data.nombre_autor,
            "fecha_nac": data.fecha_nac,
            "nacionalidad": data.nacionalidad,
        }
    return new_dict


# --------------------------------------------------------------------
# Metodo para registrar autores
@app.route("/registrarAutor", methods=["POST"])
def registrarAutor():
    request_data = request.get_json()
    nombre_autor = request_data["nombre_autor"]
    fecha_nac = request_data["fecha_nac"]
    nacionalidad = request_data["nacionalidad"]

    autor_nuevo = Autor(
        nombre_autor=nombre_autor, fecha_nac=fecha_nac, nacionalidad=nacionalidad
    )
    db.session.add(autor_nuevo)
    db.session.commit()
    return "Autor registrado"


@app.route("/crearAutor", methods=["POST"])
def crearAutor():
    return "Autor registrado"


# --------------------------------------------------------------------
# Metodo para mostrar libros
@app.route("/consultaLibros")
def consultaLibro():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_libros = (
        Libro.query.join(Genero, Libro.id_genero == Genero.id_genero)
        .join(Autor, Libro.id_autor == Autor.id_autor)
        .join(Editorial, Libro.id_editorial == Editorial.id_editorial)
        .add_columns(
            Libro.id_libro,
            Libro.titulo_libro,
            Libro.fecha_publicacion,
            Libro.numero_paginas,
            Libro.formato,
            Editorial.nombre_editorial,
            Genero.nombre_genero,
            Autor.nombre_autor,
        )
    )
    # Convertir en diccionario
    dict_consultas["libros"] = list_libros(consulta_libros)
    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False, default=str)
    return json_string, 200


def list_libros(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_libro": data.id_libro,
            "titulo_libro": data.titulo_libro,
            "fecha_publicacion": data.fecha_publicacion,
            "numero_paginas": data.numero_paginas,
            "formato": data.formato,
            "nombre_editorial": data.nombre_editorial,
            "nombre_genero": data.nombre_genero,
            "nombre_autor": data.nombre_autor,
        }
    return new_dict


# --------------------------------------------------------------------
# Metodo para registrar libros
@app.route("/registrarLibro", methods=["POST"])
def registrarLibro():
    request_data = request.get_json()
    titulo_libro = request_data["titulo_libro"]
    fecha_publicacion = request_data["fecha_publicacion"]
    numero_paginas = request_data["numero_paginas"]
    formato = request_data["formato"]
    id_editorial = request_data["id_editorial"]
    id_genero = request_data["id_genero"]
    id_autor = request_data["id_autor"]

    libro_nuevo = Libro(
        titulo_libro=titulo_libro,
        fecha_publicacion=fecha_publicacion,
        numero_paginas=numero_paginas,
        formato=formato,
        id_editorial=id_editorial,
        id_genero=id_genero,
        id_autor=id_autor,
    )
    db.session.add(libro_nuevo)
    db.session.commit()
    return "Libro registrado"


@app.route("/crearLibro", methods=["POST"])
def crearLibro():
    return "Libro registrado"


# --------------------------------------------------------------------
# Metodo para eliminar libros
@app.route("/eliminarLibro/<id_libro>", methods=["DELETE"])
def eliminarLibro(id_libro):
    print(id_libro)
    libro = Libro.query.filter_by(id_libro=id_libro).first()
    print(libro)
    db.session.delete(libro)
    db.session.commit()
    return "Libro eliminado exitosamente"


# --------------------------------------------------------------------
# Metodo para editar libros
# 1. Metodo para obtener libro a eliminar
@app.route("/obtenerLibro/<id_libro>")
def obtenerLibro(id_libro):
    print(id_libro)
    libro = Libro.query.filter_by(id_libro=id_libro).first()
    dict_libro = {}
    dict_libro = {
        "titulo_libro": libro.titulo_libro,
        "fecha_publicacion": libro.fecha_publicacion,
        "numero_paginas": libro.numero_paginas,
        "formato": libro.formato,
        "id_editorial": libro.id_editorial,
        "id_genero": libro.id_genero,
        "id_autor": libro.id_autor,
    }
    return json.dumps(dict_libro, ensure_ascii=False, default=str)


# 2. Metodo para actualizar datos del libro
@app.route("/actualizarLibro", methods=["PATCH"])
def actualizar_libro():
    request_data = request.get_json()
    libro = Libro.query.filter_by(id_libro=request_data["id_libro"]).first()
    libro.titulo_libro = request_data["titulo_libro"]
    libro.fecha_publicacion = request_data["fecha_publicacion"]
    libro.numero_paginas = request_data["numero_paginas"]
    libro.formato = request_data["formato"]
    libro.id_editorial = request_data["id_editorial"]
    libro.id_genero = request_data["id_genero"]
    libro.id_autor = request_data["id_autor"]
    db.session.commit()
    return "El libro fue actualizado"


# --------------------------------------------------------------------
# Metodo para mostrar favoritos
@app.route("/consultaFavoritos")
def consultaFavorito():
    # Inicializar diccionario
    dict_consultas = {}
    # Consultas a la base de datos
    consulta_favorito = (
        Libro.query.join(Usuarios, Favorito.id_usuario == Usuarios.id)
        .join(Libro, Favorito.id_libro == Libro.id_libro)
        .add_columns(Favorito.id_favorito, Usuarios.email, Libro.titulo_libro)
    )
    # Convertir en diccionario
    dict_consultas["favoritos"] = list_favoritos(consulta_favorito)
    # Convertir en formato JSON
    json_string = json.dumps(dict_consultas, ensure_ascii=False, default=str)
    return json_string, 200


def list_favoritos(list):
    new_dict = {}
    for idx, data in enumerate(list):
        new_dict[idx] = {
            "id_favorito": data.id_favorito,
            "email": data.email,
            "titulo_libro": data.titulo_libro,
        }
    return new_dict


# --------------------------------------------------------------------
# Metodo para registrar favoritos
@app.route("/registrarFavorito", methods=["POST"])
def registrarFavorito():
    request_data = request.get_json()
    id_usuario = request_data["id_usuario"]
    id_libro = request_data["id_libro"]

    favorito_nuevo = Favorito(id_usuario=id_usuario, id_libro=id_libro)
    db.session.add(favorito_nuevo)
    db.session.commit()
    return "Favorito registrado"


@app.route("/crearFavorito", methods=["POST"])
def crearFavorito():
    return "Favorito registrado"


# --------------------------------------------------------------------
# Metodo para eliminar favoritos
@app.route("/eliminarFavorito/<id_favorito>", methods=["DELETE"])
def eliminarFavorito(id_favorito):
    favorito = Favorito.query.filter_by(id_favorito=id_favorito).first()
    db.session.delete(favorito)
    db.session.commit()
    return "Libro favorito eliminado exitosamente"


# --------------------------------------------------------------------

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
