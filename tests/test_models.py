"""
Test cases for Pet Model
"""

import os
import logging
from datetime import datetime
from unittest import TestCase
from wsgi import app
from service.models import Promotion, DataValidationError, db
from .factories import PromotionFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)

######################################################################
#  YourResourceModel   M O D E L   T E S T   C A S E S
######################################################################


# pylint: disable=too-many-public-methods
class TestPromotions(TestCase):
    """Test Cases for YourResourceModel Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Promotion).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    # Todo: Add your test cases here...
    def test_create_promotion(self):
        """It should create a Promotion"""
        test_promotion = PromotionFactory()

        test_promotion.create()
        assert test_promotion.promotion_name == "some_promotion"
        assert test_promotion.created_by == test_promotion.created_by
        found = Promotion.all()
        self.assertEqual(len(found), 1)
        data = Promotion.find(test_promotion.promotion_id)
        self.assertEqual(data.promotion_name, test_promotion.promotion_name)
        self.assertEqual(data.start_date, datetime(2025, 1, 1, 0, 0))

    def test_create_invalid_promotion(self):
        """It should throw a DataValidationError"""
        test_promotion = PromotionFactory()
        test_promotion.start_date = "abcadw"
        self.assertRaises(DataValidationError, test_promotion.create)
