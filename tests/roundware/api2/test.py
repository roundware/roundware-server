# from django.core.urlresolvers import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase


# class API2Tests(APITestCase):
#     fixtures = ['default_auth', 'test_project']

#     def test_api2_in_order(self):
#         self.users_post()
#         self.sessions_post()
#         self.projects_get()
#         self.projects_tags_get()
#         self.projects_assets_get()

#         # some endpoints cannot be tested currently
#         # self.streams_post()
#         # self.streams_patch()
#         # self.streams_heartbeat_post()
#         # self.streams_next_post()
#         # self.streams_current_get()

#         self.ensure_token_required()

#     def users_post(self):
#         url = reverse('user-list')
#         data = {"device_id": "12891038109281",
#                 "client_type": "phone",
#                 "client_system": "iOS"}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # check that a username was generated and token returned
#         self.assertIsNotNone(response.data["username"])
#         self.assertIsNotNone(response.data["token"])
#         # set the token for later requests
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data["token"])

#     def sessions_post(self):
#         url = reverse('session-list')
#         data = {"timezone": "-0500",
#                 "project_id": 1,
#                 "client_system": "iOS"}
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # language wasn't provided, so should be set default to "en"
#         self.assertEqual(response.data["language"], "en")
#         # check returned data matches data provided
#         self.assertEqual(response.data["timezone"], data["timezone"])
#         self.assertEqual(response.data["client_system"], data["client_system"])
#         self.assertEqual(response.data["project_id"], data["project_id"])
#         self.assertIsNotNone(response.data["session_id"])
#         # save session_id for later requests
#         self.session_id = response.data["session_id"]

#     def projects_get(self):
#         url = "%s?session_id=%s" % (reverse('project-detail', args=[1]), self.session_id)
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         # ensure _loc fields are transformed
#         self.assertIn("out_of_range_message", response.data)
#         self.assertNotIn("out_of_range_message_loc", response.data)
#         self.assertEqual(1, response.data["project_id"])

#     def projects_tags_get(self):
#         url = "%s?session_id=%s" % (reverse('project-tags', args=[1]), self.session_id)
#         data = {}
#         response = self.client.get(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 2)
#         self.assertEqual(len(response.data["speak"]), 3)
#         self.assertEqual(len(response.data["listen"]), 3)

#     def projects_assets_get(self):
#         url = reverse('project-assets', args=[1])
#         data = {}
#         response = self.client.get(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data), 1)
#         self.assertEqual(response.data[0]["project"], 1)

#     def ensure_token_required(self):
#         self.client.credentials(HTTP_AUTHORIZATION='')
#         self.assertRaises(AssertionError, self.sessions_post)
#         self.assertRaises(AssertionError, self.projects_get)
#         self.assertRaises(AssertionError, self.projects_tags_get)
#         self.assertRaises(AssertionError, self.projects_assets_get)
