from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user, LoginManager
import pyodbc



usuario=""

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'


# Configuración de la conexión a la base de datos SQL Server
server = 'BRIANPC'
database = 'BusesTerminator'
username = 'sa'
password = 'Welcome!23'
conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password+';')


# Página de inicio
@app.route('/')

def index():
    return render_template ('index.html')

# Listar todas las categorías
@app.route('/rutas')
def listar_rutas():
    cursor = conn.cursor()
    cursor.execute('EXEC spObtenerRutasConDetalles')
    rutas = cursor.fetchall()
    return render_template('rutas.html', rutas=rutas)

# Crear nueva categoría
@app.route('/rutas/comprarTicket', methods=['GET', 'POST'])

def ComprarTicket():
    cursor = conn.cursor()
    cursor.execute('EXEC spObtenerRutasConDetalles')
    rutas = cursor.fetchall()
    cursor.execute('select*from MetodoPago')
    metodos= cursor.fetchall()
    if request.method == 'POST':
        error=None
        idRuta = request.form.get("IDRuta")
        metodo=request.form.get("IDMetodo")
        Usuario = request.form.get("UsuarioHidden")
        cursor.execute("EXEC sp_ComprarTiquete @Ruta=?, @IDMetodo=?, @Usuario=?", (idRuta, metodo, Usuario))
        conn.commit()
        flash('Compra exitosa')
        


        return redirect(url_for('showFactura'))
    else:
        error='Credenciales invalidas'
    return render_template('comprarTicket.html',rutas=rutas, metodos=metodos, usuario=usuario, error=error)




@app.route('/iniciarSesion',methods=['GET', 'POST'])
def iniciarSesion():
    
    if request.method=='POST':
        global usuario
        usuario=int(request.form.get('Usuario'))
        contraseñaP=request.form.get('passw')
        cursor=conn.cursor()
        cursor.execute('EXEC sp_ValidarUsuario @Usuario=?,@Contrasena=?',(usuario,contraseñaP ))
        cursor.execute('select*from tablaValidacion')
        validacion=cursor.fetchone()
        validacion1= int(validacion[0])
        if validacion1==1:
           # login_user(usuario, remember=True)
            flash('Inicio de sesion exitoso', category='success')
            return redirect('main')      
        else :
            flash('Inicio de sesion fallido', category='error')
            return redirect('iniciarSesion')  
    

    return render_template('login.html')

@app.route('/iniciar/sesion/registro',methods=['GET', 'POST'])
def registrar():
    if request.method=='POST':
        id=int(request.form.get("cedula"))
        nombre=request.form.get("Nombre")
        pApellido=request.form.get("primerApellido")
        sApellido=request.form.get("segundoApellido")
        tel=int(request.form.get("telefono"))
        contra=request.form.get("contra")
        cursor=conn.cursor()
        cursor.execute('EXEC sp_InsertarUsuario @Id=?, @NombreU=?, @Apell1=?, @Apell2=?, @Tel=?,@Contra=?',(id,nombre,pApellido,sApellido,tel,contra))
        cursor.commit()
        return render_template('login.html')
    
    return render_template('sign_up.html')


@app.route('/main')
def mainPage():
    return render_template('mainPage.html')

@app.route('/cerrarSesion')
def logout():
    return render_template('index.html')


@app.route('/rutas/verTickets')
def showTickets():
    cursor = conn.cursor()
    cursor.execute('EXEC sp_MostrarTiquete @Identificacion=?',(usuario,))
    tiquetes=cursor.fetchall()

    return render_template('verTickets.html',tiquetes=tiquetes)



@app.route('/rutas/verFacturas')
def showFacturas():

    cursor = conn.cursor()
    cursor.execute('EXEC sp_MostrarFacturas @Identificacion=?',(usuario,))
    facturas=cursor.fetchall()

    return render_template('facturas.html',facturas=facturas)


@app.route('/rutas/comprarTicket/factura')
def showFactura():
    cursor=conn.cursor()
    cursor.execute('EXEC sp_MostrarUltimaFactura @Identificacion=?',(usuario))
    factura=cursor.fetchone()
    
    return render_template('facturaTicket.html', factura=factura)






if __name__ == '__main__':
    app.run(debug=True)