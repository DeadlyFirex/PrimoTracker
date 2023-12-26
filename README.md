## PrimoTracker
Suite of tools to track your income over time of primo's.

### Description
Application built in pure Python, acts as an REST API.\
Made with Flask and several extensions and uses JWT to authenticate

### Installation
Looking in the flaskr folder, the init file is the file to run.\
It is however recommended to run the application through flask itself.\
You can run the app on Linux by executing
```
/usr/bin/python3 -m flask run -h 0.0.0.0 -p 8000
```
Docker support will soon be available.

### Roadmap
The roadmap is not yet available, but will be soon.

### Configuration
Configuration is accessible [here](config-example.json), rename the file to `config.json` on finish.\
Extended explanation will be provided soon.

### URL mapping
Will be provided soon.

### Database
Currently, the application only supports MySQL-type databases.\
Extended support for different database structures will be added later.

### Libraries
- [Flask](https://github.com/pallets/flask)
- [flask-jwt-extended](https://github.com/vimalloc/flask-jwt-extended)
- [flask-sqlalchemy](https://github.com/pallets/flask-sqlalchemy)
- [SQLAlchemy](https://github.com/sqlalchemy/sqlalchemy)
- [Flask-Limiter](https://github.com/alisaifee/flask-limiter)
- [flask-marshmallow](https://github.com/marshmallow-code/flask-marshmallow)
- [marshmallow-sqlalchemy](https://github.com/marshmallow-code/marshmallow-sqlalchemy)
- [marshmallow](https://github.com/marshmallow-code/marshmallow)
- [python_json_config](https://github.com/janehmueller/python-json-config)