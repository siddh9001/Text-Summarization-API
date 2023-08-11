import unittest
from server import app

class TestApiClass(unittest.TestCase):

    # check if response is 200
    def test_index(self):
        data = {
        'text_to_summarize' : "this is test data"
        }
        tester = app.test_client(self)
        response = tester.post("/summarize", json=data, content_type='application/json')
        statuscode = response.status_code
        self.assertEqual(statuscode, 200)

    #check if content return is application/json
    def test_index_content(self):
        data = {
        'text_to_summarize' : "this is test data"
        }
        tester = app.test_client(self)
        response = tester.post("/summarize", json=data, content_type='application/json')
        self.assertEqual(response.content_type, "application/json")

    #check for data returned
    def test_index_data(self):
        data = {
        'text_to_summarize' : "this is test data"
        }
        tester = app.test_client(self)
        response = tester.post("/summarize", json=data, content_type='application/json')
        self.assertTrue(b'success' and b'message' in response.data)

    # check for empty data input
    def test_index_for_bad_request(self):
        data = {
        'text_to_summarize' : ""
        }
        tester = app.test_client(self)
        response = tester.post("/summarize", json=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "input cannot be empty")

    # test for token limit exceeded
    def test_for_token_limit(self):
        data={
            "text_to_summarize" : "Each time our eyes hit the newspaper, the headlines provoke outrage with news of gang rapes, violence, molestations and harassment of women. The species which consists half of our population is still subject to violence and discrimination. Women continue to live in fear and under the domination of men in present-day India.When we talk of freedom and independence of the country from the outside forces we are proud of what we have achieved today but women who were equal contributors in the freedom struggle continue to remain shackled by chains of patriarchal mindset. Women are often denied their freedom of choice. Nobody asks a girl what her dreams are or what role she aspires to play in life. Rather her status is confined to the conventional roles that the society has assigned to her. To make this country a free and enjoyable place for women, we first need to empower the police and government in order to provide a safe environment to women so that they can travel wherever and whenever they want. We also need to improve our law and order situation and get serious about the investigation, prosecution and trials. More investment needs to be made in promoting equality and improving ways for the women to take a stand for themselves."
        }
        tester = app.test_client(self)
        response = tester.post("/summarize", json=data, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "token limit exceeded(less than 200 words)")

    


if __name__ == '__main__':
    unittest.main()