from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Category
from ..schemas import CategoryCreate, CategoryPatch, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryRead])
def list_categories(
    db: Session = Depends(get_db), skip: int = 0, limit: int = Query(50, le=200)
) -> list[CategoryRead]:
    stmt = select(Category).order_by(desc(Category.created_at))
    rows = db.execute(stmt.offset(skip).limit(limit)).scalars().all()
    return [CategoryRead.model_validate(row) for row in rows]


@router.post("/", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> CategoryRead:
    # Check for duplicate name
    existing = db.execute(
        select(Category).where(Category.name == payload.name)
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Category with this name already exists")

    category = Category(name=payload.name, description=payload.description)
    db.add(category)
    db.flush()
    db.refresh(category)
    return CategoryRead.model_validate(category)


@router.get("/{category_id}", response_model=CategoryRead)
def get_category(category_id: int, db: Session = Depends(get_db)) -> CategoryRead:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
def patch_category(
    category_id: int, payload: CategoryPatch, db: Session = Depends(get_db)
) -> CategoryRead:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if payload.name is not None:
        # Check for duplicate name (excluding current category)
        existing = db.execute(
            select(Category).where(Category.name == payload.name).where(Category.id != category_id)
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(status_code=400, detail="Category with this name already exists")
        category.name = payload.name

    if payload.description is not None:
        category.description = payload.description

    db.add(category)
    db.flush()
    db.refresh(category)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.flush()
