import re

def validate(password):
    if " " in password:
        return False, "La contraseña no debe contener espacios en blanco"
    
    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"
    
    if len(password) > 15:
        return False, "La contraseña debe tener un maxímo de 15 caracteres"
    
    if not re.search("[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"
    
    if not re.search("[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"
    
    if not re.search("[0-9]", password):
        return False, "La contraseña debe contener al menos un dígito"
    
    
    if not re.search("[!@#$%^&*()-+]", password):
        return False, "La contraseña debe contener al menos un carácter especial"
    
    return True, 'Contraseña válida'