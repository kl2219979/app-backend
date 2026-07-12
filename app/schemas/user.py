"""Schemas Pydantic del recurso User.

Un schema define y valida la forma de los datos que entran y salen por la API.
No es una tabla, no consulta la base de datos y no sustituye al modelo SQLAlchemy
``app.models.user.User``. Es el contrato JSON de nuestros endpoints.
"""

# ``date`` representa solo una fecha (por ejemplo: 2000-01-15).
# ``datetime`` representa fecha y hora (por ejemplo, la fecha de creación).
from datetime import date, datetime

# BaseModel: clase base de Pydantic; valida automáticamente los datos recibidos.
# ConfigDict: configuración del schema de respuesta.
# Field: permite añadir reglas de validación a cada campo.
from pydantic import BaseModel, ConfigDict, Field


class userCreate(BaseModel):
    """Cuerpo que recibe POST /users para crear un usuario.

    Todos los campos son obligatorios porque no tienen ``= None`` ni un valor
    predeterminado. FastAPI devuelve un error 422 si falta alguno o no cumple
    sus reglas.
    """

    # ``str`` obliga a recibir texto. Field evita texto vacío y respeta el
    # tamaño de la columna ``users.nombres`` (VARCHAR(150)).
    nombres: str = Field(min_length=1, max_length=150)

    # Mismas reglas que ``nombres`` y que la columna ``users.apellidos``.
    apellidos: str = Field(min_length=1, max_length=150)

    # Pydantic convierte y valida el texto JSON "2000-01-15" como un date.
    # La tabla también guarda este valor como tipo DATE, sin hora.
    fecha_nacimiento: date

    # Límite igual al definido en ``users.genero`` (VARCHAR(30)).
    genero: str = Field(min_length=1, max_length=30)

    # Por ahora comprobamos que sea texto no vacío y que quepa en la columna.
    # Más adelante podemos usar EmailStr para validar formato de correo.
    correo: str = Field(min_length=1, max_length=255)

    # El usuario necesita al menos 3 caracteres. La BD admite hasta 50.
    usuario: str = Field(min_length=3, max_length=50)

    # Esta es la contraseña ORIGINAL enviada solo al crear el usuario.
    # Jamás se guarda directamente: el servicio la transformará en hash y
    # almacenará el resultado en ``users.contrasena_hash``.
    contrasena: str = Field(min_length=8, max_length=128)


class userUpdate(BaseModel):
    """Cuerpo para PUT/PATCH /users/{id}.

    ``str | None`` significa "texto o None". El ``default=None`` hace que el
    campo sea opcional: así se pueden actualizar solo los datos enviados.
    """

    nombres: str | None = Field(default=None, min_length=1, max_length=150)
    apellidos: str | None = Field(default=None, min_length=1, max_length=150)
    fecha_nacimiento: date | None = None
    genero: str | None = Field(default=None, min_length=1, max_length=30)
    correo: str | None = Field(default=None, min_length=1, max_length=255)
    usuario: str | None = Field(default=None, min_length=3, max_length=50)

    # Si se recibe una contraseña nueva, el servicio también deberá hashearla;
    # nunca se asigna directamente a ``contrasena_hash``.
    contrasena: str | None = Field(default=None, min_length=8, max_length=128)


class userResponse(BaseModel):
    """Forma segura de un usuario que la API devuelve al cliente.

    Aquí NO aparecen ``contrasena`` ni ``contrasena_hash``: una contraseña,
    incluso hasheada, es información sensible y no debe salir de la API.
    """

    # Permite crear este schema directamente desde un objeto SQLAlchemy User,
    # por ejemplo: UserResponse.model_validate(usuario_db).
    model_config = ConfigDict(from_attributes=True)

    # Datos que la tabla ya tiene y que sí es seguro devolver al frontend.
    id: int
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    genero: str
    correo: str
    usuario: str
    creado_en: datetime
