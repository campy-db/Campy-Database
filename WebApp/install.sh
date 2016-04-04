#!bin/bash

if ! find flask/bin/pip; then
    virtualenv flask
    flask/bin/pip install flask
    flask/bin/pip install flask-login
    flask/bin/pip install flask-mail
    flask/bin/pip install flask-wtf
    flask/bin/pip install flask-babel
    flask/bin/pip install guess_language
    flask/bin/pip install flipflop
    flask/bin/pip install coverage
    flask/bin/pip install request
    flask/bin/pip install session
    flask/bin/pip install g
    flask/bin/pip install redirect
    flask/bin/pip install url_for
    flask/bin/pip install abort
    flask/bin/pip install render_template
    flask/bin/pip install flash
    flask/bin/pip install _app_ctx_stack
    flask/bin/pip install pycountry
    flask/bin/pip install pandas
fi