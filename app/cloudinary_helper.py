import cloudinary
import cloudinary.uploader

from fastapi import HTTPException, status

from .config import settings


cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

IMAGE_FORMATS = {
    "jpg",
    "jpeg",
    "png",
    "gif",
    "webp",
}


def upload_image(
    file,
    folder: str = "resume_ready/images",
) -> str:
    """
    Upload an image to Cloudinary.
    """

    try:

        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="image",
            allowed_formats=list(IMAGE_FORMATS),
            transformation=[
                {
                    "quality": "auto",
                    "fetch_format": "auto",
                }
            ],
        )

        return result["secure_url"]

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Image upload failed: {str(e)}",
        )


def upload_audio(
    file,
    folder: str = "resume_ready/audio",
) -> str:
    """
    Upload an audio file to Cloudinary.
    """

    try:

        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="video",
        )

        return result["secure_url"]

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Audio upload failed: {str(e)}",
        )


def upload_file(
    file,
    folder: str = "resume_ready/files",
) -> str:
    """
    Upload any supported file.
    """

    try:

        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto",
        )

        return result["secure_url"]

    except Exception as e:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"File upload failed: {str(e)}",
        )