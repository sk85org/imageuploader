from flask import (
    Flask,
    flash,
    request,
    redirect,
    url_for,
    send_file,
    send_from_directory,
    render_template,
    make_response,
    jsonify,
)
import datetime, secrets
import mimetypes
import os
import calendar
import pymongo
from bson.objectid import ObjectId

UPLOAD_DIST = "/img"

app = Flask(__name__)

client = pymongo.MongoClient("mongodb://root:pass@db", 27017)
db = client["testdb"]
collection = db["image_collection"]


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/post", methods=["POST"])
def upload_file():
    if request.method == "POST":
        if (
            "uploadFile" not in request.files
            or request.files.getlist("uploadFile")[0].filename == ""
        ):
            return make_response(jsonify({"result": "uploadFile is required."}))

        files = request.files.getlist("uploadFile")
        print(files)

        files_info = []
        for file in files:
            # print(file)
            # print(file.mimetype)
            extension = mimetypes.guess_extension(file.mimetype, strict=True)
            # print(extension)
            time = datetime.datetime.now()
            filename = (
                time.strftime("%Y%m%d-%H-%M-%S-")
                + secrets.token_urlsafe(15)
                + extension
            )
            # print(path)
            post = {
                "filename": filename,
                "date": time,
            }

            file.save(imgpath(filename))
            result = collection.insert_one(post)

            # print(result.inserted_id)
            files_info.append(post)
        # print(names)
        return render_template("upload_result.html", files_info=files_info)


@app.route("/list")
def list():
    this_year = datetime.datetime.now().year
    return render_template("list.html", this_year=this_year)


@app.route("/list/id/<id>", methods=["GET"])
def list2(id):
    if id:
        result = collection.find_one({"_id": ObjectId(id)})
        return render_template("imgshow.html", result=result)
    else:
        this_year = datetime.datetime.now().year
        print(this_year)
        return render_template("list.html", this_year=this_year)


@app.route("/list/allposts", methods=["GET"])
def allposts():
    allposts = collection.find()
    result = []
    for doc in allposts:
        result.append(doc)
    return render_template("allposts.html", result=result)


@app.route(
    "/list/date/<int:year>", defaults={"month": None, "day": None}, methods=["GET"]
)
@app.route("/list/date/<int:year>/<int:month>", defaults={"day": None}, methods=["GET"])
@app.route("/list/date/<int:year>/<int:month>/<int:day>", methods=["GET"])
def list_by_date(year, month, day):
    if year and month and day:
        result = search_by_data(year, month, day)
        return render_template(
            "list_by_day.html", result=result, year=year, month=month, day=day
        )

    elif year and month and (day is None):

        result = search_by_data(year, month, day)
        return render_template(
            "list_by_month.html", result=result, year=year, month=month
        )

    elif year and (month is None and day is None):
        result = search_by_data(year, month, day)
        return render_template("list_by_year.html", result=result, year=year)


@app.route("/del/<id>")
def delete(id):
    if id:
        result = collection.find_one({"_id": ObjectId(id)})
        filename = result["filename"]
        os.remove(imgpath(filename))
        result = collection.remove({"_id": ObjectId(id)})
        return render_template("delete.html", id=id)


@app.route("/imgshow/<filename>")
def send_file(filename):
    return send_from_directory(UPLOAD_DIST, filename)


@app.route("/upload", methods=["GET"])
def upload():
    return render_template("upload.html")


@app.route("/search", methods=["GET"])
def search():
    return render_template("search.html")


@app.route("/search_file", methods=["GET"])
def search_file():
    query = request.args.get("query")
    result = collection.find(filter={"filename": {"$regex": query, "$options": "iu"}})
    array = []
    for doc in result:
        doc["_id"] = str(doc["_id"])
        array.append(doc)
    return make_response(jsonify({"result": array}))


def imgpath(filename):
    return os.path.join(UPLOAD_DIST, filename)


def search_by_data(year, month, day):

    start_hour, end_hour = 0, 23
    start_min, end_min = 0, 59
    start_sec, end_sec = 0, 59
    start_microsec, end_microsec = 0, 999999

    if year and (month is None and day is None):
        start_year = end_year = year
        start_month, end_month = 1, 12
        start_day, end_day = 1, calendar.monthrange(year, end_month)[1]

    elif year and month and (day is None):
        start_year = end_year = year
        start_month = end_month = month
        start_day, end_day = 1, calendar.monthrange(year, end_month)[1]

    elif year and month and day:
        start_year = end_year = year
        start_month = end_month = month
        start_day = day
        end_day = day

    result = collection.find(
        filter={
            "date": {
                "$gte": datetime.datetime(
                    start_year,
                    start_month,
                    start_day,
                    start_hour,
                    start_min,
                    start_sec,
                    start_microsec,
                ),
                "$lt": datetime.datetime(
                    end_year,
                    end_month,
                    end_day,
                    end_hour,
                    end_min,
                    end_sec,
                    end_microsec,
                ),
            }
        }
    )
    array = []
    for doc in result:
        array.append(doc)
    return array


if __name__ == "__main__":
    app.run()

