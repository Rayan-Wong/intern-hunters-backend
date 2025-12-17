"""Modules for boto3 and its dependencies"""
import io
import uuid

import aioboto3
from aiofiles import open as async_open
import aiofiles.os as os

from app.exceptions.internship_listings_exceptions import R2Down
from app.exceptions.resume_creator_exceptions import CacheFail
from app.core.config import get_settings
from app.core.timer import timed
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class R2:
    """Class for R2 upload and download"""
    def __init__(self):
        """Initialises boto3 session"""
        self.settings = get_settings()
        self.session = aioboto3.Session(
            aws_access_key_id=self.settings.r2_access_key_id,
            aws_secret_access_key=self.settings.r2_secret_access_key
        )

    @timed("R2 Upload")
    async def upload_resume(
        self,
        file: io.BytesIO,
        user_id: uuid.UUID
    ):
        """Uploads resume to R2 and stores in local for caching"""
        try:
            logger.info(f"Beginning resume upload for {user_id}.")
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
            logger.info(f"Resume upload for {user_id} successful, beginning caching.")
            await self.__cache(file, user_id)
        except CacheFail as e:
            pass
        except Exception as e:
            logger.error(f"Failed to upload {user_id}'s resume from R2.")
            raise R2Down from e

    @timed("R2 Download")
    async def download_resume(
        self,
        user_id: uuid.UUID
    ) -> io.BytesIO:
        """Retrieves from local cache first, if not R2"""
        try:
            # check local cache first
            path = self.settings.local_cache_dir + f"/resumes/resume_{user_id}.pdf"
            if await os.path.exists(path):
                logger.info(f"{user_id}'s resume found in cache.")
                try:
                    async with async_open(path, "rb") as f:
                        return io.BytesIO(await f.read())
                except Exception as e:
                    logger.info(f"Failed to retrieve {user_id}'s from cache, falling back to R2.")
                    pass
            logger.info(f"{user_id}'s resume not in cache. Downloading from R2.")
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
            logger.info(f"{user_id}'s resume downloaded, beginning caching.")
            try:
                await self.__cache(file, user_id)
            except CacheFail as e:
                pass
            return file
        except Exception as e:
            logger.error(f"Failed to retrieve {user_id}'s resume from R2.")
            raise R2Down from e

    async def __cache(self, file: io.BytesIO, user_id: uuid.UUID):
        await os.makedirs(self.settings.local_cache_dir + "/resumes", exist_ok=True)
        path = self.settings.local_cache_dir + f"/resumes/resume_{user_id}"
        try:
            async with async_open(path + ".tmp", "wb") as f:
                await f.write(file.getvalue())
            await os.replace(path + ".tmp", path + ".pdf")
            logger.info(f"Cached {user_id}'s resume.")
        except Exception as e:
            logger.error(f"Failed to cache {user_id}'s resume.")
            try:
                await os.remove(path + ".tmp")
            except FileNotFoundError:
                pass
            raise CacheFail from e
