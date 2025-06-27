# """Stores sub processes for CPU heavy tasks like spaCy"""
# from concurrent.futures import ProcessPoolExecutor

# from app.workers.resume_parser import load_model

# executor = None

# def create_process_pool():
#     try:
#         global executor
#         executor = ProcessPoolExecutor(max_workers=2, initializer=load_model)
#     except Exception as e:
#         raise e