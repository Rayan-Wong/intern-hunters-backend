import io
import uuid

import aioboto3
import aiofiles

from app.exceptions.internship_listings_exceptions import R2Down
from app.core.config import get_settings

class R2:
    def __init__(self):
        """Initialises boto3 session"""
        self.settings = get_settings()
        self.session = aioboto3.Session(
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key
        )

    async def upload_resume(self,
        file: io.BytesIO,
        user_id: uuid.UUID
    ):
        """Uploads resume to R2"""
        try:
            async with self.session.client(
                service_name="s3",
                endpoint_url=self.settings.r2_bucket_url,
                region_name=self.settings.r2_region
            ) as s3:
                await s3.upload_fileobj(
                    file,
                    self.settings.r2_bucket_name,
                    f"{user_id}/resume.pdf"
                )
        except Exception as e:
            raise R2Down from e