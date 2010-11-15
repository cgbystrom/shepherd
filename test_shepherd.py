import shepherd
import unittest
import json as pyjson
import logging
import sys
import time
import StringIO
import gzip
from gridfs import GridFS

rpm_name = 'test/buffer-1.19-2.el5.rf.x86_64.rpm'
rpm_name2 = 'test/devilspie-0.11-1.el5.rf.x86_64.rpm'
rpm_name3 = 'test/rpmforge-release-0.3.6-1.el5.rf.x86_64.rpm'

def json(response):
    return pyjson.loads(response.data)

def read_file(filename):
    f = open(filename, "r")
    content = f.read()
    f.close()
    return content

def decompress(data):
    data_stream = StringIO.StringIO(data)
    return gzip.GzipFile(fileobj=data_stream).read()

def get_testable_app():
    app = shepherd.app
    app.config['TESTING'] = True
    db = app.config['DATABASE']
    if '_test' not in db:
        app.config['DATABASE'] = db + '_test'
    return app

def setup_db():
    db = shepherd.connect_db()
    db_name = get_testable_app().config['DATABASE'] 
    db.drop_collection('fs.files')
    db.drop_collection('fs.chunks')
    db.drop_collection('channels')
   
    fs = GridFS(db)
    fs.put(read_file(rpm_name), _id=rpm_name, tags=['pinacolada', 'football'])
    fs.put(read_file(rpm_name3), _id=rpm_name3, tags=['music', 'football'])
    db.channels.insert({'_id': 'mysite-production', 'tags': ['pinacolada', 'football']}, safe=True)
    db.channels.insert({'_id': 'mysite-qa', 'tags': ['pinacolada', 'music']}, safe=True)
    db.channels.insert({'_id': 'mysite-development', 'tags': ['music']}, safe=True)

class PackageTest(unittest.TestCase):

    def setUp(self):
        self.app = get_testable_app().test_client()
        setup_db()

    def test_get_package(self):
        r = self.app.get("/packages/%s" % rpm_name)
        self.assertTrue(r.data == read_file(rpm_name))

    def test_package_tags(self):
        r = self.app.get("/packages/%s/tags" % rpm_name)
        self.assertTrue('pinacolada' in json(r)['tags'])
        self.assertTrue('football' in json(r)['tags'])
    
    def test_upload_package(self):
        r = self.app.post("/packages/%s" % rpm_name2, data=read_file(rpm_name2))
        self.assertEquals(r.status_code, 201)
        r = self.app.get("/packages/%s" % rpm_name2)
        self.assertTrue(r.data == read_file(rpm_name2))

    def test_upload_package_with_tags(self):
        r = self.app.post("/packages/%s?tag=summer&tag=meatballs" % rpm_name2, data=read_file(rpm_name2))
        self.assertEquals(r.status_code, 201)
        r = self.app.get("/packages/%s/tags" % rpm_name2)
        self.assertTrue('summer' in json(r)['tags'])
        self.assertTrue('meatballs' in json(r)['tags'])
        
    def test_remove_package(self):
        r = self.app.delete("packages/%s" % rpm_name)
        self.assertEquals(r.status_code, 204)
        r = self.app.get("/packages/%s" % rpm_name)
        self.assertEquals(r.status_code, 404)

    def test_change_tags(self):
        t = {'tags': ['banana', 'apple']}
        r = self.app.put("/packages/%s/tags" % rpm_name, data=json.dumps(t))
        self.assertEquals(r.status_code, 200)
        r = self.app.get("/packages/%s/tags" % rpm_name)
        self.assertTrue('banana' in json(r)['tags'])
        self.assertTrue('apple' in json(r)['tags'])

class ChannelTest(unittest.TestCase):

    def setUp(self):
        self.app = get_testable_app().test_client()
        setup_db()

    def test_list_channels(self):
        r = self.app.get("/channels")
        c = json(r)['channels']
        self.assertTrue('mysite-production' in c)
        self.assertTrue('mysite-qa' in c)
        self.assertTrue('mysite-development' in c)

    def test_list_channel_packages(self):
        r = self.app.get("/channels/mysite-qa")
        p = json(r)['packages']
        self.assertTrue(rpm_name in p)
        self.assertFalse(rpm_name2 in p)
        self.assertTrue(rpm_name3 in p)

    def test_create_channel(self):
        r = self.app.post("/channels/my-new-channel")
        self.assertEquals(r.status_code, 201)
        r = self.app.get("/channels/my-new-channel")
        self.assertEquals(len(json(r)['packages']), 0)
        r = self.app.get("/channels/my-new-channel/tags")
        self.assertEquals(len(json(r)['tags']), 0)

    def test_remove_channel(self):
        r = self.app.delete("/channels/mysite-production")
        self.assertEquals(r.status_code, 204)
        r = self.app.get("/channels/mysite-production")
        self.assertEquals(r.status_code, 404)

    def test_get_tags(self):
        r = self.app.get("/channels/mysite-production/tags")
        self.assertEquals(len(json(r)['tags']), 2)
        self.assertTrue('pinacolada' in json(r)['tags'])
        self.assertTrue('football' in json(r)['tags'])

    def test_change_tags(self):
        t = {'tags': ['banana', 'apple']}
        r = self.app.put("/channels/mysite-production/tags", data=pyjson.dumps(t))
        self.assertEquals(r.status_code, 200)
        r = self.app.get("/channels/mysite-production/tags")
        self.assertTrue('banana' in json(r)['tags'])
        self.assertTrue('apple' in json(r)['tags'])

    def test_repomd_xml(self):
        r = self.app.get("/channels/mysite-production/repodata/repomd.xml")
        self.assertEquals(r.status_code, 200)

    def test_filelists_xml(self):
        r = self.app.get("/channels/mysite-production/repodata/filelists.xml.gz")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('metadata/filelists' in decompress(r.data))

    def test_primary_xml(self):
        pass

    def test_other_xml(self):
        r = self.app.get("/channels/mysite-production/repodata/other.xml.gz")
        self.assertEquals(r.status_code, 200)
        self.assertTrue('metadata/other' in decompress(r.data))

if __name__ == '__main__':
    unittest.main()



