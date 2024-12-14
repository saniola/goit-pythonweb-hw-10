from typing import List

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from database.models import Contact, User
from schemas import ContactBase

class ContactRepository:
  def __init__(self, session: AsyncSession):
    self.db = session

  async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
    stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
    contacts = await self.db.execute(stmt)
    return contacts.scalars().all()

  async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    contact = await self.db.execute(stmt)
    return contact.scalar_one_or_none()

  async def create_contact(self, body: ContactBase, user: User) -> Contact:
    if body.birthday and body.birthday.tzinfo:
      body.birthday = body.birthday.replace(tzinfo=None)
    contact = Contact(
      **body.model_dump(exclude_unset=True),
      user=user
    )
    self.db.add(contact)
    await self.db.commit()
    await self.db.refresh(contact)
    return await self.get_contact_by_id(contact.id, user)

  async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
    contact = await self.get_contact_by_id(contact_id, user)
    if contact:
      await self.db.delete(contact)
      await self.db.commit()
    return contact

  async def update_contact(
    self, contact_id: int, body: ContactBase, user: User) -> Contact | None:
    if body.birthday and body.birthday.tzinfo:
      body.birthday = body.birthday.replace(tzinfo=None)
    contact = await self.get_contact_by_id(contact_id, user)
    if contact:
      for key, value in body.dict(exclude_unset=True).items():
        setattr(contact, key, value)

      await self.db.commit()
      await self.db.refresh(contact)

    return contact

  async def search_contacts(
      self, skip: int, limit: int, first_name: str | None, last_name: str | None, email: str | None,  user: User,
  ) -> List[Contact]:
    stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)

    if first_name or last_name or email:
      filters = []
      if first_name:
        filters.append(Contact.first_name.ilike(f"%{first_name}%"))
      if last_name:
        filters.append(Contact.last_name.ilike(f"%{last_name}%"))
      if email:
        filters.append(Contact.email.ilike(f"%{email}%"))
      stmt = stmt.filter(or_(*filters))

    results = await self.db.execute(stmt)
    return results.scalars().all()
  
  async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
    today = datetime.utcnow()
    next_week = today + timedelta(days=7)

    stmt = select(Contact).filter(
      and_(
        Contact.user == user,
        Contact.birthday >= today.replace(hour=0, minute=0, second=0, microsecond=0),
        Contact.birthday <= next_week.replace(hour=23, minute=59, second=59, microsecond=999999),
      )
    )

    results = await self.db.execute(stmt)
    return results.scalars().all()

