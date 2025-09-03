# from sqlalchemy import Column, String, ForeignKey
# from sqlalchemy.orm import relationship
# from database.session import Base


# class StoreLocation(Base):
#     __tablename__ = "store_location"
    
#     store_id = Column(String(255), ForeignKey("stores.store_id"), primary_key=True)
#     # TODO: Add PostGIS support for geometry column
#     # location = Column(Geometry('POINT', srid=4326))
#     address = Column(String(500), nullable=False)
#     address_detail = Column(String(255))
#     postal_code = Column(String(10))
    
#     # Relationships
#     store = relationship("Store", back_populates="location")