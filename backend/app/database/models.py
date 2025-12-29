from sqlalchemy import (
    Column, Boolean, Integer, String, Date, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from .db import Base
from datetime import datetime
import enum


# --------------------------------------------------
# USER (PIC)
# --------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    borrowed_transactions = relationship(
        "BorrowTransaction",
        foreign_keys="BorrowTransaction.borrowed_by_id",
        back_populates="borrowed_by"
    )

    return_events = relationship(
        "ReturnEvent",
        foreign_keys="ReturnEvent.returned_by_id",
        back_populates="returned_by"
    )


# --------------------------------------------------
# CONTAINER
# --------------------------------------------------
class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    cabinet_number = Column(Integer, nullable=False)
    shelf_number = Column(Integer, nullable=True)  # 1-5, NULL if not assigned to shelf
    qr_path = Column(String, nullable=False)

    components = relationship(
        "Component",
        back_populates="container",
        cascade="all, delete-orphan"
    )


# --------------------------------------------------
# COMPONENT
# --------------------------------------------------
class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)

    quantity = Column(Integer, nullable=False)
    remarks = Column(String(500))
    image_path = Column(String, nullable=False)

    # Storage location fields
    storage_type = Column(String(20), default="CABINET", nullable=False)  # CABINET | DRAWER | STORAGE_BOX
    
    # For CABINET storage
    cabinet_number = Column(Integer, nullable=True)
    shelf_number = Column(Integer, nullable=True)  # 0-5, 0 = no shelf
    container_id = Column(Integer, ForeignKey("containers.id"), nullable=True)  # Made nullable
    
    # For DRAWER storage
    drawer_index = Column(Integer, nullable=True)
    
    # For STORAGE_BOX storage
    storage_box_index = Column(Integer, nullable=True)
    
    # Box/Partition within container/drawer (existing location fields)
    location_type = Column(String(20), default="NONE", nullable=False)  # NONE | BOX | PARTITION
    location_index = Column(Integer)

    is_deleted = Column(Boolean, default=False)
    deleted_reason = Column(String)
    deleted_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow,nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    container = relationship("Container", back_populates="components")

    borrow_items = relationship(
        "BorrowItem",
        back_populates="component",
        cascade="all, delete-orphan"
    )


# --------------------------------------------------
# BORROWER
# --------------------------------------------------
class Borrower(Base):
    __tablename__ = "borrowers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    tp_id = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, index=True)

    transactions = relationship(
        "BorrowTransaction",
        back_populates="borrower"
    )


# --------------------------------------------------
# BORROW TRANSACTION
# --------------------------------------------------
class BorrowStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"


class BorrowTransaction(Base):
    __tablename__ = "borrow_transactions"

    id = Column(Integer, primary_key=True, index=True)

    borrower_id = Column(Integer, ForeignKey("borrowers.id"), nullable=False)
    borrowed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    reason = Column(String, nullable=False)
    borrowed_at = Column(DateTime, default=datetime.utcnow)
    expected_return_date = Column(Date, nullable=False)

    status = Column(Enum(BorrowStatus), default=BorrowStatus.ACTIVE, nullable=False)
    overdue_email_sent = Column(Boolean, default=False, nullable=False)

    borrower = relationship("Borrower", back_populates="transactions")

    borrowed_by = relationship(
        "User",
        foreign_keys=[borrowed_by_id],
        back_populates="borrowed_transactions"
    )

    items = relationship(
        "BorrowItem",
        back_populates="transaction",
        cascade="all, delete-orphan"
    )


# --------------------------------------------------
# BORROW ITEM
# --------------------------------------------------
class BorrowItem(Base):
    __tablename__ = "borrow_items"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(Integer, ForeignKey("borrow_transactions.id"), nullable=False)
    component_id = Column(Integer, ForeignKey("components.id"), nullable=False)

    quantity_borrowed = Column(Integer, nullable=False)
    quantity_returned = Column(Integer, default=0)

    component = relationship("Component", back_populates="borrow_items")
    transaction = relationship("BorrowTransaction", back_populates="items")

    return_events = relationship(
        "ReturnEvent",
        back_populates="borrow_item",
        cascade="all, delete-orphan"
    )


# --------------------------------------------------
# RETURN EVENT (SINGLE SOURCE OF TRUTH)
# --------------------------------------------------
class ReturnEvent(Base):
    __tablename__ = "return_events"

    id = Column(Integer, primary_key=True, index=True)

    borrow_item_id = Column(Integer, ForeignKey("borrow_items.id"), nullable=False)
    quantity_returned = Column(Integer, nullable=False)
    remarks = Column(String(500), nullable=True)  
    returned_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    returned_at = Column(DateTime, default=datetime.utcnow)

    borrow_item = relationship(
        "BorrowItem",
        back_populates="return_events"
    )

    returned_by = relationship(
        "User",
        back_populates="return_events"
    )