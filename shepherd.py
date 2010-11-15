from pymongo import Connection
from flask import Flask, jsonify, g, request, render_template
from gridfs import GridFS
from gridfs.errors import NoFile
from werkzeug.exceptions import NotFound
from functools import wraps
import json
import StringIO
import gzip
from pyrpm import rpmdefs
from pyrpm.rpm import RPM


DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)
app.config['DATABASE'] = 'shepherd'

def connect_db():
   c = Connection()
   return c[app.config['DATABASE']]

def get_package(name):
    try:
        return g.fs.get(name)
    except NoFile, e:
        raise NotFound('Package not found')

def compressed(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        d = f(*args, **kwargs)
        buffer = StringIO.StringIO()
        gf = gzip.GzipFile(fileobj=buffer, mode='wb')
        gf.write(d)
        gf.close()
        return buffer.getvalue()
    return decorated

@app.before_request
def before_request():
    g.db = connect_db()
    g.fs = GridFS(g.db)

@app.route("/packages/<name>")
def get_package_data(name):
    return get_package(name).read()

@app.route("/packages/<name>/tags")
def get_package_tags(name):
    return jsonify(tags=get_package(name).tags)

@app.route("/packages/<name>/tags", methods=['PUT'])
def update_package_tags(name):
    tags = json.loads(request.data)['tags']
    g.db.fs.files.update({'_id': name}, {'$set': {'tags': tags}})
    return 'Tags updated'

@app.route("/packages/<name>", methods=['POST'])
def upload_package(name):
    g.fs.put(request.data, _id=name, tags=request.args.getlist('tag'))
    return 'Package created', 201

@app.route("/packages/<name>", methods=['DELETE'])
def delete_package(name):
    g.fs.delete(name)
    return '', 204

@app.route("/channels")
def get_channels():
    channels = [c['_id'] for c in g.db.channels.find({}, {'_id': 1})]
    return jsonify(channels=channels)

@app.route("/channels/<name>")
def get_channel_packages(name):
    c = g.db.channels.find_one({'_id': name})
    if not c: return 'Channel not found', 404
    tags = c['tags']
    packages = [p['_id'] for p in g.db.fs.files.find({'tags': {'$in': tags}})]
    return jsonify(packages=packages)

@app.route("/channels/<name>", methods=['POST'])
def create_channel(name):
    g.db.channels.insert({'_id': name, 'tags': []})
    return 'Channel created', 201

@app.route("/channels/<name>", methods=['DELETE'])
def delete_channel(name):
    g.db.channels.remove({'_id': name})
    return '', 204

@app.route("/channels/<name>/tags")
def get_channel_tags(name):
    c = g.db.channels.find_one({'_id': name})
    if not c: return 'Channel not found', 404
    return jsonify(tags=c['tags'])

@app.route("/channels/<name>/tags", methods=['PUT'])
def update_channel_tags(name):
    tags = json.loads(request.data)['tags']
    g.db.channels.update({'_id': name}, {'$set': {'tags': tags}})
    return jsonify(tags=tags)

@app.route("/channels/<name>/repodata/repomd.xml")
def channel_repomd(name):
    files = [
        {
            'type': 'primary',
            'href': 'my-best-file',
            'checksum_type': 'sha',
            'checksum': 'abcabcd',
            'timestamp': 123123123,
            'open_checksum_type': 'sha',
            'open_checksum': 'abcabcd',

        }]
    return render_template('repomd.xml', files=files)

@app.route("/channels/<name>/repodata/filelists.xml.gz")
@compressed
def channel_filelists(name):
    return render_template('filelists.xml')

@app.route("/channels/<name>/repodata/primary.xml.gz")
#@compressed
def channel_primary(name):
    rpm = RPM(file('skype-2.1.0.81-fc.i586.rpm'))

    p = [
        {
            'name': rpm[rpmdefs.RPMTAG_NAME],
            'arch': rpm[rpmdefs.RPMTAG_ARCH],
            'version': rpm[rpmdefs.RPMTAG_VERSION],
            'release': rpm[rpmdefs.RPMTAG_RELEASE],
            'epoch': rpm[rpmdefs.RPMTAG_SERIAL],
            'summary': rpm[rpmdefs.RPMTAG_SUMMARY],
            'description': rpm[rpmdefs.RPMTAG_DESCRIPTION],
            'packager': rpm[rpmdefs.RPMTAG_PACKAGER],
            'url': rpm[rpmdefs.RPMTAG_URL],
            'time': {'file': -1, 'build': rpm[rpmdefs.RPMTAG_BUILDTIME][0]},
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
            'arch1': rpm[rpmdefs.RPMTAG_ARCH],
        }        
    ]
    r = app.make_response(render_template('primary.xml', packages=p))
    r.mimetype = 'text/xml'
    return r

@app.route("/channels/<name>/repodata/other.xml.gz")
@compressed
def channel_other(name):
    return render_template('other.xml')


if __name__ == "__main__":
    app.run()

