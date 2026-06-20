from .. import models, schemas,oauth2
from fastapi import FastAPI,Response,status,HTTPException,Depends,APIRouter,File, UploadFile, Form
from sqlalchemy.orm import Session
from ..database import engine, get_db
from typing import List,Optional
from sqlalchemy import func, or_

from ..cloudinary_helper import upload_image
router=APIRouter(
    prefix="/posts",
    tags=['posts']
)

# @router.get("/",response_model=List[schemas.Post])
@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db: Session=Depends(get_db),current_user :int=Depends(oauth2.get_current_user),limit: int=10,skip: int=0,search: Optional[str]=""):
    # cursor.execute(""" SELECT * FROM posts""")
    # posts=cursor.fetchall()
    print(limit)
    # posts=db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    posts=db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    

    return posts




@router.post("/",status_code=status.HTTP_201_CREATED,response_model=schemas.Post)
# def create_posts(payload: dict=Body(...)):
def create_posts(
    title: str = Form(...),
    content: str = Form(...),
    published: bool = Form(True),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),current_user = Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title,content,published) VALUES (%s,%s,%s) RETURNING *""",(post.title,post.content,post.published))
    # new_post=cursor.fetchone()
    # conn.commit()
    image_url = None

    if image:
        image_url = upload_image(
        image.file)
    new_post = models.Post(
    title=title,
    content=content,
    published=published,
    owner_id=current_user.id,
    image_url=image_url)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/feed", response_model=list[schemas.PostOut])
def get_feed(
    db: Session = Depends(get_db),
    current_user = Depends(oauth2.get_current_user)
):

    following_users = (
        db.query(models.Follow.following_id)
        .filter(
            models.Follow.follower_id == current_user.id
        )
        .subquery()
    )

    posts = (
        db.query(
            models.Post,
            func.count(models.Vote.post_id).label("votes")
        )
        .join(
            models.Vote,
            models.Vote.post_id == models.Post.id,
            isouter=True
        )
        .filter(
            or_(
                models.Post.owner_id.in_(following_users),
                models.Post.owner_id == current_user.id
            )
        )
        .group_by(models.Post.id)
        .order_by(models.Post.created_at.desc())
        .all()
    )

    return posts
  
@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id: int,db: Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):   
    # cursor.execute(""" SELECT * FROM posts WHERE "Id" = %s """,(str(id),))   
    # post=cursor.fetchone()  
    # post=db.query(models.Post).filter(models.Post.id==id).first()
    post=db.query(models.Post,func.count(models.Vote.post_id).label("votes")).join(models.Vote,models.Vote.post_id==models.Post.id,isouter=True).group_by(models.Post.id).filter(models.Post.id==id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    #     response.status_code=status.HTTP_404_NOT_FOUND
    #     return {"message": f" post with id: {id} was not found"}
    
    return post


@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session=Depends(get_db),current_user :int=Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE "Id"=%s  RETURNING *""",(str(id),))
    # deleted_post=cursor.fetchone()
    # conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)  #here post is the query , to run this u used first in the seconf line
    post=post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    
    if post.owner_id!= current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="not authorized to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    #find the index in the array that has 

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int,updated_post:schemas.PostCreate,db: Session=Depends(get_db),current_user:int=Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET "title"=%s,"content"=%s,published=%s WHERE "Id"=%s RETURNING *""",(post.title,post.content,post.published,str(id)))
    # updated_post=cursor.fetchone()
    # conn.commit()
    post_query=db.query(models.Post).filter(models.Post.id==id)
    post=post_query.first()
    if post==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} does not exist")
    post_query.update(updated_post.dict(),synchronize_session=False)
    
    if post.owner_id!=current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="not authorized to perform requested action")
    
    db.commit()
    return post_query.first()

