from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from ..services import notification_service
from sqlalchemy.orm import Session, joinedload
router = APIRouter(tags=["Comments"])

@router.post(
    "/posts/{post_id}/comments",
    response_model=schemas.CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    post_id: int,
    comment: schemas.CommentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    post = (
        db.query(models.Post)
        .filter(models.Post.id == post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    new_comment = models.Comment(
        content=comment.content,
        user_id=current_user.id,
        post_id=post_id,
    )

    db.add(new_comment)
    db.commit()

    # Reload with the user relationship
    new_comment = (
        db.query(models.Comment)
        .options(joinedload(models.Comment.user))
        .filter(models.Comment.id == new_comment.id)
        .first()
    )

    # Notify the post owner
    if post.owner_id != current_user.id:
        notification_service.create_notification(
            recipient_id=post.owner_id,
            actor_id=current_user.id,
            notification_type="COMMENT",
            reference_id=post.id,
            db=db,
        )

    return new_comment


@router.get(
    "/posts/{post_id}/comments",
    response_model=list[schemas.CommentOut],
)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    skip: int = Query(0, ge=0),
):
    return (
        db.query(models.Comment)
        .options(joinedload(models.Comment.user))
        .filter(models.Comment.post_id == post_id)
        .order_by(models.Comment.created_at)
        .limit(limit)
        .offset(skip)
        .all()
    )

@router.put("/comments/{comment_id}", response_model=schemas.CommentOut)
def update_comment(
    comment_id: int,
    updated_comment: schemas.CommentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    comment_query = db.query(models.Comment).filter(models.Comment.id == comment_id)
    comment = comment_query.first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    comment_query.update({"content": updated_comment.content}, synchronize_session=False)
    db.commit()
    return comment_query.first()


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    comment_query = db.query(models.Comment).filter(models.Comment.id == comment_id)
    comment = comment_query.first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    comment_query.delete(synchronize_session=False)
    db.commit()
