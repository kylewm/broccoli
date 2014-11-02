#!/usr/bin/env python
import sys
for submodule in ('mf2py', 'mf2util'):
    sys.path.append(submodule)

from broccoli import create_app
from broccoli.extensions import db

app = create_app()

with app.test_request_context():
    db.create_all()

app.run(debug=True)
