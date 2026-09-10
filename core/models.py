from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class UserSettings(db.Model):
    __tablename__ = 'user_settings'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False) # Para cuando haya login múltiple
    equipo_actual = db.Column(db.String(100), default="Freelance")
    
class ShortlistPlayer(db.Model):
    """Tabla para los jugadores en seguimiento (Preselección)"""
    __tablename__ = 'shortlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100))
    age = db.Column(db.Integer)
    minutes = db.Column(db.Integer)

class SquadPlannerPlayer(db.Model):
    """Tabla para los jugadores en la Pizarra Táctica"""
    __tablename__ = 'squad_planner'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    player_name = db.Column(db.String(100), nullable=False)
    x_pos = db.Column(db.Float, default=50.0)
    y_pos = db.Column(db.Float, default=50.0)
    is_filial = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False) # Para la papelera de descartes
    is_fichaje = db.Column(db.Boolean, default=True) # Diferenciar entre plantilla actual y fichajes