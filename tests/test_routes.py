"""
TestYourResourceModel API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from uuid import UUID
from wsgi import app
from service.common import status
from service.common.datetime_utils import datetime_from_str, datetime_to_str
from service.models import db, Promotion, PromotionScope
from tests.factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_update_with_valid_promotion(self):
        """It should update the model with a valid promotion when a valid object is supplied and return the updated json"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()

        new_promotion_data = {
            "promotion_name": "New Promotion Name",
            "start_date": "2025-03-03",
            "promotion_scope": "ENTIRE_STORE",
        }
        resp = self.client.put(
            f"/promotions/{existing_promotion.promotion_id}",
            json=new_promotion_data,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        db.session.expire_all()
        updated_promotion = Promotion.find(existing_promotion.promotion_id)
        assert updated_promotion.promotion_name == "New Promotion Name"
        assert updated_promotion.start_date == datetime_from_str(
            new_promotion_data["start_date"]
        )
        assert updated_promotion.promotion_scope == PromotionScope.ENTIRE_STORE
        response_json = resp.get_json()
        self.assertEqual(response_json["promotion_id"], updated_promotion.promotion_id)
        self.assertEqual(
            response_json["promotion_name"], new_promotion_data["promotion_name"]
        )
        self.assertEqual(
            response_json["promotion_value"], existing_promotion.promotion_value
        )
        self.assertEqual(
            datetime_from_str(response_json["start_date"]),
            datetime_from_str(new_promotion_data["start_date"]),
        )
        self.assertEqual(
            response_json["promotion_scope"], new_promotion_data["promotion_scope"]
        )

    def test_update_with_invalid_promotion_id(self):
        """It should not update any model and return a 404 not found when an invalid_promotion_id is supplied"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()

        new_promotion_data = {
            "promotion_name": "New Promotion Name",
            "start_date": "2025-03-03",
            "promotion_scope": "ENTIRE_STORE",
        }
        resp = self.client.put(
            f"/promotions/{184182325}", json=new_promotion_data
        )
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
        db.session.expire_all()
        updated_promotion = Promotion.find(existing_promotion.promotion_id)
        assert updated_promotion.promotion_name != "New Promotion Name"

    def test_update_with_invalid_data(self):
        """It should not update model and return a 400 not found when invalid data is supplied"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()

        new_promotion_data = {
            "promotion_name": "Newest Promotion Name",
            "start_date": "2023/04/21",
            "promotion_scope": "ENTIRE_STORE",
        }
        resp = self.client.put(
            f"/promotions/{existing_promotion.promotion_id}",
            json=new_promotion_data,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        db.session.expire_all()
        updated_promotion = Promotion.find(existing_promotion.promotion_id)
        self.assertNotEqual(updated_promotion.promotion_name, new_promotion_data["promotion_name"])

    def test_update_with_unknown_exception(self):
        """It should not update model and return a 400 not found when invalid data is supplied"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()

        new_promotion_data = {
            "promotion_name": "Newest Promotion Name",
            "start_date": "2023-04-21",
            "promotion_scope": "ENTIRE_STORE",
        }
        original_update = existing_promotion.update
        try:
            # Create mock function to raise connection error on any update
            def mock_update_with_exception():
                raise ConnectionError
            existing_promotion.update = mock_update_with_exception
            resp = self.client.put(
                f"/promotions/{existing_promotion.promotion_id}",
                json=new_promotion_data,
            )
            self.assertEqual(resp.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
            db.session.expire_all()
            saved_promotion = Promotion.find(existing_promotion.promotion_id)
            self.assertNotEqual(saved_promotion.promotion_name, new_promotion_data["promotion_name"])
        finally:
            existing_promotion.update = original_update

    def test_get_promotion(self):
        """It should Get a single Promotion"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()
        response = self.client.get(f"/promotions/{existing_promotion.promotion_id}",)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["promotion_name"], existing_promotion.promotion_name)
        self.assertEqual(data["promotion_description"], existing_promotion.promotion_description)
        self.assertEqual(data["promotion_type"], existing_promotion.promotion_type.name)
        self.assertEqual(data["promotion_scope"], existing_promotion.promotion_scope.name)
        self.assertEqual(data["start_date"], datetime_to_str(existing_promotion.start_date))
        self.assertEqual(data["end_date"], datetime_to_str(existing_promotion.end_date))
        self.assertEqual(data["promotion_value"], existing_promotion.promotion_value)
        self.assertEqual(data["promotion_code"], existing_promotion.promotion_code)
        self.assertEqual(UUID(data["created_by"]), existing_promotion.created_by)
        self.assertEqual(UUID(data["modified_by"]), existing_promotion.modified_by)
        self.assertEqual(data["created_when"], datetime_to_str(existing_promotion.created_when))
        self.assertEqual(data["modified_when"], existing_promotion.modified_when)

    def test_get_promotion_not_found(self):
        """It should not Get a Promotion thats not found"""
        existing_promotion = PromotionFactory()
        existing_promotion.create()
        response = self.client.get("/promotions/1234567",)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
