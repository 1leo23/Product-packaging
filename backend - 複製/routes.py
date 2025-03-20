from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List

from models import Member, MemberUpdate

router = APIRouter()


@router.post("/", response_description="Create a new account", status_code=status.HTTP_201_CREATED, response_model=Member)
def create_member(request: Request, member: Member = Body(...)):
    # 檢查帳號是否已存在
    existing_member = request.app.database["member_data"].find_one(
        {"account": member.account}
    )
    if existing_member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account already exists")

    # 新增會員
    member = jsonable_encoder(member)
    new_member = request.app.database["member_data"].insert_one(member)
    created_member = request.app.database["member_data"].find_one(
        {"_id": new_member.inserted_id}
    )

    return created_member


@router.get("/", response_description="List all member", response_model=List[Member])
def list_memberships(request: Request):
    books = list(request.app.database["member_data"].find(limit=100))
    return books


@router.get("/{account}", response_description="Get member by id", response_model=Member)
def find_member(account: str, request: Request):
    if (member := request.app.database["member_data"].find_one({"account": account})) is not None:
        return member

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Member with account {account} not found")


@router.patch("/{account}", response_description="Update member info", response_model=Member)
def update_member(account: str, request: Request, member: MemberUpdate = Body(...)):
    member = {k: v for k, v in member.dict().items() if v is not None}

    if len(member) >= 1:
        update_result = request.app.database["member_data"].update_one(
            {"account": account}, {"$set": member}
        )

        if update_result.modified_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Member with ID {account} not found")

    if (
        existing_book := request.app.database["member_data"].find_one({"account": account})
    ) is not None:
        return existing_book

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Member with ID {account} not found")


@router.delete("/{account}", response_description="Delete account")
def delete_member(account: str, request: Request, response: Response):
    delete_result = request.app.database["member_data"].delete_one(
        {"account": account})

    if delete_result.deleted_count == 1:
        response.status_code = status.HTTP_204_NO_CONTENT
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Member with ID {account} not found")