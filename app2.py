from flask import Flask, render_template, Response, request
from json import dumps
from datetime import datetime
import udp
url = '172.20.10.3'

from camera_pi import Camera
app = Flask(__name__)
cons = udp.consumer()

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/_get_time')
def get_time():
        notdone = True
        lastmsg = ""
        while(notdone):
            msg = cons.receive()
            if msg == None:
                notdone = False
            else:
                lastmsg = msg
        if len(lastmsg) == 2:
            bounced = str(lastmsg[1])
        else:
            bounced = " "
	rv = [{"time":str(datetime.now()),
               "bbb":bounced}]
	Response.content_type = 'application/json'
	return dumps(rv)


if __name__ == '__main__':
    app.run(host=url, debug=True, threaded=True)