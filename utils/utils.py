import config

def allowed_file(filename):
    if '.' not in filename:
        return False
    if(filename.split('.')[1] in config.ALLOWED_EXTENSIONS):
        return True
    return False

def get_extension(filename):
    return filename.split('.')[1]