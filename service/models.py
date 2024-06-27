"""
Models for YourResourceModel

All of the models are stored in this module
"""

import logging
import enum
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class PromotionType(enum.Enum):
    """Used to represent different types of promotions"""

    PERCENTAGE = 1
    ABSOLUTE = 2


class PromotionScope(enum.Enum):
    """Used to represent the scope a promotion is applicable to"""

    PRODUCT_ID = 1
    PRODUCT_CATEGORY = 2
    ENTIRE_STORE = 3


class Promotion(db.Model):
    """
    Class that represents a YourResourceModel
    """

    ##################################################
    # Table Schema
    ##################################################
    promotion_id = db.Column(db.Integer, primary_key=True)
    promotion_name = db.Column(db.String(63))
    promotion_description = db.Column(db.String(255))
    promotion_type = db.Column(db.Enum(PromotionType))
    promotion_scope = db.Column(db.Enum(PromotionScope))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    promotion_value = db.Column(db.Double)
    promotion_code = db.Column(db.String(63), nullable=True)
    created_by = db.Column(db.Uuid)
    modified_by = db.Column(db.Uuid, nullable=True)
    created_when = db.Column(db.DateTime)
    modified_when = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Promotion {self.promotion_name} promotion_id=[{self.promotion_id}], promotion_name=[{self.promotion_name}]>"

    def create(self):
        """
        Creates a YourResourceModel to the database
        """
        logger.info("Creating %s", self.promotion_name)
        self.promotion_id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a YourResourceModel to the database
        """
        logger.info("Saving %s", self.promotion_name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a YourResourceModel from the data store"""
        logger.info("Deleting %s", self.promotion_name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Promotion into a dictionary"""
        return {
            "promotion_id": self.promotion_id,
            "promotion_name": self.promotion_name,
            "promotion_description": self.promotion_description,
            "promotion_type": self.promotion_type.name,
            "promotion_scope": self.promotion_scope.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "promotion_value": self.promotion_value,
            "promotion_code": self.promotion_code,
            "created_by": self.created_by,
            "modified_by": self.modified_by,
            "created_when": self.created_when.isoformat() if self.created_when else None,
            "modified_when": self.modified_when.isoformat() if self.modified_when else None
        }

    def deserialize(self, data):
        """
        Deserializes a Promotion from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.promotion_name = data["promotion_name"]
            self.promotion_description = data.get("promotion_description")
            self.promotion_type = PromotionType[data["promotion_type"]]
            self.promotion_scope = PromotionScope[data["promotion_scope"]]
            self.start_date = datetime.fromisoformat(data["start_date"])
            self.end_date = datetime.fromisoformat(data["end_date"])
            self.promotion_value = data["promotion_value"]
            self.promotion_code = data.get("promotion_code")
            self.created_by = data["created_by"]
            self.modified_by = data.get("modified_by")
            self.created_when = datetime.fromisoformat(data["created_when"])
            self.modified_when = datetime.fromisoformat(data["modified_when"]) if data.get("modified_when") else None
        except (KeyError, TypeError, ValueError) as error:
            raise DataValidationError("Invalid promotion: " + str(error)) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the YourResourceModels in the database"""
        logger.info("Processing all YourResourceModels")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a YourResourceModel by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all YourResourceModels with the given name

        Args:
            name (string): the name of the YourResourceModels you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
