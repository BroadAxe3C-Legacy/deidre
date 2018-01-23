# -*- coding: utf-8 -*-

import unittest


class ApiTests(unittest.TestCase):
    pass
    # @Mocker()
    # def test_timeout_exception(self, m):
    #     # given
    #     m._adapter = Co2ApiTimeoutAdapter(m._adapter)
    #     m.register_uri(ANY, ANY, text=self.hanging_callback)
    #     client = ApiClient(adapter=Co2ApiTimeoutAdapter(), timeout=10)
    #
    #     # when/then
    #     with self.assertRaises(ApiException):
    #         client.retrieve('GET', f'{BASE_URI}/foobar')
