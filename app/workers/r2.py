import io
import uuid

import aioboto3
from aiofiles import open as async_open
import aiofiles.os as os
from pathlib import Path

from app.exceptions.internship_listings_exceptions import R2Down
from app.exceptions.resume_creator_exceptions import CacheFail
from app.core.config import get_settings

class R2:
    def __init__(self):
        """Initialises boto3 session"""
        self.settings = get_settings()
        self.session = aioboto3.Session(
            aws_access_key_id=self.settings.aws_access_key_id,
            aws_secret_access_key=self.settings.aws_secret_access_key
        )

    async def upload_resume(
        self,
        file: io.BytesIO,
        user_id: uuid.UUID
    ):
        """Uploads resume to R2 and stores in local for caching"""
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
            file.seek(0)
            await self.__cache(file, user_id)
        except CacheFail as e:
            raise CacheFail from e
        except Exception as e:
            raise R2Down from e
    
    async def download_resume(
        self,
        user_id: uuid.UUID
    ) -> io.BytesIO: 
        try:
            # check local cache first
            path = self.settings.local_cache_dir + f"/resumes/resume_{user_id}.pdf"
            if await os.path.exists(path):
                async with async_open(path, "rb") as f:
                    return io.BytesIO(await f.read())
            else:
                file = io.BytesIO()
                async with self.session.client(
                    service_name="s3",
                    endpoint_url=self.settings.r2_bucket_url,
                    region_name=self.settings.r2_region
                ) as s3:
                    await s3.download_fileobj(
                        self.settings.r2_bucket_name,
                        f"{user_id}/resume.pdf",
                        Fileobj=file
                    )
                file.seek(0)
                await self.__cache(file, user_id)
                return file
        except Exception as e:
            raise R2Down from e
        
    async def __cache(self, file: io.BytesIO, user_id: uuid.UUID):
        path = self.settings.local_cache_dir + f"/resumes/resume_{user_id}"
        try:
            async with async_open(path + ".tmp", "wb") as f:
                await f.write(file.getvalue())
            await os.replace(path + ".tmp", path + ".pdf")
        except Exception as e:
            raise CacheFail from e