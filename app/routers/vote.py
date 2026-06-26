from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from .. import schemas, database, models, oauth2
from ..services import notification_service

router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    post = (
        db.query(models.Post)
        .filter(models.Post.id == vote.post_id)
        .first()
    )

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post {vote.post_id} not found",
        )

    vote_query = (
        db.query(models.Vote)
        .filter(
            models.Vote.post_id == vote.post_id,
            models.Vote.user_id == current_user.id,
        )
    )

    found_vote = vote_query.first()

    # ==========================
    # LIKE
    # ==========================

    if vote.dir == 1:

        if found_vote:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Already voted on this post",
            )

        new_vote = models.Vote(
            post_id=vote.post_id,
            user_id=current_user.id,
        )

        db.add(new_vote)
        db.commit()

        # Create notification
        if post.owner_id != current_user.id:
            notification_service.create_notification(
                recipient_id=post.owner_id,
                actor_id=current_user.id,
                notification_type="LIKE",
                reference_id=post.id,
                db=db,
            )

        return {
            "message": "Vote added"
        }

    # ==========================
    # REMOVE LIKE
    # ==========================

    if not found_vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found",
        )

    vote_query.delete(synchronize_session=False)
    db.commit()

    return {
        "message": "Vote removed"
    }