# Use AWS Lambda Python 3.11 base image
FROM public.ecr.aws/lambda/python:3.11

# Install ALL system dependencies needed for ML packages
RUN yum update -y && yum install -y \
    gcc \
    gcc-c++ \
    zlib-devel \
    libjpeg-devel \
    freetype-devel \
    openssl-devel \
    libffi-devel \
    && yum clean all

# Set ALL environment variables for cache directories
ENV HF_HOME=/tmp \
    HF_DATASETS_CACHE=/tmp \
    TRANSFORMERS_CACHE=/tmp \
    HUGGINGFACE_HUB_CACHE=/tmp \
    SENTENCE_TRANSFORMERS_HOME=/tmp \
    TORCH_HOME=/tmp \
    XDG_CACHE_HOME=/tmp \
    TMPDIR=/tmp

# Copy and install Python requirements
COPY requirements-container.txt ${LAMBDA_TASK_ROOT}
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-container.txt

# Copy function code
COPY lambda_function_semantic.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD ["lambda_function_semantic.lambda_handler"] 