"""
Module for python unit tests
"""
import json
import unittest

from application.app import app


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
            "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyZWZyZXNoX3Rva2VuIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJbiIsImFjY2Vzc190b2tlbiI6ImFjY2Vzc190b2tlbiIsInNjb3BlIjpbInBzLnJlYWQiLCJwcy53cml0ZSJdLCJleHBpcmVzX2F0IjoiMTAwMTIzNDU2Nzg5IiwidXNlcm5hbWUiOiJqb2huZG9lIn0.8kPGKb_UMyd0WasQr7TJVwTVjhQ2nhZoM54SNDkFfdg"}

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

    def test_get_enrolment_code_not_found(self):

        response = self.app.get('/enrolment-codes/XXXX-XXXX-XXXX-XXXX', headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_set_enrolment_code_as_redeemed(self):

        response = self.app.put('/enrolment-codes/"1111-1111-1111-1111"', headers=self.headers)

        self.assertTrue(response.status_code, 200)

    def test_set_enrolment_code_as_redeemed_not_found(self):

        response = self.app.put('/enrolment-codes/"XXXX-XXXX-XXXX-XXXX"', headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_get_business_by_ref(self):

       response = self.app.get('/businesses/ref/11111111111', headers=self.headers)

       expected_response = [{"businessRef": "11111111111",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessName": "AAA Ltd",
                             "businessTradingName": None,
                             "businessEnterpriseName": None,
                             "businessContactName": None,
                             "addressLine1": "1 New St",
                             "addressLine2": None,
                             "addressLine3": None,
                             "city": "Newtown",
                             "postcode": "AA1 1AA",
                             "telephone": "+44 1111 111111",
                             "facsimile": None,
                             "employeeCount": 100,
                             "fulltimeCount": 100,
                             "legaStatus": "PRIVATE_LIMITED_COMPANY",
                             "sic2003": "1111",
                             "sic2007": "1111",
                             "turnover": 100000}]

       self.assertEquals(expected_response, json.loads(response.data))

    def test_get_business_by_ref_not_found(self):

        response = self.app.get('/businesses/ref/XXXXXXXXXXX', headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_get_business_by_id(self):

       response = self.app.get('/businesses/id/urn:ons.gov.uk:id:business:00000000001', headers=self.headers)

       expected_response = [{"businessRef": "11111111111",
                             "businessId": "urn:ons.gov.uk:id:business:00000000001",
                             "businessName": "AAA Ltd",
                             "businessTradingName": None,
                             "businessEnterpriseName": None,
                             "businessContactName": None,
                             "addressLine1": "1 New St",
                             "addressLine2": None,
                             "addressLine3": None,
                             "city": "Newtown",
                             "postcode": "AA1 1AA",
                             "telephone": "+44 1111 111111",
                             "facsimile": None,
                             "employeeCount": 100,
                             "fulltimeCount": 100,
                             "legaStatus": "PRIVATE_LIMITED_COMPANY",
                             "sic2003": "1111",
                             "sic2007": "1111",
                             "turnover": 100000}]

       self.assertEquals(expected_response, json.loads(response.data))

    def test_get_business_by_id_not_found(self):

       response = self.app.get('/businesses/id/urn:ons.gov.uk:id:business:XXXXXXXXXXX', headers=self.headers)

       self.assertTrue(response.status_code, 404)

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

    def test_get_business_associations_by_business_id_not_found(self):

        response = self.app.get('/businesses/id/urn:ons.gov.uk:id:business:XXXXXXXXXXX/business-associations', headers=self.headers)

        self.assertTrue(response.status_code, 404)

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

    def test_get_business_associations_by_respondent_id_not_found(self):

        response = self.app.get('/respondents/id/urn:uk.gov.ons:id:respondent:XXXX/business-associations', headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_create_businesses(self):

        new_business = {"businessRef": "00000000001",
                        "name": "XXX Ltd",
                        "tradingName": "XXX Ltd",
                        "enterpriseName": "XXX Ltd",
                        "contactName": "Mr X",
                        "addressLine1": "1 Exe St",
                        "addressLine2": "Exwood",
                        "addressLine3": "Exetown",
                        "city": "Exeville",
                        "postcode": "XX1 1XX",
                        "telephone": "01234 567890",
                        "employeeCount": "100",
                        "facsimile": "01234 567891",
                        "fulltimeCount": "90",
                        "legalStatus": "PRIVATE_LIMITED_COMPANY",
                        "sic2003": "12345",
                        "sic2007": "12345",
                        "turnover": "1000000"}

        response = self.app.post('/businesses/', data=new_business, headers=self.headers)

        self.assertTrue(response.status_code, 200)

    def test_create_businesses_invalid_legal_status(self):

        new_business = {"businessRef": "00000000001",
                        "name": "XXX Ltd",
                        "tradingName": "XXX Ltd",
                        "enterpriseName": "XXX Ltd",
                        "contactName": "Mr X",
                        "addressLine1": "1 Exe St",
                        "addressLine2": "Exwood",
                        "addressLine3": "Exetown",
                        "city": "Exeville",
                        "postcode": "XX1 1XX",
                        "telephone": "01234 567890",
                        "employeeCount": "100",
                        "facsimile": "01234 567891",
                        "fulltimeCount": "90",
                        "legalStatus": "XXX",
                        "sic2003": "12345",
                        "sic2007": "12345",
                        "turnover": "1000000"}

        response = self.app.post('/businesses/', data=new_business, headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_create_respondent(self):

        new_respondent = {"status":"CREATED",
                          "emailAddress":"testuser1@xxx.com",
                          "firstName":"Test",
                          "lastName":"User",
                          "telephone": "01234 567890",
                          "enrolmentCode": "1111-1111-1111-1111"}

        response = self.app.post('/respondents/', data=new_respondent, headers=self.headers)

        self.assertTrue(response.status_code, 200)

    def test_create_respondent_invalid_status(self):

        new_respondent = {"status":"XXX",
                          "emailAddress":"testuser1@xxx.com",
                          "firstName":"Test",
                          "lastName":"User",
                          "telephone": "01234 567890",
                          "enrolmentCode": "1111-1111-1111-1111"}

        response = self.app.post('/respondents/', data=new_respondent, headers=self.headers)

        self.assertTrue(response.status_code, 404)

    def test_set_verification_token_as_redeemed(self):

        response = self.app.put('/verification-tokens/a1aaaa11-1a1a-1aa1-aa1a-1aa1aa111a11', headers=self.headers)

        self.assertTrue(response.status_code, 200)


    def test_set_verification_token_as_redeemed_not_found(self):

        response = self.app.put('/verification-tokens/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx', headers=self.headers)

        self.assertTrue(response.status_code, 404)