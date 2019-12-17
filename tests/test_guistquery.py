import unittest, os, sqlite3
from gistquery.gistquery import GistQuery
from unittest import mock
from mock import Mock
from testfixtures import LogCapture

class TestGistQuery(unittest.TestCase):
    def setUp(self):
        self.test_db_file = '/tmp/test_gists.db'
        if os.path.exists(self.test_db_file):
            os.remove(self.test_db_file)
        self.connection = sqlite3.connect(self.test_db_file)
        self.gist_query = GistQuery(self.connection, True)
        self.gist_query.insert_data(self.connection, '5e7e3b1eb2a6af996da8cf810078ed91', '2019-12-17T12:08:09Z')
        self.gist_query.insert_data(self.connection, 'a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z')

    def test_convert_date_to_unix(self):
        unix_date = self.gist_query.convert_date_to_unix('2019-12-16T16:28:50Z')
        self.assertEqual(unix_date, 1576513730.0)

    def test_insert_delete_update_data(self):
        # Test insert
        self.gist_query.insert_data(self.connection, 'to_be_deleted', '2019-12-16T16:28:50Z')
        befor_delete_data = self.gist_query.select_all(self.connection)
        self.assertEqual(befor_delete_data, [('5e7e3b1eb2a6af996da8cf810078ed91', '2019-12-17T12:08:09Z'),
                                ('a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z'),
                                ('to_be_deleted', '2019-12-16T16:28:50Z')])

        # Test delete
        self.gist_query.delete_data(self.connection, 'to_be_deleted')
        after_delete_data = self.gist_query.select_all(self.connection)
        self.assertEqual(after_delete_data, [('5e7e3b1eb2a6af996da8cf810078ed91', '2019-12-17T12:08:09Z'),
                                             ('a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z')])

        # Test update
        self.gist_query.update_data(self.connection, '5e7e3b1eb2a6af996da8cf810078ed91', '0000-00-00T00:00:00Z')
        after_update_data = self.gist_query.select_all(self.connection)
        self.assertEqual(after_update_data, [('5e7e3b1eb2a6af996da8cf810078ed91', '0000-00-00T00:00:00Z'),
                                             ('a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z')])

    def test_select_data(self):
        data = self.gist_query.select_data(self.connection, '5e7e3b1eb2a6af996da8cf810078ed91')
        self.assertEqual(data, ('2019-12-17T12:08:09Z',))

    def test_select_all(self):
        data = self.gist_query.select_all(self.connection)
        self.assertEqual(data, [('5e7e3b1eb2a6af996da8cf810078ed91', '2019-12-17T12:08:09Z'),
                                ('a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z')])

    @mock.patch("gistquery.gistquery.GistQuery.delete_data")
    @mock.patch("gistquery.gistquery.GistQuery.select_all")
    def test_garbage_collection(self, select_all, delete_data):
        # Given
        select_all.return_value = [('95ebcb6fd65c2ea91c943940783ed0d4', '2019-12-16T18:19:45Z'), ('a385835626589eb8023ddd5791c933ed', '2019-12-16T16:28:50Z')]
        gists = [{'id': '95ebcb6fd65c2ea91c943940783ed0d4', 'updated_at': '2019-12-17T12:08:09Z'}]

        with mock.patch("sqlite3.connect") as mock_sqlite_connect:
            self.gist_query.garbage_collection(mock_sqlite_connect, gists)
            select_all.assert_called_once
            delete_data.assert_called_once_with(mock_sqlite_connect, 'a385835626589eb8023ddd5791c933ed')

    @mock.patch("requests.get")
    def test_get_gists_for_other_response_code(self, request):
        response = Mock()
        response.status_code = 321
        request.return_value = response
        with LogCapture() as log_capture:
            with self.assertRaises(SystemExit) as cm:
                self.gist_query.get_gist("gitlab_username")
            self.assertEqual(cm.exception.code, 255)
        log_capture.check(
            ('gistquery.gistquery',
             'ERROR',
             'Error: Github user / unexpected status code!'),
        )

    @mock.patch("requests.get")
    def test_get_gists_when_there_is_no_published_gists(self, request):
        response = Mock()
        response.status_code = 200
        response.content = '{}'
        request.return_value = response
        with LogCapture() as log_capture:
            with self.assertRaises(SystemExit) as cm:
                self.gist_query.get_gist("gitlab_username")
            self.assertEqual(cm.exception.code, 1)
        log_capture.check(
            ('gistquery.gistquery',
             'ERROR',
             'Github user gitlab_username has not published any gists.'),
        )

    @mock.patch("requests.get")
    def test_get_gists_for_200_response_code(self, request):
        response = Mock()
        response.status_code = 200
        response.content = '{"foo": "bar"}'
        request.return_value = response
        gists = self.gist_query.get_gist("gitlab_username")

        self.assertEqual(gists, {'foo': 'bar'})

    @mock.patch("requests.get")
    def test_get_gists_for_404_response_code(self, request):
        response = Mock()
        response.status_code = 404
        request.return_value = response
        with LogCapture() as log_capture:
            with self.assertRaises(SystemExit) as cm:
                self.gist_query.get_gist("gitlab_username")
            self.assertEqual(cm.exception.code, 1)
        log_capture.check(
            ('gistquery.gistquery',
             'ERROR',
             'Error: Github user gitlab_username not found.'),
        )

if __name__ == '__main__':
    unittest.main()
