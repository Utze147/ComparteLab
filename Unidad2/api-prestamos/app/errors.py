class AppError(Exception):
    def __init__(self, status_code: int, codigo: str, mensaje: str, detalles=None):
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles