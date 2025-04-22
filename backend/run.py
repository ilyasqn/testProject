import uvicorn

from loguru import logger

if __name__ == '__main__':
    logger.info("Uvicorn server started")
    uvicorn.run("src.main:app", host='0.0.0.0', port=8000, log_level="error")