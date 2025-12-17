from sqlalchemy import Column, Integer, String, Date, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime
import enum

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    cabinet_number = Column(Integer, nullable=False)
    qr_path = Column(String, nullable=False)

#Components field
class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    remarks = Column(String, nullable=True)

    image_path = Column(String, nullable=False)

    container_id = Column(
        Integer,
        ForeignKey("containers.id"),
        nullable=False
    )

    container = relationship("Container", backref="components")

    #Borrower 
class Borrower(Base):
    __tablename__ = "borrowers"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False, index=True)
    tp_id = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)

    transactions = relationship("BorrowTransaction", back_populates="borrower")

class BorrowStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"

class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    id = Column(Integer, primary_key=True, index=True)

    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=False)
    reason = Column(String, nullable=False)

    borrowed_at = Column(DateTime, default=datetime.utcnow)
    expected_return_date = Column(Date, nullable=False)

    status = Column(
        Enum(BorrowStatus),
        default=BorrowStatus.ACTIVE,
        nullable=False
    )

    borrower = relationship("Borrower", back_populates="transactions")
    items = relationship("BorrowItem", back_populates="transaction")

class BorrowItem(Base):
    __tablename__ = "borrow_items"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
        Integer,
        ForeignKey("borrow_transactions.id"),
        nullable=False
    )

    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)

    quantity_borrowed = Column(Integer, nullable=False)
    quantity_returned = Column(Integer, default=0)

    transaction = relationship("BorrowTransaction", back_populates="items")
    component = relationship("Component")


