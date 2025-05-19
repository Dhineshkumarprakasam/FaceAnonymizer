from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2
from mediapipe import solutions
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'


app = Flask(__name__)

def face_blur(img):
    face_detector = solutions.face_detection
    with face_detector.FaceDetection(0.1,1) as detection:
        img_rgb = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        out = detection.process(img_rgb)

        if out.detections!=None:
            for dd in out.detections:
                location_data = dd.location_data
                bbox = location_data.relative_bounding_box

                x1 = int(bbox.xmin * img.shape[1])
                y1 = int(bbox.ymin * img.shape[0])-10
                w = int(bbox.width * img.shape[1])+10
                h = int(bbox.height * img.shape[0])+20

                #blur
                img[y1:y1+h,x1:x1+w,:] = cv2.blur(img[y1:y1+h,x1:x1+w,:],(50,50))

        return img


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.errorhandler(Exception)
def handle_exception(e):
    return redirect(url_for('index'))

@app.route("/")
def index():
    return render_template("index.html")


app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

@app.route("/uploaded", methods=["POST"])
def uploaded():
    try:
        if 'file' not in request.files:
            return redirect(url_for('index'))

        file = request.files['file']

        if file.filename == '':
            return redirect(url_for('index'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            img = cv2.imread(file_path)
            out = face_blur(img)
            out_path = os.path.join(app.config['UPLOAD_FOLDER'], "out_" + filename)
            cv2.imwrite(out_path, out)
            out_name="out_"+filename

            return render_template("finished.html", filename=filename,outfile=out_name)
        return redirect(url_for('index'))
    except:
        return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)