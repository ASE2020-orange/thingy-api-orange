import aiounittest
import unittest
import json
from aiohttp import ClientSession

class TestApi(aiounittest.AsyncTestCase):

    async def test_opentriviadb(self):
        tdb_request = 'https://opentdb.com/api.php?amount=10&type=multiple'
        async with ClientSession() as session:
            async with session.get(tdb_request) as resp:
                self.assertEqual(resp.status, 200)
                json_response = json.loads(await resp.text())
                self.assertIn('results',json_response.keys())
                for result in json_response["results"]:
                    self.assertIn('category',result.keys())
                    self.assertIn('type',result.keys())
                    self.assertIn('difficulty',result.keys())
                    self.assertIn('question',result.keys())
                    self.assertIn('correct_answer',result.keys())
                    self.assertIn('incorrect_answers',result.keys())
                    self.assertEqual(len(result['incorrect_answers']),3)


if __name__ == "__main__":
    unittest.main()