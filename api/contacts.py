from typing import List

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.db import get_db
from schemas import ContactBase, ContactResponse
from services.contacts import ContactService

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
  skip: int = 0,
  limit: int = 100,
  first_name: str | None = None,
  last_name: str | None = None,
  email: str | None = None,
  db: AsyncSession = Depends(get_db),
):
  contact_service = ContactService(db)
  contacts = await contact_service.search_contacts(skip, limit, first_name, last_name, email)
  return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
  contact_service = ContactService(db)
  contact = await contact_service.get_contact(contact_id)
  if contact is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
    )
  return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactBase, db: AsyncSession = Depends(get_db)):
  contact_service = ContactService(db)
  return await contact_service.create_contact(body)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
  body: ContactBase, contact_id: int, db: AsyncSession = Depends(get_db)
):
  contact_service = ContactService(db)
  contact = await contact_service.update_contact(contact_id, body)
  if contact is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
    )
  return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: AsyncSession = Depends(get_db)):
  contact_service = ContactService(db)
  contact = await contact_service.remove_contact(contact_id)
  if contact is None:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
    )
  return contact

@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(db: AsyncSession = Depends(get_db)):
  contact_service = ContactService(db)
  contacts = await contact_service.get_upcoming_birthdays()
  return contacts

