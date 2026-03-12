FROM debian:bullseye-slim

# 1. Install the list of build dependencies
RUN apt-get update && apt-get install -y \
    build-essential cmake pkg-config \
    libusb-1.0-0-dev libturbojpeg0-dev libglfw3-dev \
    git python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# 2. Download and compile the Kinect drivers (CPU ONLY for performance)
RUN git clone https://github.com/OpenKinect/libfreenect2.git /opt/libfreenect2 \
    && cd /opt/libfreenect2 \
    && mkdir build && cd build \
    && cmake .. -DENABLE_OPENGL=OFF -DENABLE_OPENCL=OFF \
    && make \
    && make install \
    && ldconfig

# 3. Install Python libraries in the correct order!
RUN pip3 install numpy Cython paho-mqtt --break-system-packages || pip3 install numpy Cython paho-mqtt

# Bypass the broken PyPI package and install directly from the developer's GitHub
RUN pip3 install git+https://github.com/r9y9/pylibfreenect2.git --break-system-packages || pip3 install git+https://github.com/r9y9/pylibfreenect2.git

# 4. Set up our working directory (MOVED TO /app TO AVOID HA OVERWRITE)
WORKDIR /app
COPY run.sh /app/
COPY motion.py /app/

# 5. Scrub Windows line endings and make executable
RUN sed -i 's/\r$//' /app/run.sh && \
    sed -i 's/\r$//' /app/motion.py && \
    chmod a+x /app/run.sh

# 6. TELL LINUX WHERE THE C++ LIBRARIES ARE HIDDEN
ENV LD_LIBRARY_PATH="/usr/local/lib:/usr/local/lib64:${LD_LIBRARY_PATH}"

CMD [ "/bin/bash", "/app/run.sh" ]
