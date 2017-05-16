"""
Module for python unit tests
"""
import json
import unittest

from app import app


class ComponentTestCase(unittest.TestCase):
    """
    The component test case
    """
    def setUp(self):
        """
        Initial setup for test class
        """
        self.app = app.test_client()
        self.headers = {
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWZyZXNoX3Rva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJbiIsImFjY2Vzc190b2tlbiI6ImFjY2Vzc190b2tlbiIsInNjb3BlIjpbInBzLnJlYWQiLCJwcy53cml0ZSJdLCJleHBpcmVzX2F0IjoiMTAwMTIzNDU2Nzg5IiwidXNlcm5hbWUiOiJqb2huZG9lIn0.8kPGKb_UMyd0WasQr7TJVwTVjhQ2nhZoM54SNDkFfdg"


    def tearDown(self):
        """
        Overriding default tearDown method
        :return:
        """
        pass


    def test_get_enrolment_code(self):

       response = self.app.get('/enrolment-codes/1111-1111-1111-1111', headers=self.headers)

       expected_response = [{"surveyId": "urn:uk.gov.ons:id:survey:BRES",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessRef": "11111111111",
                             "businessName": "AAA Ltd",
                             "IACStatus": "ACTIVE"}]

       self.assertEquals(expected_response, json.loads(response.data))


    def test_get_business_by_ref(self):

       response = self.app.get('/businesses/ref/11111111111', headers=self.headers)

       expected_response = [{"businessRef": "11111111111",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessName": "AAA Ltd",
                             "businessTradingName": "",
                             "businessEnterpriseName": "",
                             "businessContactName": "",
                             "addressLine1": "1 New St",
                             "addressLine2": "",
                             "addressLine3": "",
                             "city": "Newtown",
                             "postcode": "AA1 1AA",
                             "telephone": "+44 1111 111111",
                             "facsimile": "",
                             "employeeCount": 100,
                             "fulltimeCount": 100,
                             "legaStatus": "PRIVATE_LIMITED_COMPANY",
                             "sic2003": "1111",
                             "sic2007": "1111",
                             "turnover": 100000}]

       self.assertEquals(expected_response, json.loads(response.data))


    def test_get_business_by_id(self):

       response = self.app.get('/businesses/id/urn:ons.gov.uk:id:business:00000000001', headers=self.headers)

       expected_response = [{"businessRef": "11111111111",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessName": "AAA Ltd",
                             "businessTradingName": "",
                             "businessEnterpriseName": "",
                             "businessContactName": "",
                             "addressLine1": "1 New St",
                             "addressLine2": "",
                             "addressLine3": "",
                             "city": "Newtown",
                             "postcode": "AA1 1AA",
                             "telephone": "+44 1111 111111",
                             "facsimile": "",
                             "employeeCount": 100,
                             "fulltimeCount": 100,
                             "legaStatus": "PRIVATE_LIMITED_COMPANY",
                             "sic2003": "1111",
                             "sic2007": "1111",
                             "turnover": 100000}]

       self.assertEquals(expected_response, json.loads(response.data))


    def test_get_business_associations_by_business_id(self):

       response = self.app.get('/businesses/id/urn:ons.gov.uk:id:business:00000000001/business-associations', headers=self.headers)

       expected_response = [{"businessRef": "11111111111",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessName": "AAA Ltd",
                             "businessStatus": "ACTIVE",
                             "respondentEmailAddress": "a.adams@nowhere.com",
                             "respondentFirstName": "Adam",
                             "respondentLastName": "Adams",
                             "surveyId": "urn:uk.gov.ons:id:survey:BRES"}]

       self.assertEquals(expected_response, json.loads(response.data))


    def test_get_business_associations_by_respondent_id(self):
        response = self.app.get('/respondents/id/urn:uk.gov.ons:id:respondent:1111/business-associations', headers=self.headers)

        expected_response = [{"businessRef": "11111111111",
                              "businessId": "urn:ons.gov.uk:id:business:00000000001",
                              "businessName": "AAA Ltd",
                              "businessStatus": "ACTIVE",
                              "respondentEmailAddress": "a.adams@nowhere.com",
                              "respondentFirstName": "Adam",
                              "respondentLastName": "Adams",
                              "surveyId": "urn:uk.gov.ons:id:survey:BRES"}]

        self.assertEquals(expected_response, json.loads(response.data))


if __name__ == '__main__':
    unittest.main()
