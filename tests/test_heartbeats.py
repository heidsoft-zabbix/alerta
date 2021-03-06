
import unittest

try:
    import simplejson as json
except ImportError:
    import json

from uuid import uuid4
from alerta.app import app, db


class HeartbeatTestCase(unittest.TestCase):

    def setUp(self):

        app.config['TESTING'] = True
        app.config['AUTH_REQUIRED'] = False
        self.app = app.test_client()

        self.origin = str(uuid4()).upper()[:8]

        self.heartbeat = {
            'origin': self.origin,
            'tags': ['foo', 'bar', 'baz']
        }

        self.headers = {
            'Content-type': 'application/json'
        }

    def tearDown(self):

        db.destroy_db()

    def test_heartbeat(self):

        # create heartbeat
        response = self.app.post('/heartbeat', data=json.dumps(self.heartbeat), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data['heartbeat']['origin'], self.origin)
        self.assertListEqual(data['heartbeat']['tags'], self.heartbeat['tags'])

        heartbeat_id = data['id']

        # create duplicate heartbeat
        response = self.app.post('/heartbeat', data=json.dumps(self.heartbeat), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEquals(heartbeat_id, data['heartbeat']['id'])

        # get heartbeat
        response = self.app.get('/heartbeat/' + heartbeat_id)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEquals(heartbeat_id, data['heartbeat']['id'])

        # delete heartbeat
        response = self.app.delete('/heartbeat/' + heartbeat_id)
        self.assertEqual(response.status_code, 200)

    def test_heartbeat_not_found(self):

        response = self.app.get('/heartbeat/doesnotexist')
        self.assertEqual(response.status_code, 404)

    def test_get_heartbeats(self):

        # create heartbeat
        response = self.app.post('/heartbeat', data=json.dumps(self.heartbeat), headers=self.headers)
        self.assertEqual(response.status_code, 201)

        response = self.app.get('/heartbeats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertGreater(data['total'], 0, "total heartbeats > 0")
