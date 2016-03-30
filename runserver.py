#!/usr/bin/env python

from slm_histviz import app

# start the flask loop
if __name__ == "__main__":
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.run(debug=True, host='0.0.0.0', port=5582)
